<div align="right">

**[🇩🇪 Deutsch](README.de.md)** | **🇬🇧 English**

</div>

# Ebay Kleinanzeigen Scraper

Production-ready API for scraping and extracting listing data from kleinanzeigen.de (formerly eBay Kleinanzeigen).

## 🎯 Overview

This service provides a REST API for extracting comprehensive listing data from kleinanzeigen.de search pages. It features anti-detection mechanisms, multi-URL support, and robust error handling.

## ✨ Features

- **Comprehensive Data Extraction** - 15 fields per listing
- **Multi-URL Support** - Scrape multiple searches simultaneously with automatic deduplication
- **Incremental Updates** - `since` parameter to get only new listings
- **Anti-Detection**
  - User-Agent rotation (7 different browsers)
  - Random delays (2-5 seconds, configurable)
  - Automatic retry with exponential backoff
  - Rate limit detection
- **Production Ready**
  - Gunicorn WSGI server
  - Health checks
  - Structured logging
  - API key authentication
  - OpenAPI/Swagger documentation

## 📊 Extracted Data Fields

Each listing contains up to 15 fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique listing ID | `"3287237963"` |
| `title` | string | Listing title | `"Designer Couchtisch"` |
| `url` | string | Full URL to listing | `"https://www.kleinanzeigen.de/..."` |
| `price` | string/null | Price as displayed | `"160 €"` or `null` |
| `location` | string/null | Postal code + district | `"80797 Schwabing-West"` |
| `image` | string/null | Main image URL | `"https://img.kleinanzeigen.de/..."` |
| `image_count` | int/null | Total number of images | `3` |
| `description` | string/null | Short description | `"Nur 1x aufgebaut, wie neu!"` |
| `posted_date` | string/null | When posted | `"Heute, 14:51"` |
| `shipping` | string/null | Shipping info | `"Versand möglich"` |
| `seller_type` | string | Seller type | `"PRIVATE"` or `"PRO"` |
| `seller_name` | string/null | Seller name | Usually `null` on search |
| `buy_now` | boolean | Direct purchase available | `false` |
| `is_featured` | boolean | Promoted/featured listing | `false` |
| `additional_info` | array | Category-specific fields | `["Automatik", "Benzin"]` |

## 🚀 Quick Start

### Docker (Recommended)

```bash
# Build
docker build -t ebay-kleinanzeigen-scraper .

# Run
docker run -d \
  -p 3000:3000 \
  -e API_KEYS=your-api-key-here \
  --name scraper \
  ebay-kleinanzeigen-scraper
```

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set API keys
export API_KEYS=test-key-123,production-key-456

# Start server
python server.py
```

## 📖 API Documentation

### Interactive Docs

Once running, visit:
- **Swagger UI:** http://localhost:3000/docs
- **OpenAPI Spec:** http://localhost:3000/openapi.yaml

### Endpoints

#### 1. Health Check (Public)

```bash
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-01-04T15:00:00Z",
  "uptime": 3600,
  "version": "1.0.0"
}
```

#### 2. Scrape Listings

```bash
GET /api/scrape?url={search_url}&since={listing_id}
```

**Authentication:** Requires `X-API-Key` header

**Parameters:**
- `url` (required) - Search URL path or comma-separated paths
- `since` (optional) - Return only listings with ID greater than this

**Single URL Example:**
```bash
curl -H "X-API-Key: test-key-123" \
  "http://localhost:3000/api/scrape?url=/s-autos/c216"
```

**Multi-URL Example:**
```bash
curl -H "X-API-Key: test-key-123" \
  "http://localhost:3000/api/scrape?url=/s-autos/c216+global.farbe:blau,/s-autos/c216+global.farbe:gelb"
```

**Incremental Update Example:**
```bash
curl -H "X-API-Key: test-key-123" \
  "http://localhost:3000/api/scrape?url=/s-autos/c216&since=3287237963"
```

**Response:**
```json
{
  "success": true,
  "urls": ["/s-autos/c216+global.farbe:blau", "/s-autos/c216+global.farbe:gelb"],
  "urlCount": 2,
  "scrapedAt": "2026-01-04T15:30:00Z",
  "count": 27,
  "listings": [
    {
      "id": "3287237963",
      "title": "Designer Couchtisch",
      "url": "https://www.kleinanzeigen.de/s-anzeige/designer-couchtisch/3287237963",
      "price": "160 €",
      "location": "80797 Schwabing-West",
      "image": "https://img.kleinanzeigen.de/...",
      "image_count": 3,
      "description": "Moderner Designer Couchtisch",
      "posted_date": "Heute, 14:51",
      "shipping": "Versand möglich",
      "seller_type": "PRIVATE",
      "seller_name": null,
      "buy_now": false,
      "is_featured": false,
      "additional_info": []
    }
  ]
}
```

#### 3. Get Newest Listing

```bash
GET /api/newest?url={search_url}
```

**Authentication:** Requires `X-API-Key` header

Returns only the newest (highest ID) non-promoted listing. Useful for quickly checking if new items have been posted.

**Example:**
```bash
curl -H "X-API-Key: test-key-123" \
  "http://localhost:3000/api/newest?url=/s-autos/c216"
```

**Response:**
```json
{
  "success": true,
  "urls": "/s-autos/c216",
  "urlCount": 1,
  "scrapedAt": "2026-01-04T15:30:00Z",
  "newest": {
    "id": "3287237963",
    "title": "Designer Couchtisch",
    ...
  }
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `3000` | Server port |
| `API_KEYS` | *required* | Comma-separated API keys |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `FLASK_DEBUG` | `false` | Flask debug mode (never use in production!) |
| `ENABLE_SWAGGER_UI` | `true` | Enable Swagger docs at /docs |

### API Key Management

API keys are configured via the `API_KEYS` environment variable:

```bash
# Single key
export API_KEYS=my-secure-key-123

# Multiple keys (comma-separated)
export API_KEYS=key1,key2,key3
```

Include the key in requests via `X-API-Key` header:

```bash
curl -H "X-API-Key: my-secure-key-123" \
  "http://localhost:3000/api/scrape?url=/s-autos/c216"
```

## 🛡️ Anti-Detection Features

### User-Agent Rotation

Automatically rotates between 7 different browser user agents:
- Chrome (Windows, Mac, Linux)
- Firefox (Windows, Mac)
- Safari (Mac)
- Edge (Windows)

### Delay Configuration

```python
# Random delay between requests (2-5 seconds)
# Configurable in server.py
MIN_DELAY = 2
MAX_DELAY = 5
```

### Retry Logic

- 3 automatic retries with exponential backoff
- Backoff factor: 0.5 seconds
- Handles network errors, timeouts, and rate limits

## 📊 Use Cases

### 1. Monitor New Listings

```bash
# First run - get newest listing
NEWEST=$(curl -H "X-API-Key: key" \
  "http://localhost:3000/api/newest?url=/s-autos/c216" \
  | jq -r '.newest.id')

# Store $NEWEST

# Subsequent runs - get only new listings
curl -H "X-API-Key: key" \
  "http://localhost:3000/api/scrape?url=/s-autos/c216&since=$NEWEST"
```

### 2. Search Multiple Criteria

```bash
# Search for blue AND yellow cars separately, combine results
curl -H "X-API-Key: key" \
  "http://localhost:3000/api/scrape?url=/s-autos/c216+global.farbe:blau,/s-autos/c216+global.farbe:gelb"

# Automatic deduplication if same listing appears in both
```

### 3. Category-Specific Searches

```bash
# Furniture
curl -H "X-API-Key: key" \
  "http://localhost:3000/api/scrape?url=/s-wohnzimmer/muenchen/tisch/k0c88l6411"

# Electronics
curl -H "X-API-Key: key" \
  "http://localhost:3000/api/scrape?url=/s-telefon-handy/c173"

# Real Estate
curl -H "X-API-Key: key" \
  "http://localhost:3000/api/scrape?url=/s-wohnung-mieten/c203"
```

## 🔍 Finding Search URLs

1. Go to https://www.kleinanzeigen.de
2. Search for what you want
3. Apply filters (location, price, etc.)
4. Copy the URL path after `kleinanzeigen.de`

**Example:**
```
Full URL: https://www.kleinanzeigen.de/s-autos/muenchen/bmw/k0c216l6411r50+autos.marke_s:bmw
Use this: /s-autos/muenchen/bmw/k0c216l6411r50+autos.marke_s:bmw
```

## 🐛 Troubleshooting

### "Invalid or missing API key"

```bash
# Verify API key is set
echo $API_KEYS

# Check header format
curl -v -H "X-API-Key: your-key" http://localhost:3000/api/scrape?url=/s-autos/c216
```

### "Failed to fetch URL: URL not found"

- Check that the URL path is correct
- Verify the search actually has results on kleinanzeigen.de
- URL might be malformed or expired

### Rate Limited

```bash
# Service automatically retries with backoff
# Check logs for "Rate limit" messages

# If persistent, increase delays in server.py:
MIN_DELAY = 5  # Increase from 2
MAX_DELAY = 10 # Increase from 5
```

### No Results Returned

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python server.py

# Check logs for detailed scraping process
```

## 📈 Performance

- **Response Time:** ~2-7 seconds per URL (including anti-detection delays)
- **Throughput:** ~10-20 requests/minute (respects rate limits)
- **Concurrent Requests:** Handled by Gunicorn workers (default: 4)

## 🔒 Security

### Production Checklist

- [ ] Use strong, random API keys
- [ ] Set `FLASK_DEBUG=false`
- [ ] Configure firewall (allow only necessary IPs)
- [ ] Use HTTPS reverse proxy
- [ ] Monitor logs for suspicious activity
- [ ] Rotate API keys regularly
- [ ] Consider disabling Swagger UI (`ENABLE_SWAGGER_UI=false`)

## 📝 Development

### Run in Development Mode

```bash
export API_KEYS=test-key-123
export LOG_LEVEL=DEBUG
export FLASK_DEBUG=false  # Even in dev, keep false for security

python server.py
```

### Testing

```bash
# Health check
curl http://localhost:3000/health

# Test scraping
curl -H "X-API-Key: test-key-123" \
  "http://localhost:3000/api/scrape?url=/s-autos/c216" \
  | jq .
```

## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

**Key Points:**
- ✅ Free for personal and commercial use
- ✅ Modify and adapt as needed
- ✅ Share improvements back to the community
- ✅ Network use requires source disclosure

See the [LICENSE](../LICENSE) file or visit https://www.gnu.org/licenses/agpl-3.0.html

## ⚠️ Disclaimer

This tool is for educational purposes. Always respect kleinanzeigen.de's:
- Terms of Service
- robots.txt
- Rate limits

Use responsibly and don't overload their servers.
