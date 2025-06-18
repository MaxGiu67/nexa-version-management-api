#!/bin/bash

echo "🚀 Deploy Backend e Frontend su Railway"
echo "======================================="

# Deploy Backend
echo "📦 Deploy Backend..."
cd /Users/maxgiu/Git_progetti/nexa-timsheet/version-management/api/
git add .
git commit -m "Backend update"
railway up

# Deploy Frontend
echo "💻 Deploy Frontend..."
cd frontend/version-manager/
REACT_APP_API_URL=https://nexa-version-management-be.up.railway.app npm run build
git add .
git commit -m "Frontend update"
railway up --service frontend

echo "✅ Deploy completato!"
echo "Backend: https://nexa-version-management-be.up.railway.app"
echo "Frontend: https://nexa-frontend.up.railway.app"