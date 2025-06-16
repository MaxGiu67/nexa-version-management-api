"""
Script per testare l'API in locale prima del deploy
"""
import requests
import json
import time
from datetime import datetime

# Base URL per test locale
BASE_URL = "http://localhost:8000"

# Colori per output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name, passed, details=""):
    status = f"{GREEN}✓ PASSED{RESET}" if passed else f"{RED}✗ FAILED{RESET}"
    print(f"\n{BLUE}Test:{RESET} {name}")
    print(f"Status: {status}")
    if details:
        print(f"Details: {details}")

def test_health_check():
    """Test endpoint health"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        passed = response.status_code == 200
        data = response.json() if passed else None
        
        print_test(
            "Health Check",
            passed,
            f"Response: {json.dumps(data, indent=2)}" if data else f"Status: {response.status_code}"
        )
        return passed
    except Exception as e:
        print_test("Health Check", False, f"Error: {str(e)}")
        return False

def test_check_updates():
    """Test check updates per diverse versioni"""
    test_cases = [
        {
            "name": "Old version (1.0.0) - Android",
            "params": {"current_version": "1.0.0", "platform": "android"},
            "expect_update": True
        },
        {
            "name": "Current version (1.2.0) - Android", 
            "params": {"current_version": "1.2.0", "platform": "android"},
            "expect_update": False
        },
        {
            "name": "Mid version (1.1.0) - iOS",
            "params": {"current_version": "1.1.0", "platform": "ios"},
            "expect_update": True
        },
        {
            "name": "Invalid version format",
            "params": {"current_version": "1.0", "platform": "android"},
            "expect_error": True
        }
    ]
    
    all_passed = True
    
    for test in test_cases:
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/app-version/check",
                params=test["params"]
            )
            
            if test.get("expect_error"):
                passed = response.status_code == 400
            else:
                passed = response.status_code == 200
                if passed:
                    data = response.json()
                    if test.get("expect_update") is not None:
                        passed = data["hasUpdate"] == test["expect_update"]
            
            print_test(
                test["name"],
                passed,
                f"Response: {json.dumps(response.json(), indent=2)}" if response.status_code == 200 else f"Status: {response.status_code}"
            )
            
            if not passed:
                all_passed = False
                
        except Exception as e:
            print_test(test["name"], False, f"Error: {str(e)}")
            all_passed = False
    
    return all_passed

def test_latest_version():
    """Test get latest version"""
    platforms = ["android", "ios", "all"]
    all_passed = True
    
    for platform in platforms:
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/app-version/latest",
                params={"platform": platform}
            )
            
            passed = response.status_code == 200
            if passed:
                data = response.json()
                passed = all([
                    "version" in data,
                    "versionCode" in data,
                    "platform" in data
                ])
            
            print_test(
                f"Latest Version - {platform}",
                passed,
                f"Response: {json.dumps(response.json(), indent=2)}" if response.status_code == 200 else f"Status: {response.status_code}"
            )
            
            if not passed:
                all_passed = False
                
        except Exception as e:
            print_test(f"Latest Version - {platform}", False, f"Error: {str(e)}")
            all_passed = False
    
    return all_passed

def test_log_update():
    """Test log update (richiede auth - simulato)"""
    # Nota: Questo test fallirà senza un token JWT valido
    # Per ora testiamo solo che l'endpoint risponda
    try:
        data = {
            "from_version": "1.0.0",
            "to_version": "1.2.0",
            "platform": "android",
            "update_type": "manual",
            "device_info": {
                "model": "Test Device",
                "os_version": "13"
            }
        }
        
        # Senza token, ci aspettiamo 403 (non autorizzato)
        response = requests.post(
            f"{BASE_URL}/api/v1/app-version/log-update",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        # Ci aspettiamo 403 senza auth
        passed = response.status_code in [403, 401]
        
        print_test(
            "Log Update (no auth)",
            passed,
            f"Expected 401/403 without auth, got {response.status_code}"
        )
        
        return passed
        
    except Exception as e:
        print_test("Log Update", False, f"Error: {str(e)}")
        return False

def test_api_docs():
    """Test che la documentazione API sia accessibile"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        passed = response.status_code == 200
        
        print_test(
            "API Documentation (Swagger)",
            passed,
            "Swagger UI available at /docs" if passed else f"Status: {response.status_code}"
        )
        
        return passed
    except Exception as e:
        print_test("API Documentation", False, f"Error: {str(e)}")
        return False

def main():
    print(f"\n{YELLOW}========================================{RESET}")
    print(f"{YELLOW}🧪 Testing Version Management API Locally{RESET}")
    print(f"{YELLOW}========================================{RESET}")
    print(f"\nBase URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Controlla se il server è attivo
    print(f"\n{BLUE}Checking if server is running...{RESET}")
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
        print(f"{GREEN}✓ Server is running!{RESET}")
    except:
        print(f"{RED}✗ Server is not running!{RESET}")
        print(f"\n{YELLOW}Please start the server with:{RESET}")
        print(f"  python main.py")
        return
    
    # Esegui tutti i test
    tests_results = []
    
    print(f"\n{BLUE}Running tests...{RESET}")
    
    tests_results.append(("Health Check", test_health_check()))
    tests_results.append(("Check Updates", test_check_updates()))
    tests_results.append(("Latest Version", test_latest_version()))
    tests_results.append(("Log Update", test_log_update()))
    tests_results.append(("API Docs", test_api_docs()))
    
    # Riassunto
    print(f"\n{YELLOW}========================================{RESET}")
    print(f"{YELLOW}📊 Test Summary{RESET}")
    print(f"{YELLOW}========================================{RESET}")
    
    total_tests = len(tests_results)
    passed_tests = sum(1 for _, passed in tests_results if passed)
    
    for test_name, passed in tests_results:
        status = f"{GREEN}PASSED{RESET}" if passed else f"{RED}FAILED{RESET}"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print(f"\n{GREEN}✅ All tests passed! Ready for deployment.{RESET}")
    else:
        print(f"\n{RED}❌ Some tests failed. Please fix before deploying.{RESET}")
    
    # Info utili
    print(f"\n{BLUE}📌 Useful commands:{RESET}")
    print(f"  - View API docs: {BASE_URL}/docs")
    print(f"  - View Redoc: {BASE_URL}/redoc")
    print(f"  - Health check: curl {BASE_URL}/health")

if __name__ == "__main__":
    main()