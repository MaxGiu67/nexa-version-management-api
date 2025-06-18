#!/usr/bin/env python3
"""Minimal session test"""

import requests
import json

# Absolute minimal payload
test_payload = {
    "app_identifier": "nexa-timesheet",
    "user_uuid": "minimal-test",
    "app_version": "0.7.3"
}

url = "http://localhost:8000/api/v2/session/start"

print("Testing minimal session...")
print(json.dumps(test_payload, indent=2))

response = requests.post(url, json=test_payload)
print(f"\nStatus: {response.status_code}")

if response.status_code == 200:
    print("✅ Success")
    print(response.json())
else:
    print(f"❌ Failed: {response.text}")