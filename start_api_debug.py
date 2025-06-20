#!/usr/bin/env python3
"""
Script di debug per avviare l'API con controlli completi
"""

import os
import sys
import subprocess

def check_environment():
    """Verifica l'ambiente di esecuzione"""
    print("🔍 Controllo ambiente...")
    print(f"   Python: {sys.executable}")
    print(f"   Version: {sys.version}")
    print(f"   Directory: {os.getcwd()}")
    print(f"   PATH: {os.environ.get('PATH', '')[:100]}...")
    
    # Verifica se siamo nella directory giusta
    if not os.path.exists('multi_app_api.py'):
        print("❌ ERRORE: multi_app_api.py non trovato!")
        print("   Assicurati di essere nella directory:")
        print("   /Users/maxgiu/Git_progetti/nexa-timsheet/version-management/api")
        return False
    
    return True

def check_modules():
    """Verifica che i moduli auth siano presenti"""
    print("\n🔍 Controllo moduli...")
    
    required_files = [
        'auth_module.py',
        'auth_endpoints.py',
        'multi_app_api.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file} trovato")
        else:
            print(f"   ❌ {file} MANCANTE!")
            return False
    
    return True

def check_imports():
    """Verifica che i moduli si importino correttamente"""
    print("\n🔍 Controllo import...")
    
    try:
        import auth_module
        print("   ✅ auth_module importato")
    except Exception as e:
        print(f"   ❌ Errore import auth_module: {e}")
        return False
    
    try:
        import auth_endpoints
        print("   ✅ auth_endpoints importato")
    except Exception as e:
        print(f"   ❌ Errore import auth_endpoints: {e}")
        return False
    
    try:
        # Test che il router esista
        from auth_endpoints import router
        print(f"   ✅ Router auth ha {len(router.routes)} routes")
    except Exception as e:
        print(f"   ❌ Errore accesso router: {e}")
        return False
    
    return True

def check_dependencies():
    """Verifica dipendenze"""
    print("\n📦 Controllo dipendenze...")
    
    deps = {
        'bcrypt': 'bcrypt',
        'pyotp': 'pyotp',
        'qrcode': 'qrcode',
        'PIL': 'pillow',
        'email_validator': 'email-validator'
    }
    
    missing = []
    for module, package in deps.items():
        try:
            __import__(module)
            print(f"   ✅ {module} installato")
        except ImportError:
            print(f"   ❌ {module} mancante")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Installa le dipendenze mancanti con:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def check_database():
    """Verifica connessione database"""
    print("\n🗄️  Controllo database...")
    
    try:
        from dotenv import load_dotenv
        import pymysql
        
        # Carica environment
        if os.path.exists('.env.local'):
            load_dotenv('.env.local')
            print("   ✅ .env.local caricato")
        
        # Test connessione
        DB_CONFIG = {
            'host': os.environ.get('DB_HOST', os.environ.get('MYSQL_HOST', 'tramway.proxy.rlwy.net')),
            'port': int(os.environ.get('DB_PORT', os.environ.get('MYSQL_PORT', 20671))),
            'user': os.environ.get('DB_USER', os.environ.get('MYSQL_USER', 'root')),
            'password': os.environ.get('DB_PASSWORD', os.environ.get('MYSQL_PASSWORD', 'aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP')),
            'database': os.environ.get('DB_NAME', os.environ.get('MYSQL_DATABASE', 'railway')),
            'charset': 'utf8mb4'
        }
        
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Verifica tabelle auth
        cursor.execute("SHOW TABLES LIKE 'admin_users'")
        if cursor.fetchone():
            print("   ✅ Tabella admin_users presente")
            
            # Verifica utente admin
            cursor.execute("SELECT username, email FROM admin_users WHERE username = 'admin'")
            admin = cursor.fetchone()
            if admin:
                print(f"   ✅ Utente admin trovato: {admin[0]} ({admin[1]})")
            else:
                print("   ⚠️  Utente admin non trovato")
        else:
            print("   ❌ Tabella admin_users non trovata!")
            print("      Esegui: python integrate_auth.py")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Errore database: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("=" * 60)
    print("🚀 Version Management API - Controllo Pre-Avvio")
    print("=" * 60)
    
    # Esegui tutti i controlli
    checks = [
        ("Ambiente", check_environment),
        ("Moduli", check_modules),
        ("Import", check_imports),
        ("Dipendenze", check_dependencies),
        ("Database", check_database)
    ]
    
    all_passed = True
    for name, check_func in checks:
        if not check_func():
            all_passed = False
            print(f"\n❌ Controllo {name} FALLITO!")
            break
    
    if all_passed:
        print("\n" + "=" * 60)
        print("✅ Tutti i controlli passati! Avvio API...")
        print("=" * 60 + "\n")
        
        # Kill processi esistenti
        os.system("pkill -f 'python.*multi_app_api' || true")
        
        # Avvia l'API
        try:
            subprocess.run([sys.executable, "multi_app_api.py"])
        except KeyboardInterrupt:
            print("\n\n👋 API fermata dall'utente")
    else:
        print("\n⚠️  Risolvi i problemi sopra prima di avviare l'API")
        sys.exit(1)

if __name__ == "__main__":
    main()