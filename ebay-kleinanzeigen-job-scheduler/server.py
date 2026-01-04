#!/usr/bin/env python3
"""
Kleinanzeigen Job Scheduler
Web-based job scheduler with APScheduler integration
"""

from flask import Flask, request, jsonify, render_template, g
from flask_cors import CORS
from werkzeug.security import check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import requests
import sqlite3
import os
import logging
import sys
import json
import jwt
import base64
from functools import wraps
from flask_swagger_ui import get_swaggerui_blueprint

# Import database module
import database

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.getenv('SESSION_SECRET', 'change-this-secret-key-in-production')
CORS(app)

# ============================================================================
# Swagger UI Configuration (flask-swagger-ui)
# ============================================================================

# Serve OpenAPI spec as static file
@app.route('/openapi.yaml')
def openapi_spec():
    """Serve the OpenAPI specification file"""
    with open('openapi.yaml', 'r') as f:
        return f.read(), 200, {'Content-Type': 'text/yaml'}

# Configure Swagger UI
SWAGGER_URL = '/docs'
API_URL = '/openapi.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Kleinanzeigen Job Scheduler API",
        'defaultModelsExpandDepth': 1  # Show schemas section
    }
)

# Conditionally register Swagger UI blueprint based on ENABLE_SWAGGER_UI
# This will be done after ENABLE_SWAGGER_UI is set in __main__





# Logger will be configured in __main__ section
logger = logging.getLogger(__name__)

# Configuration
PORT = int(os.getenv('PORT', 3001))
VERSION = '1.0.0'

# UI Configuration (default: enabled)
ENABLE_SWAGGER_UI = os.getenv('ENABLE_SWAGGER_UI', 'true').lower() in ('true', '1', 'yes')
ENABLE_WEB_UI = os.getenv('ENABLE_WEB_UI', 'true').lower() in ('true', '1', 'yes')

# APScheduler setup
scheduler = BackgroundScheduler(daemon=True)

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET', app.secret_key)
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 604800))  # 7 days

# Encryption Configuration
# Generate a key from app secret (in production, use a separate env variable)
ENCRYPTION_KEY = base64.urlsafe_b64encode(app.secret_key[:32].ljust(32).encode())
cipher_suite = Fernet(ENCRYPTION_KEY)

# Sensitive config keys that should be encrypted
SENSITIVE_KEYS = {'scraper_api_key', 'matterbridge_token'}

def encrypt_value(value):
    """Encrypt a sensitive value"""
    if not value:
        return value
    return cipher_suite.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value):
    """Decrypt a sensitive value"""
    if not encrypted_value:
        return encrypted_value
    try:
        return cipher_suite.decrypt(encrypted_value.encode()).decode()
    except Exception:
        return encrypted_value  # Return as-is if decryption fails (backwards compatibility)

# ============================================================================
# JWT Helper Functions
# ============================================================================

def generate_token(user_id, username, token_type='access'):
    """Generate JWT token"""
    expires_delta = JWT_ACCESS_TOKEN_EXPIRES if token_type == 'access' else JWT_REFRESH_TOKEN_EXPIRES
    
    payload = {
        'user_id': user_id,
        'username': username,
        'type': token_type,
        'exp': datetime.utcnow() + timedelta(seconds=expires_delta),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def decode_token(token):
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_token(f):
    """Decorator for token-based authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if auth_header:
            # Accept both "Bearer TOKEN" and just "TOKEN"
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Remove 'Bearer ' prefix
            else:
                token = auth_header  # Use as-is
        
        if not token:
            return jsonify({'success': False, 'error': 'Missing authentication token'}), 401
        
        # Decode token
        payload = decode_token(token)
        if not payload:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
        
        # Verify it's an access token
        if payload.get('type') != 'access':
            return jsonify({'success': False, 'error': 'Invalid token type'}), 401
        
        # Store user info in g for access in route
        g.user_id = payload['user_id']
        g.username = payload['username']
        
        return f(*args, **kwargs)
    
    return decorated

# ============================================================================
# Helper Functions
# ============================================================================

def get_config(key, default=None):
    """Get configuration value from database (decrypts sensitive values)"""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM global_config WHERE key = ?', (key,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return default
    
    # Decrypt sensitive values
    if key in SENSITIVE_KEYS:
        return decrypt_value(row['value'])
    
    return row['value']

def call_scraper_api_scrape(url, since=None):
    """Call Scraper API - get all or new listings"""
    scraper_url = get_config('scraper_api_url', 'http://localhost:3000')
    scraper_api_key = get_config('scraper_api_key', 'test-key-123')
    timeout = int(get_config('scraper_request_timeout', '30'))
    
    params = {'url': url}
    if since:
        params['since'] = since
    
    headers = {'X-API-Key': scraper_api_key}
    
    response = requests.get(
        f'{scraper_url}/api/scrape',
        params=params,
        headers=headers,
        timeout=timeout
    )
    response.raise_for_status()
    return response.json()

def call_scraper_api_newest(url):
    """Call Scraper API - get only newest non-promoted listing"""
    scraper_url = get_config('scraper_api_url', 'http://localhost:3000')
    scraper_api_key = get_config('scraper_api_key', 'test-key-123')
    timeout = int(get_config('scraper_request_timeout', '30'))
    
    params = {'url': url}
    headers = {'X-API-Key': scraper_api_key}
    
    response = requests.get(
        f'{scraper_url}/api/newest',
        params=params,
        headers=headers,
        timeout=timeout
    )
    response.raise_for_status()
    return response.json()

def send_notification(job_data, listings):
    """Send notification via Matterbridge"""
    if not job_data.get('notify_enabled'):
        return False
    
    # Get Matterbridge config from global settings
    matterbridge_url = get_config('matterbridge_url', 'http://192.168.10.10:4242')
    matterbridge_token = get_config('matterbridge_token', '')
    gateway = get_config('matterbridge_gateway', 'gateway_ebaykleinanzeigen')
    username = get_config('matterbridge_username', 'Kleinanzeigen Bot')
    language = get_config('notification_language', 'de')  # de or en
    
    if not matterbridge_token:
        logger.warning('Matterbridge token not configured, skipping notification')
        return False
    
    # Translation dictionary
    translations = {
        'de': {
            'new_listing': 'Neue Anzeige',
            'title': 'Titel',
            'posted': 'Veröffentlicht',
            'image': 'Bild',
            'description': 'Beschreibung',
            'link': 'Link',
            'location': 'Standort',
            'price': 'Preis',
            'seller': 'Verkäufer',
            'shipping': 'Versand',
            'id': 'ID',
            'images': 'Bilder',
            'additional_info': 'Zusatzinfo'
        },
        'en': {
            'new_listing': 'New Listing',
            'title': 'Title',
            'posted': 'Posted',
            'image': 'Image',
            'description': 'Description',
            'link': 'Link',
            'location': 'Location',
            'price': 'Price',
            'seller': 'Seller',
            'shipping': 'Shipping',
            'id': 'ID',
            'images': 'Images',
            'additional_info': 'Additional Info'
        }
    }
    
    # Get translations for selected language (fallback to German)
    t = translations.get(language, translations['de'])
    
    # Send each listing as a separate message to Matterbridge
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {matterbridge_token}'
    }
    
    success_count = 0
    
    for idx, listing in enumerate(listings, 1):
        # Build detailed message for this listing
        message_parts = []
        
        # Job Name header
        message_parts.append(f"🔔 **{job_data['name']}** - {t['new_listing']} {idx}/{len(listings)}")
        message_parts.append("")  # Empty line
        
        # Title (always present)
        if listing.get('title'):
            message_parts.append(f"📌 **{t['title']}:** {listing['title']}")
        
        # Posted date
        if listing.get('posted_date'):
            message_parts.append(f"🕐 **{t['posted']}:** {listing['posted_date']}")
        
        # Image (show if available)
        if listing.get('image'):
            message_parts.append(f"🖼️ **{t['image']}:** {listing['image']}")
        
        # Description
        if listing.get('description'):
            # Truncate long descriptions
            desc = listing['description']
            if len(desc) > 300:
                desc = desc[:297] + '...'
            message_parts.append(f"📝 **{t['description']}:** {desc}")
        
        # URL (always show)
        if listing.get('url'):
            message_parts.append(f"🔗 **{t['link']}:** {listing['url']}")
        
        # Location
        if listing.get('location'):
            message_parts.append(f"📍 **{t['location']}:** {listing['location']}")
        
        # Price
        if listing.get('price'):
            message_parts.append(f"💰 **{t['price']}:** {listing['price']}")
        
        # Seller type
        if listing.get('seller_type'):
            seller_emoji = "👤" if listing['seller_type'] == "PRIVATE" else "🏢"
            message_parts.append(f"{seller_emoji} **{t['seller']}:** {listing['seller_type']}")
        
        # Shipping
        if listing.get('shipping'):
            message_parts.append(f"📦 **{t['shipping']}:** {listing['shipping']}")
        
        # ID
        if listing.get('id'):
            message_parts.append(f"🆔 **{t['id']}:** {listing['id']}")
        
        # Image count
        if listing.get('image_count'):
            message_parts.append(f"📸 **{t['images']}:** {listing['image_count']}")
        
        # Additional info (if present and not empty)
        if listing.get('additional_info') and len(listing['additional_info']) > 0:
            info_text = ', '.join(listing['additional_info'])
            message_parts.append(f"ℹ️ **{t['additional_info']}:** {info_text}")
        
        message_parts.append("")  # Empty line at end
        message_parts.append("─" * 40)  # Separator
        
        message = '\n'.join(message_parts)
        
        # Send to Matterbridge
        try:
            payload = {
                'text': message,
                'username': username,
                'gateway': gateway
            }
            
            logger.debug(f'Sending listing {idx}/{len(listings)} to Matterbridge')
            logger.debug(f'Payload: {json.dumps(payload, indent=2)}')
            
            response = requests.post(
                f'{matterbridge_url}/api/message',
                json=payload,
                headers=headers,
                timeout=10
            )
            
            response.raise_for_status()
            success_count += 1
            logger.info(f'✅ Listing {idx}/{len(listings)} sent successfully')
            
        except Exception as e:
            logger.error(f'❌ Failed to send listing {idx}/{len(listings)}: {e}')
    
    if success_count > 0:
        logger.info(f'✅ Sent {success_count}/{len(listings)} listings to Matterbridge gateway "{gateway}"')
        return True
    else:
        logger.error(f'❌ Failed to send any listings to Matterbridge')
        return False

def execute_job(job_id):
    """Execute a scheduled job"""
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Get job details
    cursor.execute('SELECT * FROM jobs WHERE id = ? AND enabled = 1', (job_id,))
    job = cursor.fetchone()
    
    if not job:
        logger.warning(f'Job {job_id} not found or disabled')
        conn.close()
        return
    
    job_dict = dict(job)
    logger.info('=' * 80)
    logger.info(f'🔄 EXECUTING JOB: {job_dict["name"]}')
    logger.info(f'   Job ID: {job_id}')
    logger.info(f'   URL: {job_dict["url"]}')
    logger.info(f'   Schedule: {job_dict["schedule"]}')
    logger.info(f'   Last Listing ID: {job_dict["last_listing_id"] or "None (first run)"}')
    logger.info('=' * 80)
    
    started_at = datetime.now()
    
    try:
        listings = []
        new_count = 0
        newest_listing_id = job_dict['last_listing_id']
        
        # First run: Get newest non-promoted listing
        if not job_dict['last_listing_id']:
            logger.info('🆕 FIRST RUN - Getting newest non-promoted listing')
            logger.debug(f'   Calling Scraper API /api/newest endpoint')
            logger.debug(f'   URL parameter: {job_dict["url"]}')
            
            result = call_scraper_api_newest(job_dict['url'])
            newest_listing = result.get('newest')
            
            if newest_listing:
                listings = [newest_listing]
                newest_listing_id = newest_listing['id']
                new_count = 1
                
                logger.info(f'✅ FOUND NEWEST LISTING')
                logger.debug(f'   ID: {newest_listing_id}')
                logger.debug(f'   Title: {newest_listing.get("title", "N/A")}')
                logger.debug(f'   Price: {newest_listing.get("price", "N/A")}')
                logger.debug(f'   Location: {newest_listing.get("location", "N/A")}')
                logger.debug(f'   Posted: {newest_listing.get("posted_date", "N/A")}')
                logger.debug(f'   Full listing data:')
                logger.debug(f'{json.dumps(newest_listing, indent=2, ensure_ascii=False)}')
            else:
                logger.warning(f'⚠️  NO LISTINGS FOUND on first run')
        
        # Subsequent runs: Get new listings since last run
        else:
            logger.info(f'🔍 CHECKING FOR NEW LISTINGS since ID {job_dict["last_listing_id"]}')
            logger.debug(f'   Calling Scraper API /api/scrape endpoint')
            logger.debug(f'   URL parameter: {job_dict["url"]}')
            logger.debug(f'   Since parameter: {job_dict["last_listing_id"]}')
            
            result = call_scraper_api_scrape(job_dict['url'], since=job_dict['last_listing_id'])
            all_listings = result.get('listings', [])
            
            logger.debug(f'   Scraper API returned {len(all_listings)} total listings')
            
            # Filter out promoted listings (they shouldn't be in the result, but double-check)
            listings = [l for l in all_listings if not l.get('is_featured', False)]
            promoted_count = len(all_listings) - len(listings)
            
            if promoted_count > 0:
                logger.debug(f'   Filtered out {promoted_count} promoted listings')
            
            new_count = len(listings)
            
            # Update newest_listing_id if we found new ones
            if listings:
                newest_listing_id = listings[0]['id']
                logger.info(f'✅ FOUND {new_count} NEW LISTING(S)')
                logger.debug(f'   Newest ID: {newest_listing_id}')
                
                # Log each listing with full data
                for idx, listing in enumerate(listings, 1):
                    logger.debug(f'   --- Listing {idx}/{new_count} ---')
                    logger.debug(f'       ID: {listing.get("id")}')
                    logger.debug(f'       Title: {listing.get("title", "N/A")}')
                    logger.debug(f'       Price: {listing.get("price", "N/A")}')
                    logger.debug(f'       Location: {listing.get("location", "N/A")}')
                    logger.debug(f'       Posted: {listing.get("posted_date", "N/A")}')
                    logger.debug(f'       URL: https://www.kleinanzeigen.de{listing.get("link", "")}')
                    logger.debug(f'       Full data:')
                    logger.debug(f'{json.dumps(listing, indent=2, ensure_ascii=False)}')
            else:
                logger.info(f'ℹ️  NO NEW LISTINGS found (all listings older than ID {job_dict["last_listing_id"]})')
        
        # Update job status
        logger.debug(f'📝 UPDATING JOB STATUS')
        logger.debug(f'   Last run: {started_at}')
        logger.debug(f'   Status: success')
        logger.debug(f'   Last listing ID: {newest_listing_id}')
        
        cursor.execute('''
            UPDATE jobs 
            SET last_run = ?, last_status = ?, last_listing_id = ?, updated_at = ?
            WHERE id = ?
        ''', (started_at, 'success', newest_listing_id, datetime.now(), job_id))
        
        conn.commit()
        logger.debug(f'✅ Database updated successfully')
        
        # Send notification if enabled and new listings found
        if job_dict.get('notify_enabled') and new_count > 0:
            logger.info(f'📢 SENDING NOTIFICATION')
            send_notification(job_dict, listings)
        
        logger.info('=' * 80)
        logger.info(f'✅ JOB COMPLETED SUCCESSFULLY: {job_dict["name"]}')
        logger.info(f'   New listings: {new_count}')
        logger.info(f'   Total execution time: {(datetime.now() - started_at).total_seconds():.2f}s')
        logger.info('=' * 80)
        
    except Exception as e:
        error_msg = str(e)
        logger.error('=' * 80)
        logger.error(f'❌ JOB FAILED: {job_dict["name"]}')
        logger.error(f'   Error: {error_msg}')
        logger.error(f'   Job ID: {job_id}')
        logger.error(f'   URL: {job_dict["url"]}')
        
        # Log full traceback for debugging
        import traceback
        logger.error(f'   Full traceback:')
        for line in traceback.format_exc().split('\n'):
            if line.strip():
                logger.error(f'   {line}')
        logger.error('=' * 80)
        
        # Update job status
        cursor.execute('''
            UPDATE jobs 
            SET last_run = ?, last_status = ?, updated_at = ?
            WHERE id = ?
        ''', (started_at, 'failed', datetime.now(), job_id))
        
        conn.commit()
    
    finally:
        conn.close()

def reload_scheduler():
    """Reload all jobs into the scheduler"""
    # Clear existing jobs
    scheduler.remove_all_jobs()
    
    # Load all enabled jobs
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs WHERE enabled = 1')
    jobs = cursor.fetchall()
    conn.close()
    
    for job in jobs:
        try:
            scheduler.add_job(
                func=execute_job,
                args=[job['id']],
                trigger=CronTrigger.from_crontab(job['schedule']),
                id=f'job_{job["id"]}',
                name=job['name'],
                replace_existing=True
            )
            logger.info(f'Loaded job: {job["name"]} ({job["schedule"]})')
        except Exception as e:
            logger.error(f'Failed to load job {job["name"]}: {e}')

# ============================================================================
# Web UI Routes
# ============================================================================

@app.before_request
def check_web_ui_access():
    """Block access to static files when web UI is disabled"""
    if request.path.startswith('/static/') and not ENABLE_WEB_UI:
        return jsonify({'error': 'Not found'}), 404

@app.route('/')
def index():
    """Main dashboard - Modern SPA with JWT auth"""
    if not ENABLE_WEB_UI:
        return jsonify({'error': 'Not found'}), 404
    return render_template('app.html')

# ============================================================================
# API Routes - Token Authentication
# ============================================================================

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.json
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'error': 'Username and password required'}), 400
    
    username = data['username']
    password = data['password']
    
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND is_active = 1', (username,))
    user_row = cursor.fetchone()
    
    if not user_row or not check_password_hash(user_row['password_hash'], password):
        conn.close()
        return jsonify({'success': False, 'error': 'Invalid username or password'}), 401
    
    # Update last login
    cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now(), user_row['id']))
    conn.commit()
    conn.close()
    
    # Generate tokens
    access_token = generate_token(user_row['id'], user_row['username'], 'access')
    refresh_token = generate_token(user_row['id'], user_row['username'], 'refresh')
    
    logger.info(f'User {username} logged in via token auth')
    
    return jsonify({
        'success': True,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': JWT_ACCESS_TOKEN_EXPIRES,
        'user': {
            'id': user_row['id'],
            'username': user_row['username'],
            'email': user_row['email']
        }
    })

@app.route('/api/auth/refresh', methods=['POST'])
def api_refresh():
    data = request.json
    
    if not data or not data.get('refresh_token'):
        return jsonify({'success': False, 'error': 'Refresh token required'}), 400
    
    # Decode refresh token
    payload = decode_token(data['refresh_token'])
    if not payload:
        return jsonify({'success': False, 'error': 'Invalid or expired refresh token'}), 401
    
    # Verify it's a refresh token
    if payload.get('type') != 'refresh':
        return jsonify({'success': False, 'error': 'Invalid token type'}), 401
    
    # Generate new access token AND new refresh token (sliding window)
    access_token = generate_token(payload['user_id'], payload['username'], 'access')
    refresh_token = generate_token(payload['user_id'], payload['username'], 'refresh')
    
    logger.info(f'User {payload["username"]} refreshed tokens (sliding window)')
    
    return jsonify({
        'success': True,
        'access_token': access_token,
        'refresh_token': refresh_token,  # NEW: Return fresh refresh token
        'token_type': 'Bearer',
        'expires_in': JWT_ACCESS_TOKEN_EXPIRES,
        'refresh_expires_in': JWT_REFRESH_TOKEN_EXPIRES
    })

@app.route('/api/auth/me', methods=['GET'])
@require_token
def api_me():
    """
    Get Current User
    ---
    tags:
      - Authentication
    summary: Get current authenticated user information
    description: Returns information about the currently authenticated user based on JWT token
    security:
      - BearerAuth: []
    responses:
      200:
        description: User information retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            user:
              type: object
              properties:
                id:
                  type: integer
                username:
                  type: string
                email:
                  type: string
                created_at:
                  type: string
                last_login:
                  type: string
      401:
        description: Missing or invalid token
      404:
        description: User not found
    """
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, created_at, last_login FROM users WHERE id = ?', (g.user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    return jsonify({
        'success': True,
        'user': dict(user)
    })

@app.route('/api/auth/change-password', methods=['POST'])
@require_token
def api_change_password():
    """
    Change Password
    ---
    tags:
      - Authentication
    summary: Change user password
    description: |
      Changes the password for the currently authenticated user.
      Requires the current password for verification.
      After successful password change, all tokens are invalidated and the user must log in again.
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - current_password
            - new_password
          properties:
            current_password:
              type: string
              description: Current password for verification
              example: "oldpassword123"
            new_password:
              type: string
              description: New password (minimum 6 characters recommended)
              example: "newpassword456"
    responses:
      200:
        description: Password changed successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Password changed successfully. Please log in again."
      400:
        description: Invalid request (missing fields or password too short)
      401:
        description: Invalid current password or missing token
      404:
        description: User not found
    """
    data = request.json
    
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'success': False, 'error': 'Current password and new password are required'}), 400
    
    current_password = data['current_password']
    new_password = data['new_password']
    
    # Validate new password length
    if len(new_password) < 6:
        return jsonify({'success': False, 'error': 'New password must be at least 6 characters long'}), 400
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Get user with password hash
    cursor.execute('SELECT id, username, password_hash FROM users WHERE id = ?', (g.user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    # Verify current password
    if not check_password_hash(user['password_hash'], current_password):
        conn.close()
        return jsonify({'success': False, 'error': 'Current password is incorrect'}), 401
    
    # Hash new password
    from werkzeug.security import generate_password_hash
    new_password_hash = generate_password_hash(new_password)
    
    # Update password
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_password_hash, g.user_id))
    conn.commit()
    conn.close()
    
    logger.info(f'User {user["username"]} changed password')
    
    return jsonify({
        'success': True,
        'message': 'Password changed successfully. Please log in again.'
    })

# ============================================================================
# API Routes - Jobs
# ============================================================================

@app.route('/api/jobs', methods=['GET'])
@require_token
def get_jobs():
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs ORDER BY created_at DESC')
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'jobs': jobs})

@app.route('/api/jobs', methods=['POST'])
@require_token
def create_job():
    data = request.json
    
    required_fields = ['name', 'url', 'schedule']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO jobs (name, url, schedule, enabled, notify_enabled)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['url'],
            data['schedule'],
            data.get('enabled', True),
            data.get('notify_enabled', False)
        ))
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Reload scheduler
        reload_scheduler()
        
        return jsonify({'success': True, 'id': job_id})
    
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'error': 'Job name already exists'}), 400

@app.route('/api/jobs/<int:job_id>', methods=['GET'])
@require_token
def get_job(job_id):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    job = cursor.fetchone()
    conn.close()
    
    if not job:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    
    return jsonify({'success': True, 'job': dict(job)})

@app.route('/api/jobs/<int:job_id>', methods=['PUT'])
@require_token
def update_job(job_id):
    """Update job"""
    data = request.json
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Check if job exists
    cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    
    # Build update query
    updates = []
    params = []
    
    updateable_fields = ['name', 'url', 'schedule', 'enabled', 'notify_enabled']
    
    for field in updateable_fields:
        if field in data:
            updates.append(f'{field} = ?')
            params.append(data[field])
    
    if updates:
        updates.append('updated_at = ?')
        params.append(datetime.now())
        params.append(job_id)
        
        cursor.execute(f'''
            UPDATE jobs SET {', '.join(updates)} WHERE id = ?
        ''', params)
        conn.commit()
    
    conn.close()
    
    # Reload scheduler
    reload_scheduler()
    
    return jsonify({'success': True})

@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
@require_token
def delete_job(job_id):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    if not deleted:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    
    # Reload scheduler
    reload_scheduler()
    
    return jsonify({'success': True})

@app.route('/api/jobs/<int:job_id>/run', methods=['POST'])
@require_token
def run_job_now(job_id):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    job = cursor.fetchone()
    conn.close()
    
    if not job:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    
    # Execute job in background
    scheduler.add_job(
        func=execute_job,
        args=[job_id],
        id=f'manual_{job_id}_{datetime.now().timestamp()}',
        name=f'Manual: {job["name"]}'
    )
    
    return jsonify({'success': True, 'message': 'Job execution started'})

# ============================================================================
# API Routes - Configuration
# ============================================================================

@app.route('/api/config', methods=['GET'])
@require_token
def get_config_api():
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM global_config')
    rows = cursor.fetchall()
    conn.close()
    
    config = {}
    for row in rows:
        key = row['key']
        value = row['value']
        is_sensitive = key in SENSITIVE_KEYS
        
        # Mask sensitive values
        if is_sensitive:
            value = '***'  # Always show masked for sensitive keys
        
        config[key] = {
            'value': value,
            'description': row['description'],
            'is_sensitive': is_sensitive
        }
    
    return jsonify({'success': True, 'config': config})

@app.route('/api/config', methods=['PUT'])
@require_token
def update_config():
    data = request.json
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    for key, value in data.items():
        # Skip if value is the masked placeholder (user didn't change it)
        if key in SENSITIVE_KEYS and value == '***':
            continue
        
        # Encrypt sensitive values before storing
        stored_value = encrypt_value(value) if key in SENSITIVE_KEYS else value
        
        cursor.execute('''
            INSERT OR REPLACE INTO global_config (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, stored_value, datetime.now()))
        
        logger.info(f'Config updated: {key}' + (' (encrypted)' if key in SENSITIVE_KEYS else ''))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# ============================================================================
# API Routes - Health
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    uptime = datetime.now().timestamp() - app.config.get('start_time', datetime.now().timestamp())
    
    return jsonify({
        'status': 'ok',
        'version': VERSION,
        'uptime': int(uptime),
        'scheduler_running': scheduler.running
    })

@app.route('/api/health/services', methods=['GET'])
@require_token
def check_services():
    services = {}
    
    # Check Scraper API
    try:
        scraper_url = get_config('scraper_api_url', 'http://localhost:3000')
        response = requests.get(f'{scraper_url}/health', timeout=5)
        services['scraper_api'] = {
            'name': 'Scraper API',
            'status': 'ok' if response.status_code == 200 else 'error',
            'url': scraper_url,
            'data': response.json() if response.status_code == 200 else None
        }
    except Exception as e:
        services['scraper_api'] = {
            'name': 'Scraper API',
            'status': 'error',
            'url': get_config('scraper_api_url', 'http://localhost:3000'),
            'error': str(e)
        }
    
    # Check Job Scheduler (Self)
    try:
        uptime = datetime.now().timestamp() - app.config.get('start_time', datetime.now().timestamp())
        
        # Get job statistics
        conn = database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM jobs')
        total_jobs = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE enabled = 1')
        active_jobs = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE last_status = ?', ('success',))
        success_jobs = cursor.fetchone()[0]
        
        conn.close()
        
        services['job_scheduler'] = {
            'name': 'Job Scheduler (Self)',
            'status': 'ok',
            'url': f'http://localhost:{PORT}',
            'data': {
                'version': VERSION,
                'uptime_seconds': int(uptime),
                'scheduler_running': scheduler.running,
                'total_jobs': total_jobs,
                'active_jobs': active_jobs,
                'success_rate': f'{int((success_jobs/total_jobs*100) if total_jobs > 0 else 0)}%'
            }
        }
    except Exception as e:
        services['job_scheduler'] = {
            'name': 'Job Scheduler (Self)',
            'status': 'error',
            'error': str(e)
        }
    
    # Check Matterbridge
    try:
        matterbridge_url = get_config('matterbridge_url', 'http://192.168.10.10:4242')
        matterbridge_token = get_config('matterbridge_token', '')
        
        if not matterbridge_token:
            services['matterbridge'] = {
                'name': 'Matterbridge',
                'status': 'not_configured',
                'url': matterbridge_url,
                'error': 'Matterbridge token not configured'
            }
        else:
            headers = {
                'Authorization': f'Bearer {matterbridge_token}'
            }
            
            # Try to get API health/info
            response = requests.get(f'{matterbridge_url}/api/health', headers=headers, timeout=5)
            
            # If health endpoint doesn't exist, try just connecting
            if response.status_code == 404:
                response = requests.get(f'{matterbridge_url}/api/messages', headers=headers, timeout=5)
            
            if response.status_code in [200, 404]:  # 404 on /api/messages is OK (no messages)
                services['matterbridge'] = {
                    'name': 'Matterbridge',
                    'status': 'ok',
                    'url': matterbridge_url,
                    'data': {
                        'gateway': get_config('matterbridge_gateway', 'gateway_ebaykleinanzeigen'),
                        'api_accessible': True,
                        'response_code': response.status_code
                    }
                }
            else:
                services['matterbridge'] = {
                    'name': 'Matterbridge',
                    'status': 'error',
                    'url': matterbridge_url,
                    'error': f'HTTP {response.status_code}'
                }
                
    except Exception as e:
        services['matterbridge'] = {
            'name': 'Matterbridge',
            'status': 'error',
            'url': get_config('matterbridge_url', 'http://192.168.10.10:4242'),
            'error': str(e)
        }
    
    return jsonify({'success': True, 'services': services})

# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    # Get log level from environment variable (default: INFO)
    log_level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # Get Flask debug mode from separate environment variable (default: False)
    # SECURITY: This should NEVER be true in production!
    # Use LOG_LEVEL=DEBUG for detailed logging without security risks
    flask_debug_env = os.getenv('FLASK_DEBUG', 'false').lower()
    flask_debug = flask_debug_env in ('true', '1', 'yes')
    
    # Configure logging with detailed format (console only)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set the root logger level
    logging.getLogger().setLevel(log_level)
    
    # Conditionally register Swagger UI
    if ENABLE_SWAGGER_UI:
        app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    else:
        @app.route('/docs')
        @app.route('/docs/<path:path>')
        def docs_disabled(path=None):
            return jsonify({'error': 'Not found'}), 404
        
        @app.route('/openapi.yaml')
        def openapi_disabled():
            return jsonify({'error': 'Not found'}), 404
    
    print('=' * 60)
    print(f'Starting Kleinanzeigen Job Scheduler v{VERSION}')
    print(f'Listening on port {PORT}')
    print(f'Log level: {log_level_name}')
    print(f'Flask debug: {flask_debug}')
    print(f'Web UI: {"Enabled" if ENABLE_WEB_UI else "Disabled (API only)"}')
    print(f'Swagger UI: {"Enabled" if ENABLE_SWAGGER_UI else "Disabled"}')
    print('=' * 60)
    
    # Initialize database
    logger.info('Initializing database...')
    database.init_database()
    
    # Store start time
    app.config['start_time'] = datetime.now().timestamp()
    
    # Start scheduler
    logger.info('Starting APScheduler...')
    scheduler.start()
    logger.info('✓ APScheduler started')
    
    # Load jobs into scheduler
    logger.info('Loading jobs into scheduler...')
    reload_scheduler()
    
    print('=' * 60)
    print('✓ Server ready')
    print(f'Dashboard: http://localhost:{PORT}')
    print(f'API Docs: http://localhost:{PORT}/docs')
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
