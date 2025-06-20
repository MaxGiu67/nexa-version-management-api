import pymysql

# Test nuove credenziali Railway
try:
    connection = pymysql.connect(
        host='centerbeam.proxy.rlwy.net',
        port=22032,
        user='root',
        password='drypjZgjDSozOUrrJJsyUtNGqkDPVsEd',
        database='railway'
    )
    print("✅ Connessione MySQL riuscita!")
    
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n📊 Tabelle trovate: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
    
    connection.close()
    
except Exception as e:
    print(f"❌ Errore connessione: {e}")