#!/bin/bash

# Script per creare l'app tramite API
curl -X POST "http://192.168.128.133:8000/api/v2/apps" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: nexa_internal_app_key_2025" \
  -d '{
    "app_identifier": "com.nexa.timesheet",
    "app_name": "Nexa Timesheet",
    "description": "Mobile app per la gestione dei timesheet NEXA DATA"
  }'

echo ""
echo "App creata. Verifica:"

# Verifica che l'app sia stata creata
curl -X GET "http://192.168.128.133:8000/api/v2/apps" \
  -H "X-API-Key: nexa_internal_app_key_2025" | python -m json.tool