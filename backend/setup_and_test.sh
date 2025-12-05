#!/bin/bash
# Interactive configuration and test script

cd "$(dirname "$0")"
source venv/bin/activate

echo "============================================================"
echo "LangChain RAG Application - Configuration and Testing"
echo "============================================================"
echo ""

# Read existing environment variables or prompt for input
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-}"
LOCATION="${VERTEX_AI_LOCATION:-}"
RAG_CORPUS_ID="${RAG_CORPUS_ID:-}"
ENDPOINT_ID="${FINE_TUNED_ENDPOINT_ID:-}"

# Get Project ID
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "your-project-id" ]; then
    echo "Please enter Google Cloud Project ID:"
    read -p "> " PROJECT_ID
    if [ -z "$PROJECT_ID" ]; then
        echo "❌ Project ID cannot be empty"
        exit 1
    fi
fi

# Get Region
if [ -z "$LOCATION" ]; then
    echo ""
    echo "Please enter Vertex AI Region (default: europe-north1):"
    read -p "> " LOCATION
    LOCATION="${LOCATION:-europe-north1}"
fi

# Get RAG Corpus ID
if [ -z "$RAG_CORPUS_ID" ] || [ "$RAG_CORPUS_ID" = "your-rag-corpus-id" ]; then
    echo ""
    echo "Please enter RAG Corpus ID (default: gems-corpus):"
    read -p "> " RAG_CORPUS_ID
    RAG_CORPUS_ID="${RAG_CORPUS_ID:-gems-corpus}"
fi

# Get Endpoint ID
if [ -z "$ENDPOINT_ID" ]; then
    echo ""
    echo "Please enter Fine-tuned Model Endpoint ID (optional, press Enter to skip LLM test):"
    read -p "> " ENDPOINT_ID
fi

# Set environment variables
export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
export VERTEX_AI_LOCATION="$LOCATION"
export RAG_CORPUS_ID="$RAG_CORPUS_ID"
if [ ! -z "$ENDPOINT_ID" ]; then
    export FINE_TUNED_ENDPOINT_ID="$ENDPOINT_ID"
fi

echo ""
echo "============================================================"
echo "Configuration Information:"
echo "============================================================"
echo "Project ID: $PROJECT_ID"
echo "Region: $LOCATION"
echo "RAG Corpus ID: $RAG_CORPUS_ID"
if [ ! -z "$ENDPOINT_ID" ]; then
    echo "Endpoint ID: $ENDPOINT_ID"
else
    echo "Endpoint ID: Not set (will skip LLM and full Chain tests)"
fi
echo "============================================================"
echo ""

# Confirm
read -p "Confirm to start testing? (y/n): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cancelled"
    exit 0
fi

echo ""
echo "Starting tests..."
echo ""

# Run tests
python test_langchain_rag.py

echo ""
echo "============================================================"
echo "Tests completed!"
echo "============================================================"
echo ""
echo "If tests pass, you can run the interactive application:"
echo "  python langchain_rag.py"
echo ""
echo "Or run with the following environment variables:"
echo "  export GOOGLE_CLOUD_PROJECT=$PROJECT_ID"
echo "  export VERTEX_AI_LOCATION=$LOCATION"
echo "  export RAG_CORPUS_ID=$RAG_CORPUS_ID"
if [ ! -z "$ENDPOINT_ID" ]; then
    echo "  export FINE_TUNED_ENDPOINT_ID=$ENDPOINT_ID"
fi
