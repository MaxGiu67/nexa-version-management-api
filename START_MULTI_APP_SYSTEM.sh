#!/bin/bash

# Script per avviare il sistema Multi-App Version Management v2.0
# Questo script avvia sia il backend che il frontend del nuovo sistema

echo "🚀 Starting Multi-App Version Management System v2.0..."
echo "=================================================="

# Colori per output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funzione per verificare se un processo è in esecuzione
check_process() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# 1. Verifica ambiente Python
echo -e "${BLUE}1. Checking Python environment...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# 2. Attiva ambiente virtuale
echo -e "${BLUE}2. Activating virtual environment...${NC}"
source venv/bin/activate

# 3. Installa/aggiorna dipendenze
echo -e "${BLUE}3. Installing/updating dependencies...${NC}"
pip install -r requirements.txt 2>/dev/null || pip install fastapi uvicorn pymysql python-multipart

# 4. Verifica database
echo -e "${BLUE}4. Checking database configuration...${NC}"
echo -e "${YELLOW}Make sure to run migrate_to_multi_app.sql if upgrading from v1!${NC}"

# 5. Kill processi esistenti se necessario
if check_process 8000; then
    echo -e "${YELLOW}Port 8000 is in use. Killing existing process...${NC}"
    kill $(lsof -ti:8000) 2>/dev/null
    sleep 2
fi

if check_process 3000; then
    echo -e "${YELLOW}Port 3000 is in use. Killing existing process...${NC}"
    kill $(lsof -ti:3000) 2>/dev/null
    sleep 2
fi

# 6. Avvia backend API v2
echo -e "${BLUE}5. Starting Multi-App API Backend (Port 8000)...${NC}"
python multi_app_api.py &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started with PID: $BACKEND_PID${NC}"

# Attendi che il backend sia pronto
sleep 3

# 7. Verifica che il backend sia attivo
if check_process 8000; then
    echo -e "${GREEN}✓ Backend is running on http://localhost:8000${NC}"
    echo -e "${GREEN}✓ API Docs available at http://localhost:8000/docs${NC}"
else
    echo -e "${RED}✗ Failed to start backend${NC}"
    exit 1
fi

# 8. Avvia frontend
echo -e "${BLUE}6. Starting Frontend Dashboard (Port 3000)...${NC}"
cd frontend/version-manager
npm install --silent 2>/dev/null
npm start &
FRONTEND_PID=$!
cd ../..

# 9. Salva i PID per lo shutdown
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# 10. Mostra informazioni sistema
echo -e "\n${GREEN}=================================================="
echo -e "🎉 Multi-App Version Management System v2.0 Started!"
echo -e "=================================================="
echo -e "${NC}"
echo -e "${BLUE}System URLs:${NC}"
echo -e "• Frontend Dashboard: ${GREEN}http://localhost:3000${NC}"
echo -e "• API Documentation: ${GREEN}http://localhost:8000/docs${NC}"
echo -e "• Health Check: ${GREEN}http://localhost:8000/health${NC}"
echo -e ""
echo -e "${BLUE}New Features:${NC}"
echo -e "• Multi-app support"
echo -e "• User tracking & analytics"
echo -e "• Error reporting system"
echo -e "• Advanced analytics dashboard"
echo -e ""
echo -e "${YELLOW}First Time Setup:${NC}"
echo -e "1. Run the migration script: mysql < migrate_to_multi_app.sql"
echo -e "2. Register your first app via API or dashboard"
echo -e "3. Update mobile apps with new tracking hooks"
echo -e ""
echo -e "${BLUE}API Examples:${NC}"
echo -e "• Register app: POST /api/v2/apps"
echo -e "• Check version: POST /api/v2/version/check"
echo -e "• Report error: POST /api/v2/errors/report"
echo -e "• View analytics: GET /api/v2/analytics/{app}/overview"
echo -e ""
echo -e "${RED}To stop the system:${NC} Press Ctrl+C or run ./stop_system.sh"
echo -e ""

# Funzione per gestire lo shutdown
cleanup() {
    echo -e "\n${YELLOW}Shutting down system...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    rm -f .backend.pid .frontend.pid
    echo -e "${GREEN}System stopped.${NC}"
    exit 0
}

# Registra handler per shutdown pulito
trap cleanup INT TERM

# Mantieni lo script in esecuzione
echo -e "${GREEN}System is running. Press Ctrl+C to stop.${NC}"
wait