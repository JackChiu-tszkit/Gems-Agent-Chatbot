#!/bin/bash
# Deployment script - unified deployment of frontend and backend to Cloud Run
# Note: This script should be run from the project root directory

set -e

# Set PATH and Python
export PATH=/opt/homebrew/share/google-cloud-sdk/bin:$PATH
export CLOUDSDK_PYTHON=/usr/bin/python3

# Ensure we're in the correct directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🚀 Starting deployment of GEMS Agent Chatbot to Cloud Run..."
echo "   This will deploy both frontend and backend to a single service"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud is not installed"
    echo "Please install Google Cloud SDK first:"
    echo "  brew install --cask google-cloud-sdk"
    exit 1
fi

# Set project (from environment variable or manual configuration)
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-project-id}"
REGION="${GOOGLE_CLOUD_REGION:-europe-north1}"
SERVICE_NAME="gems-agent-chatbot"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Check if already logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "🔐 Need to log in to Google Cloud first..."
    echo "Please complete login in your browser..."
    gcloud auth login
fi

echo "📦 Setting project..."
gcloud config set project ${PROJECT_ID}

# Read Google Client ID (for build-time injection)
GOOGLE_CLIENT_ID=""
if [ -f ".env" ]; then
    GOOGLE_CLIENT_ID=$(grep "VITE_GOOGLE_CLIENT_ID" .env | cut -d '=' -f2 | tr -d ' ' || echo "")
fi

if [ -z "$GOOGLE_CLIENT_ID" ]; then
    echo "⚠️  Warning: VITE_GOOGLE_CLIENT_ID not found"
    echo "   Please set it in .env file, or specify manually during build"
    read -p "   Enter Google OAuth Client ID (or press Enter to skip): " GOOGLE_CLIENT_ID
fi

echo ""
echo "🔨 Building and pushing Docker image..."
echo "   This may take a few minutes..."
echo ""

# Build arguments
BUILD_ARGS=""
if [ ! -z "$GOOGLE_CLIENT_ID" ]; then
    BUILD_ARGS="--build-arg VITE_GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}"
fi

# Build and push image
gcloud builds submit \
    --tag ${IMAGE_NAME} \
    ${BUILD_ARGS} \
    --timeout=20m

echo ""
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars GOOGLE_CLOUD_PROJECT=${PROJECT_ID},VERTEX_AI_LOCATION=${REGION},RAG_CORPUS_ID=${RAG_CORPUS_ID:-your-rag-corpus-id} \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10

echo ""
echo "✅ Deployment completed!"
echo ""
echo "📋 Getting service URL..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Deployment successful!"
echo ""
echo "   Service URL: ${SERVICE_URL}"
echo ""
echo "   Everyone can now access GEMS Agent Chatbot via this link!"
echo "   - Frontend UI and API are on the same service"
echo "   - Login with @company domain email"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

