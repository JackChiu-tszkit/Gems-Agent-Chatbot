#!/bin/bash
# Real-time log monitoring script

echo "📺 Real-time Monitoring GEMS Agent Chatbot Logs"
echo "Press Ctrl+C to stop"
echo ""

# Use tail -f to monitor both log files simultaneously
tail -f backend.log frontend.log 2>/dev/null || {
    echo "⚠️  Log files do not exist, creating..."
    touch backend.log frontend.log
    echo "Waiting for log output..."
    tail -f backend.log frontend.log
}
