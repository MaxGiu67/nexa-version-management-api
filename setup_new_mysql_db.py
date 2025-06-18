#!/usr/bin/env python3
"""
Setup script per creare tutte le tabelle nel nuovo database MySQL su Railway
"""
import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

def create_all_tables():
    """Crea tutte le tabelle necessarie per il Version Management System"""
    
    print("🚀 Setup nuovo database MySQL su Railway")
    print("=" * 50)
    
    # Database configuration
    config = {
        'host': os.getenv('DB_HOST', 'tramway.proxy.rlwy.net'),
        'port': int(os.getenv('DB_PORT', '20671')),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'railway'),
        'charset': 'utf8mb4'
    }
    
    try:
        # Connect to MySQL
        print(f"\n📡 Connessione a MySQL: {config['host']}:{config['port']}")
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        print("✅ Connesso con successo!")
        
        # Read SQL file
        print("\n📄 Lettura script SQL...")
        with open('create_all_tables.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Split into individual statements
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
        
        print(f"📊 Trovati {len(statements)} comandi SQL da eseguire")
        
        # Execute each statement
        for i, statement in enumerate(statements):
            if statement and not statement.startswith('--'):
                try:
                    # Extract table name for logging
                    table_name = "Unknown"
                    if 'CREATE TABLE' in statement:
                        parts = statement.split()
                        for j, part in enumerate(parts):
                            if part.upper() == 'TABLE':
                                table_name = parts[j+3].strip('`')
                                break
                    elif 'INSERT INTO' in statement:
                        table_name = statement.split()[2].strip('`')
                    elif 'CREATE' in statement and 'VIEW' in statement:
                        table_name = statement.split()[4].strip('`')
                    
                    print(f"\n🔨 Esecuzione comando {i+1}/{len(statements)}: {table_name}")
                    cursor.execute(statement)
                    
                    if 'CREATE TABLE' in statement:
                        print(f"   ✅ Tabella '{table_name}' creata")
                    elif 'INSERT' in statement:
                        print(f"   ✅ Dati inseriti in '{table_name}'")
                    elif 'VIEW' in statement:
                        print(f"   ✅ Vista '{table_name}' creata")
                        
                except pymysql.Error as e:
                    if 'already exists' in str(e):
                        print(f"   ⚠️  {table_name} esiste già (OK)")
                    else:
                        print(f"   ❌ Errore: {e}")
        
        # Commit changes
        connection.commit()
        
        # Show created tables
        print("\n📋 Verifica tabelle create:")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"\n✨ Totale tabelle nel database: {len(tables)}")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   - {table[0]}: {count} record")
        
        # Close connection
        cursor.close()
        connection.close()
        
        print("\n🎉 Setup completato con successo!")
        print("\n📌 Prossimi passi:")
        print("1. Avvia il backend: python multi_app_api.py")
        print("2. Avvia il frontend: cd frontend/version-manager && npm start")
        print("3. Accedi a http://localhost:3000")
        
    except pymysql.Error as e:
        print(f"\n❌ Errore di connessione MySQL: {e}")
        print("\n🔍 Verifica:")
        print("1. Il database MySQL è attivo su Railway")
        print("2. Le credenziali in .env.local sono corrette")
        print("3. Il tuo IP non è bloccato da Railway")
    except FileNotFoundError:
        print("\n❌ File 'create_all_tables.sql' non trovato!")
        print("Assicurati di essere nella directory corretta")
    except Exception as e:
        print(f"\n❌ Errore inaspettato: {e}")

if __name__ == "__main__":
    create_all_tables()