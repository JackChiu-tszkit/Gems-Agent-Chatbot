# GEMS Agent Chatbot - Quick Start Guide

## 📋 Overview

This project includes:
- **Frontend**: React + TypeScript + Vite chat interface
- **Backend**: Python + FastAPI, calling Vertex AI RAG Engine
- **Unified Deployment**: Frontend and backend can be deployed together to Cloud Run

## 🚀 Local Testing

### Method 1: Use Startup Script (Recommended)

```bash
# Run from project root directory
./start.sh
```

This will automatically:
1. Start backend API (port 8080)
2. Start frontend UI (port 3000)
3. Open browser to http://localhost:3000

### Method 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or: python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export $(cat .env | xargs)
python main.py
```

**Terminal 2 - Frontend:**
```bash
npm install
npm run dev
```

Then open in browser: http://localhost:3000

## ☁️ Deploy to Cloud Run

### One-Click Deployment

```bash
# Run from project root directory
./deploy.sh
```

This will:
1. Build frontend static files
2. Create Docker image containing both frontend and backend
3. Deploy to Cloud Run
4. Provide a public URL that everyone can access

### After Deployment

After deployment completes, you'll get a URL, for example:
```
https://gems-agent-chatbot-xxxxx.run.app
```

**Everyone can access via this link:**
1. Open the link
2. Login with @randstad.no email
3. Start using GEMS Agent

## 📁 Project Structure

```
Gems Agent Chatbot UI/
├── start.sh              # Local startup script
├── deploy.sh              # Cloud Run deployment script
├── Dockerfile             # Unified deployment Dockerfile
├── src/                   # Frontend source code
├── backend/               # Backend source code
│   ├── main.py           # FastAPI application (also serves static files)
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Backend environment variables
└── dist/                  # Frontend build output (used for deployment)
```

## ⚙️ Configuration

### Frontend Configuration

`.env` file (optional, for local development):
```
VITE_CHAT_API_URL=http://localhost:8080/chat
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

### Backend Configuration

`backend/.env` file:
```
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=europe-north1
RAG_CORPUS_ID=your-rag-corpus-id
PORT=8080
```

## 🔧 Troubleshooting

### Local Startup Failure

1. **Backend startup failure**:
   - Check if `backend/.env` file exists
   - Check if virtual environment is activated
   - View `backend.log` file

2. **Frontend startup failure**:
   - Run `npm install` to install dependencies
   - View `frontend.log` file

### Deployment Failure

1. **Build failure**:
   - Check if `gcloud` is logged in
   - Check if project ID is correct
   - View Cloud Build logs

2. **Cannot access after deployment**:
   - Check if service allows unauthenticated access
   - View Cloud Run logs

## 📝 Important Notes

1. **Local Development**: Frontend and backend run separately, frontend uses `http://localhost:8080/chat`
2. **Cloud Run Deployment**: Frontend and backend unified deployment, frontend uses relative path `/chat`
3. **Google OAuth**: Ensure Client ID is configured correctly
4. **Permissions**: Ensure Cloud Run service account has Vertex AI access permissions
