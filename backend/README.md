# GEMS Agent API

Backend API service for calling Vertex AI Agent and RAG Engine.

## Architecture Overview

### Local Development vs Cloud Deployment

**Local Development (Testing):**
- Use `.env` file to configure environment variables
- Run `python main.py` or `uvicorn main:app --reload`
- Used for development and testing

**Cloud Deployment (Production):**
- **Cloud Run (Recommended)**: Serverless, auto-scaling
- **VM (Compute Engine)**: Full control, suitable for long-running services
- **Cloud Functions**: Lightweight, suitable for simple scenarios

## Quick Start

### Local Development

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env file and fill in your configuration
```

4. **Run the service**
```bash
python main.py
# or
uvicorn main:app --reload
```

Service runs on `http://localhost:8080`

### Deploy to Cloud Run (Recommended)

#### Method 1: Using gcloud command

```bash
# 1. Build and push image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/gems-agent-api

# 2. Deploy to Cloud Run
gcloud run deploy gems-agent-api \
  --image gcr.io/YOUR_PROJECT_ID/gems-agent-api \
  --region europe-north1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID,VERTEX_AI_LOCATION=europe-north1,RAG_CORPUS_ID=YOUR_RAG_CORPUS_ID
```

#### Method 2: Using Cloud Build

```bash
# Commit code to Git, then trigger Cloud Build
gcloud builds submit --config cloudbuild.yaml
```

#### Method 3: Via Google Cloud Console

1. Open Cloud Run page
2. Click "Create Service"
3. Select "Deploy from source" or "Deploy from container image"
4. Configure environment variables
5. Deploy

### Deploy to VM (Compute Engine)

1. **Create VM instance**
```bash
gcloud compute instances create gems-agent-api-vm \
  --zone=europe-north1-a \
  --machine-type=e2-medium \
  --image-family=cos-stable \
  --image-project=cos-cloud
```

2. **SSH to VM and install Docker**
```bash
gcloud compute ssh gems-agent-api-vm --zone=europe-north1-a
```

3. **Run container on VM**
```bash
# Pull image
docker pull gcr.io/YOUR_PROJECT_ID/gems-agent-api

# Run container
docker run -d \
  -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID \
  -e VERTEX_AI_LOCATION=europe-north1 \
  -e RAG_CORPUS_ID=YOUR_RAG_CORPUS_ID \
  gcr.io/YOUR_PROJECT_ID/gems-agent-api
```

## Environment Variable Configuration

### Required Variables

- `GOOGLE_CLOUD_PROJECT`: Google Cloud Project ID
- `VERTEX_AI_LOCATION`: Vertex AI Region (e.g., europe-north1)
- `RAG_CORPUS_ID`: RAG Corpus ID

### Optional Variables

- `PORT`: Service port (default: 8080)
- `FINE_TUNED_ENDPOINT_ID`: Fine-tuned Model Endpoint ID
- `FINE_TUNED_MODEL_ID`: Fine-tuned Model ID (direct model ID)
- `USE_FINE_TUNED_MODEL`: Whether to use Fine-tuned model (default: true)
- `GEMINI_MODEL`: Gemini model name (default: gemini-2.5-pro)
- `GOOGLE_APPLICATION_CREDENTIALS`: Service account key path (may be needed for local development)

## Authentication Configuration

### Cloud Run / Cloud Functions
- Automatically uses default service account
- Ensure service account has Vertex AI permissions

### VM / Local
- Use service account key JSON file
- Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

## API Endpoints

- `GET /`: Health check
- `GET /health`: Health check
- `POST /chat`: Chat endpoint
  ```json
  {
    "message": "Your question"
  }
  ```
  Returns:
  ```json
  {
    "reply": "AI response"
  }
  ```

## Local Testing

```bash
# Test health check
curl http://localhost:8080/health

# Test chat endpoint
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message"}'
```

## LangChain RAG Integration

The backend supports LangChain RAG Chain integration:

- **Primary**: Uses LangChain RAG Chain with Fine-tuned Model (if available)
- **Fallback**: Falls back to direct RAG API calls if LangChain is unavailable

See `langchain_rag.py` for the LangChain implementation.

## Notes

1. **Security**:
   - Production environment should enable authentication
   - Restrict CORS origins
   - Use HTTPS

2. **Performance**:
   - Cloud Run auto-scales
   - VM requires manual load balancer configuration

3. **Cost**:
   - Cloud Run: Pay per use
   - VM: Pay per running time

## Troubleshooting

### Cannot connect to Vertex AI locally
- Check if `GOOGLE_APPLICATION_CREDENTIALS` is set
- Confirm service account has Vertex AI permissions

### Cloud Run deployment fails
- Check if environment variables are correct
- View Cloud Run logs

### RAG/Agent call fails
- Confirm RAG Corpus ID is correct
- Check if resources are in the specified region
- View Vertex AI logs
