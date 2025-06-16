"""
Test completi per l'API Version Management
"""
import requests
import json
import time
from datetime import datetime
import sys

# URL base API
BASE_URL = "http://localhost:8000"

# Colori per output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{title.center(60)}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")

def print_test(test_name, passed, details="", expected="", actual=""):
    status = f"{Colors.GREEN}✅ PASSED{Colors.RESET}" if passed else f"{Colors.RED}❌ FAILED{Colors.RESET}"
    print(f"\n{Colors.BLUE}🧪 Test:{Colors.RESET} {test_name}")
    print(f"Status: {status}")
    
    if details:
        print(f"Details: {details}")
    
    if expected and actual:
        print(f"Expected: {Colors.YELLOW}{expected}{Colors.RESET}")
        print(f"Actual: {Colors.WHITE}{actual}{Colors.RESET}")
    
    return passed

def test_server_status():
    """Test 1: Verifica che il server sia attivo"""
    print_header("TEST 1: SERVER STATUS")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        data = response.json()
        
        passed = (
            response.status_code == 200 and
            data.get("status") == "healthy" and
            data.get("service") == "version-management"
        )
        
        return print_test(
            "Server Health Check",
            passed,
            f"Response: {json.dumps(data, indent=2)}" if passed else f"Status code: {response.status_code}",
            "status: healthy, service: version-management",
            f"status: {data.get('status')}, service: {data.get('service')}"
        )
        
    except Exception as e:
        return print_test("Server Health Check", False, f"Error: {str(e)}")

def test_check_updates():
    """Test 2: Test controllo aggiornamenti"""
    print_header("TEST 2: CHECK UPDATES")
    
    test_cases = [
        {
            "name": "Versione vecchia (1.0.0) - Android",
            "params": {"current_version": "1.0.0", "platform": "android"},
            "expected_update": True,
            "expected_mandatory": True
        },
        {
            "name": "Versione corrente (1.2.0) - Android", 
            "params": {"current_version": "1.2.0", "platform": "android"},
            "expected_update": False
        },
        {
            "name": "Versione intermedia (1.1.0) - iOS",
            "params": {"current_version": "1.1.0", "platform": "ios"},
            "expected_update": True
        },
        {
            "name": "Versione molto vecchia (0.9.0) - All platforms",
            "params": {"current_version": "0.9.0", "platform": "all"},
            "expected_update": True,
            "expected_mandatory": True
        }
    ]
    
    all_passed = True
    
    for test in test_cases:
        try:
            response = requests.get(f"{BASE_URL}/api/v1/app-version/check", params=test["params"])
            
            if response.status_code != 200:
                all_passed = False
                print_test(test["name"], False, f"HTTP {response.status_code}")
                continue
            
            data = response.json()
            
            # Verifica hasUpdate
            update_correct = data.get("hasUpdate") == test.get("expected_update")
            
            # Verifica mandatory se specificato
            mandatory_correct = True
            if "expected_mandatory" in test:
                mandatory_correct = data.get("isMandatory") == test["expected_mandatory"]
            
            # Verifica struttura response
            required_fields = ["hasUpdate", "latestVersion", "versionCode"]
            structure_correct = all(field in data for field in required_fields)
            
            passed = update_correct and mandatory_correct and structure_correct
            
            details = f"hasUpdate: {data.get('hasUpdate')}, latestVersion: {data.get('latestVersion')}"
            if "isMandatory" in data:
                details += f", mandatory: {data.get('isMandatory')}"
            
            if not print_test(test["name"], passed, details):
                all_passed = False
                
        except Exception as e:
            all_passed = False
            print_test(test["name"], False, f"Error: {str(e)}")
    
    return all_passed

def test_latest_version():
    """Test 3: Test ultima versione per piattaforma"""
    print_header("TEST 3: LATEST VERSION")
    
    platforms = ["android", "ios", "all"]
    all_passed = True
    
    for platform in platforms:
        try:
            response = requests.get(f"{BASE_URL}/api/v1/app-version/latest", params={"platform": platform})
            
            if response.status_code != 200:
                all_passed = False
                print_test(f"Latest Version - {platform}", False, f"HTTP {response.status_code}")
                continue
            
            data = response.json()
            
            # Verifica campi obbligatori
            required_fields = ["version", "versionCode", "platform", "releaseDate"]
            fields_present = all(field in data for field in required_fields)
            
            # Verifica formato versione
            version_format_ok = True
            try:
                parts = data.get("version", "").split(".")
                if len(parts) != 3 or not all(p.isdigit() for p in parts):
                    version_format_ok = False
            except:
                version_format_ok = False
            
            passed = fields_present and version_format_ok
            
            details = f"version: {data.get('version')}, platform: {data.get('platform')}, code: {data.get('versionCode')}"
            
            if not print_test(f"Latest Version - {platform}", passed, details):
                all_passed = False
                
        except Exception as e:
            all_passed = False
            print_test(f"Latest Version - {platform}", False, f"Error: {str(e)}")
    
    return all_passed

def test_api_docs():
    """Test 4: Test documentazione API"""
    print_header("TEST 4: API DOCUMENTATION")
    
    try:
        # Test Swagger UI
        response = requests.get(f"{BASE_URL}/docs")
        swagger_ok = response.status_code == 200
        
        # Test OpenAPI JSON
        response = requests.get(f"{BASE_URL}/openapi.json")
        openapi_ok = response.status_code == 200
        
        passed = swagger_ok and openapi_ok
        
        return print_test(
            "API Documentation",
            passed,
            f"Swagger UI: {'✓' if swagger_ok else '✗'}, OpenAPI: {'✓' if openapi_ok else '✗'}",
            "Both Swagger UI and OpenAPI available",
            f"Swagger: {swagger_ok}, OpenAPI: {openapi_ok}"
        )
        
    except Exception as e:
        return print_test("API Documentation", False, f"Error: {str(e)}")

def test_edge_cases():
    """Test 5: Test casi limite"""
    print_header("TEST 5: EDGE CASES")
    
    test_cases = [
        {
            "name": "Versione formato invalido",
            "url": f"{BASE_URL}/api/v1/app-version/check?current_version=1.0&platform=android",
            "expect_error": True
        },
        {
            "name": "Piattaforma inesistente",
            "url": f"{BASE_URL}/api/v1/app-version/check?current_version=1.0.0&platform=windows",
            "expect_success": True  # Dovrebbe funzionare ma non trovare versioni specifiche
        },
        {
            "name": "Parametri mancanti",
            "url": f"{BASE_URL}/api/v1/app-version/check",
            "expect_error": True
        },
        {
            "name": "Versione futura",
            "url": f"{BASE_URL}/api/v1/app-version/check?current_version=999.999.999&platform=android",
            "expect_success": True,
            "expect_no_update": True
        }
    ]
    
    all_passed = True
    
    for test in test_cases:
        try:
            response = requests.get(test["url"])
            
            if test.get("expect_error"):
                # Aspettiamo un errore
                passed = response.status_code >= 400 or "error" in response.json()
                details = f"Status: {response.status_code}"
            else:
                # Aspettiamo successo
                passed = response.status_code == 200
                if passed and test.get("expect_no_update"):
                    data = response.json()
                    passed = data.get("hasUpdate") == False
                details = f"Status: {response.status_code}, Response: {response.json()}"
            
            if not print_test(test["name"], passed, details):
                all_passed = False
                
        except Exception as e:
            all_passed = False
            print_test(test["name"], False, f"Error: {str(e)}")
    
    return all_passed

def test_performance():
    """Test 6: Test performance"""
    print_header("TEST 6: PERFORMANCE")
    
    print(f"{Colors.BLUE}Testing response times...{Colors.RESET}")
    
    endpoints = [
        ("/health", "Health Check"),
        ("/api/v1/app-version/check?current_version=1.0.0&platform=android", "Check Updates"),
        ("/api/v1/app-version/latest?platform=android", "Latest Version")
    ]
    
    all_passed = True
    
    for endpoint, name in endpoints:
        times = []
        
        for i in range(5):
            start_time = time.time()
            try:
                response = requests.get(f"{BASE_URL}{endpoint}")
                end_time = time.time()
                
                if response.status_code == 200:
                    times.append(end_time - start_time)
            except:
                pass
        
        if times:
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            # Consideriamo buone le risposte sotto 1 secondo
            passed = avg_time < 1.0 and max_time < 2.0
            
            details = f"Avg: {avg_time:.3f}s, Min: {min_time:.3f}s, Max: {max_time:.3f}s"
            
            if not print_test(f"Performance - {name}", passed, details):
                all_passed = False
        else:
            all_passed = False
            print_test(f"Performance - {name}", False, "No successful requests")
    
    return all_passed

def test_data_integrity():
    """Test 7: Test integrità dati"""
    print_header("TEST 7: DATA INTEGRITY")
    
    try:
        # Ottieni ultima versione
        response = requests.get(f"{BASE_URL}/api/v1/app-version/latest?platform=all")
        latest_data = response.json()
        
        # Verifica con check updates
        response = requests.get(f"{BASE_URL}/api/v1/app-version/check?current_version=0.1.0&platform=all")
        check_data = response.json()
        
        # I dati dovrebbero essere consistenti
        version_consistent = latest_data.get("version") == check_data.get("latestVersion")
        code_consistent = latest_data.get("versionCode") == check_data.get("versionCode")
        
        passed = version_consistent and code_consistent
        
        return print_test(
            "Data Consistency",
            passed,
            f"Latest version endpoint vs Check updates endpoint",
            f"Same version and code",
            f"Version match: {version_consistent}, Code match: {code_consistent}"
        )
        
    except Exception as e:
        return print_test("Data Consistency", False, f"Error: {str(e)}")

def run_all_tests():
    """Esegui tutti i test"""
    print(f"\n{Colors.PURPLE}{Colors.BOLD}🚀 COMPREHENSIVE API TESTING{Colors.RESET}")
    print(f"{Colors.PURPLE}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print(f"{Colors.PURPLE}Target: {BASE_URL}{Colors.RESET}")
    
    # Lista dei test
    tests = [
        ("Server Status", test_server_status),
        ("Check Updates", test_check_updates),
        ("Latest Version", test_latest_version),
        ("API Documentation", test_api_docs),
        ("Edge Cases", test_edge_cases),
        ("Performance", test_performance),
        ("Data Integrity", test_data_integrity)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"{Colors.RED}❌ Test {test_name} crashed: {str(e)}{Colors.RESET}")
            results.append((test_name, False))
    
    # Riepilogo finale
    print_header("TEST SUMMARY")
    
    passed_tests = 0
    total_tests = len(results)
    
    for test_name, passed in results:
        status = f"{Colors.GREEN}✅ PASSED{Colors.RESET}" if passed else f"{Colors.RED}❌ FAILED{Colors.RESET}"
        print(f"{test_name:.<40} {status}")
        if passed:
            passed_tests += 1
    
    print(f"\n{Colors.BOLD}Results: {passed_tests}/{total_tests} tests passed{Colors.RESET}")
    
    if passed_tests == total_tests:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! API is ready for production!{Colors.RESET}")
        return True
    else:
        failed_tests = total_tests - passed_tests
        print(f"\n{Colors.RED}{Colors.BOLD}❌ {failed_tests} test(s) failed. Please fix before deploying.{Colors.RESET}")
        return False

if __name__ == "__main__":
    # Controlla se il server è in esecuzione
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except:
        print(f"{Colors.RED}❌ Server not running on {BASE_URL}{Colors.RESET}")
        print(f"{Colors.YELLOW}Please start the server with: python simple_api.py{Colors.RESET}")
        sys.exit(1)
    
    # Esegui tutti i test
    success = run_all_tests()
    sys.exit(0 if success else 1)