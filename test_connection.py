#!/usr/bin/env python3
"""Test connection to the deployed backend"""

import requests
import json

# Backend URL
BASE_URL = "https://nexa-version-management-be.up.railway.app"
API_KEY = "nexa_internal_app_key_2025"

# Test endpoints
endpoints = [
    ("/health", "GET", False),  # No auth needed
    ("/api/v2/apps", "GET", True),  # Auth required
    ("/api/v2/users", "GET", True),  # Auth required
    ("/docs", "GET", False),  # Swagger docs
]

print("Testing Backend Connection...")
print(f"Base URL: {BASE_URL}")
print("-" * 50)

for endpoint, method, needs_auth in endpoints:
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if needs_auth:
        headers["X-API-Key"] = API_KEY
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        
        print(f"\n{method} {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Try to parse JSON
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"Response (text): {response.text[:200]}...")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n{method} {endpoint}")
        print(f"Connection Error: {e}")

print("\n" + "-" * 50)
print("Testing CORS headers...")

# Test CORS preflight
try:
    response = requests.options(
        f"{BASE_URL}/api/v2/apps",
        headers={
            "Origin": "https://nexa-version-manager-fe.up.railway.app",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-API-Key"
        },
        timeout=10
    )
    print(f"\nOPTIONS request status: {response.status_code}")
    print("CORS headers:")
    for header, value in response.headers.items():
        if header.lower().startswith('access-control'):
            print(f"  {header}: {value}")
except Exception as e:
    print(f"CORS test failed: {e}")