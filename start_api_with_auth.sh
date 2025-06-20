#!/bin/bash

# Script per avviare l'API con autenticazione
# Garantisce che tutto sia configurato correttamente

echo "🚀 Avvio Version Management API con Autenticazione..."

# Vai alla directory corretta
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Directory: $(pwd)"

# Attiva virtual environment se esiste
if [ -d "venv" ]; then
    echo "🐍 Attivazione virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "🐍 Attivazione .venv..."
    source .venv/bin/activate
fi

# Verifica che i moduli esistano
echo "🔍 Verifica moduli..."
if [ ! -f "multi_app_api.py" ]; then
    echo "❌ Errore: multi_app_api.py non trovato!"
    exit 1
fi

if [ ! -f "auth_module.py" ]; then
    echo "❌ Errore: auth_module.py non trovato!"
    exit 1
fi

if [ ! -f "auth_endpoints.py" ]; then
    echo "❌ Errore: auth_endpoints.py non trovato!"
    exit 1
fi

# Verifica dipendenze
echo "📦 Verifica dipendenze..."
python -c "import bcrypt, pyotp, qrcode" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installazione dipendenze mancanti..."
    pip install bcrypt pyotp qrcode pillow email-validator
fi

# Kill processi esistenti
echo "🔄 Chiusura processi esistenti..."
pkill -f "python.*multi_app_api" || true
sleep 2

# Avvia l'API
echo "🚀 Avvio API..."
echo "============================================================"
python multi_app_api.py