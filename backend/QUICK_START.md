# LangChain RAG Application - Quick Start

## 🚀 Quick Test

### Method 1: Use Interactive Script (Recommended)

```bash
cd backend
source venv/bin/activate
./setup_and_test.sh
```

The script will prompt you to enter:
- Google Cloud Project ID
- Vertex AI Region (default: europe-north1)
- RAG Corpus ID (default: gems-corpus)
- Fine-tuned Endpoint ID (optional)

### Method 2: Set Environment Variables Manually

```bash
cd backend
source venv/bin/activate

# Set environment variables (replace with actual values)
export GOOGLE_CLOUD_PROJECT=your-project-id
export VERTEX_AI_LOCATION=europe-north1
export RAG_CORPUS_ID=gems-corpus
export FINE_TUNED_ENDPOINT_ID=your-endpoint-id

# Run tests
python test_langchain_rag.py
```

### Method 3: Run Full Application

```bash
cd backend
source venv/bin/activate

# Set environment variables
export GOOGLE_CLOUD_PROJECT=your-project-id
export VERTEX_AI_LOCATION=europe-north1
export RAG_CORPUS_ID=gems-corpus
export FINE_TUNED_ENDPOINT_ID=your-endpoint-id

# Run interactive application
python langchain_rag.py
```

## 📋 Configuration Guide

### Required Configuration

1. **GOOGLE_CLOUD_PROJECT**: Your Google Cloud Project ID
2. **VERTEX_AI_LOCATION**: Vertex AI Region (e.g., europe-north1)
3. **RAG_CORPUS_ID**: RAG Corpus ID (e.g., gems-corpus)

### Optional Configuration

4. **FINE_TUNED_ENDPOINT_ID**: Fine-tuned Model Endpoint ID
   - If not set, LLM and full Chain tests will be skipped
   - Use `python test_finetuned_endpoint.py` to find Endpoint ID

## 🔍 Finding Endpoint ID

If you have a Fine-tuned Model but don't know the Endpoint ID:

```bash
# Method 1: Use test script
python test_finetuned_endpoint.py

# Method 2: Use gcloud
gcloud ai endpoints list --region=europe-north1

# Method 3: In Google Cloud Console
# Visit: https://console.cloud.google.com/vertex-ai/endpoints
```

## ✅ Test Checklist

Before running tests, please confirm:

- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Google Cloud authentication configured: `gcloud auth application-default login`
- [ ] Project ID set
- [ ] Region set
- [ ] RAG Corpus ID set
- [ ] (Optional) Endpoint ID set

## 🎯 Test Results Explanation

### Retriever Test
- ✅ Passed: Successfully retrieved documents from RAG Corpus
- ⚠️ Skipped: Environment variables not correctly set

### LLM Test
- ✅ Passed: Successfully called Fine-tuned Model Endpoint
- ⚠️ Skipped: Endpoint ID not set

### Full Chain Test
- ✅ Passed: Full RAG workflow (retrieval + generation) succeeded
- ⚠️ Skipped: Endpoint ID not set

## 📝 Example Output

```
LangChain RAG Application Test
============================================================

Current environment variables:
  GOOGLE_CLOUD_PROJECT: your-project-id
  VERTEX_AI_LOCATION: europe-north1
  RAG_CORPUS_ID: gems-corpus
  FINE_TUNED_ENDPOINT_ID: your-endpoint-id

Test 1: VertexRAGEngineRetriever
============================================================
✅ Retrieval successful! Found 3 documents

Test 2: VertexCustomEndpoint
============================================================
✅ Generation successful!
Answer: GEMS Agent is...

Test 3: Full RAG Chain
============================================================
✅ Full workflow successful!
Answer: ...
```

## 🆘 Troubleshooting

### Issue 1: Authentication Error

**Solution**: `gcloud auth application-default login`

### Issue 2: Permission Error

**Solution**: Ensure service account has Vertex AI User permissions

### Issue 3: Endpoint Not Found

**Solution**: 
1. Check if Endpoint ID is correct
2. Confirm Endpoint is deployed
3. Confirm region is correct

## 📚 Related Documentation

- `LANGCHAIN_RAG_TEST_RESULTS.md` - Detailed test results
- `FINE_TUNED_MODEL_SETUP.md` - Fine-tuned Model configuration
- `README.md` - Project documentation
