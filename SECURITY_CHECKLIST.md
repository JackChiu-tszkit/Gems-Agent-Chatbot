# Security Checklist - Pre-GitHub Upload Check

## ✅ Completed Cleanup

1. **Environment Variable Files**
   - ✅ `.env` added to `.gitignore`
   - ✅ `backend/.env` added to `.gitignore`
   - ✅ All `.env.*` files ignored

2. **Code Files**
   - ✅ `test-google-signin.html` - Removed hardcoded Client ID
   - ✅ `backend/main.py` - Removed hardcoded RAG_CORPUS_ID
   - ✅ `deploy.sh` - Uses environment variables
   - ✅ `backend/deploy.sh` - Uses environment variables

3. **Documentation Files**
   - ✅ `README.md` - Uses placeholders
   - ✅ `QUICKSTART.md` - Uses placeholders
   - ✅ `LOCAL_SETUP.md` - Uses placeholders
   - ✅ `backend/DEPLOYMENT.md` - Uses placeholders

4. **Debug Documentation (Added to .gitignore)**
   - ⚠️ `DEBUG_OAUTH.md` - Contains sensitive information, ignored
   - ⚠️ `FIX_OAUTH_CONFIG.md` - Contains sensitive information, ignored
   - ⚠️ `GOOGLE_OAUTH_SETUP.md` - Contains sensitive information, ignored
   - ⚠️ `test-google-signin.html` - Contains sensitive information, ignored

## 📋 Pre-Upload Checklist

- [ ] Confirm `.env` file is not in Git
- [ ] Confirm `backend/.env` file is not in Git
- [ ] Confirm all log files (*.log) are not in Git
- [ ] Confirm `node_modules/` is not in Git
- [ ] Confirm `dist/` is not in Git
- [ ] Confirm `venv/` and `backend/venv/` are not in Git
- [ ] Confirm debug documentation is not in Git

## 🔒 Sensitive Information Checklist

The following information should NOT appear in code (should use environment variables):

- ❌ Google OAuth Client ID
- ❌ Google Cloud Project ID
- ❌ RAG Corpus ID
- ❌ API Keys
- ❌ Secrets
- ❌ Passwords
- ❌ Tokens

## 📝 Environment Variable Template

Create `.env.example` file as template (already created):

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

## 🚀 Final Check Before Uploading to GitHub

Run the following commands to check:

```bash
# Check if sensitive files are tracked
git status

# Check if .gitignore is working
git check-ignore .env backend/.env

# Check for hardcoded sensitive information
grep -r "235818822530" . --exclude-dir=node_modules --exclude-dir=dist
grep -r "test-project-306412" . --exclude-dir=node_modules --exclude-dir=dist
grep -r "4611686018427387904" . --exclude-dir=node_modules --exclude-dir=dist
```

If the above commands have no output (except files in .gitignore), cleanup is successful!
