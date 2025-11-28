# GEMS Agent Chat UI

Frontend-klient for å snakke med GEMS Agent (Vertex AI + RAG) via Cloud Run API. Applikasjonen er bygget i React + TypeScript + Vite og støtter Google Workspace-pålogging for å begrense bruken til `@randstad.no`.

## Quick Start

### Local Testing (Run Frontend and Backend Together)

```bash
# Run the startup script (automatically starts both frontend and backend)
./start.sh
```

Or start manually:

```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2: Start frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`, backend runs on `http://localhost:8080`.

## Configuration

### Local Development

Create `.env` file (optional, to override defaults):

```
VITE_CHAT_API_URL=http://localhost:8080/chat   # Used for local development
VITE_GOOGLE_CLIENT_ID=YOUR_GOOGLE_OAUTH_CLIENT_ID
```

### Backend Configuration

Create `backend/.env` file:

```
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=europe-north1
RAG_CORPUS_ID=your-rag-corpus-id
PORT=8080
```

## Deploy to Cloud Run

### Unified Deployment (Frontend and Backend Together)

```bash
# Run from project root directory
./deploy.sh
```

This will:
1. Build frontend static files
2. Create a Docker image containing both frontend and backend
3. Deploy to Cloud Run
4. Frontend and API are on the same service, accessible via a single URL

After deployment, everyone can access the application via the URL provided by Cloud Run.

## Funksjoner

- Chat-grensesnitt med historikk, bobler for bruker/agent og tastaturstøtte (Enter for å sende, Shift+Enter for linjeskift).
- Laster-status og feilhåndtering når Cloud Run API-et svarer sent eller ikke kan nås.
- Google Workspace login via `@randstad.no` sjekk (ID-token dekodes og verifiserer e-postdomene).
- Tilpasset statussbanner som minner om manglende konfigurering.

## Videre tilpasning

- Oppdater tekstene i `src/App.tsx` dersom du ønsker mer lokaliserte meldinger.
- Tilpass styling i `src/App.css` og globale variabler i `src/index.css`.
- Legg gjerne inn telemetri/logging når du kobler UI-et til produksjon.
