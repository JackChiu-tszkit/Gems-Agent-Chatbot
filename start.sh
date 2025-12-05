#!/bin/bash
# Local testing - start both frontend and backend

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🚀 Starting GEMS Agent Chatbot (local testing)..."
echo ""

# Check backend environment variables
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env file does not exist"
    echo "   Please create backend/.env file and fill in configuration"
    exit 1
fi

# Start backend
echo "📡 Starting backend API (port 8080)..."
cd backend

# Check and activate virtual environment
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies (if needed)
if ! python -c "import fastapi" 2>/dev/null; then
    echo "   Installing Python dependencies..."
    pip install -q -r requirements.txt
fi

# Load environment variables
export $(cat .env 2>/dev/null | grep -v '^#' | xargs)

# Start backend (run in background)
python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "   Waiting for backend to start..."
sleep 3

# Check if backend started successfully
if ! curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "❌ Backend failed to start, please check backend.log"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "   ✅ Backend started: http://localhost:8080"
echo ""

# Start frontend
echo "🎨 Starting frontend UI (port 3000)..."
echo "   Using local backend API: http://localhost:8080/chat"

# Set frontend environment variables (use local backend)
export VITE_CHAT_API_URL=http://localhost:8080/chat

npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 3

echo "   ✅ Frontend started: http://localhost:3000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Services started!"
echo ""
echo "   📡 Backend API:  http://localhost:8080"
echo "   🎨 Frontend UI:   http://localhost:3000"
echo ""
echo "   Open in browser: http://localhost:3000"
echo ""
echo "   Press Ctrl+C to stop all services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

trap cleanup INT TERM
wait

