#!/usr/bin/env python3
"""Test simple version check"""

import requests

# Test the compatibility endpoint
url = "http://localhost:8000/api/v2/app-version/check"
params = {
    "current_version": "0.7.1",
    "platform": "android",
    "app_identifier": "nexa-timesheet"
}

try:
    print(f"Testing {url}")
    print(f"Params: {params}")
    
    response = requests.get(url, params=params)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print("\nUpdate available:", data.get('is_update_available'))
        print("Latest version:", data.get('latest_version'))
        print("Is mandatory:", data.get('is_mandatory'))
except Exception as e:
    print(f"Error: {e}")