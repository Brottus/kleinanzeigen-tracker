<div align="right">

**[🇩🇪 Deutsch](README.de.md)** | **🇬🇧 English**

</div>

# Ebay Kleinanzeigen Monitoring System

<div align="center">
  <img src="assets/banner.svg" alt="kleinanzeigen tracker" width="800">
</div>

<br>

[![Create Release](https://github.com/Brottus/kleinanzeigen-tracker/actions/workflows/release.yml/badge.svg)](https://github.com/Brottus/kleinanzeigen-tracker/actions/workflows/release.yml)
[![Build and Push Docker Images](https://github.com/Brottus/kleinanzeigen-tracker/actions/workflows/build-and-push.yml/badge.svg)](https://github.com/Brottus/kleinanzeigen-tracker/actions/workflows/build-and-push.yml)
[![CodeQL](https://github.com/Brottus/kleinanzeigen-tracker/actions/workflows/github-code-scanning/codeql/badge.svg?branch=main)](https://github.com/Brottus/kleinanzeigen-tracker/actions/workflows/github-code-scanning/codeql)
[![Dependabot Status](https://img.shields.io/badge/Dependabot-enabled-success?logo=dependabot)](https://github.com/Brottus/ebaykleinanzeigen/network/updates)

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.14+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

[![Docker Pulls - Scraper](https://img.shields.io/docker/pulls/brottus/ebay-kleinanzeigen-scraper?logo=docker&label=Scraper%20Pulls)](https://hub.docker.com/r/brottus/ebay-kleinanzeigen-scraper)
[![Docker Pulls - Scheduler](https://img.shields.io/docker/pulls/brottus/ebay-kleinanzeigen-job-scheduler?logo=docker&label=Scheduler%20Pulls)](https://hub.docker.com/r/brottus/ebay-kleinanzeigen-job-scheduler)
[![Docker Image Size - Scraper](https://img.shields.io/docker/image-size/brottus/ebay-kleinanzeigen-scraper/latest?logo=docker&label=Scraper%20Size)](https://hub.docker.com/r/brottus/ebay-kleinanzeigen-scraper)
[![Docker Image Size - Scheduler](https://img.shields.io/docker/image-size/brottus/ebay-kleinanzeigen-job-scheduler/latest?logo=docker&label=Scheduler%20Size)](https://hub.docker.com/r/brottus/ebay-kleinanzeigen-job-scheduler)

A comprehensive microservices-based system for monitoring and scraping listings from kleinanzeigen.de (formerly eBay Kleinanzeigen) with automated job scheduling and optional Matterbridge notifications.

---

<div align="center">

### 🤖 Support This Project

*This project was built with AI assistance. If you find it useful, consider buying me some AI tokens!* ☕

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/brottus)

</div>

---

## 🎯 Project Overview

This system consists of two main services that work together to provide automated monitoring of kleinanzeigen.de listings:

1. **Ebay Kleinanzeigen Scraper** - Production-ready API for extracting listing data
2. **Ebay Kleinanzeigen Job Scheduler** - Automated job scheduling with web dashboard

### Key Features

- ✅ **Comprehensive Data Extraction** - 15 fields per listing including images, prices, locations, and more
- ✅ **Multi-URL Support** - Scrape multiple search URLs simultaneously with automatic deduplication
- ✅ **Automated Scheduling** - Cron-based job scheduling with APScheduler
- ✅ **Anti-Detection** - User-Agent rotation, random delays, and automatic retries
- ✅ **Real-time Notifications** - Apprise (80+ services) and/or Matterbridge integration for instant alerts
- ✅ **Priority Jobs** - Mark jobs as priority to append `@everyone` to notification titles
- ✅ **Web Dashboard** - Modern SPA with JWT authentication
- ✅ **REST API** - Full OpenAPI/Swagger documentation
- ✅ **Docker Support** - Production-ready containerization
- ✅ **Production Ready** - Gunicorn WSGI server, health checks, logging

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network                            │
│                                                              │
│  ┌──────────────────────┐      ┌──────────────────────┐    │
│  │     Scraper          │      │       Scheduler      │    │
│  │  Port: 3000          │◄─────┤ Port: 3001           │    │
│  │                      │      │                      │    │
│  │  • Data extraction   │      │  • Job management    │    │
│  │  • API key auth      │      │  • Web dashboard     │    │
│  │  • Multi-URL support │      │  • JWT auth          │    │
│  │  • Anti-detection    │      │  • Notifications     │    │
│  └──────────────────────┘      └──────────────────────┘    │
│           │                              │                  │
└───────────┼──────────────────────────────┼──────────────────┘
            │                              │
            ▼                         ▼         ▼
     kleinanzeigen.de            Apprise    Matterbridge
                               (default)   (optional)
```

## 🚀 Quick Start

### Prerequisites

- Docker (for production deployment)
- Docker Compose (for development/testing only)
- OR Python 3.11+ (for manual setup)

### Production Deployment (Recommended)

**Run each service in its own Docker container:**

1. **Build and run Scraper API**
```bash
cd ebay-kleinanzeigen-scraper
docker build -t kleinanzeigen-scraper-api .
docker run -d \
  -p 3000:3000 \
  -e API_KEYS=your-secure-api-key \
  --name scraper-api \
  kleinanzeigen-scraper-api
```

2. **Build and run Job Scheduler**
```bash
cd ebay-kleinanzeigen-job-scheduler
docker build -t kleinanzeigen-job-scheduler .
docker run -d \
  -p 3001:3001 \
  -v scheduler-data:/app/data \
  -e ADMIN_PASSWORD=your-secure-password \
  -e SESSION_SECRET=$(openssl rand -base64 32) \
  -e JWT_SECRET=$(openssl rand -base64 32) \
  -e SCRAPER_API_URL=http://scraper-api:3000 \
  -e SCRAPER_API_KEY=your-secure-api-key \
  --link scraper-api \
  --name job-scheduler \
  kleinanzeigen-job-scheduler
```

3. **Access the services**
- Scraper API: http://scraper:3000
- Scraper Docs: http://scraper:3000/docs
- Scheduler Dashboard: http://localhost:3001
- Scheduler API Docs: http://localhost:3001/docs

4. **Default credentials**
- Username: `admin`
- Password: Set via `ADMIN_PASSWORD`

### Development/Testing with Docker Compose

**For development and testing only:**

```bash
# Clone the repository
git clone <repository-url>
cd ebaykleinanzeigen

# 1. Edit docker-compose.yml to set secrets (SESSION_SECRET, JWT_SECRET, etc.)

# 2. Start all services — Apprise is the default notifier
docker-compose up -d

# 3. Add notification URLs to Apprise for the key "kleinanzeigen"
curl -X POST http://localhost:8000/add/kleinanzeigen \
  -d "urls=tgram://bottoken/ChatID"
```

**Services included:**
- `scraper` - Scraper API (port 3000)
- `scheduler` - Job Scheduler (port 3001)
- `apprise` - Notification backend, **default** (port 8000)
- `matterbridge` - Optional message bridge (port 4242, see [Matterbridge Setup](#matterbridge-setup))

**⚠️ Note:** Docker Compose is recommended for development/testing only. For production, use individual Docker containers as shown above.

### Manual Setup

See individual service README files:
- [Scraper Setup](./ebay-kleinanzeigen-scraper/README.md)
- [Scheduler Setup](./ebay-kleinanzeigen-job-scheduler/README.md)

## 📚 Services Documentation

### Ebay Kleinanzeigen Scraper API

**Purpose:** Extract listing data from kleinanzeigen.de search pages

**Key Endpoints:**
- `GET /api/scrape` - Scrape listings from URL(s)
- `GET /api/newest` - Get newest listing only
- `GET /health` - Health check

**Features:**
- 15-field data extraction (ID, title, price, location, images, etc.)
- Multi-URL scraping with deduplication
- `since` parameter for incremental updates
- API key authentication
- User-Agent rotation & anti-detection
- Docker deployment ready

[Full Documentation →](./ebay-kleinanzeigen-scraper/README.md)

### Ebay Kleinanzeigen Job Scheduler

**Purpose:** Automate monitoring with scheduled jobs and notifications

**Key Features:**
- Cron-based job scheduling
- Web dashboard with JWT authentication
- Apprise integration for notifications (80+ services — default)
- Matterbridge integration for notifications (optional)
- Priority Jobs — appends `@everyone` to notification titles
- Job history and status tracking
- Manual job execution
- Docker deployment ready

**Endpoints:**
- `POST /api/auth/login` - Authenticate
- `GET /api/jobs` - List jobs
- `POST /api/jobs` - Create job
- `POST /api/jobs/{id}/run` - Run job manually

[Full Documentation →](./ebay-kleinanzeigen-job-scheduler/README.md)

## 🔧 Configuration

### Environment Variables

#### Scraper API
```bash
PORT=3000                          # Server port
API_KEYS=key1,key2                # Comma-separated API keys
LOG_LEVEL=INFO                     # Logging level
ENABLE_SWAGGER_UI=true            # Enable API docs
```

#### Job Scheduler
```bash
PORT=3001                          # Server port
ADMIN_USERNAME=admin              # Admin username
ADMIN_PASSWORD=admin              # Admin password (change this!)
SESSION_SECRET=random-secret      # Session encryption key
JWT_SECRET=random-jwt-secret      # JWT signing key
ENABLE_SWAGGER_UI=true            # Enable API docs
ENABLE_WEB_UI=true                # Enable web dashboard

# Scraper API Connection
SCRAPER_API_URL=http://scraper:3000
SCRAPER_API_KEY=test-key-123

# Notification language
NOTIFICATION_LANGUAGE=de          # de or en

# Apprise (default notification method — 80+ services)
APPRISE_ENABLED=true
APPRISE_API_URL=http://apprise:8000
APPRISE_API_KEY=kleinanzeigen
APPRISE_USERNAME=                  # Optional: HTTP Basic Auth (reverse proxy only)
APPRISE_PASSWORD=                  # Optional: HTTP Basic Auth (reverse proxy only)

# Matterbridge (optional — disable if not using)
MATTERBRIDGE_ENABLED=false
MATTERBRIDGE_URL=http://matterbridge:4242
MATTERBRIDGE_TOKEN=your-token
MATTERBRIDGE_GATEWAY=gateway_name
```

### Apprise Setup

**Apprise** is the default notification backend. It supports 80+ services including Telegram, Discord, Slack, Pushover, ntfy, Signal, and many more.

- Repository: https://github.com/caronc/apprise
- Wiki & full service list: https://github.com/caronc/apprise/wiki

#### Option 1: Using Docker Compose (Development/Testing — default)

The included `docker-compose.yml` already has Apprise configured as the **default** notifier. Just start the stack:

```bash
docker-compose up -d
# Apprise API available at http://apprise:8000 (within Docker network)
# or http://localhost:8000 (from host)
```

Add notification URLs for the key `kleinanzeigen` via curl:
```bash
curl -X POST http://localhost:8000/add/kleinanzeigen \
  -d "urls=tgram://bottoken/ChatID"
```

Or use the Apprise web UI at http://localhost:8000 to manage URLs.

#### Option 2: Standalone Apprise (Production)

```bash
# Run Apprise separately
docker run -d \
  -p 8000:8000 \
  --name apprise \
  caronc/apprise:latest

# Configure Job Scheduler to connect to it
docker run -d \
  -e APPRISE_ENABLED=true \
  -e APPRISE_API_URL=http://apprise:8000 \
  -e APPRISE_API_KEY=kleinanzeigen \
  --link apprise \
  kleinanzeigen-job-scheduler
```

#### Configuration Steps

1. **Install Apprise** (via Docker as shown above)
2. **Add notification URLs** for your `APPRISE_API_KEY` (e.g. `kleinanzeigen`) — see the [Apprise wiki](https://github.com/caronc/apprise/wiki) for service-specific URL formats
3. **Configure Job Scheduler:**
   - Set `APPRISE_ENABLED=true`, `APPRISE_API_URL`, `APPRISE_API_KEY`
   - Or use the dashboard Configuration tab
4. **Enable notifications** on individual jobs

**Popular notification URL formats:**

| Service | URL format |
|---------|-----------|
| Telegram | `tgram://bottoken/ChatID` |
| Discord | `discord://WebhookID/WebhookToken` |
| Slack | `slack://TokenA/TokenB/TokenC/Channel` |
| Pushover | `pover://UserKey/AppToken` |
| ntfy | `ntfy://topic` or `ntfys://host/topic` |
| Signal | `signal://PhoneNo/TargetPhoneNo` |
| E-Mail | `mailto://user:pass@gmail.com` |

For a full list of supported services see https://github.com/caronc/apprise/wiki

---

### Matterbridge Setup

**Matterbridge** is a message bridge that forwards notifications to various chat platforms (Discord, Slack, Teams, Telegram, IRC, Matrix, etc.).

- Repository: https://github.com/42wim/matterbridge
- Wiki & Setup Guide: https://github.com/42wim/matterbridge/wiki
- Configuration examples: https://github.com/42wim/matterbridge/wiki/How-to-create-your-config

#### Option 1: Using Docker Compose (Development/Testing)

Add Matterbridge to your `docker-compose.yml` stack alongside Apprise:

```bash
# 1. Create Matterbridge config directory
mkdir -p matterbridge

# 2. Create matterbridge.toml configuration file
# See official guide: https://github.com/42wim/matterbridge/wiki/How-to-create-your-config
nano matterbridge/matterbridge.toml

# 3. Set your API token
export MATTERBRIDGE_TOKEN="your-api-token"

# 4. Start all services
docker-compose up -d

# 5. Matterbridge is available at http://matterbridge:4242 (within Docker network)
#    or http://localhost:4242 (from host)
```

#### Option 2: Standalone Matterbridge (Production)

```bash
# Run Matterbridge separately
docker run -d \
  -p 4242:4242 \
  -v /path/to/config:/etc/matterbridge:ro \
  --name matterbridge \
  42wim/matterbridge:stable

# Configure Job Scheduler to connect to it
docker run -d \
  -e MATTERBRIDGE_ENABLED=true \
  -e MATTERBRIDGE_URL=http://matterbridge:4242 \
  -e MATTERBRIDGE_TOKEN=your-token \
  -e MATTERBRIDGE_GATEWAY=your-gateway \
  --link matterbridge \
  kleinanzeigen-job-scheduler
```

#### Configuration Steps

1. **Install Matterbridge** (via Docker as shown above)
2. **Create configuration file** `matterbridge.toml` — [Configuration Guide](https://github.com/42wim/matterbridge/wiki/How-to-create-your-config)
3. **Set up your gateway** (Discord, Slack, etc.) in the config
4. **Get API token** from your Matterbridge instance
5. **Configure Job Scheduler:**
   - Set `MATTERBRIDGE_ENABLED=true`, `MATTERBRIDGE_URL=http://matterbridge:4242`, `MATTERBRIDGE_TOKEN`, `MATTERBRIDGE_GATEWAY`
   - Or use the dashboard Configuration tab
6. **Enable notifications** on individual jobs

**Example `matterbridge.toml` API section:**
```toml
[api]
  [api.myapi]
  BindAddress = "0.0.0.0:4242"
  Token = "your-secret-token"
  Buffer = 1000

[[gateway]]
name = "gateway_kleinanzeigen"
enable = true

  [[gateway.inout]]
  account = "api.myapi"
  channel = "api"

  [[gateway.inout]]
  account = "discord.mydiscord"
  channel = "general"
```

**Supported platforms include:** Discord, Slack, Telegram, Teams, IRC, Matrix, Mattermost, Rocket.Chat, XMPP, and [many more](https://github.com/42wim/matterbridge#supported-protocols).

For detailed configuration, refer to the [official wiki](https://github.com/42wim/matterbridge/wiki).

## 💡 Usage Examples

### Example 1: Monitor Munich Furniture

1. **Login to Scheduler Dashboard**
```
http://localhost:3001
Username: admin
Password: admin
```

2. **Create a Job**
- Name: "Munich Tables"
- URL: `/s-wohnzimmer/muenchen/tisch/k0c88l6411`
- Schedule: `*/30 * * * *` (every 30 minutes)
- Enable Notifications: Yes

3. **Job runs automatically** and notifies you of new listings!

### Example 2: API Usage

**Scrape listings:**
```bash
curl -H "X-API-Key: test-key-123" \
  "http://scraper:3000/api/scrape?url=/s-autos/c216"
```

**Get only new listings since last check:**
```bash
curl -H "X-API-Key: test-key-123" \
  "http://scraper:3000/api/scrape?url=/s-autos/c216&since=3287237963"
```

**Create a job via API:**
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
    "name": "Monitor Cars",
    "url": "/s-autos/c216",
    "schedule": "*/30 * * * *",
    "notify_enabled": true
  }'
```

## 📖 API Documentation

Both services provide interactive Swagger UI documentation:

- **Scraper API Docs:** http://scraper:3000/docs
- **Scheduler API Docs:** http://localhost:3001/docs

## 🔒 Security

### Production Checklist

- [ ] Change default admin password
- [ ] Generate strong `SESSION_SECRET` and `JWT_SECRET`
- [ ] Use secure API keys (not `test-key-123`)
- [ ] Set `FLASK_DEBUG=false`
- [ ] Configure firewall rules
- [ ] Use HTTPS reverse proxy (nginx/traefik)
- [ ] Regularly update dependencies
- [ ] Consider disabling Swagger UI in production (`ENABLE_SWAGGER_UI=false`)

### Authentication

**Scraper API:**
- API Key authentication via `X-API-Key` header
- Keys configured via `API_KEYS` environment variable

**Job Scheduler:**
- JWT-based authentication
- Access tokens (1 hour) + Refresh tokens (7 days)
- Sliding window refresh

## 🐛 Troubleshooting

### Scraper API won't start
```bash
# Check logs
docker logs ebay-kleinanzeigen-scraper

# Common issues:
# - Port 3000 already in use
# - Missing API_KEYS environment variable
```

### Job Scheduler can't connect to Scraper API
```bash
# Verify Scraper API is running
curl http://scraper:3000/health

# Check network connectivity
docker exec ebay-kleinanzeigen-job-scheduler curl http://scraper:3000/health

# Verify API key matches in both services
```

### Jobs not executing
```bash
# Check scheduler logs
docker logs ebay-kleinanzeigen-job-scheduler

# Verify cron expression is valid
# Use https://crontab.guru to validate

# Check if job is enabled in dashboard
```

## 📊 Monitoring

### Health Checks

```bash
# Scraper API
curl http://scraper:3000/health

# Job Scheduler
curl http://localhost:3001/health

# All services via Scheduler API
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/health/services
```

### Logs

```bash
# View real-time logs
docker-compose logs -f

# Scraper API only
docker logs -f ebay-kleinanzeigen-scraper

# Job Scheduler only
docker logs -f ebay-kleinanzeigen-job-scheduler
```

## 🔄 Updates

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📝 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

**What this means:**
- ✅ **Free to use** - Personal and commercial use allowed
- ✅ **Modify freely** - Change and adapt the code as needed
- ✅ **Share improvements** - Any modifications must be shared back under AGPL-3.0
- ✅ **Network use disclosure** - If you run this as a web service, you must provide source code to users

This license ensures the project stays open source and improvements benefit everyone.

See the [LICENSE](LICENSE) file for full details or visit https://www.gnu.org/licenses/agpl-3.0.html

### Third-Party Notices

This project uses many excellent open-source libraries and tools. See [NOTICE.md](NOTICE.md) for a complete list of dependencies, copyright holders, and their licenses.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## ⚠️ Disclaimer

This tool is for educational purposes. Always respect kleinanzeigen.de's terms of service and robots.txt. Use responsibly and don't overload their servers.

## 📧 Support

For issues and questions:
- Open a GitHub issue
- Check existing documentation
- Review API docs at `/docs` endpoints

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐
