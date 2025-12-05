#!/bin/bash
# Quick run script

cd "$(dirname "$0")"
source venv/bin/activate

echo "============================================================"
echo "LangChain RAG Application - Quick Run"
echo "============================================================"
echo ""

# Check environment variables
if [ -z "$GOOGLE_CLOUD_PROJECT" ] || [ "$GOOGLE_CLOUD_PROJECT" = "your-project-id" ]; then
    echo "⚠️  Environment variables not set"
    echo ""
    echo "Please set environment variables first, then run:"
    echo "  export GOOGLE_CLOUD_PROJECT=your-project-id"
    echo "  export VERTEX_AI_LOCATION=europe-north1"
    echo "  export RAG_CORPUS_ID=gems-corpus"
    echo "  export FINE_TUNED_ENDPOINT_ID=your-endpoint-id"
    echo ""
    echo "Or run interactive configuration:"
    echo "  ./setup_and_test.sh"
    exit 1
fi

echo "✅ Environment variables set"
echo "   PROJECT_ID: $GOOGLE_CLOUD_PROJECT"
echo "   LOCATION: ${VERTEX_AI_LOCATION:-europe-north1}"
echo "   RAG_CORPUS_ID: ${RAG_CORPUS_ID:-gems-corpus}"
echo "   ENDPOINT_ID: ${FINE_TUNED_ENDPOINT_ID:-Not set}"
echo ""

# Select run mode
echo "Select run mode:"
echo "  1) Run tests (test_langchain_rag.py)"
echo "  2) Run full application (langchain_rag.py)"
echo "  3) Exit"
echo ""
read -p "Please choose (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Running tests..."
        python test_langchain_rag.py
        ;;
    2)
        echo ""
        echo "Running full application..."
        python langchain_rag.py
        ;;
    3)
        echo "Exiting"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
