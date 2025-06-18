#!/usr/bin/env python3
"""Test version check without user tracking"""

import requests
import json

# Test without user_uuid
test_cases = [
    {
        "name": "Android Version Check (No User)",
        "payload": {
            "app_identifier": "nexa-timesheet",
            "current_version": "0.7.1",
            "platform": "android"
            # No user_uuid, so no user tracking
        }
    },
    {
        "name": "iOS Version Check (No User)",
        "payload": {
            "app_identifier": "nexa-timesheet",
            "current_version": "0.7.1",
            "platform": "ios"
        }
    }
]

url = "http://localhost:8000/api/v2/version/check"

print("Testing Version Check Without User Tracking")
print("=" * 60)

for test in test_cases:
    print(f"\n{test['name']}:")
    
    try:
        response = requests.post(url, json=test['payload'])
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success")
            print(f"  Current: {data.get('current_version')}")
            print(f"  Latest: {data.get('latest_version')}")
            print(f"  Platform: {data.get('platform')}")
            print(f"  Update available: {data.get('is_update_available')}")
            if data.get('is_update_available'):
                print(f"  Download URL: {data.get('download_url')}")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")