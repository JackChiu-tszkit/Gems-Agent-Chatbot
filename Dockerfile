# 多阶段构建 - 统一部署前后端到 Cloud Run
# Stage 1: 构建前端
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# 复制前端依赖文件
COPY package*.json ./

# 安装前端依赖
RUN npm ci

# 复制前端源代码
COPY . .

# 构建前端（使用环境变量，如果没有设置则使用默认值）
# 在 Cloud Run 部署时，前端会使用相对路径调用后端 API
ARG VITE_CHAT_API_URL=/chat
ARG VITE_GOOGLE_CLIENT_ID
ENV VITE_CHAT_API_URL=${VITE_CHAT_API_URL}
ENV VITE_GOOGLE_CLIENT_ID=${VITE_GOOGLE_CLIENT_ID}

RUN npm run build

# Stage 2: Python 后端 + 前端静态文件
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖文件
COPY backend/requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 从构建阶段复制前端静态文件
COPY --from=frontend-builder /app/dist ./dist

# 复制后端代码
COPY backend/main.py .

# 暴露端口（Cloud Run 使用 PORT 环境变量）
EXPOSE 8080

# 运行后端（后端会同时服务 API 和前端静态文件）
CMD ["python", "main.py"]

