# Deployment Guide

## Method 1: Using gcloud Command Line (Recommended)

### Step 1: Install Google Cloud SDK

**macOS:**
```bash
brew install --cask google-cloud-sdk
```

**Or manual installation:**
Visit https://cloud.google.com/sdk/docs/install to download and install

### Step 2: Login and Configuration

```bash
# Login
gcloud auth login

# Set project
gcloud config set project your-project-id
```

### Step 3: Deploy

**Using deployment script (easiest):**
```bash
cd "Gems Agent Chatbot UI/backend"
./deploy.sh
```

**Or execute manually:**
```bash
# 1. Build and push image
gcloud builds submit --tag gcr.io/your-project-id/gems-agent-api

# 2. Deploy to Cloud Run
gcloud run deploy gems-agent-api \
  --image gcr.io/your-project-id/gems-agent-api \
  --region europe-north1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=your-project-id,VERTEX_AI_LOCATION=europe-north1,RAG_CORPUS_ID=your-rag-corpus-id \
  --port 8080
```

## Method 2: Using Google Cloud Console (GUI)

### Step 1: Open Cloud Run

Visit: https://console.cloud.google.com/run?project=your-project-id

### Step 2: Create Service

1. Click **"Create Service"**
2. Select **"Deploy from source"** or **"Deploy from container image"**

### Step 3: Configure Service

**If selecting "Deploy from source":**
- Select source code location (GitHub, Cloud Source Repositories, etc.)
- Or upload code ZIP file

**If selecting "Deploy from container image":**
- Need to build image first (use Method 1 Step 1)

**Service Configuration:**
- **Service Name**: `gems-agent-api`
- **Region**: `europe-north1`
- **Platform**: Cloud Run (fully managed)
- **Authentication**: Allow unauthenticated invocations

**Environment Variables:**
- `GOOGLE_CLOUD_PROJECT` = `your-project-id`
- `VERTEX_AI_LOCATION` = `europe-north1`
- `RAG_CORPUS_ID` = `your-rag-corpus-id`
- `FINE_TUNED_ENDPOINT_ID` = `your-endpoint-id` (optional)
- `FINE_TUNED_MODEL_ID` = `your-model-id` (optional)

### Step 4: Deploy

Click **"Create"** button and wait for deployment to complete.

## After Deployment

After successful deployment, you'll see the service URL, for example:
```
https://gems-agent-api-xxxxx-nw.a.run.app
```

### Update Frontend Configuration

Add service URL to frontend `.env` file:

```bash
VITE_CHAT_API_URL=https://gems-agent-api-xxxxx-nw.a.run.app/chat
```

### Test API

```bash
# Test health check
curl https://your-service-url.run.app/health

# Test chat endpoint
curl -X POST https://your-service-url.run.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message"}'
```

## Troubleshooting

### Issue 1: Insufficient Permissions

Ensure your account has the following permissions:
- Cloud Run Admin
- Service Account User
- Cloud Build Editor

### Issue 2: Build Failure

Check:
- Dockerfile is correct
- Dependencies in requirements.txt are available
- View build logs: `gcloud builds list`

### Issue 3: Cannot Access After Deployment

Check:
- Environment variables are correctly set
- View service logs: `gcloud run services logs read gems-agent-api --region europe-north1`
