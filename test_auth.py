#!/usr/bin/env python3
"""
Test script for authentication system
"""

import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "nexa_internal_app_key_2025"

def test_auth_flow():
    """Test the complete authentication flow"""
    print("Testing Authentication Flow...")
    
    # 1. Test login
    print("\n1. Testing login...")
    login_response = requests.post(
        f"{BASE_URL}/api/v2/auth/login",
        json={"username": "admin", "password": "admin123"},
        headers={"X-API-Key": API_KEY}
    )
    print(f"Status: {login_response.status_code}")
    print(f"Response: {json.dumps(login_response.json(), indent=2)}")
    
    if login_response.status_code != 200:
        print("❌ Login failed!")
        return
    
    login_data = login_response.json()
    session_token = login_data["session_token"]
    print(f"✅ Login successful! Session token: {session_token[:20]}...")
    
    # 2. Test getting current user
    print("\n2. Testing get current user...")
    me_response = requests.get(
        f"{BASE_URL}/api/v2/auth/me",
        headers={
            "Authorization": f"Bearer {session_token}",
            "X-API-Key": API_KEY
        }
    )
    print(f"Status: {me_response.status_code}")
    print(f"Response: {json.dumps(me_response.json(), indent=2)}")
    
    # 3. Test enabling 2FA
    print("\n3. Testing enable 2FA...")
    enable_2fa_response = requests.post(
        f"{BASE_URL}/api/v2/auth/enable-2fa",
        headers={
            "Authorization": f"Bearer {session_token}",
            "X-API-Key": API_KEY
        }
    )
    print(f"Status: {enable_2fa_response.status_code}")
    if enable_2fa_response.status_code == 200:
        data = enable_2fa_response.json()
        print(f"✅ 2FA enabled!")
        print(f"Secret: {data['secret']}")
        print(f"Backup codes: {data['backup_codes']}")
        print("\n⚠️  Scan the QR code with Google Authenticator app")
        print("QR Code data URL available in response")
    
    # 4. Test logout
    print("\n4. Testing logout...")
    logout_response = requests.post(
        f"{BASE_URL}/api/v2/auth/logout",
        headers={
            "Authorization": f"Bearer {session_token}",
            "X-API-Key": API_KEY
        }
    )
    print(f"Status: {logout_response.status_code}")
    print(f"Response: {json.dumps(logout_response.json(), indent=2)}")

if __name__ == "__main__":
    print("Version Management Authentication Test")
    print("=" * 50)
    test_auth_flow()
