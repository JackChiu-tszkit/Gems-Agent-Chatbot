# GEMS Agent Chatbot - 快速开始指南

## 📋 概述

这个项目包含：
- **前端**：React + TypeScript + Vite 聊天界面
- **后端**：Python + FastAPI，调用 Vertex AI RAG Engine
- **统一部署**：前后端可以一起部署到 Cloud Run

## 🚀 本地测试

### 方法 1：使用启动脚本（推荐）

```bash
# 在项目根目录运行
./start.sh
```

这将自动：
1. 启动后端 API (端口 8080)
2. 启动前端 UI (端口 5173)
3. 在浏览器中打开 http://localhost:5173

### 方法 2：手动启动

**终端 1 - 后端：**
```bash
cd backend
source venv/bin/activate  # 或: python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export $(cat .env | xargs)
python main.py
```

**终端 2 - 前端：**
```bash
npm install
npm run dev
```

然后在浏览器打开：http://localhost:5173

## ☁️ 部署到 Cloud Run

### 一键部署

```bash
# 在项目根目录运行
./deploy.sh
```

这将：
1. 构建前端静态文件
2. 创建包含前后端的 Docker 镜像
3. 部署到 Cloud Run
4. 提供一个公共 URL，所有人都可以访问

### 部署后

部署完成后，你会得到一个 URL，例如：
```
https://gems-agent-chatbot-xxxxx.run.app
```

**所有人可以通过这个链接：**
1. 打开链接
2. 使用 @randstad.no 邮箱登录
3. 开始使用 GEMS Agent

## 📁 项目结构

```
Gems Agent Chatbot UI/
├── start.sh              # 本地启动脚本
├── deploy.sh              # Cloud Run 部署脚本
├── Dockerfile             # 统一部署的 Dockerfile
├── src/                   # 前端源代码
├── backend/               # 后端源代码
│   ├── main.py           # FastAPI 应用（同时服务静态文件）
│   ├── requirements.txt   # Python 依赖
│   └── .env              # 后端环境变量
└── dist/                  # 前端构建输出（部署时使用）
```

## ⚙️ 配置

### 前端配置

`.env` 文件（可选，用于本地开发）：
```
VITE_CHAT_API_URL=http://localhost:8080/chat
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

### 后端配置

`backend/.env` 文件：
```
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=europe-north1
RAG_CORPUS_ID=your-rag-corpus-id
PORT=8080
```

## 🔧 故障排除

### 本地启动失败

1. **后端启动失败**：
   - 检查 `backend/.env` 文件是否存在
   - 检查虚拟环境是否激活
   - 查看 `backend.log` 文件

2. **前端启动失败**：
   - 运行 `npm install` 安装依赖
   - 查看 `frontend.log` 文件

### 部署失败

1. **构建失败**：
   - 检查 `gcloud` 是否已登录
   - 检查项目 ID 是否正确
   - 查看 Cloud Build 日志

2. **部署后无法访问**：
   - 检查服务是否允许未认证访问
   - 查看 Cloud Run 日志

## 📝 注意事项

1. **本地开发**：前端和后端分开运行，前端使用 `http://localhost:8080/chat`
2. **Cloud Run 部署**：前后端统一部署，前端使用相对路径 `/chat`
3. **Google OAuth**：确保 Client ID 配置正确
4. **权限**：确保 Cloud Run 服务账号有 Vertex AI 访问权限

