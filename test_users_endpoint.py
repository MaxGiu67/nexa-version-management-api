#!/usr/bin/env python3
"""Test users endpoints"""

import requests
import json

base_url = "http://localhost:8000"
headers = {"X-API-Key": "nexa_internal_app_key_2025"}

# Test endpoints che il frontend userà
tests = [
    {
        "name": "Get All Users",
        "method": "GET",
        "url": f"{base_url}/api/v2/users",
        "params": {"limit": 10, "offset": 0}
    },
    {
        "name": "Get User Details (User ID 4)",
        "method": "GET", 
        "url": f"{base_url}/api/v2/users/4",
        "params": None
    },
    {
        "name": "Get Sessions for App",
        "method": "GET",
        "url": f"{base_url}/api/v2/sessions/recent/nexa-timesheet",
        "params": {"limit": 10}
    },
    {
        "name": "Get Session Analytics",
        "method": "GET",
        "url": f"{base_url}/api/v2/analytics/nexa-timesheet/sessions",
        "params": {"days": 7}
    }
]

print("Testing Users and Sessions Endpoints")
print("=" * 60)

for test in tests:
    print(f"\n{test['name']}:")
    print(f"URL: {test['url']}")
    
    try:
        if test['method'] == 'GET':
            response = requests.get(test['url'], params=test['params'], headers=headers)
        else:
            response = requests.post(test['url'], json=test.get('data'), headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success")
            data = response.json()
            
            # Show sample data structure
            if 'users' in data:
                print(f"  Found {len(data['users'])} users")
                if data['users']:
                    user = data['users'][0]
                    print(f"  Sample user: {user.get('email', 'No email')} - {user.get('name', 'No name')}")
            
            elif 'sessions' in data:
                print(f"  Found {len(data['sessions'])} sessions")
                
            elif 'stats' in data:
                stats = data['stats']
                print(f"  Daily active users: {stats.get('daily_active_users', 'N/A')}")
                print(f"  Total sessions: {stats.get('total_sessions', 'N/A')}")
                
            elif 'email' in data:  # Single user
                print(f"  User: {data.get('email', 'No email')} - {data.get('name', 'No name')}")
                print(f"  Sessions: {len(data.get('recent_sessions', []))}")
                print(f"  Installations: {len(data.get('installations', []))}")
                
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

print(f"\n{'=' * 60}")
print("Frontend should now be able to display users and sessions!")
print("Navigate to:")
print("- http://localhost:3000/users (Global users view)")
print("- http://localhost:3000/app/nexa-timesheet (App detail with Sessions tab)")