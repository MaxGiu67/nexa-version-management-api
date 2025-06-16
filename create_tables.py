#!/usr/bin/env python3
"""
Script per creare le tabelle del database multi-app
"""
import pymysql
import os

# Configurazione database
DB_CONFIG = {
    'host': 'tramway.proxy.rlwy.net',
    'port': 20671,
    'user': 'root',
    'password': 'aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP',
    'database': 'railway'
}

def create_tables():
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    try:
        # Leggi il file SQL
        with open('database_schema_multi_app.sql', 'r') as f:
            sql_content = f.read()
        
        # Dividi in singole query (separatore ;)
        queries = [q.strip() for q in sql_content.split(';') if q.strip()]
        
        # Esegui ogni query
        for i, query in enumerate(queries):
            if query and not query.startswith('--'):
                print(f"Eseguendo query {i+1}/{len(queries)}...")
                cursor.execute(query)
        
        connection.commit()
        print("✅ Tutte le tabelle sono state create con successo!")
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    print("🔧 Creazione tabelle database multi-app...")
    create_tables()