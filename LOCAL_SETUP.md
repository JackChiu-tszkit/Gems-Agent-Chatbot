# 本地开发设置指南

## 问题诊断

如果看到错误 "Kunne ikke hente svar fra GEMS Agent"，可能的原因：

### 1. 前端配置问题 ✅ 已修复

`.env` 文件已更新为使用本地后端：
```
VITE_CHAT_API_URL=http://localhost:8080/chat
```

### 2. Google Cloud 认证问题 ⚠️ 需要配置

本地测试需要配置 Google Cloud 认证才能调用 Vertex AI RAG Engine。

## 解决方案

### 方法 1：配置 Application Default Credentials（推荐）

```bash
# 安装 gcloud（如果还没安装）
brew install --cask google-cloud-sdk

# 配置认证
gcloud auth application-default login

# 设置项目
gcloud config set project your-project-id
```

### 方法 2：使用服务账号密钥

1. 在 Google Cloud Console 创建服务账号
2. 下载 JSON 密钥文件
3. 设置环境变量：
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### 方法 3：直接部署到 Cloud Run 测试

如果不想配置本地认证，可以直接部署到 Cloud Run：

```bash
./deploy.sh
```

Cloud Run 会自动使用服务账号的凭据，不需要本地配置。

## 验证

配置认证后，重启服务：

```bash
# 停止当前服务（Ctrl+C）
# 然后重新启动
./start.sh
```

测试 API：
```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "测试"}'
```

如果返回 RAG 结果而不是认证错误，说明配置成功！

