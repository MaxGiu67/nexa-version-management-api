#!/bin/bash

echo "🚀 Avvio Sistema Version Management in LOCALE"
echo "============================================="
echo "📦 Database: Railway Remote"
echo "🔧 Backend: http://localhost:8000"  
echo "💻 Frontend: http://localhost:3000"
echo ""

# Funzione per terminare tutti i processi
cleanup() {
    echo -e "\n🛑 Arresto servizi..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup EXIT INT TERM

# Avvia Backend
echo "▶️  Avvio Backend..."
cd /Users/maxgiu/Git_progetti/nexa-timsheet/version-management/api/
source venv/bin/activate
export ENVIRONMENT=local
python multi_app_api.py &
BACKEND_PID=$!

# Attendi che il backend sia pronto
sleep 3

# Avvia Frontend
echo "▶️  Avvio Frontend..."
cd frontend/version-manager/
npm start &
FRONTEND_PID=$!

echo ""
echo "✅ Sistema avviato!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 API Docs: http://localhost:8000/docs"
echo ""
echo "Premi CTRL+C per fermare tutto"

# Mantieni lo script in esecuzione
wait