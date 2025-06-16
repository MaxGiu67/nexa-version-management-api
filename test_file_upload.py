"""
Test completo per upload e download file
"""
import requests
import os
import json
from create_test_file import create_test_apk, create_test_ipa

BASE_URL = "http://localhost:8000"

def test_upload_and_download():
    """Test completo upload e download"""
    
    print("🔧 Creating test files...")
    apk_path = create_test_apk()
    ipa_path = create_test_ipa()
    
    print("\n🧪 Testing file upload and download...")
    
    # Test 1: Upload APK Android
    print("\n1. Testing Android APK upload...")
    with open(apk_path, 'rb') as f:
        files = {'file': f}
        data = {
            'version': '1.3.0',
            'platform': 'android',
            'version_code': 5,
            'is_mandatory': False,
            'changelog': '{"changes": ["Test upload APK", "File management system"]}'
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/app-version/upload", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ APK uploaded successfully: {result['file_info']['filename']}")
            print(f"   Size: {result['file_info']['size']} bytes")
            print(f"   Download URL: {result['file_info']['download_url']}")
        else:
            print(f"❌ APK upload failed: {response.status_code} - {response.text}")
    
    # Test 2: Upload IPA iOS
    print("\n2. Testing iOS IPA upload...")
    with open(ipa_path, 'rb') as f:
        files = {'file': f}
        data = {
            'version': '1.3.0',
            'platform': 'ios',
            'version_code': 5,
            'is_mandatory': True,
            'changelog': '{"changes": ["Test upload IPA", "iOS version"]}'
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/app-version/upload", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ IPA uploaded successfully: {result['file_info']['filename']}")
            print(f"   Size: {result['file_info']['size']} bytes")
            print(f"   Download URL: {result['file_info']['download_url']}")
        else:
            print(f"❌ IPA upload failed: {response.status_code} - {response.text}")
    
    # Test 3: Lista file caricati
    print("\n3. Testing file list...")
    response = requests.get(f"{BASE_URL}/api/v1/app-version/files")
    if response.status_code == 200:
        files_data = response.json()
        print(f"✅ Found {len(files_data['files'])} uploaded files:")
        for file_info in files_data['files']:
            print(f"   - {file_info['filename']} ({file_info['platform']}) - {file_info['size_mb']} MB")
    else:
        print(f"❌ Failed to get file list: {response.status_code}")
    
    # Test 4: Download file
    print("\n4. Testing file download...")
    if 'files_data' in locals() and files_data['files']:
        first_file = files_data['files'][0]
        download_url = f"{BASE_URL}{first_file['download_url']}"
        
        response = requests.get(download_url)
        if response.status_code == 200:
            print(f"✅ File download successful: {len(response.content)} bytes")
            print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
        else:
            print(f"❌ File download failed: {response.status_code}")
    
    # Test 5: Verifica che l'API check updates restituisca i nuovi file
    print("\n5. Testing updated API with file URLs...")
    response = requests.get(f"{BASE_URL}/api/v1/app-version/check?current_version=1.0.0&platform=android")
    if response.status_code == 200:
        data = response.json()
        if data.get('hasUpdate'):
            print(f"✅ Check updates shows new version: {data.get('latestVersion')}")
            if 'downloadUrl' in data and data['downloadUrl']:
                print(f"   Download URL available: {data['downloadUrl']}")
            else:
                print("   ⚠️ No download URL in response")
        else:
            print("   ⚠️ No update detected")
    else:
        print(f"❌ Check updates failed: {response.status_code}")
    
    # Test 6: Test upload file invalido
    print("\n6. Testing invalid file upload...")
    
    # Crea file di testo (non APK/IPA)
    test_txt_path = "test_files/invalid.txt"
    with open(test_txt_path, 'w') as f:
        f.write("This is not an APK or IPA file")
    
    with open(test_txt_path, 'rb') as f:
        files = {'file': f}
        data = {
            'version': '1.4.0',
            'platform': 'android',
            'version_code': 6
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/app-version/upload", files=files, data=data)
        
        if response.status_code == 400:
            print("✅ Invalid file correctly rejected")
        else:
            print(f"❌ Invalid file should have been rejected: {response.status_code}")
    
    # Cleanup
    print("\n🧹 Cleaning up test files...")
    for path in [apk_path, ipa_path, test_txt_path]:
        if os.path.exists(path):
            os.remove(path)
    
    if os.path.exists("test_files"):
        os.rmdir("test_files")
    
    print("\n✅ File upload/download tests completed!")

if __name__ == "__main__":
    # Verifica che il server sia attivo
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            raise Exception("Server not healthy")
    except:
        print(f"❌ Server not running on {BASE_URL}")
        print("Please start the server with: python simple_api.py")
        exit(1)
    
    test_upload_and_download()