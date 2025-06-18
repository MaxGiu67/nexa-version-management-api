#!/usr/bin/env python3
"""Test version check endpoint"""

import requests
import json

# Test data
test_payload = {
    "app_identifier": "nexa-timesheet",
    "current_version": "0.7.1",
    "platform": "android",
    "user_uuid": "test-user-123",
    "device_info": {
        "os": "Android",
        "model": "Samsung Galaxy",
        "version": "11"
    }
}

# Make request
url = "http://localhost:8000/api/v2/version/check"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "nexa_internal_app_key_2025"  # Not needed for this endpoint
}

try:
    print(f"Testing {url}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    response = requests.post(url, json=test_payload, headers=headers)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print("\nParsed Response:")
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")