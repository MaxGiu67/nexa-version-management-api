#!/bin/bash

# 🚀 Script di avvio completo per il sistema di gestione versioni
# Avvia backend API e frontend React insieme

echo "🗄️ Starting Nexa Timesheet Version Management System"
echo "============================================="

# Controlla se siamo nella directory corretta
if [ ! -f "complete_api_with_blob.py" ]; then
    echo "❌ Error: Run this script from the /api directory"
    exit 1
fi

# Ferma processi esistenti
echo "🔄 Stopping existing processes..."
pkill -f "complete_api_with_blob.py" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true

# Attendi che i processi si fermino
sleep 2

# Avvia backend API
echo "🚀 Starting backend API (localhost:8000)..."
source venv/bin/activate && python complete_api_with_blob.py &
BACKEND_PID=$!

# Attendi che il backend si avvii
echo "⏳ Waiting for backend to start..."
sleep 5

# Controlla se il backend è attivo
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend started successfully"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Avvia frontend React
echo "🚀 Starting frontend React (localhost:3000)..."
cd frontend/version-manager
npm start &
FRONTEND_PID=$!

echo ""
echo "🎉 System started successfully!"
echo "================================"
echo "📱 Frontend: http://localhost:3000"
echo "🗄️  Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "📤 Upload:   http://localhost:8000/api/v1/app-version/upload-form"
echo ""
echo "💡 To stop the system, run: pkill -f 'complete_api_with_blob.py' && pkill -f 'react-scripts start'"
echo ""

# Mantieni lo script attivo
wait