<div align="right">

**[🇩🇪 Deutsch](README.de.md)** | **🇬🇧 English**

</div>

# Ebay Kleinanzeigen Job Scheduler

Automated job scheduling service with web dashboard for monitoring kleinanzeigen.de listings with optional Matterbridge notifications.

## 🎯 Overview

This service provides automated scheduling for kleinanzeigen.de monitoring jobs. It features a modern web dashboard, REST API, JWT authentication, and optional Matterbridge integration for real-time notifications.

## ✨ Features

- **Cron-Based Scheduling** - Flexible scheduling with cron expressions
- **Web Dashboard** - Modern SPA with responsive design
- **JWT Authentication** - Secure token-based auth with refresh tokens
- **Job Management** - Create, update, delete, and manually trigger jobs
- **Notification System** - Optional Matterbridge integration (Discord, Slack, Teams, etc.)
- **Incremental Updates** - Only processes new listings since last run
- **Job History** - Track execution status and timestamps
- **Service Health Monitoring** - Check connectivity to all services
- **Production Ready** - Gunicorn WSGI, SQLite database, health checks

## 🚀 Quick Start

### Production Deployment (Recommended)

**Run with Docker:**

```bash
# Build
docker build -t ebay-kleinanzeigen-job-scheduler .

# Run
docker run -d \
  -p 3001:3001 \
  -v scheduler-data:/app/data \
  -e ADMIN_PASSWORD=your-secure-password \
  -e SESSION_SECRET=$(openssl rand -base64 32) \
  -e JWT_SECRET=$(openssl rand -base64 32) \
  -e SCRAPER_API_URL=http://scraper-api:3000 \
  -e SCRAPER_API_KEY=your-api-key \
  --link scraper-api \
  --name job-scheduler \
  ebay-kleinanzeigen-job-scheduler
```

### Development/Testing with Docker Compose

**For development and testing only:**

```bash
# Edit docker-compose.yml to set your secrets
docker-compose up -d
```

**⚠️ Note:** Docker Compose is for development/testing. For production, use Docker as shown above.

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment  
cp .env.example .env
# Edit .env with your settings

# Start server
python server.py
```

## 📖 Web Dashboard

### Access

Open http://localhost:3001

### Default Credentials

- **Username:** `admin`
- **Password:** `admin`
- **⚠️ Change in production!**

### Dashboard Tabs

1. **Jobs** - Manage monitoring jobs
2. **Configuration** - Service settings
3. **Services** - Health monitoring
4. **Account** - User settings

## 📖 API Documentation

### Swagger UI

http://localhost:3001/docs

### Authentication

#### Login
```bash
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

Response includes `access_token` and `refresh_token`.

#### Use Token
```bash
TOKEN="your-access-token"
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/jobs
```

#### Refresh Token
```bash
curl -X POST http://localhost:3001/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"your-refresh-token"}'
```

### Key Endpoints

```bash
# Jobs
GET    /api/jobs           # List jobs
POST   /api/jobs           # Create job
GET    /api/jobs/{id}      # Get job
PUT    /api/jobs/{id}      # Update job
DELETE /api/jobs/{id}      # Delete job
POST   /api/jobs/{id}/run  # Run manually

# Config
GET /api/config            # Get config
PUT /api/config            # Update config

# Health
GET /health                # Basic health (no auth)
GET /api/health/services   # All services (auth required)
```

## 🔧 Configuration

### Environment Variables

#### Core
- `PORT` - Server port (default: 3001)
- `DB_PATH` - Database path (default: /app/data/jobs.db)
- `LOG_LEVEL` - Logging level (default: INFO)
- `FLASK_DEBUG` - Debug mode (default: false)
- `ENABLE_SWAGGER_UI` - Enable docs (default: true)
- `ENABLE_WEB_UI` - Enable dashboard (default: true)

#### Authentication
- `ADMIN_USERNAME` - Admin user (default: admin)
- `ADMIN_PASSWORD` - Admin password (**change this!**)
- `SESSION_SECRET` - Session key (generate random)
- `JWT_SECRET` - JWT key (generate random)
- `JWT_ACCESS_TOKEN_EXPIRES` - Access token TTL (default: 3600s)
- `JWT_REFRESH_TOKEN_EXPIRES` - Refresh token TTL (default: 604800s)

#### Scraper API
- `SCRAPER_API_URL` - Scraper URL (default: `http://localhost:3000`)
- `SCRAPER_API_KEY` - API key (default: `test-key-123`)
- `SCRAPER_REQUEST_TIMEOUT` - Timeout seconds (default: `30`)

#### Matterbridge (Optional - for notifications)
- `MATTERBRIDGE_URL` - Matterbridge API URL (default: `http://matterbridge:4242`)
- `MATTERBRIDGE_TOKEN` - Bearer token for authentication (default: empty)
- `MATTERBRIDGE_GATEWAY` - Gateway name (default: `gateway_ebaykleinanzeigen`)
- `MATTERBRIDGE_USERNAME` - Bot display name (default: `Kleinanzeigen Bot`)

#### Notifications
- `NOTIFICATION_LANGUAGE` - Language for messages: `de` or `en` (default: `de`)

#### Job Defaults
- `DEFAULT_JOB_SCHEDULE` - Default cron schedule (default: `*/30 * * * *` = every 30 minutes)

**Matterbridge Documentation:**
- Repository: https://github.com/42wim/matterbridge
- Setup Guide: https://github.com/42wim/matterbridge/wiki
- Config Examples: https://github.com/42wim/matterbridge/wiki/How-to-create-your-config

## 📅 Cron Schedules

Standard 5-field cron expressions:

```
┌─────── minute (0-59)
│ ┌───── hour (0-23)
│ │ ┌─── day of month (1-31)
│ │ │ ┌─ month (1-12)
│ │ │ │ ┌ day of week (0-6, 0=Sunday)
* * * * *
```

### Examples

| Expression | Description |
|------------|-------------|
| `*/30 * * * *` | Every 30 minutes |
| `0 * * * *` | Every hour |
| `0 9 * * *` | Daily at 9 AM |
| `0 9 * * 1` | Mondays at 9 AM |
| `0 9-17 * * 1-5` | Weekdays 9 AM-5 PM |

Use https://crontab.guru to validate expressions.

## 💡 Usage Examples

### Create Monitoring Job

```bash
# 1. Login
TOKEN=$(curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  | jq -r '.access_token')

# 2. Create job
curl -X POST http://localhost:3001/api/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Munich Tables",
    "url": "/s-wohnzimmer/muenchen/tisch/k0c88l6411",
    "schedule": "*/30 * * * *",
    "enabled": true,
    "notify_enabled": true
  }'
```

### Monitor Job Execution

```bash
# List jobs with status
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/jobs | jq .

# Check specific job
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/jobs/1 | jq .
```

## 🔔 Notifications with Matterbridge

### What is Matterbridge?

**Matterbridge** is a bridge between multiple chat platforms (Discord, Slack, Teams, Telegram, IRC, Matrix, etc.). The Job Scheduler uses Matterbridge's API to send formatted notifications when new listings are found.

**Official Documentation:**
- Main Repo: https://github.com/42wim/matterbridge
- Wiki: https://github.com/42wim/matterbridge/wiki
- Configuration Guide: https://github.com/42wim/matterbridge/wiki/How-to-create-your-config

### Setup Steps

1. **Install and configure Matterbridge** (see [official docs](https://github.com/42wim/matterbridge/wiki))
2. **Set up your gateway** (Discord, Slack, etc.)
3. **Get API token** from your Matterbridge instance
4. **Configure in Job Scheduler:**
   - Dashboard → Configuration tab
   - Or set environment variables (see above)
5. **Enable notifications** on individual jobs
6. **Choose language** (German or English)

### Notification Content

Each listing notification includes:
- 📌 Title, 💰 Price, 📍 Location
- 🕐 Posted date, 👤 Seller type
- 📝 Description, 🖼️ Image
- 🔗 Direct link
- All category-specific fields (shipping, condition, etc.)

Notifications are sent in real-time when new listings are detected.

## 🐛 Troubleshooting

### Jobs not running
```bash
# Check scheduler status
curl http://localhost:3001/health

# Verify job is enabled
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/jobs

# Check cron expression
# Use https://crontab.guru
```

### Can't connect to Scraper API
```bash
# Test Scraper API
curl http://localhost:3000/health

# Check configuration
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/config

# Verify API key matches
```

### Authentication issues
```bash
# Token expired - refresh it
curl -X POST http://localhost:3001/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"your-refresh-token"}'

# Reset password via dashboard
# Or reset database: rm jobs.db && python server.py
```

## 📊 Database

### Schema

- **users** - User accounts
- **jobs** - Job configurations  
- **global_config** - System settings

### Manual Queries

```bash
# View jobs
sqlite3 /app/data/jobs.db "SELECT * FROM jobs;"

# View config
sqlite3 /app/data/jobs.db "SELECT * FROM global_config;"

# Check last run
sqlite3 /app/data/jobs.db \
  "SELECT name, last_run, last_status FROM jobs;"
```

## 🔒 Security

### Production Checklist

- [ ] Change default admin password
- [ ] Generate strong SESSION_SECRET and JWT_SECRET
- [ ] Use secure API keys
- [ ] Set FLASK_DEBUG=false
- [ ] Configure firewall
- [ ] Use HTTPS reverse proxy
- [ ] Regularly update dependencies
- [ ] Disable Swagger UI if not needed

## 📈 Performance

- **Memory:** ~100-150 MB
- **Database:** SQLite (embedded, no external DB needed)
- **Scheduler:** APScheduler (background thread)
- **WSGI Server:** Gunicorn (production)

## 📝 Development

```bash
# Run in development
export LOG_LEVEL=DEBUG
export FLASK_DEBUG=false
python server.py

# Test API
python test_cli.py

# Check logs
tail -f logs/scheduler.log
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

Educational purposes. Respect kleinanzeigen.de's terms of service and rate limits.
