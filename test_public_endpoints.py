#!/usr/bin/env python3
"""Test all public endpoints"""

import requests
import json

base_url = "http://localhost:8000"

# Test endpoints
tests = [
    {
        "name": "Version Check (GET)",
        "method": "GET",
        "url": f"{base_url}/api/v2/app-version/check",
        "params": {
            "current_version": "0.7.1",
            "platform": "android",
            "app_identifier": "nexa-timesheet"
        },
        "data": None
    },
    {
        "name": "Version Check (POST)",
        "method": "POST",
        "url": f"{base_url}/api/v2/version/check",
        "params": None,
        "data": {
            "app_identifier": "nexa-timesheet",
            "current_version": "0.7.1",
            "platform": "android"
        }
    },
    {
        "name": "Session Start",
        "method": "POST",
        "url": f"{base_url}/api/v2/session/start",
        "params": None,
        "data": {
            "app_identifier": "nexa-timesheet",
            "user_uuid": "test-user-123",
            "email": "test@example.com",
            "device_info": {
                "os": "Android",
                "model": "Test Device"
            },
            "app_version": "0.7.2"
        }
    },
    {
        "name": "Error Report",
        "method": "POST",
        "url": f"{base_url}/api/v2/errors/report",
        "params": None,
        "data": {
            "app_identifier": "nexa-timesheet",
            "user_uuid": "test-user-123",
            "error_type": "TestError",
            "error_message": "This is a test error",
            "app_version": "0.7.2",
            "platform": "android"
        }
    }
]

print("Testing Public Endpoints")
print("=" * 50)

for test in tests:
    print(f"\n{test['name']}:")
    print(f"URL: {test['url']}")
    
    try:
        if test['method'] == 'GET':
            response = requests.get(test['url'], params=test['params'])
        else:
            response = requests.post(test['url'], json=test['data'])
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success")
            if len(response.text) < 200:
                print(f"Response: {response.text}")
        else:
            print("❌ Failed")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("Note: If you see 401 errors, restart the backend to apply the public endpoint changes.")