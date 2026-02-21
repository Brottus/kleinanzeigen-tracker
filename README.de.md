<div align="right">

**🇩🇪 Deutsch** | **[🇬🇧 English](README.md)**

</div>

# Ebay Kleinanzeigen Monitoring System

<div align="center">
  <img src="assets/banner.svg" alt="kleinanzeigen tracker" width="800">
</div>

<br>

[![Create Release](https://github.com/Brottus/kleinanzeigen-tracker/actions/workflows/release.yml/badge.svg)](https://github.com/Brottus/kleinanzeigen-tracker/actions/workflows/release.yml)
[![Build and Push Docker Images](https://github.com/Brottus/kleinanzeigen-tracker/actions/workflows/build-and-push.yml/badge.svg)](https://github.com/Brottus/kleinanzeigen-tracker/actions/workflows/build-and-push.yml)
[![CodeQL](https://github.com/Brottus/kleinanzeigen-tracker/actions/workflows/github-code-scanning/codeql/badge.svg?branch=main)](https://github.com/Brottus/kleinanzeigen-tracker/actions/workflows/github-code-scanning/codeql)
[![Dependabot Status](https://img.shields.io/badge/Dependabot-aktiviert-success?logo=dependabot)](https://github.com/Brottus/ebaykleinanzeigen/network/updates)

[![Lizenz: AGPL v3](https://img.shields.io/badge/Lizenz-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.14+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Bereit-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

[![Docker Pulls - Scraper](https://img.shields.io/docker/pulls/brottus/ebay-kleinanzeigen-scraper?logo=docker&label=Scraper%20Downloads)](https://hub.docker.com/r/brottus/ebay-kleinanzeigen-scraper)
[![Docker Pulls - Scheduler](https://img.shields.io/docker/pulls/brottus/ebay-kleinanzeigen-job-scheduler?logo=docker&label=Scheduler%20Downloads)](https://hub.docker.com/r/brottus/ebay-kleinanzeigen-job-scheduler)
[![Docker Image Size - Scraper](https://img.shields.io/docker/image-size/brottus/ebay-kleinanzeigen-scraper/latest?logo=docker&label=Scraper%20Größe)](https://hub.docker.com/r/brottus/ebay-kleinanzeigen-scraper)
[![Docker Image Size - Scheduler](https://img.shields.io/docker/image-size/brottus/ebay-kleinanzeigen-job-scheduler/latest?logo=docker&label=Scheduler%20Größe)](https://hub.docker.com/r/brottus/ebay-kleinanzeigen-job-scheduler)

Ein umfassendes Microservices-basiertes System zur Überwachung und zum Scraping von Kleinanzeigen auf kleinanzeigen.de (ehemals eBay Kleinanzeigen) mit automatischer Job-Planung und Benachrichtigungen über Apprise oder Matterbridge.

---

<div align="center">

### 🤖 Unterstütze dieses Projekt

*Dieses Projekt wurde mit KI-Unterstützung entwickelt. Wenn du es nützlich findest, spendiere mir ein paar KI-Token!* ☕

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/brottus)

</div>

---

## 🎯 Projektübersicht

Dieses System besteht aus zwei Hauptdiensten, die zusammenarbeiten, um eine automatisierte Überwachung von kleinanzeigen.de-Anzeigen zu ermöglichen:

1. **Ebay Kleinanzeigen Scraper** - Produktionsreife API zum Extrahieren von Anzeigendaten
2. **Ebay Kleinanzeigen Job Scheduler** - Automatische Job-Planung mit Web-Dashboard

### Hauptfunktionen

- ✅ **Umfassende Datenextraktion** - 15 Felder pro Anzeige inkl. Bilder, Preise, Standorte und mehr
- ✅ **Multi-URL-Unterstützung** - Scrape mehrere Such-URLs gleichzeitig mit automatischer Deduplizierung
- ✅ **Automatische Planung** - Cron-basierte Job-Planung mit APScheduler
- ✅ **Anti-Detection** - User-Agent-Rotation, zufällige Verzögerungen und automatische Wiederholungen
- ✅ **Echtzeit-Benachrichtigungen** - Apprise (80+ Dienste) und/oder Matterbridge für sofortige Benachrichtigungen
- ✅ **Prioritäts-Jobs** - Jobs als Priorität markieren, um `@everyone` an Benachrichtigungstitel anzuhängen
- ✅ **Web-Dashboard** - Moderne SPA mit JWT-Authentifizierung
- ✅ **REST API** - Vollständige OpenAPI/Swagger-Dokumentation
- ✅ **Docker-Unterstützung** - Produktionsreife Containerisierung
- ✅ **Produktionsbereit** - Gunicorn WSGI-Server, Health-Checks, Logging

## 📊 Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker-Netzwerk                           │
│                                                              │
│  ┌──────────────────────┐      ┌──────────────────────┐    │
│  │     Scraper          │      │       Scheduler      │    │
│  │  Port: 3000          │◄─────┤ Port: 3001           │    │
│  │                      │      │                      │    │
│  │  • Datenextraktion   │      │  • Job-Verwaltung    │    │
│  │  • API-Key-Auth      │      │  • Web-Dashboard     │    │
│  │  • Multi-URL-Support │      │  • JWT-Auth          │    │
│  │  • Anti-Detection    │      │  • Benachrichtigungen│    │
│  └──────────────────────┘      └──────────────────────┘    │
│           │                              │                  │
└───────────┼──────────────────────────────┼──────────────────┘
            │                              │
            ▼                         ▼         ▼
     kleinanzeigen.de            Apprise    Matterbridge
                               (Standard)   (optional)
```

## 🚀 Schnellstart

### Voraussetzungen

- Docker (für Produktionsbereitstellung)
- Docker Compose (nur für Entwicklung/Tests)
- ODER Python 3.11+ (für manuelle Installation)

### Produktionsbereitstellung (Empfohlen)

**Jeden Dienst in einem eigenen Docker-Container ausführen:**

1. **Scraper API erstellen und ausführen**
```bash
cd ebay-kleinanzeigen-scraper
docker build -t kleinanzeigen-scraper-api .
docker run -d \
  -p 3000:3000 \
  -e API_KEYS=dein-sicherer-api-key \
  --name scraper-api \
  kleinanzeigen-scraper-api
```

2. **Job Scheduler erstellen und ausführen**
```bash
cd ebay-kleinanzeigen-job-scheduler
docker build -t kleinanzeigen-job-scheduler .
docker run -d \
  -p 3001:3001 \
  -v scheduler-data:/app/data \
  -e ADMIN_PASSWORD=dein-sicheres-passwort \
  -e SESSION_SECRET=$(openssl rand -base64 32) \
  -e JWT_SECRET=$(openssl rand -base64 32) \
  -e SCRAPER_API_URL=http://scraper-api:3000 \
  -e SCRAPER_API_KEY=dein-sicherer-api-key \
  --link scraper-api \
  --name job-scheduler \
  kleinanzeigen-job-scheduler
```

3. **Auf die Dienste zugreifen**
- Scraper API: http://scraper:3000
- Scraper Dokumentation: http://scraper:3000/docs
- Scheduler Dashboard: http://localhost:3001
- Scheduler API Dokumentation: http://localhost:3001/docs

4. **Standard-Zugangsdaten**
- Benutzername: `admin`
- Passwort: Über `ADMIN_PASSWORD` festgelegt

### Entwicklung/Tests mit Docker Compose

**Nur für Entwicklung und Tests:**

```bash
# Repository klonen
git clone <repository-url>
cd ebaykleinanzeigen

# 1. docker-compose.yml bearbeiten, um Secrets zu setzen (SESSION_SECRET, JWT_SECRET, etc.)

# 2. Alle Dienste starten — Apprise ist der Standard-Benachrichtigungsdienst
docker-compose up -d

# 3. Benachrichtigungs-URLs zu Apprise für den Key "kleinanzeigen" hinzufügen
curl -X POST http://localhost:8000/add/kleinanzeigen \
  -d "urls=tgram://bottoken/ChatID"
```

**Enthaltene Dienste:**
- `scraper` - Scraper API (Port 3000)
- `scheduler` - Job Scheduler (Port 3001)
- `apprise` - Benachrichtigungs-Backend, **Standard** (Port 8000)
- `matterbridge` - Optionale Message Bridge (Port 4242, siehe [Matterbridge-Einrichtung](#matterbridge-einrichtung))

**⚠️ Hinweis:** Docker Compose wird nur für Entwicklung/Tests empfohlen. Für die Produktion verwende individuelle Docker-Container wie oben gezeigt.

### Manuelle Installation

Siehe individuelle Service README-Dateien:
- [Scraper Setup](./ebay-kleinanzeigen-scraper/README.de.md)
- [Scheduler Setup](./ebay-kleinanzeigen-job-scheduler/README.de.md)

## 📚 Dienst-Dokumentation

### Ebay Kleinanzeigen Scraper API

**Zweck:** Anzeigendaten von kleinanzeigen.de-Suchseiten extrahieren

**Wichtige Endpunkte:**
- `GET /api/scrape` - Anzeigen von URL(s) scrapen
- `GET /api/newest` - Nur neueste Anzeige abrufen
- `GET /health` - Health-Check

**Funktionen:**
- 15-Felder-Datenextraktion (ID, Titel, Preis, Standort, Bilder, etc.)
- Multi-URL-Scraping mit Deduplizierung
- `since`-Parameter für inkrementelle Updates
- API-Key-Authentifizierung
- User-Agent-Rotation & Anti-Detection
- Docker-Bereitstellung verfügbar

[Vollständige Dokumentation →](./ebay-kleinanzeigen-scraper/README.de.md)

### Ebay Kleinanzeigen Job Scheduler

**Zweck:** Überwachung mit geplanten Jobs und Benachrichtigungen automatisieren

**Hauptfunktionen:**
- Cron-basierte Job-Planung
- Web-Dashboard mit JWT-Authentifizierung
- Apprise-Integration für Benachrichtigungen (80+ Dienste — Standard)
- Matterbridge-Integration für Benachrichtigungen (optional)
- Prioritäts-Jobs — hängt `@everyone` an Benachrichtigungstitel an
- Job-Historie und Statusverfolgung
- Manuelle Job-Ausführung
- Docker-Bereitstellung verfügbar

**Endpunkte:**
- `POST /api/auth/login` - Authentifizieren
- `GET /api/jobs` - Jobs auflisten
- `POST /api/jobs` - Job erstellen
- `POST /api/jobs/{id}/run` - Job manuell ausführen

[Vollständige Dokumentation →](./ebay-kleinanzeigen-job-scheduler/README.de.md)

## 🔧 Konfiguration

### Umgebungsvariablen

#### Scraper API
```bash
PORT=3000                          # Server-Port
API_KEYS=key1,key2                # Kommagetrennte API-Keys
LOG_LEVEL=INFO                     # Logging-Level
ENABLE_SWAGGER_UI=true            # API-Dokumentation aktivieren
```

#### Job Scheduler
```bash
PORT=3001                          # Server-Port
ADMIN_USERNAME=admin              # Admin-Benutzername
ADMIN_PASSWORD=admin              # Admin-Passwort (ändern!)
SESSION_SECRET=random-secret      # Session-Verschlüsselungskey
JWT_SECRET=random-jwt-secret      # JWT-Signaturkey
ENABLE_SWAGGER_UI=true            # API-Dokumentation aktivieren
ENABLE_WEB_UI=true                # Web-Dashboard aktivieren

# Scraper API Verbindung
SCRAPER_API_URL=http://scraper:3000
SCRAPER_API_KEY=test-key-123

# Benachrichtigungssprache
NOTIFICATION_LANGUAGE=de          # de oder en

# Apprise (Standard-Benachrichtigungsmethode — 80+ Dienste)
APPRISE_ENABLED=true
APPRISE_API_URL=http://apprise:8000
APPRISE_API_KEY=kleinanzeigen
APPRISE_USERNAME=                  # Optional: HTTP Basic Auth (nur Reverse Proxy)
APPRISE_PASSWORD=                  # Optional: HTTP Basic Auth (nur Reverse Proxy)

# Matterbridge (optional — deaktivieren falls nicht verwendet)
MATTERBRIDGE_ENABLED=false
MATTERBRIDGE_URL=http://matterbridge:4242
MATTERBRIDGE_TOKEN=dein-token
MATTERBRIDGE_GATEWAY=gateway_name
```

### Apprise-Einrichtung

**Apprise** ist das Standard-Benachrichtigungs-Backend. Es unterstützt über 80 Dienste, darunter Telegram, Discord, Slack, Pushover, ntfy, Signal und viele mehr.

- Repository: https://github.com/caronc/apprise
- Wiki & vollständige Dienstliste: https://github.com/caronc/apprise/wiki

#### Option 1: Docker Compose verwenden (Entwicklung/Tests — Standard)

Die enthaltene `docker-compose.yml` hat Apprise bereits als **Standard**-Benachrichtigungsdienst konfiguriert. Einfach den Stack starten:

```bash
docker-compose up -d
# Apprise API verfügbar unter http://apprise:8000 (im Docker-Netzwerk)
# oder http://localhost:8000 (vom Host aus)
```

Benachrichtigungs-URLs für den Key `kleinanzeigen` per curl hinzufügen:
```bash
curl -X POST http://localhost:8000/add/kleinanzeigen \
  -d "urls=tgram://bottoken/ChatID"
```

Oder die Apprise Web-UI unter http://localhost:8000 zur URL-Verwaltung nutzen.

#### Option 2: Eigenständiges Apprise (Produktion)

```bash
# Apprise separat ausführen
docker run -d \
  -p 8000:8000 \
  --name apprise \
  caronc/apprise:latest

# Job Scheduler konfigurieren, um sich damit zu verbinden
docker run -d \
  -e APPRISE_ENABLED=true \
  -e APPRISE_API_URL=http://apprise:8000 \
  -e APPRISE_API_KEY=kleinanzeigen \
  --link apprise \
  kleinanzeigen-job-scheduler
```

#### Konfigurationsschritte

1. **Apprise installieren** (via Docker wie oben gezeigt)
2. **Benachrichtigungs-URLs hinzufügen** für den `APPRISE_API_KEY` (z.B. `kleinanzeigen`) — siehe das [Apprise-Wiki](https://github.com/caronc/apprise/wiki) für dienstspezifische URL-Formate
3. **Scheduler konfigurieren:**
   - `APPRISE_ENABLED=true`, `APPRISE_API_URL`, `APPRISE_API_KEY` setzen
   - Oder Dashboard-Konfigurationsreiter verwenden
4. **Benachrichtigungen aktivieren** für einzelne Jobs

**Beliebte Benachrichtigungs-URL-Formate:**

| Dienst | URL-Format |
|--------|-----------|
| Telegram | `tgram://bottoken/ChatID` |
| Discord | `discord://WebhookID/WebhookToken` |
| Slack | `slack://TokenA/TokenB/TokenC/Channel` |
| Pushover | `pover://UserKey/AppToken` |
| ntfy | `ntfy://topic` oder `ntfys://host/topic` |
| Signal | `signal://PhoneNo/TargetPhoneNo` |
| E-Mail | `mailto://user:pass@gmail.com` |

Vollständige Dienstliste: https://github.com/caronc/apprise/wiki

---

### Matterbridge-Einrichtung

**Matterbridge** ist eine Message-Bridge, die Benachrichtigungen an verschiedene Chat-Plattformen weiterleitet (Discord, Slack, Teams, Telegram, IRC, Matrix, etc.).

- Repository: https://github.com/42wim/matterbridge
- Wiki & Setup-Anleitung: https://github.com/42wim/matterbridge/wiki
- Konfigurationsbeispiele: https://github.com/42wim/matterbridge/wiki/How-to-create-your-config

#### Option 1: Docker Compose verwenden (Entwicklung/Tests)

Matterbridge zusätzlich zu Apprise in den `docker-compose.yml`-Stack einfügen:

```bash
# 1. Matterbridge-Konfigurationsverzeichnis erstellen
mkdir -p matterbridge

# 2. matterbridge.toml-Konfigurationsdatei erstellen
# Siehe offizielle Anleitung: https://github.com/42wim/matterbridge/wiki/How-to-create-your-config
nano matterbridge/matterbridge.toml

# 3. API-Token setzen
export MATTERBRIDGE_TOKEN="dein-api-token"

# 4. Alle Dienste starten
docker-compose up -d

# 5. Matterbridge verfügbar unter http://matterbridge:4242 (im Docker-Netzwerk)
#    oder http://localhost:4242 (vom Host aus)
```

#### Option 2: Eigenständiges Matterbridge (Produktion)

```bash
# Matterbridge separat ausführen
docker run -d \
  -p 4242:4242 \
  -v /pfad/zur/config:/etc/matterbridge:ro \
  --name matterbridge \
  42wim/matterbridge:stable

# Job Scheduler konfigurieren, um sich damit zu verbinden
docker run -d \
  -e MATTERBRIDGE_ENABLED=true \
  -e MATTERBRIDGE_URL=http://matterbridge:4242 \
  -e MATTERBRIDGE_TOKEN=dein-token \
  -e MATTERBRIDGE_GATEWAY=dein-gateway \
  --link matterbridge \
  kleinanzeigen-job-scheduler
```

#### Konfigurationsschritte

1. **Matterbridge installieren** (via Docker wie oben gezeigt)
2. **Konfigurationsdatei erstellen** `matterbridge.toml` — [Konfigurationsanleitung](https://github.com/42wim/matterbridge/wiki/How-to-create-your-config)
3. **Gateway einrichten** (Discord, Slack, etc.) in der Config
4. **API-Token abrufen** von deiner Matterbridge-Instanz
5. **Job Scheduler konfigurieren:**
   - `MATTERBRIDGE_ENABLED=true`, `MATTERBRIDGE_URL=http://matterbridge:4242`, `MATTERBRIDGE_TOKEN`, `MATTERBRIDGE_GATEWAY` setzen
   - Oder Dashboard-Konfigurationsreiter verwenden
6. **Benachrichtigungen aktivieren** für einzelne Jobs

**Beispiel `matterbridge.toml` API-Abschnitt:**
```toml
[api]
  [api.myapi]
  BindAddress = "0.0.0.0:4242"
  Token = "dein-geheimes-token"
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

**Unterstützte Plattformen:** Discord, Slack, Telegram, Teams, IRC, Matrix, Mattermost, Rocket.Chat, XMPP und [viele mehr](https://github.com/42wim/matterbridge#supported-protocols).

Für detaillierte Konfiguration siehe das [offizielle Wiki](https://github.com/42wim/matterbridge/wiki).

## 💡 Verwendungsbeispiele

### Beispiel 1: Münchner Möbel überwachen

1. **Beim Scheduler Dashboard anmelden**
```
http://localhost:3001
Benutzername: admin
Passwort: admin
```

2. **Einen Job erstellen**
- Name: "Münchner Tische"
- URL: `/s-wohnzimmer/muenchen/tisch/k0c88l6411`
- Zeitplan: `*/30 * * * *` (alle 30 Minuten)
- Benachrichtigungen aktivieren: Ja

3. **Job läuft automatisch** und benachrichtigt dich über neue Anzeigen!

### Beispiel 2: API-Nutzung

**Anzeigen scrapen:**
```bash
curl -H "X-API-Key: test-key-123" \
  "http://scraper:3000/api/scrape?url=/s-autos/c216"
```

**Nur neue Anzeigen seit letzter Prüfung abrufen:**
```bash
curl -H "X-API-Key: test-key-123" \
  "http://scraper:3000/api/scrape?url=/s-autos/c216&since=3287237963"
```

**Job via API erstellen:**
```bash
# 1. Anmelden
TOKEN=$(curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  | jq -r '.access_token')

# 2. Job erstellen
curl -X POST http://localhost:3001/api/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Autos überwachen",
    "url": "/s-autos/c216",
    "schedule": "*/30 * * * *",
    "notify_enabled": true
  }'
```

## 📖 API-Dokumentation

Beide Dienste bieten interaktive Swagger UI-Dokumentation:

- **Scraper API Dokumentation:** http://scraper:3000/docs
- **Scheduler API Dokumentation:** http://localhost:3001/docs

## 🔒 Sicherheit

### Produktions-Checkliste

- [ ] Standard-Admin-Passwort ändern
- [ ] Starke `SESSION_SECRET` und `JWT_SECRET` generieren
- [ ] Sichere API-Keys verwenden (nicht `test-key-123`)
- [ ] `FLASK_DEBUG=false` setzen
- [ ] Firewall-Regeln konfigurieren
- [ ] HTTPS-Reverse-Proxy verwenden (nginx/traefik)
- [ ] Abhängigkeiten regelmäßig aktualisieren
- [ ] Erwäge Swagger UI in Produktion zu deaktivieren (`ENABLE_SWAGGER_UI=false`)

### Authentifizierung

**Scraper API:**
- API-Key-Authentifizierung via `X-API-Key`-Header
- Keys konfiguriert via `API_KEYS`-Umgebungsvariable

**Job Scheduler:**
- JWT-basierte Authentifizierung
- Access Tokens (1 Stunde) + Refresh Tokens (7 Tage)
- Sliding Window Refresh

## 🐛 Fehlerbehebung

### Scraper API startet nicht
```bash
# Logs prüfen
docker logs ebay-kleinanzeigen-scraper

# Häufige Probleme:
# - Port 3000 bereits in Verwendung
# - Fehlende API_KEYS-Umgebungsvariable
```

### Job Scheduler kann sich nicht mit Scraper API verbinden
```bash
# Prüfen, ob Scraper API läuft
curl http://scraper:3000/health

# Netzwerkverbindung prüfen
docker exec ebay-kleinanzeigen-job-scheduler curl http://scraper:3000/health

# Prüfen, ob API-Key in beiden Diensten übereinstimmt
```

### Jobs werden nicht ausgeführt
```bash
# Scheduler-Logs prüfen
docker logs ebay-kleinanzeigen-job-scheduler

# Cron-Ausdruck validieren
# Verwende https://crontab.guru zur Validierung

# Prüfen, ob Job im Dashboard aktiviert ist
```

## 📊 Monitoring

### Health Checks

```bash
# Scraper API
curl http://scraper:3000/health

# Job Scheduler
curl http://localhost:3001/health

# Alle Dienste via Scheduler API
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/health/services
```

### Logs

```bash
# Echtzeit-Logs anzeigen
docker-compose logs -f

# Nur Scraper API
docker logs -f ebay-kleinanzeigen-scraper

# Nur Job Scheduler
docker logs -f ebay-kleinanzeigen-job-scheduler
```

## 🔄 Updates

```bash
# Neueste Änderungen abrufen
git pull

# Neu erstellen und neu starten
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📝 Lizenz

Dieses Projekt ist unter der **GNU Affero General Public License v3.0 (AGPL-3.0)** lizenziert.

**Was das bedeutet:**
- ✅ **Kostenlos nutzbar** - Private und kommerzielle Nutzung erlaubt
- ✅ **Frei modifizierbar** - Code nach Bedarf ändern und anpassen
- ✅ **Verbesserungen teilen** - Alle Änderungen müssen unter AGPL-3.0 zurück geteilt werden
- ✅ **Netzwerknutzung offenlegen** - Bei Betrieb als Webdienst muss Quellcode Nutzern zur Verfügung gestellt werden

Diese Lizenz stellt sicher, dass das Projekt Open Source bleibt und Verbesserungen allen zugutekommen.

Siehe [LICENSE](LICENSE)-Datei für vollständige Details oder besuche https://www.gnu.org/licenses/agpl-3.0.html

### Drittanbieter-Hinweise

Dieses Projekt verwendet viele hervorragende Open-Source-Bibliotheken und Tools. Siehe [NOTICE.md](NOTICE.md) für eine vollständige Liste der Abhängigkeiten, Urheberrechtsinhaber und deren Lizenzen.

## 🤝 Mitwirken

Beiträge sind willkommen! Bitte:
1. Repository forken
2. Feature-Branch erstellen
3. Änderungen vornehmen
4. Pull Request einreichen

## ⚠️ Haftungsausschluss

Dieses Tool dient nur zu Bildungszwecken. Respektiere immer die Nutzungsbedingungen und robots.txt von kleinanzeigen.de. Verwende es verantwortungsvoll und überlade ihre Server nicht.

## 📧 Support

Für Probleme und Fragen:
- Öffne ein GitHub Issue
- Prüfe bestehende Dokumentation
- Sieh dir die API-Dokumentation unter `/docs`-Endpunkten an

## 🌟 Star History

Wenn du dieses Projekt nützlich findest, gib ihm bitte einen Stern! ⭐
