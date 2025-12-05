# How to Run LangChain RAG Application

## 🚀 Quick Start (3 Methods)

### Method 1: Interactive Configuration Script (Easiest)

```bash
cd backend
source venv/bin/activate
./setup_and_test.sh
```

### Method 2: Run Tests Directly

```bash
cd backend
source venv/bin/activate

# Set environment variables
export GOOGLE_CLOUD_PROJECT=your-project-id
export VERTEX_AI_LOCATION=europe-north1
export RAG_CORPUS_ID=gems-corpus
export FINE_TUNED_ENDPOINT_ID=your-endpoint-id

# Run tests
python test_langchain_rag.py
```

### Method 3: Run Full Interactive Application

```bash
cd backend
source venv/bin/activate

# Set environment variables
export GOOGLE_CLOUD_PROJECT=your-project-id
export VERTEX_AI_LOCATION=europe-north1
export RAG_CORPUS_ID=gems-corpus
export FINE_TUNED_ENDPOINT_ID=your-endpoint-id

# Run application
python langchain_rag.py
```

## 📝 Detailed Steps

### Step 1: Navigate to Directory and Activate Virtual Environment

```bash
cd backend
source venv/bin/activate
```

### Step 2: Set Environment Variables

You need to provide the following information:
- **GOOGLE_CLOUD_PROJECT**: Your Google Cloud Project ID
- **VERTEX_AI_LOCATION**: Region (usually `europe-north1`)
- **RAG_CORPUS_ID**: RAG Corpus ID (usually `gems-corpus`)
- **FINE_TUNED_ENDPOINT_ID**: Fine-tuned Model Endpoint ID (optional)

### Step 3: Run

Choose one of the following:
- **Test**: `python test_langchain_rag.py`
- **Interactive Application**: `python langchain_rag.py`

## 🔍 Finding Configuration Information

### Find Project ID
```bash
gcloud config get-value project
```

### Find Endpoint ID
```bash
# Method 1: Use test script
python test_finetuned_endpoint.py

# Method 2: Use gcloud
gcloud ai endpoints list --region=europe-north1
```

## ⚠️ Common Issues

### Issue: "your-project-id" error
**Solution**: Set the correct `GOOGLE_CLOUD_PROJECT` environment variable

### Issue: Authentication error
**Solution**: Run `gcloud auth application-default login`

### Issue: Endpoint not found
**Solution**: Confirm Endpoint ID is correct, or run `python test_finetuned_endpoint.py` first to find it
