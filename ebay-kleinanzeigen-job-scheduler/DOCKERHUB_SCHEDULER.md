# kleinanzeigen Job Scheduler

Automated job scheduling service with web dashboard for monitoring kleinanzeigen.de listings. Uses **Apprise** (80+ services) as the default notification backend, with optional Matterbridge integration.

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
  -e APPRISE_ENABLED=true \
  -e APPRISE_API_URL=http://apprise:8000 \
  -e APPRISE_API_KEY=kleinanzeigen \
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
| `SCRAPER_API_URL` | Scraper API URL (e.g., `http://scraper:3000`) |
| `SCRAPER_API_KEY` | API key for the Scraper API |

### Optional — Core

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `3001` | Server port |
| `ADMIN_USERNAME` | `admin` | Admin username |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `FLASK_DEBUG` | `false` | Flask debug mode (never enable in production!) |
| `ENABLE_SWAGGER_UI` | `true` | Enable API docs at `/docs` |
| `ENABLE_WEB_UI` | `true` | Enable web dashboard |
| `DB_PATH` | `/app/data/jobs.db` | SQLite database path |

### Optional — Scraper API

| Variable | Default | Description |
|----------|---------|-------------|
| `SCRAPER_REQUEST_TIMEOUT` | `30` | Timeout in seconds for Scraper API requests |

### Optional — Notifications

| Variable | Default | Description |
|----------|---------|-------------|
| `NOTIFICATION_LANGUAGE` | `en` | Language for messages: `en` (English) or `de` (German) |

### Optional — Apprise (Default notification backend)

| Variable | Default | Description |
|----------|---------|-------------|
| `APPRISE_ENABLED` | `true` | Enable Apprise notifications |
| `APPRISE_API_URL` | `http://apprise:8000` | Apprise API URL |
| `APPRISE_API_KEY` | `kleinanzeigen` | Notification key configured in Apprise |
| `APPRISE_USERNAME` | _(empty)_ | HTTP Basic Auth username (reverse proxy only) |
| `APPRISE_PASSWORD` | _(empty)_ | HTTP Basic Auth password (reverse proxy only) |

### Optional — Matterbridge (Optional notification bridge)

| Variable | Default | Description |
|----------|---------|-------------|
| `MATTERBRIDGE_ENABLED` | `false` | Enable Matterbridge notifications |
| `MATTERBRIDGE_URL` | `http://matterbridge:4242` | Matterbridge API URL |
| `MATTERBRIDGE_TOKEN` | _(empty)_ | Bearer token for authentication |
| `MATTERBRIDGE_GATEWAY` | `gateway_ebaykleinanzeigen` | Gateway name configured in Matterbridge |

### Optional — Job Defaults

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFAULT_JOB_SCHEDULE` | `*/30 * * * *` | Default cron schedule for new jobs (every 30 minutes) |

### Optional — JWT Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_ACCESS_TOKEN_EXPIRES` | `3600` | Access token lifetime in seconds (1 hour) |
| `JWT_REFRESH_TOKEN_EXPIRES` | `604800` | Refresh token lifetime in seconds (7 days) |

## 🔗 Connecting Services

The scheduler requires the Scraper API and Apprise to be running.

```bash
# 1. Start Apprise (notification backend)
docker run -d \
  -p 8000:8000 \
  --name apprise \
  caronc/apprise:latest

# Add notification URLs for the key "kleinanzeigen"
curl -X POST http://localhost:8000/add/kleinanzeigen \
  -d "urls=tgram://bottoken/ChatID"

# 2. Start Scraper
docker run -d \
  -p 3000:3000 \
  -e API_KEYS=my-key \
  --name scraper \
  brottus/ebay-kleinanzeigen-scraper:latest

# 3. Start Scheduler
docker run -d \
  -p 3001:3001 \
  -v scheduler-data:/app/data \
  -e ADMIN_PASSWORD=mypassword \
  -e SESSION_SECRET=$(openssl rand -base64 32) \
  -e JWT_SECRET=$(openssl rand -base64 32) \
  -e SCRAPER_API_URL=http://scraper:3000 \
  -e SCRAPER_API_KEY=my-key \
  -e APPRISE_ENABLED=true \
  -e APPRISE_API_URL=http://apprise:8000 \
  -e APPRISE_API_KEY=kleinanzeigen \
  --link scraper \
  --link apprise \
  --name scheduler \
  brottus/ebay-kleinanzeigen-job-scheduler:latest
```

## 🔔 Notification Setup

### Apprise (Default — 80+ services)

Apprise supports Telegram, Discord, Slack, Pushover, ntfy, Signal, E-Mail, and [80+ more](https://github.com/caronc/apprise/wiki).

**Popular URL formats:**

| Service | URL format |
|---------|-----------|
| Telegram | `tgram://bottoken/ChatID` |
| Discord | `discord://WebhookID/WebhookToken` |
| Slack | `slack://TokenA/TokenB/TokenC/Channel` |
| Pushover | `pover://UserKey/AppToken` |
| ntfy | `ntfy://topic` |
| Signal | `signal://PhoneNo/TargetPhoneNo` |
| E-Mail | `mailto://user:pass@gmail.com` |

Add URLs via the Apprise API or web UI at http://localhost:8000.

### Matterbridge (Optional)

Set `MATTERBRIDGE_ENABLED=true` and configure `MATTERBRIDGE_URL`, `MATTERBRIDGE_TOKEN`, and `MATTERBRIDGE_GATEWAY` to route notifications through a [Matterbridge](https://github.com/42wim/matterbridge) instance.

## ✨ Features

- Cron-based job scheduling
- Web dashboard with JWT authentication
- **Priority Jobs** — appends `@everyone` to notification titles
- Apprise notifications (default, 80+ services)
- Matterbridge notifications (optional)
- Job history and status tracking
- Manual job execution
- Service health monitoring

## 📖 Documentation

- **Web Dashboard:** http://localhost:3001
- **API Docs:** http://localhost:3001/docs
- **Health Check:** http://localhost:3001/health

**[🐳 View All Tags on Docker Hub](https://hub.docker.com/r/brottus/ebay-kleinanzeigen-job-scheduler/tags)**

**[📦 GitHub Releases](https://github.com/Brottus/ebaykleinanzeigen/releases)**

## 🌐 Platforms

- `linux/amd64` (Intel/AMD)
- `linux/arm64` (ARM, Raspberry Pi, Apple Silicon)

## 📚 Full Documentation

**GitHub Repository:** https://github.com/Brottus/ebaykleinanzeigen

For complete documentation, Apprise setup, Matterbridge setup, cron examples, and advanced configuration, visit the GitHub repository.

## 📄 License

AGPL-3.0 — See [LICENSE](https://github.com/Brottus/ebaykleinanzeigen/blob/main/LICENSE)