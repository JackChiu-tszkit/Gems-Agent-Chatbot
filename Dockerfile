# Multi-stage build - Unified deployment of frontend and backend to Cloud Run
# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Copy frontend dependency files
COPY package*.json ./

# Install frontend dependencies
RUN npm ci

# Copy frontend source code
COPY . .

# Build frontend (use environment variables, use defaults if not set)
# When deploying to Cloud Run, frontend will use relative paths to call backend API
ARG VITE_CHAT_API_URL=/chat
ARG VITE_GOOGLE_CLIENT_ID
ENV VITE_CHAT_API_URL=${VITE_CHAT_API_URL}
ENV VITE_GOOGLE_CLIENT_ID=${VITE_GOOGLE_CLIENT_ID}

RUN npm run build

# Stage 2: Python backend + frontend static files
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend dependency files
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend static files from build stage
COPY --from=frontend-builder /app/dist ./dist

# Copy backend code
COPY backend/main.py .

# Expose port (Cloud Run uses PORT environment variable)
EXPOSE 8080

# Run backend (backend serves both API and frontend static files)
CMD ["python", "main.py"]

