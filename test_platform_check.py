#!/usr/bin/env python3
"""Test version check with platform filtering"""

import requests
import json

# Test cases for different platforms
test_cases = [
    {
        "name": "Android Version Check",
        "payload": {
            "app_identifier": "nexa-timesheet",
            "current_version": "0.7.1",
            "platform": "android",
            "user_uuid": "android-test-user"
        }
    },
    {
        "name": "iOS Version Check",
        "payload": {
            "app_identifier": "nexa-timesheet",
            "current_version": "0.7.1",
            "platform": "ios",
            "user_uuid": "ios-test-user"
        }
    },
    {
        "name": "Invalid Platform Check",
        "payload": {
            "app_identifier": "nexa-timesheet",
            "current_version": "0.7.1",
            "platform": "windows",  # Invalid platform
            "user_uuid": "windows-test-user"
        }
    }
]

url = "http://localhost:8000/api/v2/version/check"
headers = {"Content-Type": "application/json"}

print("Testing Platform-Specific Version Checks")
print("=" * 60)

for test in test_cases:
    print(f"\n{test['name']}:")
    print(f"Platform: {test['payload']['platform']}")
    
    try:
        response = requests.post(url, json=test['payload'], headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success")
            print(f"  Latest version: {data.get('latest_version')}")
            print(f"  Platform: {data.get('platform')}")
            print(f"  Update available: {data.get('is_update_available')}")
            print(f"  Download URL: {data.get('download_url')}")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

# Also test the compatibility endpoint
print("\n" + "=" * 60)
print("\nTesting Compatibility Endpoint (GET):")

for platform in ['android', 'ios']:
    params = {
        "current_version": "0.7.1",
        "platform": platform,
        "app_identifier": "nexa-timesheet"
    }
    
    try:
        response = requests.get(
            "http://localhost:8000/api/v2/app-version/check",
            params=params
        )
        
        print(f"\nPlatform: {platform}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Latest version: {data.get('latest_version')}")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")