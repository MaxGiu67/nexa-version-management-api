"""
Test completo per API con storage BLOB
"""
import requests
import json
import os
from create_test_file import create_test_apk, create_test_ipa

BASE_URL = "http://localhost:8000"

def test_blob_api():
    """Test completo dell'API con storage BLOB"""
    
    print("🗄️ TESTING API WITH DATABASE BLOB STORAGE")
    print("=" * 60)
    
    # Test 1: Verifica health check
    print("\n1. 🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        if data.get('storage') == 'database-blob':
            print("✅ Health check OK - BLOB storage confirmed")
            print(f"   Response: {data}")
        else:
            print("❌ Health check failed or wrong storage type")
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Verifica endpoint base
    print("\n2. 📱 Testing base version endpoints...")
    try:
        response = requests.get(f"{BASE_URL}/api/v2/app-version/latest?platform=android")
        data = response.json()
        print(f"✅ Latest version: {data.get('version')} (code {data.get('versionCode')})")
        if data.get('downloadUrl'):
            print(f"   Download URL: {data['downloadUrl']}")
        else:
            print("   No file uploaded yet")
    except Exception as e:
        print(f"❌ Latest version error: {e}")
    
    # Test 3: Storage info
    print("\n3. 💾 Testing storage info...")
    try:
        response = requests.get(f"{BASE_URL}/api/v2/app-version/storage-info")
        data = response.json()
        print(f"✅ Storage info:")
        print(f"   Files: {data.get('total_files')}")
        print(f"   Total size: {data.get('total_size_mb')} MB")
        print(f"   Downloads: {data.get('total_downloads')}")
    except Exception as e:
        print(f"❌ Storage info error: {e}")
    
    # Test 4: Lista file
    print("\n4. 📂 Testing file list...")
    try:
        response = requests.get(f"{BASE_URL}/api/v2/app-version/files")
        data = response.json()
        print(f"✅ Files in database: {len(data.get('files', []))}")
        for file_info in data.get('files', [])[:3]:  # Mostra primi 3
            print(f"   - {file_info.get('filename')} ({file_info.get('size_mb')} MB)")
    except Exception as e:
        print(f"❌ File list error: {e}")
    
    # Test 5: Upload file di test
    print("\n5. 📤 Testing file upload...")
    
    # Crea file di test
    print("   Creating test APK...")
    apk_path = create_test_apk()
    
    try:
        with open(apk_path, 'rb') as f:
            files = {'file': f}
            data = {
                'version': '1.3.0',
                'platform': 'android',
                'version_code': 5,
                'is_mandatory': False,
                'changelog': '{"changes": ["Test BLOB upload", "Database storage"]}'
            }
            
            response = requests.post(f"{BASE_URL}/api/v2/app-version/upload", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload successful!")
                print(f"   File: {result['file_info']['filename']}")
                print(f"   Size: {result['file_info']['size_mb']} MB")
                print(f"   Hash: {result['file_info']['hash'][:16]}...")
                print(f"   Download URL: {result['file_info']['download_url']}")
                
                # Test download del file appena caricato
                print("\n6. 📥 Testing file download...")
                download_url = f"{BASE_URL}{result['file_info']['download_url']}"
                download_response = requests.get(download_url)
                
                if download_response.status_code == 200:
                    print(f"✅ Download successful!")
                    print(f"   Downloaded: {len(download_response.content)} bytes")
                    print(f"   Content-Type: {download_response.headers.get('content-type')}")
                    
                    # Verifica che il file scaricato sia identico
                    with open(apk_path, 'rb') as original:
                        original_content = original.read()
                        if original_content == download_response.content:
                            print("✅ Downloaded file matches original!")
                        else:
                            print("❌ Downloaded file differs from original")
                else:
                    print(f"❌ Download failed: {download_response.status_code}")
                
            else:
                print(f"❌ Upload failed: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"❌ Upload test error: {e}")
    finally:
        # Cleanup file di test
        if os.path.exists(apk_path):
            os.remove(apk_path)
        if os.path.exists("test_files"):
            try:
                os.rmdir("test_files")
            except:
                pass
    
    # Test 7: Verifica check updates con file
    print("\n7. 🔄 Testing check updates with file...")
    try:
        response = requests.get(f"{BASE_URL}/api/v2/app-version/check?current_version=1.0.0&platform=android")
        data = response.json()
        if data.get('hasUpdate'):
            print(f"✅ Update available: {data.get('latestVersion')}")
            if data.get('downloadUrl'):
                print(f"   Download URL: {data['downloadUrl']}")
                print(f"   File size: {data.get('fileSize')} bytes")
            if data.get('isMandatory'):
                print("   ⚠️ Mandatory update")
        else:
            print("   No update needed")
    except Exception as e:
        print(f"❌ Check updates error: {e}")
    
    print(f"\n🌐 Web Interface available at:")
    print(f"   📱 Upload Form: {BASE_URL}/api/v2/app-version/upload-form")
    print(f"   📚 API Docs: {BASE_URL}/docs")
    
    print(f"\n✅ BLOB storage testing completed!")
    print(f"📌 Files are now stored directly in MySQL database as binary data")
    print(f"🔒 More secure and centralized than file system storage")

if __name__ == "__main__":
    # Verifica server attivo
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            raise Exception("Server not healthy")
    except:
        print(f"❌ Server not running on {BASE_URL}")
        print("Please start the server with: python complete_api_with_blob.py")
        exit(1)
    
    test_blob_api()