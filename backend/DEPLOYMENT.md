# 部署指南

## 方法 1：使用 gcloud 命令行（推荐）

### 步骤 1：安装 Google Cloud SDK

**macOS:**
```bash
brew install --cask google-cloud-sdk
```

**或手动安装:**
访问 https://cloud.google.com/sdk/docs/install 下载并安装

### 步骤 2：登录和配置

```bash
# 登录
gcloud auth login

# 设置项目
gcloud config set project your-project-id
```

### 步骤 3：部署

**使用部署脚本（最简单）:**
```bash
cd "Gems Agent Chatbot UI/backend"
./deploy.sh
```

**或手动执行:**
```bash
# 1. 构建并推送镜像
gcloud builds submit --tag gcr.io/your-project-id/gems-agent-api

# 2. 部署到 Cloud Run
gcloud run deploy gems-agent-api \
  --image gcr.io/your-project-id/gems-agent-api \
  --region europe-north1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=your-project-id,VERTEX_AI_LOCATION=europe-north1,RAG_CORPUS_ID=your-rag-corpus-id \
  --port 8080
```

## 方法 2：使用 Google Cloud Console（图形界面）

### 步骤 1：打开 Cloud Run

访问：https://console.cloud.google.com/run?project=your-project-id

### 步骤 2：创建服务

1. 点击 **"创建服务"**
2. 选择 **"从源代码部署"** 或 **"从容器镜像部署"**

### 步骤 3：配置服务

**如果选择"从源代码部署":**
- 选择源代码位置（GitHub、Cloud Source Repositories 等）
- 或上传代码 ZIP 文件

**如果选择"从容器镜像部署":**
- 需要先构建镜像（使用方法 1 的步骤 1）

**服务配置:**
- **服务名称**: `gems-agent-api`
- **区域**: `europe-north1`
- **平台**: Cloud Run (fully managed)
- **身份验证**: 允许未经验证的调用

**环境变量:**
- `GOOGLE_CLOUD_PROJECT` = `your-project-id`
- `VERTEX_AI_LOCATION` = `europe-north1`
- `RAG_CORPUS_ID` = `your-rag-corpus-id`

### 步骤 4：部署

点击 **"创建"** 按钮，等待部署完成。

## 部署后

部署成功后，你会看到服务 URL，例如：
```
https://gems-agent-api-xxxxx-nw.a.run.app
```

### 更新前端配置

将服务 URL 填入前端 `.env` 文件：

```bash
VITE_CHAT_API_URL=https://gems-agent-api-xxxxx-nw.a.run.app/chat
```

### 测试 API

```bash
# 测试健康检查
curl https://your-service-url.run.app/health

# 测试聊天端点
curl -X POST https://your-service-url.run.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "测试消息"}'
```

## 故障排除

### 问题 1：权限不足

确保你的账号有以下权限：
- Cloud Run Admin
- Service Account User
- Cloud Build Editor

### 问题 2：构建失败

检查：
- Dockerfile 是否正确
- requirements.txt 中的依赖是否可用
- 查看构建日志：`gcloud builds list`

### 问题 3：部署后无法访问

检查：
- 环境变量是否正确设置
- 查看服务日志：`gcloud run services logs read gems-agent-api --region europe-north1`

