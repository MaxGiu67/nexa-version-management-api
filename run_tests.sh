#!/bin/bash

echo "🧪 Running API Tests"
echo "==================="

# Attiva ambiente virtuale
source venv/bin/activate

echo "1. Testing database connection..."
python simple_test.py

echo -e "\n2. Starting API server in background..."
python simple_api.py &
API_PID=$!

# Aspetta che il server si avvii
sleep 3

echo -e "\n3. Testing API endpoints..."

echo "📍 Health check:"
curl -s http://localhost:8000/health | python -m json.tool

echo -e "\n📍 Check updates (1.0.0 -> latest):"
curl -s "http://localhost:8000/api/v1/app-version/check?current_version=1.0.0&platform=android" | python -m json.tool

echo -e "\n📍 Latest version:"
curl -s "http://localhost:8000/api/v1/app-version/latest?platform=android" | python -m json.tool

echo -e "\n📍 Current version (no update):"
curl -s "http://localhost:8000/api/v1/app-version/check?current_version=1.2.0&platform=android" | python -m json.tool

# Ferma il server
echo -e "\n🛑 Stopping server..."
kill $API_PID 2>/dev/null

echo -e "\n✅ Tests completed!"
echo "📌 If all worked, the API is ready for Railway deployment!"