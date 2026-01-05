# kleinanzeigen Scraper API

Production-ready API for extracting listing data from kleinanzeigen.de (formerly eBay Kleinanzeigen).

## 🚀 Quick Start

```bash
docker pull brottus/ebay-kleinanzeigen-scraper:latest

docker run -d \
  -p 3000:3000 \
  -e API_KEYS=your-secure-api-key \
  --name scraper \
  brottus/ebay-kleinanzeigen-scraper:latest
```

**Access:** http://localhost:3000

## 📋 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_KEYS` | ✅ Yes | - | Comma-separated API keys for authentication |
| `PORT` | No | `3000` | Server port |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `FLASK_DEBUG` | No | `false` | Flask debug mode (never use in production!) |
| `ENABLE_SWAGGER_UI` | No | `true` | Enable API docs at /docs |

## 🔑 Authentication

Include API key in requests:

```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:3000/api/scrape?url=/s-autos/c216"
```

## 📖 API Documentation

- **Swagger UI:** http://localhost:3000/docs
- **Health Check:** http://localhost:3000/health

**[🐳 View All Tags on Docker Hub](https://hub.docker.com/r/brottus/ebay-kleinanzeigen-scraper/tags)** - See all available container images

**[📦 GitHub Releases](https://github.com/Brottus/ebaykleinanzeigen/releases)** - View changelogs and source code

## 🌐 Platforms

- `linux/amd64` (Intel/AMD)
- `linux/arm64` (ARM, Raspberry Pi, Apple Silicon)

## 📚 Full Documentation

**GitHub Repository:** https://github.com/Brottus/ebaykleinanzeigen

For complete documentation, examples, and configuration options, visit the GitHub repository.

## 📄 License

AGPL-3.0 - See [LICENSE](https://github.com/Brottus/ebaykleinanzeigen/blob/main/LICENSE)
