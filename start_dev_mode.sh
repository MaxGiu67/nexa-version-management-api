#!/bin/bash

echo "🚀 Starting Development Mode (with Mock API)"
echo "=========================================="
echo ""
echo "This will start:"
echo "- Mock API (no database required) on port 8000"
echo "- Frontend on port 3000"
echo ""

# Start mock API in background
echo "Starting Mock API..."
python mock_api.py &
MOCK_PID=$!

# Wait for API to start
sleep 2

# Start frontend
echo "Starting Frontend..."
cd frontend/version-manager
npm start &
FRONTEND_PID=$!

echo ""
echo "✅ Development environment started!"
echo ""
echo "📌 Access points:"
echo "- API: http://localhost:8000/docs"
echo "- Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait and cleanup on exit
trap "kill $MOCK_PID $FRONTEND_PID 2>/dev/null" EXIT
wait