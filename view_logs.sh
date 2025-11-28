#!/bin/bash
# View logs script - display recent errors and important information

echo "📋 GEMS Agent Chatbot - Log Viewer"
echo "=========================================="
echo ""

# Select which log to view
case "${1:-all}" in
    backend|b)
        echo "📝 Backend Log (last 50 lines):"
        echo "---"
        if [ -f "backend.log" ]; then
            tail -50 backend.log
        else
            echo "backend.log file does not exist"
        fi
        ;;
    frontend|f)
        echo "📝 Frontend Log (last 50 lines):"
        echo "---"
        if [ -f "frontend.log" ]; then
            tail -50 frontend.log
        else
            echo "frontend.log file does not exist"
        fi
        ;;
    errors|e)
        echo "❌ Error Logs:"
        echo "---"
        echo "Backend errors:"
        if [ -f "backend.log" ]; then
            grep -i "error\|exception\|failed\|traceback" backend.log | tail -20 || echo "No errors"
        else
            echo "backend.log file does not exist"
        fi
        echo ""
        echo "Frontend errors:"
        if [ -f "frontend.log" ]; then
            grep -i "error\|failed" frontend.log | tail -20 || echo "No errors"
        else
            echo "frontend.log file does not exist"
        fi
        ;;
    all|*)
        echo "📝 Backend Log (last 30 lines):"
        echo "---"
        if [ -f "backend.log" ]; then
            tail -30 backend.log
        else
            echo "backend.log file does not exist"
        fi
        echo ""
        echo "📝 Frontend Log (last 20 lines):"
        echo "---"
        if [ -f "frontend.log" ]; then
            tail -20 frontend.log
        else
            echo "frontend.log file does not exist"
        fi
        ;;
esac

echo ""
echo "💡 Usage:"
echo "   ./view_logs.sh          # View all logs"
echo "   ./view_logs.sh backend  # View backend log only"
echo "   ./view_logs.sh frontend # View frontend log only"
echo "   ./view_logs.sh errors   # View errors only"
