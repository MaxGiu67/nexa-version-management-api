#!/bin/bash

echo "🚀 Avvio Backend in modalità LOCALE..."
echo "📦 Database: Railway Remote"
echo "🖥️  Backend: http://localhost:8000"
echo ""

# Attiva virtual environment
source venv/bin/activate || source .venv/bin/activate || echo "⚠️  Virtual env non trovato"

# Imposta environment locale
export ENVIRONMENT=local

# Avvia il backend
python multi_app_api.py