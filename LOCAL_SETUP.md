# Local Development Setup Guide

## Problem Diagnosis

If you see the error "Could not get response from GEMS Agent", possible causes:

### 1. Frontend Configuration Issue ✅ Fixed

`.env` file has been updated to use local backend:
```
VITE_CHAT_API_URL=http://localhost:8080/chat
```

### 2. Google Cloud Authentication Issue ⚠️ Needs Configuration

Local testing requires Google Cloud authentication to call Vertex AI RAG Engine.

## Solutions

### Method 1: Configure Application Default Credentials (Recommended)

```bash
# Install gcloud (if not already installed)
brew install --cask google-cloud-sdk

# Configure authentication
gcloud auth application-default login

# Set project
gcloud config set project your-project-id
```

### Method 2: Use Service Account Key

1. Create service account in Google Cloud Console
2. Download JSON key file
3. Set environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### Method 3: Deploy Directly to Cloud Run for Testing

If you don't want to configure local authentication, you can deploy directly to Cloud Run:

```bash
./deploy.sh
```

Cloud Run will automatically use service account credentials, no local configuration needed.

## Verification

After configuring authentication, restart the service:

```bash
# Stop current service (Ctrl+C)
# Then restart
./start.sh
```

Test API:
```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Test"}'
```

If it returns RAG results instead of authentication errors, configuration is successful!
