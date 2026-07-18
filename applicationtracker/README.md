# Application Tracker

Ein umfassendes Tool zur Verwaltung und Verfolgung deiner Bewerbungen. Mit dieser Web-App kannst du den Überblick über deine versendeten Bewerbungen behalten, den Status aktualisieren und wichtige Dokumente wie Anschreiben und Screenshots der Stellenanzeigen speichern.

## 🌐 Live-Demo
Die Anwendung ist live auf Render gehostet und kann hier aufgerufen werden:  
👉 **[https://application-tracker-lejq.onrender.com](https://application-tracker-lejq.onrender.com)**

## 🛠️ Tech-Stack

**Frontend:**
- Vue.js 3
- Vite
- Vue Router

**Backend:**
- Python / Flask
- Flask-SQLAlchemy (ORM)
- PostgreSQL (Datenbank)
- BeautifulSoup4 (für das Scraping von Stellenanzeigen-Details)

**Hosting / Deployment:**
- Render (mit `render.yaml` und `build.sh`)

## ✨ Features
- **Dashboard:** Übersicht aller deiner Bewerbungen und deren aktueller Status.
- **Bewerbungen verwalten:** Neue Bewerbungen hinzufügen, bestehende bearbeiten oder löschen.
- **Dokumenten-Upload:** Anschreiben und Screenshots von Stellenanzeigen direkt zur jeweiligen Bewerbung hochladen und speichern.
- **Authentifizierung:** Sicheres Login- und Registrierungssystem zum Schutz deiner Daten.

## 🚀 Lokale Installation

Um das Projekt lokal auf deinem Rechner auszuführen, folge diesen Schritten:

### Voraussetzungen
- [Node.js](https://nodejs.org/) (für das Frontend)
- [Python 3.x](https://www.python.org/) (für das Backend)
- [PostgreSQL](https://www.postgresql.org/) (oder SQLite für lokale Testzwecke, abhängig von der Konfiguration in `config.py`)

### 1. Repository klonen
```bash
git clone git@github.com:sherifKhamis/applicationTracker.git
cd applicationTracker
```

### 2. Backend einrichten
Wechsle in den Backend-Ordner und erstelle eine virtuelle Umgebung:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
```

Installiere die benötigten Abhängigkeiten:
```bash
pip install -r requirements.txt
```

Starte den Flask-Entwicklungsserver:
```bash
python app.py
# oder
flask run
```
Das Backend läuft standardmäßig auf `http://127.0.0.1:5000`.

### 3. Frontend einrichten
Öffne ein neues Terminal, wechsle in den Frontend-Ordner und installiere die Abhängigkeiten:
```bash
cd frontend
npm install
```

Starte den Vite-Entwicklungsserver:
```bash
npm run dev
```
Das Frontend läuft in der Regel auf `http://localhost:5173`.

## 📦 Deployment (Render)
Dieses Projekt ist für das Deployment auf [Render](https://render.com) vorkonfiguriert.
- `render.yaml`: Definiert die Web-Services für Frontend und Backend (oder einen kombinierten Service).
- `build.sh`: Ein Skript, das während des Build-Prozesses auf Render ausgeführt wird, um sowohl das Frontend zu bauen als auch die Python-Abhängigkeiten zu installieren.

## 📄 Lizenz
Dieses Projekt ist Open Source und zur freien Verwendung verfügbar.

Redeploy trigger Sat Jul 18 18:28:21 UTC 2026
