#!/usr/bin/env python3
"""Test session start endpoint"""

import requests
import json

# Test data for session
test_payload = {
    "app_identifier": "nexa-timesheet",
    "user_uuid": "test-user-123",
    "email": "test@example.com",
    "device_info": {
        "os": "Android",
        "model": "Samsung Galaxy S21",
        "version": "11",
        "manufacturer": "Samsung"
    },
    "app_version": "0.7.2"
}

# Make request
url = "http://localhost:8000/api/v2/session/start"
headers = {
    "Content-Type": "application/json"
}

try:
    print(f"Testing {url}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    response = requests.post(url, json=test_payload, headers=headers)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print("\nSession created:")
        print(f"Session ID: {data.get('session_id')}")
        print(f"User ID: {data.get('user_id')}")
except Exception as e:
    print(f"Error: {e}")