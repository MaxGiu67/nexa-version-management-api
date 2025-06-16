#!/bin/bash

echo "🚀 Setup Local Test Environment"
echo "=============================="

# Colori
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Controlla Python
echo -e "\n${YELLOW}1. Checking Python...${NC}"

# Cerca una versione di Python compatibile
PYTHON_CMD=""
for cmd in python3.11 python3.10 python3.9 python3.8 python3; do
    if command -v $cmd &> /dev/null; then
        VERSION=$($cmd --version 2>&1 | awk '{print $2}')
        MAJOR=$(echo $VERSION | cut -d. -f1)
        MINOR=$(echo $VERSION | cut -d. -f2)
        
        # Usa Python 3.8-3.11 (3.12+ hanno problemi con pydantic)
        if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 8 ] && [ "$MINOR" -le 11 ]; then
            PYTHON_CMD=$cmd
            echo -e "${GREEN}✓ Found compatible Python: $cmd ($VERSION)${NC}"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}✗ No compatible Python found!${NC}"
    echo -e "${YELLOW}Please install Python 3.8, 3.9, 3.10, or 3.11${NC}"
    echo -e "${YELLOW}Python 3.13 is too new for some dependencies${NC}"
    echo -e "\n${YELLOW}Install with Homebrew:${NC}"
    echo -e "  brew install python@3.11"
    exit 1
fi

# 2. Crea virtual environment
echo -e "\n${YELLOW}2. Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    # Rimuovi e ricrea se esiste (per usare la versione Python corretta)
    echo -e "${YELLOW}Removing old virtual environment...${NC}"
    rm -rf venv
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✓ Virtual environment recreated with $PYTHON_CMD${NC}"
fi

# 3. Attiva virtual environment
echo -e "\n${YELLOW}3. Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# 4. Installa dipendenze
echo -e "\n${YELLOW}4. Installing dependencies...${NC}"
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi

# 5. Installa requests per i test
echo -e "\n${YELLOW}5. Installing test dependencies...${NC}"
pip install requests > /dev/null 2>&1
echo -e "${GREEN}✓ Test dependencies installed${NC}"

# 6. Info database
echo -e "\n${YELLOW}6. Database configuration${NC}"
echo -e "${GREEN}✓ Database credentials are embedded in main.py${NC}"
echo -e "   Host: tramway.proxy.rlwy.net"
echo -e "   Port: 20671"
echo -e "   Database: railway"

# 7. Istruzioni finali
echo -e "\n${YELLOW}=============================="
echo -e "✅ Setup Complete!${NC}"
echo -e "${YELLOW}==============================${NC}"

echo -e "\n${GREEN}Next steps:${NC}"
echo -e "1. In this terminal, run the API server:"
echo -e "   ${YELLOW}python main.py${NC}"
echo -e ""
echo -e "2. In a new terminal, run the tests:"
echo -e "   ${YELLOW}python test_local_api.py${NC}"
echo -e ""
echo -e "The API will be available at:"
echo -e "   - API: ${GREEN}http://localhost:8000${NC}"
echo -e "   - Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo -e ""
echo -e "${YELLOW}Note: The server will connect to your Railway MySQL database${NC}"

# Mantieni l'ambiente attivo
echo -e "\n${GREEN}Virtual environment is active. Start the server with: python main.py${NC}"