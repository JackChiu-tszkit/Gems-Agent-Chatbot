# Fine-tuned Model Integration Guide

This document explains how to configure and use Fine-tuned Model combined with RAG Agent.

## Architecture Overview

The system now supports two generation modes:

1. **Fine-tuned Model (Priority)**: Uses your fine-tuned model to generate more standardized, business-aligned responses
2. **Standard Gemini Model (Fallback)**: Automatically falls back to standard Gemini model if Fine-tuned Model is unavailable

## Workflow

```
User Question
    ↓
RAG Retrieval (get relevant documents from Corpus)
    ↓
Build Enhanced Prompt (include retrieved context)
    ↓
Try to generate using Fine-tuned Model
    ├─ Success → Return Fine-tuned model response
    └─ Failure → Fall back to standard Gemini model
```

## Configuration Steps

### 1. Get Endpoint ID

After Fine-tuned Model is deployed, an Endpoint is created. You need to get the Endpoint ID:

**Method 1: Via Google Cloud Console**
1. Visit [Vertex AI Console](https://console.cloud.google.com/vertex-ai)
2. Go to "Endpoints" page
3. Find the Endpoint corresponding to your Fine-tuned Model
4. Copy the Endpoint ID (format like: `1234567890123456789`)

**Method 2: Using gcloud command**
```bash
gcloud ai endpoints list --region=europe-north1 --format="table(name,displayName)"
```

**Method 3: Using test script**
```bash
cd backend
source venv/bin/activate
export GOOGLE_CLOUD_PROJECT=your-project-id
export VERTEX_AI_LOCATION=europe-north1
python test_finetuned_endpoint.py
```

### 2. Configure Environment Variables

**Local Development** (create `backend/.env` file):
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=europe-north1
RAG_CORPUS_ID=gems-corpus
FINE_TUNED_ENDPOINT_ID=your-endpoint-id  # Replace with actual Endpoint ID
FINE_TUNED_MODEL_ID=your-model-id  # Optional: Direct model ID
USE_FINE_TUNED_MODEL=true  # Set to false to disable Fine-tuned Model
```

**Cloud Run Deployment** (set during deployment):
```bash
gcloud run deploy gems-agent-api \
  --set-env-vars \
    GOOGLE_CLOUD_PROJECT=your-project-id,\
    VERTEX_AI_LOCATION=europe-north1,\
    RAG_CORPUS_ID=gems-corpus,\
    FINE_TUNED_ENDPOINT_ID=your-endpoint-id,\
    FINE_TUNED_MODEL_ID=your-model-id,\
    USE_FINE_TUNED_MODEL=true
```

### 3. Verify Configuration

After starting the service, check logs for the following information:
- `✅ Successfully generated answer using Fine-tuned Model` - Fine-tuned Model is working
- `Fine-tuned Model unavailable or returned empty, falling back to standard Gemini model` - Falling back to standard model

## Environment Variable Reference

| Variable Name | Required | Description | Default |
|---------------|----------|-------------|---------|
| `FINE_TUNED_ENDPOINT_ID` | No | Fine-tuned Model Endpoint ID | Empty string |
| `FINE_TUNED_MODEL_ID` | No | Fine-tuned Model ID (direct model ID) | Empty string |
| `USE_FINE_TUNED_MODEL` | No | Whether to enable Fine-tuned Model | `true` |

## Troubleshooting

### Issue 1: Fine-tuned Model Cannot Be Called

**Symptoms**: Logs show `Fine-tuned Model generation error`

**Possible Causes**:
- Endpoint ID is incorrect
- Endpoint is not deployed or has been deleted
- Insufficient permissions

**Solutions**:
1. Verify Endpoint ID is correct
2. Check Endpoint status: `gcloud ai endpoints describe ENDPOINT_ID --region=europe-north1`
3. Confirm service account has Vertex AI User permissions

### Issue 2: Response Format Incorrect

**Symptoms**: Fine-tuned Model returns a response, but format is incorrect

**Solutions**:
Fine-tuned Model response format may vary by training data. Code automatically tries multiple formats:
- Gemini standard format (`candidates[0].content.parts[0].text`)
- Simple text format (`text` key)
- String format

If still unable to parse, check the actual Endpoint response format and modify the `generate_with_fine_tuned_model()` function.

### Issue 3: Always Falls Back to Standard Model

**Symptoms**: Even with Endpoint ID configured, still uses standard Gemini model

**Checklist**:
- [ ] `FINE_TUNED_ENDPOINT_ID` environment variable is correctly set
- [ ] `USE_FINE_TUNED_MODEL` is `true`
- [ ] Endpoint is in the correct region (`europe-north1`)
- [ ] Check detailed error messages in logs

## Testing

### Test Fine-tuned Model

Use test script:
```bash
cd backend
source venv/bin/activate
python test_finetuned_endpoint.py
```

### Test Full RAG + Fine-tuned Workflow

1. Start service:
```bash
cd backend
source venv/bin/activate
python main.py
```

2. Send test request:
```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Test question"}'
```

3. Check logs to confirm Fine-tuned Model is being used

## Performance Optimization

- Fine-tuned Model usually responds faster than standard model (optimized for specific tasks)
- If Fine-tuned Model response is slow, adjust `max_output_tokens` parameter
- Recommend monitoring Fine-tuned Model call latency and cost in production

## Important Notes

1. **Region Consistency**: Ensure RAG Corpus, Fine-tuned Endpoint, and Vertex AI initialization use the same region
2. **Cost**: Fine-tuned Model call cost may be higher than standard model, monitor usage
3. **Fallback Mechanism**: System automatically falls back to standard model to ensure service availability
4. **Prompt Format**: Fine-tuned Model prompt format is optimized to explicitly instruct model to answer only based on retrieved context

## Changelog

- **2025-12-05**: Initial version, supports Fine-tuned Model integration with RAG
