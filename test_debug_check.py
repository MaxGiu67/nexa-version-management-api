#!/usr/bin/env python3
"""Debug version check endpoint"""

import requests
import json

# Test the POST endpoint with detailed error capture
url = "http://localhost:8000/api/v2/version/check"
payload = {
    "app_identifier": "nexa-timesheet",
    "current_version": "0.7.1",
    "platform": "android",
    "user_uuid": "android-test-user"
}

try:
    print(f"Testing {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, json=payload)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")