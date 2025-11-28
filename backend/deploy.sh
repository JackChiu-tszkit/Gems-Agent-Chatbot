#!/bin/bash
# Deployment script - deploy GEMS Agent API to Cloud Run
# Note: This script should be run from the backend directory

set -e

# Set PATH and Python
export PATH=/opt/homebrew/share/google-cloud-sdk/bin:$PATH
export CLOUDSDK_PYTHON=/usr/bin/python3

# Ensure we're in the correct directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🚀 Starting deployment of GEMS Agent API to Cloud Run..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud is not installed"
    echo "Please install Google Cloud SDK first:"
    echo "  brew install --cask google-cloud-sdk"
    exit 1
fi

# Set project
# Get from environment variable or use default value
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-project-id}"
REGION="${GOOGLE_CLOUD_REGION:-europe-north1}"
SERVICE_NAME="gems-agent-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Check if already logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "🔐 Need to log in to Google Cloud first..."
    echo "Please complete login in your browser..."
    gcloud auth login
fi

echo "📦 Setting project..."
gcloud config set project ${PROJECT_ID}

echo "🔨 Building and pushing Docker image..."
echo "This may take a few minutes..."
gcloud builds submit --tag ${IMAGE_NAME}

echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --region ${REGION} \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=${PROJECT_ID},VERTEX_AI_LOCATION=${REGION},RAG_CORPUS_ID=${RAG_CORPUS_ID:-your-rag-corpus-id} \
  --port 8080

echo ""
echo "✅ Deployment completed!"
echo ""
echo "📋 Getting service URL..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Please add the following URL to VITE_CHAT_API_URL in frontend .env file:"
echo "${SERVICE_URL}/chat"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
