"""
Test semplice del database prima di avviare FastAPI
"""
import pymysql

def test_database():
    print("🔌 Test connessione database...")
    
    try:
        connection = pymysql.connect(
            host='tramway.proxy.rlwy.net',
            port=20671,
            user='root',
            password='aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP',
            database='railway'
        )
        
        print("✅ Connessione al database OK!")
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM app_versions")
            count = cursor.fetchone()[0]
            print(f"📊 Versioni nel database: {count}")
            
            cursor.execute("SELECT version, platform FROM app_versions ORDER BY version_code DESC LIMIT 3")
            versions = cursor.fetchall()
            print("🚀 Ultime versioni:")
            for version in versions:
                print(f"  - {version[0]} ({version[1]})")
        
        connection.close()
        print("\n✅ Test database completato!")
        return True
        
    except Exception as e:
        print(f"❌ Errore database: {e}")
        return False

if __name__ == "__main__":
    test_database()