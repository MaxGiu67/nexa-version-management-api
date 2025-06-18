#!/usr/bin/env python3
"""Test user detail endpoint specifically"""

import requests

headers = {"X-API-Key": "nexa_internal_app_key_2025"}

# First get list of users to find a valid ID
print("Getting users list...")
response = requests.get("http://localhost:8000/api/v2/users", headers=headers)

if response.status_code == 200:
    users = response.json()['users']
    if users:
        user_id = users[0]['id']
        print(f"Testing user detail for ID: {user_id}")
        
        # Test user detail
        detail_response = requests.get(f"http://localhost:8000/api/v2/users/{user_id}", headers=headers)
        print(f"Status: {detail_response.status_code}")
        
        if detail_response.status_code == 200:
            print("✅ Success")
            print(detail_response.json())
        else:
            print(f"❌ Failed: {detail_response.text}")
    else:
        print("No users found")
else:
    print(f"Failed to get users: {response.text}")