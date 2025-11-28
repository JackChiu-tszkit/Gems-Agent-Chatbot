# GEMS Agent API

后端 API 服务，用于调用 Vertex AI Agent 和 RAG Engine。

## 架构说明

### 本地开发 vs 云部署

**本地开发（测试）：**
- 使用 `.env` 文件配置环境变量
- 运行 `python main.py` 或 `uvicorn main:app --reload`
- 用于开发和测试

**云部署（生产）：**
- **Cloud Run（推荐）**：无服务器，自动扩缩容
- **VM（Compute Engine）**：完全控制，适合长期运行
- **Cloud Functions**：轻量级，适合简单场景

## 快速开始

### 本地开发

1. **进入后端目录**
```bash
cd backend
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

3. **运行服务**
```bash
python main.py
# 或
uvicorn main:app --reload
```

服务运行在 `http://localhost:8080`

### 部署到 Cloud Run（推荐）

#### 方法 1：使用 gcloud 命令

```bash
# 1. 构建并推送镜像
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/gems-agent-api

# 2. 部署到 Cloud Run
gcloud run deploy gems-agent-api \
  --image gcr.io/YOUR_PROJECT_ID/gems-agent-api \
  --region europe-north1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID,VERTEX_AI_LOCATION=europe-north1,VERTEX_AGENT_ID=YOUR_AGENT_ID
```

#### 方法 2：使用 Cloud Build

```bash
# 提交代码到 Git，然后触发 Cloud Build
gcloud builds submit --config cloudbuild.yaml
```

#### 方法 3：通过 Google Cloud Console

1. 打开 Cloud Run 页面
2. 点击 "创建服务"
3. 选择 "从源代码部署" 或 "从容器镜像部署"
4. 配置环境变量
5. 部署

### 部署到 VM（Compute Engine）

1. **创建 VM 实例**
```bash
gcloud compute instances create gems-agent-api-vm \
  --zone=europe-north1-a \
  --machine-type=e2-medium \
  --image-family=cos-stable \
  --image-project=cos-cloud
```

2. **SSH 到 VM 并安装 Docker**
```bash
gcloud compute ssh gems-agent-api-vm --zone=europe-north1-a
```

3. **在 VM 上运行容器**
```bash
# 拉取镜像
docker pull gcr.io/YOUR_PROJECT_ID/gems-agent-api

# 运行容器
docker run -d \
  -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID \
  -e VERTEX_AI_LOCATION=europe-north1 \
  -e VERTEX_AGENT_ID=YOUR_AGENT_ID \
  gcr.io/YOUR_PROJECT_ID/gems-agent-api
```

## 环境变量配置

### 必需变量

- `GOOGLE_CLOUD_PROJECT`: Google Cloud 项目 ID
- `VERTEX_AI_LOCATION`: Vertex AI 区域（例如：europe-north1）
- `VERTEX_AGENT_ID`: Vertex AI Agent ID

### 可选变量

- `PORT`: 服务端口（默认：8080）
- `GOOGLE_APPLICATION_CREDENTIALS`: 服务账号密钥路径（本地开发时可能需要）

## 认证配置

### Cloud Run / Cloud Functions
- 自动使用默认服务账号
- 确保服务账号有 Vertex AI 权限

### VM / 本地
- 使用服务账号密钥 JSON 文件
- 设置 `GOOGLE_APPLICATION_CREDENTIALS` 环境变量

## API 端点

- `GET /`: 健康检查
- `GET /health`: 健康检查
- `POST /chat`: 聊天端点
  ```json
  {
    "message": "你的问题"
  }
  ```
  返回：
  ```json
  {
    "reply": "AI 回答"
  }
  ```

## 本地测试

```bash
# 测试健康检查
curl http://localhost:8080/health

# 测试聊天端点
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "测试消息"}'
```

## 注意事项

1. **安全性**：
   - 生产环境应该启用身份验证
   - 限制 CORS 来源
   - 使用 HTTPS

2. **性能**：
   - Cloud Run 自动扩缩容
   - VM 需要手动配置负载均衡

3. **成本**：
   - Cloud Run：按使用量付费
   - VM：按运行时间付费

## 故障排除

### 本地无法连接 Vertex AI
- 检查 `GOOGLE_APPLICATION_CREDENTIALS` 是否设置
- 确认服务账号有 Vertex AI 权限

### Cloud Run 部署失败
- 检查环境变量是否正确
- 查看 Cloud Run 日志

### Agent 调用失败
- 确认 Agent ID 正确
- 检查 Agent 是否在指定区域
- 查看 Vertex AI 日志

