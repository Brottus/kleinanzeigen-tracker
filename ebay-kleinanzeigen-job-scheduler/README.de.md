<div align="right">

**🇩🇪 Deutsch** | **[🇬🇧 English](README.md)**

</div>

# Ebay Kleinanzeigen Job Scheduler

Automatisierter Job-Scheduling-Dienst mit Web-Dashboard zur Überwachung von kleinanzeigen.de-Anzeigen mit optionalen Matterbridge-Benachrichtigungen.

## 🎯 Übersicht

Dieser Dienst bietet automatische Planung für kleinanzeigen.de-Überwachungsjobs. Er verfügt über ein modernes Web-Dashboard, REST-API, JWT-Authentifizierung und optionale Matterbridge-Integration für Echtzeit-Benachrichtigungen.

## ✨ Funktionen

- **Cron-basierte Planung** - Flexible Planung mit Cron-Ausdrücken
- **Web-Dashboard** - Moderne SPA mit responsivem Design
- **JWT-Authentifizierung** - Sichere token-basierte Authentifizierung mit Refresh-Tokens
- **Job-Verwaltung** - Erstellen, Aktualisieren, Löschen und manuelles Auslösen von Jobs
- **Benachrichtigungssystem** - Optionale Matterbridge-Integration (Discord, Slack, Teams, etc.)
- **Inkrementelle Updates** - Verarbeitet nur neue Anzeigen seit letztem Durchlauf
- **Job-Historie** - Verfolgt Ausführungsstatus und Zeitstempel
- **Service-Health-Überwachung** - Prüft Konnektivität zu allen Diensten
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
  --link scraper-api \
  --name job-scheduler \
  ebay-kleinanzeigen-job-scheduler
```

### Entwicklung/Tests mit Docker Compose

**Nur für Entwicklung und Tests:**

```bash
# docker-compose.yml bearbeiten, um deine Secrets zu setzen
docker-compose up -d
```

**⚠️ Hinweis:** Docker Compose ist für Entwicklung/Tests. Für Produktion verwende Docker wie oben gezeigt.

### Manuelle Installation

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# Umgebung konfigurieren
cp .env.example .env
# .env mit deinen Einstellungen bearbeiten

# Server starten
python server.py
```

## 📖 Web-Dashboard

### Zugriff

Öffne http://localhost:3001

### Standard-Zugangsdaten

- **Benutzername:** `admin`
- **Passwort:** `admin`
- **⚠️ In Produktion ändern!**

### Dashboard-Reiter

1. **Jobs** - Überwachungsjobs verwalten
2. **Konfiguration** - Diensteinstellungen
3. **Services** - Health-Überwachung
4. **Account** - Benutzereinstellungen

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

Antwort enthält `access_token` und `refresh_token`.

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

# Config
GET /api/config            # Config abrufen
PUT /api/config            # Config aktualisieren

# Health
GET /health                # Basis-Health (keine Auth)
GET /api/health/services   # Alle Services (Auth erforderlich)
```

## 🔧 Konfiguration

### Umgebungsvariablen

#### Kern
- `PORT` - Server-Port (Standard: 3001)
- `DB_PATH` - Datenbankpfad (Standard: /app/data/jobs.db)
- `LOG_LEVEL` - Logging-Level (Standard: INFO)
- `FLASK_DEBUG` - Debug-Modus (Standard: false)
- `ENABLE_SWAGGER_UI` - Dokumentation aktivieren (Standard: true)
- `ENABLE_WEB_UI` - Dashboard aktivieren (Standard: true)

#### Authentifizierung
- `ADMIN_USERNAME` - Admin-Benutzer (Standard: admin)
- `ADMIN_PASSWORD` - Admin-Passwort (**ändern!**)
- `SESSION_SECRET` - Session-Key (zufällig generieren)
- `JWT_SECRET` - JWT-Key (zufällig generieren)
- `JWT_ACCESS_TOKEN_EXPIRES` - Access-Token-TTL (Standard: 3600s)
- `JWT_REFRESH_TOKEN_EXPIRES` - Refresh-Token-TTL (Standard: 604800s)

#### Scraper API
- `SCRAPER_API_URL` - Scraper-URL (Standard: `http://localhost:3000`)
- `SCRAPER_API_KEY` - API-Key (Standard: `test-key-123`)
- `SCRAPER_REQUEST_TIMEOUT` - Timeout-Sekunden (Standard: `30`)

#### Matterbridge (Optional - für Benachrichtigungen)
- `MATTERBRIDGE_URL` - Matterbridge-API-URL (Standard: `http://matterbridge:4242`)
- `MATTERBRIDGE_TOKEN` - Bearer-Token für Authentifizierung (Standard: leer)
- `MATTERBRIDGE_GATEWAY` - Gateway-Name (Standard: `gateway_ebaykleinanzeigen`)
- `MATTERBRIDGE_USERNAME` - Bot-Anzeigename (Standard: `Kleinanzeigen Bot`)

#### Benachrichtigungen
- `NOTIFICATION_LANGUAGE` - Sprache für Nachrichten: `de` oder `en` (Standard: `de`)

#### Job-Standards
- `DEFAULT_JOB_SCHEDULE` - Standard-Cron-Zeitplan (Standard: `*/30 * * * *` = alle 30 Minuten)

**Matterbridge-Dokumentation:**
- Repository: https://github.com/42wim/matterbridge
- Setup-Anleitung: https://github.com/42wim/matterbridge/wiki
- Konfigurationsbeispiele: https://github.com/42wim/matterbridge/wiki/How-to-create-your-config

## 📅 Cron-Zeitpläne

Standard 5-Feld-Cron-Ausdrücke:

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
|----------|--------------|
| `*/30 * * * *` | Alle 30 Minuten |
| `0 * * * *` | Jede Stunde |
| `0 9 * * *` | Täglich um 9 Uhr |
| `0 9 * * 1` | Montags um 9 Uhr |
| `0 9-17 * * 1-5` | Wochentags 9-17 Uhr |

Verwende https://crontab.guru zur Validierung von Ausdrücken.

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
    "notify_enabled": true
  }'
```

### Job-Ausführung überwachen

```bash
# Jobs mit Status auflisten
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/jobs | jq .

# Spezifischen Job prüfen
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/jobs/1 | jq .
```

## 🔔 Benachrichtigungen mit Matterbridge

### Was ist Matterbridge?

**Matterbridge** ist eine Brücke zwischen mehreren Chat-Plattformen (Discord, Slack, Teams, Telegram, IRC, Matrix, etc.). Der Job Scheduler verwendet die Matterbridge-API, um formatierte Benachrichtigungen zu senden, wenn neue Anzeigen gefunden werden.

**Offizielle Dokumentation:**
- Haupt-Repo: https://github.com/42wim/matterbridge
- Wiki: https://github.com/42wim/matterbridge/wiki
- Konfigurationsanleitung: https://github.com/42wim/matterbridge/wiki/How-to-create-your-config

### Setup-Schritte

1. **Matterbridge installieren und konfigurieren** (siehe [offizielle Dokumentation](https://github.com/42wim/matterbridge/wiki))
2. **Gateway einrichten** (Discord, Slack, etc.)
3. **API-Token abrufen** von deiner Matterbridge-Instanz
4. **Im Job Scheduler konfigurieren:**
   - Dashboard → Konfigurationsreiter
   - Oder Umgebungsvariablen setzen (siehe oben)
5. **Benachrichtigungen aktivieren** für einzelne Jobs
6. **Sprache wählen** (Deutsch oder Englisch)

### Benachrichtigungsinhalt

Jede Anzeigenbenachrichtigung enthält:
- 📌 Titel, 💰 Preis, 📍 Standort
- 🕐 Veröffentlichungsdatum, 👤 Verkäufertyp
- 📝 Beschreibung, 🖼️ Bild
- 🔗 Direktlink
- Alle kategoriespezifischen Felder (Versand, Zustand, etc.)

Benachrichtigungen werden in Echtzeit gesendet, wenn neue Anzeigen erkannt werden.

## 🐛 Fehlerbehebung

### Jobs werden nicht ausgeführt
```bash
# Scheduler-Status prüfen
curl http://localhost:3001/health

# Prüfen, ob Job aktiviert ist
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/jobs

# Cron-Ausdruck prüfen
# Verwende https://crontab.guru
```

### Kann keine Verbindung zur Scraper-API herstellen
```bash
# Scraper-API testen
curl http://localhost:3000/health

# Konfiguration prüfen
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/config

# Prüfen, ob API-Key übereinstimmt
```

### Authentifizierungsprobleme
```bash
# Token abgelaufen - erneuern
curl -X POST http://localhost:3001/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"dein-refresh-token"}'

# Passwort über Dashboard zurücksetzen
# Oder Datenbank zurücksetzen: rm jobs.db && python server.py
```

## 📊 Datenbank

### Schema

- **users** - Benutzerkonten
- **jobs** - Job-Konfigurationen
- **global_config** - Systemeinstellungen

### Manuelle Abfragen

```bash
# Jobs anzeigen
sqlite3 /app/data/jobs.db "SELECT * FROM jobs;"

# Config anzeigen
sqlite3 /app/data/jobs.db "SELECT * FROM global_config;"

# Letzten Durchlauf prüfen
sqlite3 /app/data/jobs.db \
  "SELECT name, last_run, last_status FROM jobs;"
```

## 🔒 Sicherheit

### Produktions-Checkliste

- [ ] Standard-Admin-Passwort ändern
- [ ] Starke SESSION_SECRET und JWT_SECRET generieren
- [ ] Sichere API-Keys verwenden
- [ ] FLASK_DEBUG=false setzen
- [ ] Firewall konfigurieren
- [ ] HTTPS-Reverse-Proxy verwenden
- [ ] Abhängigkeiten regelmäßig aktualisieren
- [ ] Swagger UI bei Bedarf deaktivieren

## 📈 Performance

- **Speicher:** ~100-150 MB
- **Datenbank:** SQLite (eingebettet, keine externe DB erforderlich)
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
- ✅ Nach Bedarf ändern und anpassen
- ✅ Verbesserungen mit der Community teilen
- ✅ Netzwerknutzung erfordert Quellcode-Offenlegung

Siehe [LICENSE](../LICENSE)-Datei oder besuche https://www.gnu.org/licenses/agpl-3.0.html

## ⚠️ Haftungsausschluss

Nur zu Bildungszwecken. Respektiere die Nutzungsbedingungen und Rate-Limits von kleinanzeigen.de.
