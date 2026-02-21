#!/usr/bin/env python3
"""
Kleinanzeigen Scraper API - Service 1
Scrapes kleinanzeigen.de and returns structured listing data
"""

from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import time
from functools import wraps
import logging
import sys
import random
import threading
import uuid
from flask_swagger_ui import get_swaggerui_blueprint

# ============================================================================
# Configure Logging FIRST (at module level - works with both Flask dev and Gunicorn)
# ============================================================================

log_level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
log_level = getattr(logging, log_level_name, logging.INFO)

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logging.getLogger().setLevel(log_level)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

PORT = int(os.getenv('PORT', 3000))
VERSION = '1.0.0'

logger.info(f'Logging initialized at {log_level_name} level')

# UI Configuration (default: enabled)
ENABLE_SWAGGER_UI = os.getenv('ENABLE_SWAGGER_UI', 'true').lower() in ('true', '1', 'yes')

# Scraper configuration (anti-detection)
SCRAPER_MIN_DELAY = float(os.getenv('SCRAPER_MIN_DELAY', '2'))
SCRAPER_MAX_DELAY = float(os.getenv('SCRAPER_MAX_DELAY', '5'))
SCRAPER_TIMEOUT = int(os.getenv('SCRAPER_TIMEOUT', '10'))  # Legacy single timeout
SCRAPER_TIMEOUT_CONNECT = int(os.getenv('SCRAPER_TIMEOUT_CONNECT', '5'))  # Connection timeout
SCRAPER_TIMEOUT_READ = int(os.getenv('SCRAPER_TIMEOUT_READ', '30'))  # Read timeout
SCRAPER_MAX_RETRIES = int(os.getenv('SCRAPER_MAX_RETRIES', '3'))  # Max retry attempts

# User-Agent rotation (appear as different browsers)
USER_AGENTS = [
    # Chrome on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    # Chrome on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    # Firefox on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    # Firefox on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    # Safari on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    # Edge on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
]

logger.info(f'Scraper delays configured: {SCRAPER_MIN_DELAY}-{SCRAPER_MAX_DELAY} seconds')

# Load API keys from Docker secret file OR environment variable
API_KEYS_FILE = os.getenv('API_KEYS_FILE', '/run/secrets/api_keys')
API_KEYS = []

if os.path.exists(API_KEYS_FILE):
    print(f'✓ Loading API keys from file: {API_KEYS_FILE}')
    with open(API_KEYS_FILE, 'r') as f:
        API_KEYS = [line.strip() for line in f if line.strip() and not line.startswith('#')]
elif os.getenv('API_KEYS'):
    print('✓ Loading API keys from environment variable')
    API_KEYS = [k.strip() for k in os.getenv('API_KEYS').split(',') if k.strip()]
else:
    print('⚠️  WARNING: No API keys configured!')

print(f'Loaded {len(API_KEYS)} API key(s)')

# Track startup time for uptime calculation
START_TIME = time.time()

# Global rate limiting state (thread-safe)
_last_request_lock = threading.Lock()
_last_request_time = None

# ============================================================================
# Flask App Setup
# ============================================================================

app = Flask(__name__)

# ============================================================================
# Swagger UI Configuration
# ============================================================================

@app.route('/openapi.yaml')
def openapi_spec():
    """Serve the OpenAPI specification file"""
    with open('openapi.yaml', 'r') as f:
        return f.read(), 200, {'Content-Type': 'text/yaml'}

SWAGGER_URL = '/docs'
API_URL = '/openapi.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Kleinanzeigen Scraper API",
        'defaultModelsExpandDepth': 1
    }
)

# Register Swagger UI conditionally at module level
if ENABLE_SWAGGER_UI:
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    logger.info(f'✓ Swagger UI enabled at {SWAGGER_URL}')
else:
    @app.route('/docs')
    @app.route('/docs/<path:path>')
    def docs_disabled(path=None):
        return jsonify({'error': 'Not found'}), 404
    logger.info('✗ Swagger UI disabled')

# ============================================================================
# Rate Limiting & Reliability Functions
# ============================================================================

def enforce_rate_limit():
    """
    Enforce configured delay between requests (anti-detection)
    Uses SCRAPER_MIN_DELAY and SCRAPER_MAX_DELAY configuration
    Thread-safe implementation
    """
    global _last_request_time
    
    with _last_request_lock:
        if _last_request_time:
            elapsed = (datetime.now() - _last_request_time).total_seconds()
            required_delay = random.uniform(SCRAPER_MIN_DELAY, SCRAPER_MAX_DELAY)
            
            if elapsed < required_delay:
                sleep_time = required_delay - elapsed
                logger.info(f'Rate limiting: sleeping for {sleep_time:.2f}s (last request was {elapsed:.2f}s ago)')
                time.sleep(sleep_time)
        
        _last_request_time = datetime.now()

def make_resilient_request(url, headers, max_retries=None):
    """
    Make HTTP request with retry logic and fresh connections
    
    Args:
        url: URL to fetch
        headers: Request headers
        max_retries: Maximum retry attempts (uses SCRAPER_MAX_RETRIES if not specified)
    
    Returns:
        requests.Response object
    
    Raises:
        requests.RequestException: After all retries exhausted
    """
    if max_retries is None:
        max_retries = SCRAPER_MAX_RETRIES
    
    last_exception = None
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.debug(f'Request attempt {attempt}/{max_retries}')
            
            # Use tuple timeout: (connect_timeout, read_timeout)
            response = requests.get(
                url, 
                headers=headers, 
                timeout=(SCRAPER_TIMEOUT_CONNECT, SCRAPER_TIMEOUT_READ)
            )
            
            # Check for various HTTP errors
            if response.status_code == 404:
                logger.warning(f'URL not found (404): {url}')
                raise requests.RequestException('URL not found - invalid search criteria or listing removed')
            elif response.status_code == 429:
                logger.warning('Rate limited (429)! Backing off...')
                time.sleep(60)  # Wait 1 minute
                raise requests.RequestException('Rate limited by server - too many requests')
            elif response.status_code == 403:
                logger.error('Access forbidden (403)! Possible IP block')
                raise requests.RequestException('Access forbidden - possible IP block')
            elif response.status_code >= 500:
                logger.error(f'Server error ({response.status_code})')
                raise requests.RequestException(f'Server error {response.status_code} - try again later')
            
            response.raise_for_status()
            logger.debug(f'Request successful on attempt {attempt}')
            return response
            
        except (requests.Timeout, requests.ConnectionError, requests.RequestException) as e:
            last_exception = e
            logger.warning(f'Request attempt {attempt}/{max_retries} failed: {str(e)}')
            
            if attempt < max_retries:
                # Exponential backoff: 1s, 2s, 4s, etc.
                backoff_time = 2 ** (attempt - 1)
                logger.info(f'Retrying in {backoff_time}s...')
                time.sleep(backoff_time)
            else:
                logger.error(f'All {max_retries} attempts failed for {url}')
                raise last_exception

# ============================================================================
# Middleware
# ============================================================================

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            logger.warning(f'Request to {request.path} rejected: Missing API key')
            return jsonify({
                'success': False,
                'error': 'Invalid or missing API key. Include X-API-Key header.'
            }), 401
        
        if api_key not in API_KEYS:
            logger.warning(f'Request to {request.path} rejected: Invalid API key')
            return jsonify({
                'success': False,
                'error': 'Invalid or missing API key. Include X-API-Key header.'
            }), 401
        
        logger.debug(f'Request to {request.path} authenticated successfully')
        return f(*args, **kwargs)
    
    return decorated_function

# ============================================================================
# Scraping Logic
# ============================================================================

def get_random_headers():
    """
    Generate random headers to appear as different browsers
    Helps avoid detection and blocking
    """
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }

def scrape_listings(path, since_id=None, request_id=None):
    """
    Scrape listings from kleinanzeigen.de with anti-detection measures
    
    Args:
        path: URL path (e.g., '/s-wohnzimmer/muenchen/tisch/k0c88l6411') or full URL
        since_id: Optional listing ID to stop at (for "new listings since" feature)
        request_id: Optional request ID for tracking (generated if not provided)
    
    Returns:
        List of listing dictionaries with 15 fields each
    """
    # Generate request ID for tracking
    if not request_id:
        request_id = str(uuid.uuid4())[:8]
    
    # Build full URL - only accept paths, not arbitrary URLs
    if path.startswith('/'):
        url = f'https://www.kleinanzeigen.de{path}'
    else:
        # Assume it's a path without leading slash
        url = f'https://www.kleinanzeigen.de/{path}'
    
    logger.info(f'[{request_id}] Starting scrape of URL: {url}')
    if since_id:
        logger.info(f'[{request_id}] Filtering for listings since ID: {since_id}')
    
    # OPTIMIZATION 1: Enforce rate limiting (anti-detection)
    logger.debug(f'[{request_id}] Enforcing rate limit...')
    enforce_rate_limit()
    
    # Use random headers to avoid detection
    headers = get_random_headers()
    selected_ua = headers['User-Agent'][:50] + '...'
    logger.debug(f'[{request_id}] Using User-Agent: {selected_ua}')
    
    # OPTIMIZATION 2: Use resilient request with retry logic
    logger.debug(f'[{request_id}] Fetching HTML from {url}')
    start_time = time.time()
    response = make_resilient_request(url, headers)
    fetch_duration = time.time() - start_time
    logger.info(f'[{request_id}] Successfully fetched HTML ({len(response.text)} bytes) in {fetch_duration:.2f}s')
    
    # Parse with BeautifulSoup (lxml parser is more forgiving with malformed HTML)
    logger.debug(f'[{request_id}] Parsing HTML with BeautifulSoup (lxml parser)')
    parse_start = time.time()
    soup = BeautifulSoup(response.text, 'lxml')
    articles = soup.select('article.aditem')
    parse_duration = time.time() - parse_start
    logger.info(f'[{request_id}] Found {len(articles)} article elements (parsing took {parse_duration:.2f}s)')
    
    listings = []
    
    for article in articles:
        listing_id = article.get('data-adid')
        
        # If since_id provided, stop when we reach it (return only newer listings)
        if since_id and listing_id == since_id:
            break
        
        # Extract all 15 fields
        listing = {
            # Core fields (always present)
            'id': listing_id,
            'url': 'https://www.kleinanzeigen.de' + article.get('data-href', ''),
            'title': None,
            'location': None,
            'image': None,
            'seller_type': 'PRO' if article.select_one('.badge-hint-pro-small-srp') else 'PRIVATE',
            
            # Optional fields
            'price': None,
            'image_count': None,
            'description': None,
            'posted_date': None,
            'shipping': None,
            'seller_name': None,
            'buy_now': False,
            'is_featured': False,
            'additional_info': []
        }
        
        # Title
        title_elem = article.select_one('a.ellipsis')
        if title_elem:
            listing['title'] = title_elem.get_text(strip=True)
        
        # Price
        price_elem = article.select_one('.aditem-main--middle--price-shipping--price')
        if price_elem:
            listing['price'] = price_elem.get_text(strip=True)
        
        # Location - extract postal code + district name, handling HTML entities
        location_elem = article.select_one('.aditem-main--top--left')
        if location_elem:
            import re
            from html import unescape
            
            # Get raw text (icons will appear as text, but we'll filter them)
            full_text = location_elem.get_text(separator=' ', strip=True)
            
            # Decode HTML entities like &#8203; (zero-width space)
            full_text = unescape(full_text)
            
            # Remove zero-width space character (U+200B)
            full_text = full_text.replace('\u200b', '')
            
            # Extract location using regex: postal code + district
            # Pattern matches: "80809 Milbertshofen - Am Hart" or "81479 Thalk.Obersendl.-Forsten-Fürstenr.-Solln"
            location_match = re.search(r'(\d{5}\s+[\w\s\-\.äöüÄÖÜß]+?)(?:\s+\d{5}|<|$)', full_text)
            if location_match:
                listing['location'] = location_match.group(1).strip()
            else:
                # Fallback: extract everything before first HTML tag or take first 100 chars
                clean_text = full_text.split('<')[0].strip()
                if clean_text:
                    listing['location'] = clean_text[:100]
        
        # Image
        img_elem = article.select_one('img')
        if img_elem and img_elem.get('src'):
            listing['image'] = img_elem['src']
        
        # Image count
        counter_elem = article.select_one('.galleryimage--counter')
        if counter_elem:
            try:
                listing['image_count'] = int(counter_elem.get_text(strip=True))
            except ValueError:
                pass
        
        # Description
        desc_elem = article.select_one('.aditem-main--middle--description')
        if desc_elem:
            listing['description'] = desc_elem.get_text(strip=True)
        
        # Posted date
        date_elem = article.select_one('.aditem-main--top--right')
        if date_elem:
            listing['posted_date'] = date_elem.get_text(strip=True)
        
        # Shipping - check article text
        article_text = article.get_text()
        if 'Versand möglich' in article_text:
            listing['shipping'] = 'Versand möglich'
        elif 'Nur Abholung' in article_text:
            listing['shipping'] = 'Nur Abholung'
        
        # Buy now
        listing['buy_now'] = 'Direkt kaufen' in article_text
        
        # Featured/promoted - check both article and parent <li> for promoted classes
        article_classes = article.get('class', [])
        parent_li = article.find_parent('li')
        parent_classes = parent_li.get('class', []) if parent_li else []
        listing['is_featured'] = (
            'is-highlight' in article_classes or 
            'is-topad' in article_classes or 
            'is-topad' in parent_classes or 
            'badge-topad' in parent_classes
        )
        
        # Additional info from bottom section (category-specific tags)
        for tag in article.select('.aditem-main--bottom .simpletag'):
            text = tag.get_text(strip=True)
            # Skip tags already captured in dedicated fields
            if text not in ['Versand möglich', 'Nur Abholung', 'Direkt kaufen']:
                listing['additional_info'].append(text)
        
        listings.append(listing)
        title = listing.get("title") or "N/A"
        logger.debug(f'[{request_id}] Extracted listing {listing_id}: {title[:50]}...')
    
    extraction_duration = time.time() - parse_start
    logger.info(f'[{request_id}] Successfully extracted {len(listings)} listings in {extraction_duration:.2f}s')
    logger.debug(f'[{request_id}] Scrape complete - Listings: {len(listings)}, Featured: {sum(1 for l in listings if l.get("is_featured"))}, Private: {sum(1 for l in listings if l.get("seller_type") == "PRIVATE")}, PRO: {sum(1 for l in listings if l.get("seller_type") == "PRO")}')
    return listings

# ============================================================================
# API Endpoints
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    uptime = int(time.time() - START_TIME)
    
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'uptime': uptime,
        'version': VERSION
    })

@app.route('/api/scrape', methods=['GET'])
@require_api_key
def scrape():
    """Scrape listings from kleinanzeigen.de search pages"""
    # Parse URL parameter - can be single URL or comma-separated list
    url_param = request.args.get('url', '')
    since_id = request.args.get('since')
    
    # Split by comma and strip whitespace
    urls = [u.strip() for u in url_param.split(',') if u.strip()]
    
    logger.info(f'API call to /api/scrape - URLs: {len(urls)}, since: {since_id}')
    
    if not urls:
        logger.warning('API call to /api/scrape rejected: Missing URL parameter')
        return jsonify({
            'success': False,
            'error': 'URL parameter or urls array required'
        }), 400
    
    try:
        # Generate request ID for tracking multi-URL request
        request_id = str(uuid.uuid4())[:8]
        logger.info(f'[{request_id}] Multi-URL scrape: {len(urls)} URL(s)')
        
        # Collect all listings from all URLs
        all_listings = []
        seen_ids = set()
        
        for i, url in enumerate(urls, 1):
            logger.info(f'[{request_id}] Scraping URL {i}/{len(urls)}: {url}')
            
            try:
                # Don't pass since_id to scrape_listings - we'll filter after collecting all
                listings = scrape_listings(url, since_id=None, request_id=request_id)
                
                # Deduplicate - some listings may appear in multiple searches
                for listing in listings:
                    if listing['id'] not in seen_ids:
                        all_listings.append(listing)
                        seen_ids.add(listing['id'])
                    else:
                        logger.debug(f'[{request_id}] Skipping duplicate listing: {listing["id"]}')
                
                logger.info(f'[{request_id}] URL {i}/{len(urls)}: Found {len(listings)} listings ({len(all_listings)} total after deduplication)')
                
            except Exception as e:
                logger.error(f'[{request_id}] Failed to scrape URL {i}/{len(urls)} ({url}): {str(e)}')
                # Continue with other URLs even if one fails
                continue
        
        # Sort by ID (descending) to get newest first
        all_listings.sort(key=lambda x: int(x['id']), reverse=True)
        
        # Filter by since_id if provided (only return listings with ID > since_id)
        if since_id:
            logger.debug(f'[{request_id}] Filtering {len(all_listings)} listings by since_id={since_id}')
            all_listings = [l for l in all_listings if int(l['id']) > int(since_id)]
            logger.info(f'[{request_id}] After since_id filter: {len(all_listings)} listings remain')
        
        result = {
            'success': True,
            'urls': urls if len(urls) > 1 else urls[0],  # Single URL as string, multiple as array
            'urlCount': len(urls),
            'scrapedAt': datetime.utcnow().isoformat() + 'Z',
            'count': len(all_listings),
            'listings': all_listings
        }
        
        # If since_id provided, add it to response
        if since_id:
            result['since'] = since_id
            result['newListingsCount'] = len(all_listings)
        
        logger.info(f'[{request_id}] Multi-URL scrape completed - {len(all_listings)} unique listings from {len(urls)} URL(s)')
        return jsonify(result)
    
    except requests.RequestException as e:
        logger.error(f'Network error in /api/scrape: {str(e)}')
        return jsonify({
            'success': False,
            'error': f'Failed to fetch URL: {str(e)}'
        }), 500
    
    except Exception as e:
        logger.error(f'Unexpected error in /api/scrape: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Scraping error: {str(e)}'
        }), 500

@app.route('/api/newest', methods=['GET'])
@require_api_key
def newest():
    """Get the newest listing from search pages"""
    # Parse URL parameter - can be single URL or comma-separated list
    url_param = request.args.get('url', '')
    
    # Split by comma and strip whitespace
    urls = [u.strip() for u in url_param.split(',') if u.strip()]
    
    logger.info(f'API call to /api/newest - URLs: {len(urls)}')
    
    if not urls:
        logger.warning('API call to /api/newest rejected: Missing URL parameter')
        return jsonify({
            'success': False,
            'error': 'URL parameter or urls array required'
        }), 400
    
    try:
        # Generate request ID for tracking multi-URL request
        request_id = str(uuid.uuid4())[:8]
        logger.info(f'[{request_id}] Multi-URL newest: {len(urls)} URL(s)')
        
        # Collect all listings from all URLs
        all_listings = []
        seen_ids = set()
        
        for i, url in enumerate(urls, 1):
            logger.info(f'[{request_id}] Scraping URL {i}/{len(urls)}: {url}')
            
            try:
                listings = scrape_listings(url, request_id=request_id)
                
                # Deduplicate - some listings may appear in multiple searches
                for listing in listings:
                    if listing['id'] not in seen_ids:
                        all_listings.append(listing)
                        seen_ids.add(listing['id'])
                
                logger.info(f'[{request_id}] URL {i}/{len(urls)}: Found {len(listings)} listings')
                
            except Exception as e:
                logger.error(f'[{request_id}] Failed to scrape URL {i}/{len(urls)} ({url}): {str(e)}')
                # Continue with other URLs even if one fails
                continue
        
        # Find newest listing (highest ID, non-featured)
        newest_listing = None
        
        # Filter out featured listings first
        non_featured = [l for l in all_listings if not l.get('is_featured', False)]
        
        if non_featured:
            # Sort by ID (descending) and take first
            non_featured.sort(key=lambda x: int(x['id']), reverse=True)
            newest_listing = non_featured[0]
        elif all_listings:
            # If all are featured, just take the one with highest ID
            all_listings.sort(key=lambda x: int(x['id']), reverse=True)
            newest_listing = all_listings[0]
        
        featured_count = sum(1 for l in all_listings if l.get('is_featured', False))
        logger.info(f'[{request_id}] Multi-URL newest completed - Newest ID: {newest_listing["id"] if newest_listing else "None"} from {len(urls)} URL(s) ({len(all_listings)} total, {featured_count} featured)')
        
        return jsonify({
            'success': True,
            'urls': urls if len(urls) > 1 else urls[0],
            'urlCount': len(urls),
            'scrapedAt': datetime.utcnow().isoformat() + 'Z',
            'newest': newest_listing
        })
    
    except requests.RequestException as e:
        logger.error(f'Network error in /api/newest: {str(e)}')
        return jsonify({
            'success': False,
            'error': f'Failed to fetch URL: {str(e)}'
        }), 500
    
    except Exception as e:
        logger.error(f'Unexpected error in /api/newest: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Scraping error: {str(e)}'
        }), 500

# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    # Get Flask debug mode from separate environment variable (default: False)
    # SECURITY: This should NEVER be true in production!
    # Use LOG_LEVEL=DEBUG for detailed logging without security risks
    flask_debug_env = os.getenv('FLASK_DEBUG', 'false').lower()
    flask_debug = flask_debug_env in ('true', '1', 'yes')
    
    print('=' * 60)
    print(f'Starting Kleinanzeigen Scraper API v{VERSION} (Flask Dev Server)')
    print(f'Listening on port {PORT}')
    print(f'Log level: {log_level_name}')
    print(f'Flask debug: {flask_debug}')
    print(f'Swagger UI: {"Enabled at /docs" if ENABLE_SWAGGER_UI else "Disabled"}')
    print('=' * 60)
    print('✓ Server ready (initialized at module level)')
    print('Endpoints:')
    print('  GET  /health          - Health check (public)')
    print('  GET  /api/scrape      - Scrape listings (protected)')
    print('  GET  /api/newest      - Get newest listing (protected)')
    print(f'  GET  /docs            - Swagger API documentation' if ENABLE_SWAGGER_UI else '')
    print('=' * 60)
    print('')
    
    # Enable reloader only in Flask debug mode
    flask_reloader = flask_debug
    
    if flask_debug:
        print('⚠️  WARNING: Flask DEBUG mode is ENABLED!')
        print('⚠️  This should NEVER be used in production!')
        print('⚠️  Set FLASK_DEBUG=false for production')
        print('⚠️  (You can still use LOG_LEVEL=DEBUG safely)')
        print('=' * 60)
        print('')
    
    app.run(host='0.0.0.0', port=PORT, debug=flask_debug, use_reloader=flask_reloader)
