# 安全清单 - GitHub 上传前检查

## ✅ 已完成的清理

1. **环境变量文件**
   - ✅ `.env` 已添加到 `.gitignore`
   - ✅ `backend/.env` 已添加到 `.gitignore`
   - ✅ 所有 `.env.*` 文件已忽略

2. **代码文件**
   - ✅ `test-google-signin.html` - 移除硬编码 Client ID
   - ✅ `backend/main.py` - 移除硬编码的 RAG_CORPUS_ID
   - ✅ `deploy.sh` - 使用环境变量
   - ✅ `backend/deploy.sh` - 使用环境变量

3. **文档文件**
   - ✅ `README.md` - 使用占位符
   - ✅ `QUICKSTART.md` - 使用占位符
   - ✅ `LOCAL_SETUP.md` - 使用占位符
   - ✅ `backend/DEPLOYMENT.md` - 使用占位符

4. **调试文档（已添加到 .gitignore）**
   - ⚠️ `DEBUG_OAUTH.md` - 包含敏感信息，已忽略
   - ⚠️ `FIX_OAUTH_CONFIG.md` - 包含敏感信息，已忽略
   - ⚠️ `GOOGLE_OAUTH_SETUP.md` - 包含敏感信息，已忽略
   - ⚠️ `test-google-signin.html` - 包含敏感信息，已忽略

## 📋 上传前检查清单

- [ ] 确认 `.env` 文件不在 Git 中
- [ ] 确认 `backend/.env` 文件不在 Git 中
- [ ] 确认所有日志文件（*.log）不在 Git 中
- [ ] 确认 `node_modules/` 不在 Git 中
- [ ] 确认 `dist/` 不在 Git 中
- [ ] 确认 `venv/` 和 `backend/venv/` 不在 Git 中
- [ ] 确认调试文档不在 Git 中

## 🔒 敏感信息清单

以下信息不应出现在代码中（应使用环境变量）：

- ❌ Google OAuth Client ID
- ❌ Google Cloud Project ID
- ❌ RAG Corpus ID
- ❌ API Keys
- ❌ Secrets
- ❌ Passwords
- ❌ Tokens

## 📝 环境变量模板

创建 `.env.example` 文件作为模板（已创建）：

```bash
# Frontend
VITE_GOOGLE_CLIENT_ID=your-google-oauth-client-id
VITE_CHAT_API_URL=http://localhost:8080/chat

# Backend
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=europe-west1
RAG_CORPUS_ID=your-rag-corpus-id
GEMINI_MODEL=gemini-2.5-pro
SYSTEM_INSTRUCTION=your-system-instruction
```

## 🚀 上传到 GitHub 前的最后检查

运行以下命令检查：

```bash
# 检查是否有敏感文件被跟踪
git status

# 检查 .gitignore 是否生效
git check-ignore .env backend/.env

# 检查是否有硬编码的敏感信息
grep -r "235818822530" . --exclude-dir=node_modules --exclude-dir=dist
grep -r "test-project-306412" . --exclude-dir=node_modules --exclude-dir=dist
grep -r "4611686018427387904" . --exclude-dir=node_modules --exclude-dir=dist
```

如果以上命令没有输出（除了 .gitignore 中的文件），说明清理成功！
