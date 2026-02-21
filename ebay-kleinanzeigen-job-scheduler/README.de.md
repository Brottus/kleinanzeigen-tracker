<div align="right">

**🇩🇪 Deutsch** | **[🇬🇧 English](README.md)**

</div>

# Ebay Kleinanzeigen Job Scheduler

Automatischer Job-Scheduling-Dienst mit Web-Dashboard zur Überwachung von kleinanzeigen.de-Anzeigen, mit Apprise-Benachrichtigungen (80+ Dienste) und optionaler Matterbridge-Integration.

## 🎯 Übersicht

Dieser Dienst bietet automatisches Scheduling für kleinanzeigen.de-Überwachungsjobs. Er verfügt über ein modernes Web-Dashboard, REST API, JWT-Authentifizierung, **Apprise** als Standard-Benachrichtigungs-Backend und optionale **Matterbridge**-Integration für Chat-Plattform-Benachrichtigungen.

## ✨ Funktionen

- **Cron-basiertes Scheduling** - Flexibles Scheduling mit Cron-Ausdrücken
- **Web-Dashboard** - Moderne SPA mit responsivem Design
- **JWT-Authentifizierung** - Sicheres Token-basiertes Auth mit Refresh-Tokens
- **Job-Verwaltung** - Jobs erstellen, aktualisieren, löschen und manuell auslösen
- **Prioritäts-Jobs** - Jobs als Priorität markieren, um `@everyone` an Benachrichtigungstitel anzuhängen
- **Apprise-Benachrichtigungen** - Standard-Benachrichtigungs-Backend mit 80+ Diensten (Telegram, Discord, Slack, Pushover, ntfy, Signal, etc.)
- **Matterbridge-Benachrichtigungen** - Optionale Bridge zu Chat-Plattformen (Discord, Slack, Teams, IRC, Matrix, etc.)
- **Inkrementelle Updates** - Verarbeitet nur neue Anzeigen seit dem letzten Durchlauf
- **Job-Historie** - Ausführungsstatus und Zeitstempel nachverfolgen
- **Dienst-Health-Monitoring** - Konnektivität zu allen Diensten prüfen
- **Produktionsbereit** - Gunicorn WSGI, SQLite-Datenbank, Health-Checks

## 🚀 Schnellstart

### Produktionsbereitstellung (Empfohlen)

**Mit Docker ausführen:**

```bash
# Erstellen
docker build -t ebay-kleinanzeigen-job-scheduler .

# Ausführen
docker run -d \
  -p 3001:3001 \
  -v scheduler-data:/app/data \
  -e ADMIN_PASSWORD=dein-sicheres-passwort \
  -e SESSION_SECRET=$(openssl rand -base64 32) \
  -e JWT_SECRET=$(openssl rand -base64 32) \
  -e SCRAPER_API_URL=http://scraper-api:3000 \
  -e SCRAPER_API_KEY=dein-api-key \
  -e APPRISE_ENABLED=true \
  -e APPRISE_API_URL=http://apprise:8000 \
  -e APPRISE_API_KEY=kleinanzeigen \
  --link scraper-api \
  --name job-scheduler \
  ebay-kleinanzeigen-job-scheduler
```

### Entwicklung/Tests mit Docker Compose

**Nur für Entwicklung und Tests:**

```bash
# Alle Dienste starten (Apprise ist als Standard-Benachrichtigungsdienst enthalten)
docker-compose up -d

# Benachrichtigungs-URLs zu Apprise für den Key "kleinanzeigen" hinzufügen
curl -X POST http://localhost:8000/add/kleinanzeigen \
  -d "urls=tgram://bottoken/ChatID"
```

**⚠️ Hinweis:** Docker Compose ist nur für Entwicklung/Tests. Für die Produktion Docker wie oben gezeigt verwenden.

### Manuelle Installation

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# Umgebung konfigurieren
cp .env.example .env
# .env mit den eigenen Einstellungen bearbeiten

# Server starten
python server.py
```

## 📖 Web-Dashboard

### Zugriff

Öffne http://localhost:3001

### Standard-Zugangsdaten

- **Benutzername:** `admin`
- **Passwort:** `admin`
- **⚠️ In der Produktion ändern!**

### Dashboard-Reiter

1. **Jobs** - Überwachungsjobs verwalten
2. **Konfiguration** - Diensteinstellungen (Benachrichtigungsanbieter, Scraper API)
3. **Dienste** - Health-Monitoring
4. **Konto** - Benutzereinstellungen

## 📖 API-Dokumentation

### Swagger UI

http://localhost:3001/docs

### Authentifizierung

#### Anmelden
```bash
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

Die Antwort enthält `access_token` und `refresh_token`.

#### Token verwenden
```bash
TOKEN="dein-access-token"
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/jobs
```

#### Token erneuern
```bash
curl -X POST http://localhost:3001/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"dein-refresh-token"}'
```

### Wichtige Endpunkte

```bash
# Jobs
GET    /api/jobs           # Jobs auflisten
POST   /api/jobs           # Job erstellen
GET    /api/jobs/{id}      # Job abrufen
PUT    /api/jobs/{id}      # Job aktualisieren
DELETE /api/jobs/{id}      # Job löschen
POST   /api/jobs/{id}/run  # Manuell ausführen

# Konfiguration
GET /api/config            # Konfiguration abrufen
PUT /api/config            # Konfiguration aktualisieren

# Health
GET /health                # Basis-Health (kein Auth)
GET /api/health/services   # Alle Dienste (Auth erforderlich)
```

## 🔧 Konfiguration

### Umgebungsvariablen

#### Kern
- `PORT` - Server-Port (Standard: `3001`)
- `DB_PATH` - Datenbankpfad (Standard: `/app/data/jobs.db`)
- `LOG_LEVEL` - Logging-Level (Standard: `INFO`)
- `FLASK_DEBUG` - Debug-Modus (Standard: `false`)
- `ENABLE_SWAGGER_UI` - Dokumentation aktivieren (Standard: `true`)
- `ENABLE_WEB_UI` - Dashboard aktivieren (Standard: `true`)

#### Authentifizierung
- `ADMIN_USERNAME` - Admin-Benutzer (Standard: `admin`)
- `ADMIN_PASSWORD` - Admin-Passwort (**unbedingt ändern!**)
- `SESSION_SECRET` - Session-Key (zufällig generieren)
- `JWT_SECRET` - JWT-Key (zufällig generieren)
- `JWT_ACCESS_TOKEN_EXPIRES` - Access-Token-TTL (Standard: `3600`s)
- `JWT_REFRESH_TOKEN_EXPIRES` - Refresh-Token-TTL (Standard: `604800`s)

#### Scraper API
- `SCRAPER_API_URL` - Scraper-URL (Standard: `http://scraper:3000`)
- `SCRAPER_API_KEY` - API-Key (Standard: `test-key-123`)
- `SCRAPER_REQUEST_TIMEOUT` - Timeout in Sekunden (Standard: `30`)

#### Benachrichtigungen
- `NOTIFICATION_LANGUAGE` - Sprache für Nachrichten: `en` oder `de` (Standard: `en`)

#### Apprise (Standard-Benachrichtigungs-Backend)
- `APPRISE_ENABLED` - Apprise aktivieren (Standard: `true`)
- `APPRISE_API_URL` - Apprise-API-URL (Standard: `http://apprise:8000`)
- `APPRISE_API_KEY` - Benachrichtigungs-Key (Standard: `kleinanzeigen`)
- `APPRISE_USERNAME` - HTTP-Basic-Auth-Benutzername (optional, nur Reverse Proxy)
- `APPRISE_PASSWORD` - HTTP-Basic-Auth-Passwort (optional, nur Reverse Proxy)

#### Matterbridge (Optional)
- `MATTERBRIDGE_ENABLED` - Matterbridge aktivieren (Standard: `false`)
- `MATTERBRIDGE_URL` - Matterbridge-API-URL (Standard: `http://matterbridge:4242`)
- `MATTERBRIDGE_TOKEN` - Bearer-Token zur Authentifizierung
- `MATTERBRIDGE_GATEWAY` - Gateway-Name (Standard: `gateway_ebaykleinanzeigen`)

#### Job-Standards
- `DEFAULT_JOB_SCHEDULE` - Standard-Cron-Schedule (Standard: `*/30 * * * *`)

---

## 🔔 Benachrichtigungen

### Apprise (Standard)

**Apprise** unterstützt 80+ Benachrichtigungsdienste, darunter Telegram, Discord, Slack, Pushover, ntfy, Signal, E-Mail und viele mehr.

- Repository: https://github.com/caronc/apprise
- Wiki & Dienstliste: https://github.com/caronc/apprise/wiki

#### Einrichtungsschritte

1. **Apprise starten** (standardmäßig in `docker-compose.yml` enthalten):
   ```bash
   docker-compose up -d
   ```
2. **Benachrichtigungs-URLs hinzufügen** für den Key `kleinanzeigen`:
   ```bash
   curl -X POST http://localhost:8000/add/kleinanzeigen \
     -d "urls=tgram://bottoken/ChatID"
   ```
   Oder die Apprise-Web-UI unter http://localhost:8000 verwenden
3. **Benachrichtigungen aktivieren** für einzelne Jobs im Dashboard

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

Vollständige Liste: https://github.com/caronc/apprise/wiki

---

### Matterbridge (Optional)

**Matterbridge** ist eine Bridge zwischen mehreren Chat-Plattformen (Discord, Slack, Teams, Telegram, IRC, Matrix, etc.).

- Repository: https://github.com/42wim/matterbridge
- Wiki: https://github.com/42wim/matterbridge/wiki
- Konfigurationsanleitung: https://github.com/42wim/matterbridge/wiki/How-to-create-your-config

#### Einrichtungsschritte

1. **Matterbridge installieren** und eine `matterbridge.toml`-Konfiguration erstellen
2. **Gateway einrichten** (Discord, Slack, etc.) in der Config
3. **API-Token abrufen** von der Matterbridge-Instanz
4. **Im Job Scheduler aktivieren:**
   ```bash
   MATTERBRIDGE_ENABLED=true
   MATTERBRIDGE_URL=http://matterbridge:4242
   MATTERBRIDGE_TOKEN=dein-token
   MATTERBRIDGE_GATEWAY=dein-gateway
   ```
   Oder über den Dashboard-Konfigurationsreiter konfigurieren
5. **Benachrichtigungen aktivieren** für einzelne Jobs

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

---

### Benachrichtigungsinhalt

Jede Anzeigenbenachrichtigung enthält:
- 📌 Titel, 💰 Preis, 📍 Standort
- 🕐 Einstellungsdatum, 👤 Verkäufertyp
- 📝 Beschreibung, 🖼️ Bild
- 🔗 Direktlink
- Alle kategoriespezifischen Felder (Versand, Zustand, etc.)

**Prioritäts-Jobs** hängen `@everyone` an den Benachrichtigungstitel an, um alle Kanalmitglieder zu benachrichtigen.

---

## 📅 Cron-Schedules

Standard 5-Felder-Cron-Ausdrücke:

```
┌─────── Minute (0-59)
│ ┌───── Stunde (0-23)
│ │ ┌─── Tag des Monats (1-31)
│ │ │ ┌─ Monat (1-12)
│ │ │ │ ┌ Wochentag (0-6, 0=Sonntag)
* * * * *
```

### Beispiele

| Ausdruck | Beschreibung |
|----------|-------------|
| `*/30 * * * *` | Alle 30 Minuten |
| `0 * * * *` | Jede Stunde |
| `0 9 * * *` | Täglich um 9 Uhr |
| `0 9 * * 1` | Montags um 9 Uhr |
| `0 9-17 * * 1-5` | Werktags 9–17 Uhr |

Ausdrücke unter https://crontab.guru validieren.

## 💡 Verwendungsbeispiele

### Überwachungsjob erstellen

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
    "name": "Münchner Tische",
    "url": "/s-wohnzimmer/muenchen/tisch/k0c88l6411",
    "schedule": "*/30 * * * *",
    "enabled": true,
    "notify_enabled": true,
    "priority": false
  }'
```

### Job-Ausführung überwachen

```bash
# Jobs mit Status auflisten
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/jobs | jq .

# Bestimmten Job prüfen
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/jobs/1 | jq .
```

## 🐛 Fehlerbehebung

### Jobs werden nicht ausgeführt
```bash
# Scheduler-Status prüfen
curl http://localhost:3001/health

# Prüfen ob Job aktiviert ist
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/jobs

# Cron-Ausdruck unter https://crontab.guru prüfen
```

### Verbindung zur Scraper API nicht möglich
```bash
# Scraper API testen
curl http://scraper:3000/health

# Konfiguration prüfen
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/config

# Prüfen ob API-Key übereinstimmt
```

### Apprise sendet keine Benachrichtigungen
```bash
# Prüfen ob Apprise läuft
curl http://localhost:8000

# Benachrichtigungs-URLs für den Key prüfen
curl http://localhost:8000/get/kleinanzeigen

# Benachrichtigung manuell testen
curl -X POST http://localhost:8000/notify/kleinanzeigen \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","body":"Hallo vom Kleinanzeigen Scheduler"}'
```

### Authentifizierungsprobleme
```bash
# Token abgelaufen — erneuern
curl -X POST http://localhost:3001/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"dein-refresh-token"}'

# Oder Datenbank zurücksetzen: rm jobs.db && python server.py
```

## 📊 Datenbank

### Schema

- **users** - Benutzerkonten
- **jobs** - Job-Konfigurationen (enthält `priority`-Spalte)
- **global_config** - Systemeinstellungen

### Manuelle Abfragen

```bash
# Jobs anzeigen
sqlite3 /app/data/jobs.db "SELECT * FROM jobs;"

# Konfiguration anzeigen
sqlite3 /app/data/jobs.db "SELECT * FROM global_config;"

# Letzten Durchlauf prüfen
sqlite3 /app/data/jobs.db \
  "SELECT name, last_run, last_status FROM jobs;"
```

## 🔒 Sicherheit

### Produktions-Checkliste

- [ ] Standard-Admin-Passwort ändern
- [ ] Starke `SESSION_SECRET` und `JWT_SECRET` generieren
- [ ] Sichere API-Keys verwenden
- [ ] `FLASK_DEBUG=false` setzen
- [ ] Firewall konfigurieren
- [ ] HTTPS-Reverse-Proxy verwenden
- [ ] Abhängigkeiten regelmäßig aktualisieren
- [ ] Swagger UI ggf. deaktivieren (`ENABLE_SWAGGER_UI=false`)

## 📈 Performance

- **Arbeitsspeicher:** ~100–150 MB
- **Datenbank:** SQLite (eingebettet, keine externe DB nötig)
- **Scheduler:** APScheduler (Hintergrund-Thread)
- **WSGI-Server:** Gunicorn (Produktion)

## 📝 Entwicklung

```bash
# Im Entwicklungsmodus ausführen
export LOG_LEVEL=DEBUG
export FLASK_DEBUG=false
python server.py

# API testen
python test_cli.py

# Logs prüfen
tail -f logs/scheduler.log
```

## 📄 Lizenz

Dieses Projekt ist unter der **GNU Affero General Public License v3.0 (AGPL-3.0)** lizenziert.

**Wichtige Punkte:**
- ✅ Kostenlos für private und kommerzielle Nutzung
- ✅ Ändern und anpassen nach Bedarf
- ✅ Verbesserungen an die Community zurückgeben
- ✅ Netzwerknutzung erfordert Offenlegung des Quellcodes

Siehe [LICENSE](../LICENSE)-Datei oder besuche https://www.gnu.org/licenses/agpl-3.0.html

## ⚠️ Haftungsausschluss

Nur für Bildungszwecke. Respektiere die Nutzungsbedingungen und Rate-Limits von kleinanzeigen.de.