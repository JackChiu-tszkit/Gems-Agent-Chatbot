#!/bin/bash
# Diagnostic script - check running status and errors

echo "🔍 GEMS Agent Chatbot - Running Status Diagnostic"
echo "=========================================="
echo ""

# Check service processes
echo "📊 Service Process Status:"
echo "---"
BACKEND_PID=$(ps aux | grep "python.*main.py" | grep -v grep | awk '{print $2}' | head -1)
FRONTEND_PID=$(ps aux | grep "vite" | grep -v grep | awk '{print $2}' | head -1)

if [ -n "$BACKEND_PID" ]; then
    echo "✅ Backend process running (PID: $BACKEND_PID)"
else
    echo "❌ Backend process not running"
fi

if [ -n "$FRONTEND_PID" ]; then
    echo "✅ Frontend process running (PID: $FRONTEND_PID)"
else
    echo "❌ Frontend process not running"
fi
echo ""

# Check ports
echo "🌐 Port Check:"
echo "---"
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Backend API (8080): Accessible"
    HEALTH=$(curl -s http://localhost:8080/health)
    echo "   Response: $HEALTH"
else
    echo "❌ Backend API (8080): Not accessible"
fi

if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ Frontend UI (5173): Accessible"
else
    echo "❌ Frontend UI (5173): Not accessible"
fi
echo ""

# Check backend log for errors
echo "📝 Backend Log (last 20 lines):"
echo "---"
if [ -f "backend.log" ]; then
    tail -20 backend.log | grep -E "(ERROR|Error|error|Exception|Traceback|Failed)" || echo "   No error messages"
else
    echo "   backend.log file does not exist"
fi
echo ""

# Check frontend log for errors
echo "📝 Frontend Log (last 20 lines):"
echo "---"
if [ -f "frontend.log" ]; then
    tail -20 frontend.log | grep -E "(ERROR|Error|error|Failed)" || echo "   No error messages"
else
    echo "   frontend.log file does not exist"
fi
echo ""

# Check API call
echo "🌐 API Test:"
echo "---"
if curl -s -X POST http://localhost:8080/chat \
    -H "Content-Type: application/json" \
    -d '{"message":"test"}' > /dev/null 2>&1; then
    echo "✅ Chat API endpoint: Responding"
else
    echo "❌ Chat API endpoint: Not responding"
fi
echo ""

# Check environment variables
echo "🔧 Environment Variables:"
echo "---"
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    if grep -q "VITE_GOOGLE_CLIENT_ID" .env; then
        echo "✅ VITE_GOOGLE_CLIENT_ID is set"
    else
        echo "❌ VITE_GOOGLE_CLIENT_ID is not set"
    fi
    if grep -q "VITE_CHAT_API_URL" .env; then
        echo "✅ VITE_CHAT_API_URL is set"
    else
        echo "❌ VITE_CHAT_API_URL is not set"
    fi
else
    echo "❌ .env file does not exist"
fi

if [ -f "backend/.env" ]; then
    echo "✅ backend/.env file exists"
else
    echo "❌ backend/.env file does not exist"
fi
echo ""

# Check Google Cloud authentication
echo "☁️  Google Cloud Authentication:"
echo "---"
if gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | grep -q .; then
    ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -1)
    echo "✅ Authenticated as: $ACCOUNT"
else
    echo "❌ Not authenticated"
    echo "   Run: gcloud auth application-default login"
fi

if gcloud config get-value project 2>/dev/null | grep -q .; then
    PROJECT=$(gcloud config get-value project 2>/dev/null)
    echo "✅ Project: $PROJECT"
else
    echo "❌ No project set"
    echo "   Run: gcloud config set project YOUR_PROJECT_ID"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 Tips:"
echo "   - If services are not running, run: ./start.sh"
echo "   - To view logs: ./view_logs.sh"
echo "   - To watch logs in real-time: ./watch_logs.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
