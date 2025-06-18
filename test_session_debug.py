#!/usr/bin/env python3
"""Debug session endpoint"""

import requests
import json

# Simple test without device_info complexity
test_payload = {
    "app_identifier": "nexa-timesheet",
    "user_uuid": "simple-test-user",
    "email": "simple@test.com",
    "name": "Simple Test",
    "app_version": "0.7.2",
    "device_info": {
        "os": "Android"
    }
}

url = "http://localhost:8000/api/v2/session/start"

print("Testing simplified session...")
print(json.dumps(test_payload, indent=2))

try:
    response = requests.post(url, json=test_payload)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code != 200:
        # Try without name to see if that's the issue
        print("\nTrying without name field...")
        del test_payload['name']
        response2 = requests.post(url, json=test_payload)
        print(f"Status: {response2.status_code}")
        print(f"Response: {response2.text}")
        
except Exception as e:
    print(f"Error: {e}")