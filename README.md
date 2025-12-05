# GEMS Agent Chat UI

Frontend client for chatting with GEMS Agent (Vertex AI + RAG) via Cloud Run API. The application is built with React + TypeScript + Vite and supports Google Workspace login to restrict usage to `@randstad.no` accounts.

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

Frontend runs on `http://localhost:3000`, backend runs on `http://localhost:8080`.

## Interface Example

The GEMS Agent Chat UI provides a clean, modern chat interface. Here's what it looks like:

![GEMS Agent Chat Interface](./docs/images/Example_figure.png)

### Chat Interface Layout

- **User Messages**: Displayed in blue rounded bubbles aligned to the right, labeled with "YOU"
- **Agent Messages**: Displayed in light grey rounded bubbles aligned to the left, labeled with "GEMS AGENT"
- **Message Input**: A text input field at the bottom with a "Send" button for submitting queries
- **Keyboard Support**: Press Enter to send, Shift+Enter for a new line

### Example Conversation

When you start a conversation, the GEMS Agent introduces itself with:

> "Hello! I am an AI agent designed to support resource management, sales enablement, market analysis, and operational automation. How can I assist you today? For example, you can ask me to:
> - Find available consultants with specific skills.
> - Generate a summary of a consultant's expertise.
> - Analyze market trends based on our project data."

The interface supports markdown rendering for agent responses, making it easy to display formatted text, lists, and structured information.

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

## Features

- Chat interface with history, message bubbles for user/agent, and keyboard support (Enter to send, Shift+Enter for new line).
- Loading status and error handling when Cloud Run API responds slowly or is unreachable.
- Google Workspace login via `@randstad.no` check (ID token is decoded and email domain is verified).
- Custom status banner that reminds about missing configuration.

## Further Customization

- Update texts in `src/App.tsx` if you want more localized messages.
- Customize styling in `src/App.css` and global variables in `src/index.css`.
- Consider adding telemetry/logging when connecting the UI to production.
