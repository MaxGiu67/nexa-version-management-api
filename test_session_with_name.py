#!/usr/bin/env python3
"""Test session start with email and name"""

import requests
import json
from datetime import datetime

# Test data matching the frontend format
test_payload = {
    "app_identifier": "nexa-timesheet",
    "user_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "email": "mario.rossi@nexadata.it",
    "name": "Mario Rossi",
    "app_version": "0.7.3",
    "device_info": {
        "model": "SM-S928B",
        "os": "Android",
        "os_version": "14",
        "screen_size": "1440x3088",
        "brand": "samsung",
        "manufacturer": "samsung"
    }
}

# Make request
url = "http://localhost:8000/api/v2/session/start"
headers = {
    "Content-Type": "application/json"
}

try:
    print("Testing Session Start with Name")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"\nPayload:")
    print(json.dumps(test_payload, indent=2))
    
    response = requests.post(url, json=test_payload, headers=headers)
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Success - Session created")
        print(f"Session ID: {data.get('session_id')}")
        print(f"User ID: {data.get('user_id')}")
        
        # Test with another user
        print("\n" + "=" * 60)
        print("\nTesting with another user...")
        
        test_payload2 = {
            "app_identifier": "nexa-timesheet",
            "user_uuid": "987e6543-e21b-12d3-a456-426614174999",
            "email": "giulia.verdi@nexadata.it",
            "name": "Giulia Verdi",
            "app_version": "0.7.3",
            "device_info": {
                "model": "iPhone 15 Pro",
                "os": "iOS",
                "os_version": "17.2",
                "brand": "Apple",
                "manufacturer": "Apple"
            }
        }
        
        response2 = requests.post(url, json=test_payload2, headers=headers)
        
        if response2.status_code == 200:
            data2 = response2.json()
            print("✅ Success - Second session created")
            print(f"Session ID: {data2.get('session_id')}")
            print(f"User ID: {data2.get('user_id')}")
        else:
            print(f"❌ Failed: {response2.text}")
            
    else:
        print(f"❌ Failed: {response.text}")
        
    # Test updating existing user
    print("\n" + "=" * 60)
    print("\nTesting update of existing user (Mario Rossi)...")
    
    # Change some data for existing user
    test_payload['name'] = "Mario Giovanni Rossi"  # Updated name
    test_payload['device_info']['os_version'] = "15"  # Updated OS
    
    response3 = requests.post(url, json=test_payload, headers=headers)
    
    if response3.status_code == 200:
        data3 = response3.json()
        print("✅ Success - Existing user session created")
        print(f"Session ID: {data3.get('session_id')} (new session)")
        print(f"User ID: {data3.get('user_id')} (same user)")
        print("User data should be updated with new name")
    else:
        print(f"❌ Failed: {response3.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")