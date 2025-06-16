"""
Test server semplice per verificare tutto funzioni
"""
import subprocess
import time
import requests
import sys
import signal
import os

def start_server():
    """Avvia il server in background"""
    print("🚀 Starting API server...")
    
    # Avvia il server
    process = subprocess.Popen([
        sys.executable, 'simple_api.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Aspetta che si avvii
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Verifica che sia attivo
    for i in range(10):
        try:
            response = requests.get('http://localhost:8000/health', timeout=1)
            if response.status_code == 200:
                print("✅ Server is running!")
                return process
        except:
            time.sleep(0.5)
    
    print("❌ Server failed to start")
    process.terminate()
    return None

def test_basic_endpoints(base_url="http://localhost:8000"):
    """Test degli endpoint base"""
    print(f"\n🧪 Testing basic endpoints at {base_url}...")
    
    tests = [
        {
            "name": "Health Check",
            "url": f"{base_url}/health",
            "expect_keys": ["status", "service"]
        },
        {
            "name": "Check Updates (old version)",
            "url": f"{base_url}/api/v1/app-version/check?current_version=1.0.0&platform=android",
            "expect_keys": ["hasUpdate", "latestVersion", "versionCode"]
        },
        {
            "name": "Check Updates (current version)",
            "url": f"{base_url}/api/v1/app-version/check?current_version=1.2.0&platform=android",
            "expect_keys": ["hasUpdate", "latestVersion"]
        },
        {
            "name": "Latest Version",
            "url": f"{base_url}/api/v1/app-version/latest?platform=android",
            "expect_keys": ["version", "versionCode", "platform"]
        }
    ]
    
    results = []
    
    for test in tests:
        try:
            print(f"\n📍 {test['name']}...")
            response = requests.get(test['url'], timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verifica chiavi richieste
                missing_keys = [key for key in test['expect_keys'] if key not in data]
                
                if not missing_keys:
                    print(f"✅ PASSED - {test['name']}")
                    print(f"   Response: {data}")
                    results.append(True)
                else:
                    print(f"❌ FAILED - Missing keys: {missing_keys}")
                    results.append(False)
            else:
                print(f"❌ FAILED - HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            results.append(False)
    
    return results

def test_file_endpoints():
    """Test degli endpoint per file"""
    print(f"\n📁 Testing file management endpoints...")
    
    # Test lista file (dovrebbe essere vuota inizialmente)
    try:
        response = requests.get('http://localhost:8000/api/v1/app-version/files')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ File list endpoint working - {len(data.get('files', []))} files")
        else:
            print(f"❌ File list failed - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ File list error: {str(e)}")
    
    # Test form upload (dovrebbe restituire HTML)
    try:
        response = requests.get('http://localhost:8000/api/v1/app-version/upload-form')
        if response.status_code == 200 and 'html' in response.text.lower():
            print("✅ Upload form endpoint working")
        else:
            print(f"❌ Upload form failed - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Upload form error: {str(e)}")

def test_database_data():
    """Test che i dati del database siano corretti"""
    print(f"\n🗄️ Testing database data...")
    
    try:
        response = requests.get('http://localhost:8000/api/v1/app-version/latest?platform=all')
        data = response.json()
        
        if data.get('version') == '1.2.0' and data.get('versionCode') == 4:
            print("✅ Database has correct latest version (1.2.0, code 4)")
        else:
            print(f"⚠️ Unexpected latest version: {data.get('version')} (code {data.get('versionCode')})")
            
        # Test aggiornamento da versione vecchia
        response = requests.get('http://localhost:8000/api/v1/app-version/check?current_version=1.0.0&platform=android')
        data = response.json()
        
        if data.get('hasUpdate') and data.get('isMandatory'):
            print("✅ Update detection working (1.0.0 → 1.2.0 mandatory)")
        else:
            print(f"⚠️ Update detection issue: hasUpdate={data.get('hasUpdate')}, mandatory={data.get('isMandatory')}")
            
    except Exception as e:
        print(f"❌ Database test error: {str(e)}")

def main():
    """Esegui tutti i test"""
    print("🔬 COMPREHENSIVE LOCAL TESTING")
    print("=" * 50)
    
    # Start server
    server_process = start_server()
    
    if not server_process:
        print("❌ Cannot start server, aborting tests")
        return False
    
    try:
        # Run tests
        basic_results = test_basic_endpoints()
        test_file_endpoints()
        test_database_data()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(basic_results)
        total = len(basic_results)
        
        print(f"Basic API Tests: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Ready for deployment!")
            success = True
        else:
            print("❌ Some tests failed. Please fix before deploying.")
            success = False
            
        # Show next steps
        print(f"\n📌 Next steps:")
        if success:
            print("1. ✅ All tests passed")
            print("2. 🚀 Deploy to Railway: git push origin main")
            print("3. 📱 Integrate with mobile app")
        else:
            print("1. 🔧 Fix failing tests")
            print("2. 🔄 Re-run tests")
            print("3. 🚀 Deploy when all pass")
            
        print(f"\n🌐 Server URLs (while running):")
        print(f"   API Docs: http://localhost:8000/docs")
        print(f"   Upload Form: http://localhost:8000/api/v1/app-version/upload-form")
        print(f"   Health: http://localhost:8000/health")
        
        return success
        
    finally:
        # Stop server
        print(f"\n🛑 Stopping server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except:
            server_process.kill()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)