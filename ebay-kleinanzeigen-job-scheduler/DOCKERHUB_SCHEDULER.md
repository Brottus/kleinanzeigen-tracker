# kleinanzeigen Job Scheduler

Automated job scheduling service with web dashboard for monitoring kleinanzeigen.de listings with optional Matterbridge notifications.

## 🚀 Quick Start

```bash
docker pull brottus/ebay-kleinanzeigen-job-scheduler:latest

docker run -d \
  -p 3001:3001 \
  -v scheduler-data:/app/data \
  -e ADMIN_PASSWORD=your-secure-password \
  -e SESSION_SECRET=$(openssl rand -base64 32) \
  -e JWT_SECRET=$(openssl rand -base64 32) \
  -e SCRAPER_API_URL=http://scraper:3000 \
  -e SCRAPER_API_KEY=your-api-key \
  --name scheduler \
  brottus/ebay-kleinanzeigen-job-scheduler:latest
```

**Access:** http://localhost:3001

**Default Login:**
- Username: `admin`
- Password: Set via `ADMIN_PASSWORD`

## 📋 Environment Variables

### Required

| Variable | Description |
|----------|-------------|
| `ADMIN_PASSWORD` | Admin password (**change this!**) |
| `SESSION_SECRET` | Session encryption key (use random 32+ chars) |
| `JWT_SECRET` | JWT signing key (use random 32+ chars) |
| `SCRAPER_API_URL` | Scraper API URL (e.g., http://scraper:3000) |
| `SCRAPER_API_KEY` | API key for Scraper API |

### Optional - Core

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `3001` | Server port |
| `ADMIN_USERNAME` | `admin` | Admin username |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `FLASK_DEBUG` | `false` | Flask debug mode (never enable in production!) |
| `ENABLE_SWAGGER_UI` | `true` | Enable API docs at /docs |
| `ENABLE_WEB_UI` | `true` | Enable web dashboard |
| `DB_PATH` | `/app/data/jobs.db` | SQLite database path |

### Optional - Scraper API Defaults

| Variable | Default | Description |
|----------|---------|-------------|
| `SCRAPER_REQUEST_TIMEOUT` | `30` | Timeout in seconds for Scraper API requests |

### Optional - Matterbridge Notifications

| Variable | Default | Description |
|----------|---------|-------------|
| `MATTERBRIDGE_URL` | `http://matterbridge:4242` | Matterbridge API URL |
| `MATTERBRIDGE_TOKEN` | _(empty)_ | Bearer token for authentication |
| `MATTERBRIDGE_GATEWAY` | `gateway_ebaykleinanzeigen` | Gateway name configured in Matterbridge |
| `MATTERBRIDGE_USERNAME` | `Kleinanzeigen Bot` | Bot display name in messages |
| `NOTIFICATION_LANGUAGE` | `de` | Language for messages: `de` (German) or `en` (English) |

### Optional - Job Defaults

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFAULT_JOB_SCHEDULE` | `*/30 * * * *` | Default cron schedule for new jobs (every 30 minutes) |

### Optional - JWT Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_ACCESS_TOKEN_EXPIRES` | `3600` | Access token lifetime in seconds (1 hour) |
| `JWT_REFRESH_TOKEN_EXPIRES` | `604800` | Refresh token lifetime in seconds (7 days) |

## 🔗 Connecting to Scraper

The scheduler requires the Scraper API to be running. Link them with Docker:

```bash
# 1. Start Scraper
docker run -d \
  -p 3000:3000 \
  -e API_KEYS=my-key \
  --name scraper \
  brottus/ebay-kleinanzeigen-scraper:latest

# 2. Start Scheduler (linked to scraper)
docker run -d \
  -p 3001:3001 \
  -v scheduler-data:/app/data \
  -e ADMIN_PASSWORD=mypassword \
  -e SESSION_SECRET=$(openssl rand -base64 32) \
  -e JWT_SECRET=$(openssl rand -base64 32) \
  -e SCRAPER_API_URL=http://scraper:3000 \
  -e SCRAPER_API_KEY=my-key \
  --link scraper \
  --name scheduler \
  brottus/ebay-kleinanzeigen-job-scheduler:latest
```

## 📖 Documentation

- **Web Dashboard:** http://localhost:3001
- **API Docs:** http://localhost:3001/docs
- **Health Check:** http://localhost:3001/health

**[🐳 View All Tags on Docker Hub](https://hub.docker.com/r/brottus/ebay-kleinanzeigen-job-scheduler/tags)** - See all available container images

**[📦 GitHub Releases](https://github.com/Brottus/ebaykleinanzeigen/releases)** - View changelogs and source code

## 🌐 Platforms

- `linux/amd64` (Intel/AMD)
- `linux/arm64` (ARM, Raspberry Pi, Apple Silicon)

## 📚 Full Documentation

**GitHub Repository:** https://github.com/Brottus/ebaykleinanzeigen

For complete documentation, Matterbridge setup, cron examples, and advanced configuration, visit the GitHub repository.

## 📄 License

AGPL-3.0 - See [LICENSE](https://github.com/Brottus/ebaykleinanzeigen/blob/main/LICENSE)
