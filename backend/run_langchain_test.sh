#!/bin/bash
# Interactive test script - Run LangChain RAG Application

cd "$(dirname "$0")"
source venv/bin/activate

echo "============================================================"
echo "LangChain RAG Application - Interactive Testing"
echo "============================================================"
echo ""

# Check environment variables
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-}"
LOCATION="${VERTEX_AI_LOCATION:-}"
RAG_CORPUS_ID="${RAG_CORPUS_ID:-}"
ENDPOINT_ID="${FINE_TUNED_ENDPOINT_ID:-}"

# Try to get project ID from gcloud
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "your-project-id" ]; then
    GCLOUD_PROJECT=$(gcloud config get-value project 2>/dev/null)
    if [ ! -z "$GCLOUD_PROJECT" ]; then
        PROJECT_ID="$GCLOUD_PROJECT"
        echo "✅ Got project ID from gcloud: $PROJECT_ID"
    fi
fi

# If still not available, prompt user for input
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "your-project-id" ]; then
    read -p "Please enter Google Cloud Project ID: " PROJECT_ID
    export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
fi

if [ -z "$LOCATION" ]; then
    read -p "Please enter Vertex AI Region (default: europe-north1): " LOCATION
    LOCATION="${LOCATION:-europe-north1}"
    export VERTEX_AI_LOCATION="$LOCATION"
fi

if [ -z "$RAG_CORPUS_ID" ] || [ "$RAG_CORPUS_ID" = "your-rag-corpus-id" ]; then
    read -p "Please enter RAG Corpus ID (default: gems-corpus): " RAG_CORPUS_ID
    RAG_CORPUS_ID="${RAG_CORPUS_ID:-gems-corpus}"
    export RAG_CORPUS_ID="$RAG_CORPUS_ID"
fi

if [ -z "$ENDPOINT_ID" ]; then
    read -p "Please enter Fine-tuned Endpoint ID (optional, press Enter to skip): " ENDPOINT_ID
    if [ ! -z "$ENDPOINT_ID" ]; then
        export FINE_TUNED_ENDPOINT_ID="$ENDPOINT_ID"
    fi
fi

echo ""
echo "============================================================"
echo "Configuration Information:"
echo "============================================================"
echo "Project ID: $PROJECT_ID"
echo "Region: $LOCATION"
echo "RAG Corpus ID: $RAG_CORPUS_ID"
echo "Endpoint ID: ${ENDPOINT_ID:-Not set}"
echo "============================================================"
echo ""

# Run tests
echo "Running test script..."
python test_langchain_rag.py

echo ""
echo "If tests pass, you can run the interactive application:"
echo "  python langchain_rag.py"
