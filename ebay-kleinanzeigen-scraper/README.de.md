<div align="right">

**🇩🇪 Deutsch** | **[🇬🇧 English](README.md)**

</div>

# Ebay Kleinanzeigen Scraper

Produktionsreife API zum Scraping und Extrahieren von Anzeigendaten von kleinanzeigen.de (ehemals eBay Kleinanzeigen).

## 🎯 Übersicht

Dieser Dienst bietet eine REST-API zum Extrahieren umfassender Anzeigendaten von kleinanzeigen.de-Suchseiten. Er verfügt über Anti-Detection-Mechanismen, Multi-URL-Unterstützung und robuste Fehlerbehandlung.

## ✨ Funktionen

- **Umfassende Datenextraktion** - 15 Felder pro Anzeige
- **Multi-URL-Unterstützung** - Scrape mehrere Suchen gleichzeitig mit automatischer Deduplizierung
- **Inkrementelle Updates** - `since`-Parameter für nur neue Anzeigen
- **Anti-Detection**
  - User-Agent-Rotation (7 verschiedene Browser)
  - Zufällige Verzögerungen (2-5 Sekunden, konfigurierbar)
  - Automatische Wiederholung mit exponentiellem Backoff
  - Rate-Limit-Erkennung
- **Produktionsbereit**
  - Gunicorn WSGI-Server
  - Health-Checks
  - Strukturiertes Logging
  - API-Key-Authentifizierung
  - OpenAPI/Swagger-Dokumentation

## 📊 Extrahierte Datenfelder

Jede Anzeige enthält bis zu 15 Felder:

| Feld | Typ | Beschreibung | Beispiel |
|------|-----|--------------|----------|
| `id` | string | Eindeutige Anzeigen-ID | `"3287237963"` |
| `title` | string | Anzeigentitel | `"Designer Couchtisch"` |
| `url` | string | Vollständige URL zur Anzeige | `"https://www.kleinanzeigen.de/..."` |
| `price` | string/null | Preis wie angezeigt | `"160 €"` oder `null` |
| `location` | string/null | PLZ + Stadtteil | `"80797 Schwabing-West"` |
| `image` | string/null | Hauptbild-URL | `"https://img.kleinanzeigen.de/..."` |
| `image_count` | int/null | Gesamtzahl der Bilder | `3` |
| `description` | string/null | Kurzbeschreibung | `"Nur 1x aufgebaut, wie neu!"` |
| `posted_date` | string/null | Veröffentlichungsdatum | `"Heute, 14:51"` |
| `shipping` | string/null | Versandinfo | `"Versand möglich"` |
| `seller_type` | string | Verkäufertyp | `"PRIVATE"` oder `"PRO"` |
| `seller_name` | string/null | Verkäufername | Meist `null` bei Suche |
| `buy_now` | boolean | Direktkauf verfügbar | `false` |
| `is_featured` | boolean | Beworbene/Featured-Anzeige | `false` |
| `additional_info` | array | Kategoriespezifische Felder | `["Automatik", "Benzin"]` |

## 🚀 Schnellstart

### Docker (Empfohlen)

```bash
# Erstellen
docker build -t ebay-kleinanzeigen-scraper .

# Ausführen
docker run -d \
  -p 3000:3000 \
  -e API_KEYS=dein-api-key \
  --name scraper \
  ebay-kleinanzeigen-scraper
```

### Manuelle Installation

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# API-Keys setzen
export API_KEYS=test-key-123,production-key-456

# Server starten
python server.py
```

## 📖 API-Dokumentation

### Interaktive Dokumentation

Nach dem Start verfügbar unter:
- **Swagger UI:** http://localhost:3000/docs
- **OpenAPI Spec:** http://localhost:3000/openapi.yaml

### Endpunkte

#### 1. Health Check (Öffentlich)

```bash
GET /health
```

**Antwort:**
```json
{
  "status": "ok",
  "timestamp": "2026-01-04T15:00:00Z",
  "uptime": 3600,
  "version": "1.0.0"
}
```

#### 2. Anzeigen scrapen

```bash
GET /api/scrape?url={such_url}&since={anzeigen_id}
```

**Authentifizierung:** Benötigt `X-API-Key`-Header

**Parameter:**
- `url` (erforderlich) - Such-URL-Pfad oder kommagetrennte Pfade
- `since` (optional) - Nur Anzeigen mit ID größer als diese zurückgeben

**Einzelne URL Beispiel:**
```bash
curl -H "X-API-Key: test-key-123" \
  "http://localhost:3000/api/scrape?url=/s-autos/c216"
```

**Multi-URL Beispiel:**
```bash
curl -H "X-API-Key: test-key-123" \
  "http://localhost:3000/api/scrape?url=/s-autos/c216+global.farbe:blau,/s-autos/c216+global.farbe:gelb"
```

**Inkrementelles Update Beispiel:**
```bash
curl -H "X-API-Key: test-key-123" \
  "http://localhost:3000/api/scrape?url=/s-autos/c216&since=3287237963"
```

**Antwort:**
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

#### 3. Neueste Anzeige abrufen

```bash
GET /api/newest?url={such_url}
```

**Authentifizierung:** Benötigt `X-API-Key`-Header

Gibt nur die neueste (höchste ID) nicht-beworbene Anzeige zurück. Nützlich zum schnellen Prüfen, ob neue Artikel gepostet wurden.

**Beispiel:**
```bash
curl -H "X-API-Key: test-key-123" \
  "http://localhost:3000/api/newest?url=/s-autos/c216"
```

**Antwort:**
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

## 🔧 Konfiguration

### Umgebungsvariablen

| Variable | Standard | Beschreibung |
|----------|----------|--------------|
| `PORT` | `3000` | Server-Port |
| `API_KEYS` | *erforderlich* | Kommagetrennte API-Keys |
| `LOG_LEVEL` | `INFO` | Logging-Level (DEBUG, INFO, WARNING, ERROR) |
| `FLASK_DEBUG` | `false` | Flask-Debug-Modus (nie in Produktion verwenden!) |
| `ENABLE_SWAGGER_UI` | `true` | Swagger-Docs unter /docs aktivieren |

### API-Key-Verwaltung

API-Keys werden über die `API_KEYS`-Umgebungsvariable konfiguriert:

```bash
# Einzelner Key
export API_KEYS=mein-sicherer-key-123

# Mehrere Keys (kommagetrennt)
export API_KEYS=key1,key2,key3
```

Key in Anfragen über `X-API-Key`-Header einschließen:

```bash
curl -H "X-API-Key: mein-sicherer-key-123" \
  "http://localhost:3000/api/scrape?url=/s-autos/c216"
```

## 🛡️ Anti-Detection-Funktionen

### User-Agent-Rotation

Rotiert automatisch zwischen 7 verschiedenen Browser-User-Agents:
- Chrome (Windows, Mac, Linux)
- Firefox (Windows, Mac)
- Safari (Mac)
- Edge (Windows)

### Verzögerungskonfiguration

```python
# Zufällige Verzögerung zwischen Anfragen (2-5 Sekunden)
# Konfigurierbar in server.py
MIN_DELAY = 2
MAX_DELAY = 5
```

### Wiederholungslogik

- 3 automatische Wiederholungen mit exponentiellem Backoff
- Backoff-Faktor: 0,5 Sekunden
- Behandelt Netzwerkfehler, Timeouts und Rate-Limits

## 📊 Anwendungsfälle

### 1. Neue Anzeigen überwachen

```bash
# Erster Durchlauf - neueste Anzeige abrufen
NEWEST=$(curl -H "X-API-Key: key" \
  "http://localhost:3000/api/newest?url=/s-autos/c216" \
  | jq -r '.newest.id')

# $NEWEST speichern

# Nachfolgende Durchläufe - nur neue Anzeigen abrufen
curl -H "X-API-Key: key" \
  "http://localhost:3000/api/scrape?url=/s-autos/c216&since=$NEWEST"
```

### 2. Mehrere Kriterien durchsuchen

```bash
# Nach blauen UND gelben Autos separat suchen, Ergebnisse kombinieren
curl -H "X-API-Key: key" \
  "http://localhost:3000/api/scrape?url=/s-autos/c216+global.farbe:blau,/s-autos/c216+global.farbe:gelb"

# Automatische Deduplizierung, falls gleiche Anzeige in beiden erscheint
```

### 3. Kategoriespezifische Suchen

```bash
# Möbel
curl -H "X-API-Key: key" \
  "http://localhost:3000/api/scrape?url=/s-wohnzimmer/muenchen/tisch/k0c88l6411"

# Elektronik
curl -H "X-API-Key: key" \
  "http://localhost:3000/api/scrape?url=/s-telefon-handy/c173"

# Immobilien
curl -H "X-API-Key: key" \
  "http://localhost:3000/api/scrape?url=/s-wohnung-mieten/c203"
```

## 🔍 Such-URLs finden

1. Gehe zu https://www.kleinanzeigen.de
2. Suche nach dem, was du willst
3. Wende Filter an (Ort, Preis, etc.)
4. Kopiere den URL-Pfad nach `kleinanzeigen.de`

**Beispiel:**
```
Vollständige URL: https://www.kleinanzeigen.de/s-autos/muenchen/bmw/k0c216l6411r50+autos.marke_s:bmw
Verwende dies: /s-autos/muenchen/bmw/k0c216l6411r50+autos.marke_s:bmw
```

## 🐛 Fehlerbehebung

### "Invalid or missing API key"

```bash
# Prüfen, ob API-Key gesetzt ist
echo $API_KEYS

# Header-Format prüfen
curl -v -H "X-API-Key: dein-key" http://localhost:3000/api/scrape?url=/s-autos/c216
```

### "Failed to fetch URL: URL not found"

- Prüfe, ob der URL-Pfad korrekt ist
- Verifiziere, dass die Suche tatsächlich Ergebnisse auf kleinanzeigen.de hat
- URL könnte fehlerhaft oder abgelaufen sein

### Rate-Limited

```bash
# Dienst wiederholt automatisch mit Backoff
# Prüfe Logs auf "Rate limit"-Meldungen

# Falls anhaltend, Verzögerungen in server.py erhöhen:
MIN_DELAY = 5  # Von 2 erhöhen
MAX_DELAY = 10 # Von 5 erhöhen
```

### Keine Ergebnisse zurückgegeben

```bash
# Debug-Logging aktivieren
export LOG_LEVEL=DEBUG
python server.py

# Logs auf detaillierten Scraping-Prozess prüfen
```

## 📈 Performance

- **Antwortzeit:** ~2-7 Sekunden pro URL (inkl. Anti-Detection-Verzögerungen)
- **Durchsatz:** ~10-20 Anfragen/Minute (respektiert Rate-Limits)
- **Gleichzeitige Anfragen:** Von Gunicorn-Workern verarbeitet (Standard: 4)

## 🔒 Sicherheit

### Produktions-Checkliste

- [ ] Starke, zufällige API-Keys verwenden
- [ ] `FLASK_DEBUG=false` setzen
- [ ] Firewall konfigurieren (nur notwendige IPs erlauben)
- [ ] HTTPS-Reverse-Proxy verwenden
- [ ] Logs auf verdächtige Aktivitäten überwachen
- [ ] API-Keys regelmäßig rotieren
- [ ] Erwäge Swagger UI zu deaktivieren (`ENABLE_SWAGGER_UI=false`)

## 📝 Entwicklung

### Im Entwicklungsmodus ausführen

```bash
export API_KEYS=test-key-123
export LOG_LEVEL=DEBUG
export FLASK_DEBUG=false  # Auch in Entwicklung aus Sicherheitsgründen false

python server.py
```

### Testen

```bash
# Health-Check
curl http://localhost:3000/health

# Scraping testen
curl -H "X-API-Key: test-key-123" \
  "http://localhost:3000/api/scrape?url=/s-autos/c216" \
  | jq .
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

Dieses Tool dient nur zu Bildungszwecken. Respektiere immer kleinanzeigen.de's:
- Nutzungsbedingungen
- robots.txt
- Rate-Limits

Verwende es verantwortungsvoll und überlade ihre Server nicht.
