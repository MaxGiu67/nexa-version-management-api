#!/usr/bin/env python3
"""
Migrazione sicura del database verso sistema multi-app v2
"""
import pymysql

# Configurazione database
DB_CONFIG = {
    'host': 'tramway.proxy.rlwy.net',
    'port': 20671,
    'user': 'root',
    'password': 'aBmAHdXPZwvBZBmDeEEmcbtJIagNMYgP',
    'database': 'railway'
}

def safe_migrate():
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    try:
        print("1. Creando tabella apps...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS apps (
          id INT AUTO_INCREMENT PRIMARY KEY,
          app_identifier VARCHAR(100) NOT NULL UNIQUE,
          app_name VARCHAR(255) NOT NULL,
          description TEXT,
          platform_support JSON,
          is_active BOOLEAN DEFAULT true,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          INDEX idx_app_identifier (app_identifier)
        )
        """)
        
        print("2. Inserendo app di default...")
        cursor.execute("""
        INSERT IGNORE INTO apps (id, app_identifier, app_name, description, platform_support)
        VALUES (
            1,
            'com.nexa.timesheet',
            'Nexa Timesheet',
            'App gestione timesheet per dipendenti NEXA DATA',
            '["android", "ios"]'
        )
        """)
        connection.commit()
        
        print("3. Verificando struttura app_versions...")
        cursor.execute("""
        SELECT COUNT(*) FROM information_schema.columns 
        WHERE table_schema = 'railway' 
        AND table_name = 'app_versions' 
        AND column_name = 'app_id'
        """)
        
        if cursor.fetchone()[0] == 0:
            print("4. Aggiungendo colonna app_id...")
            cursor.execute("ALTER TABLE app_versions ADD COLUMN app_id INT DEFAULT 1 AFTER id")
            connection.commit()
            
            print("5. Impostando app_id = 1 per tutte le versioni esistenti...")
            cursor.execute("UPDATE app_versions SET app_id = 1")
            connection.commit()
            
            print("6. Aggiungendo foreign key...")
            cursor.execute("ALTER TABLE app_versions ADD CONSTRAINT fk_app_id FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE")
            connection.commit()
        
        print("7. Creando altre tabelle necessarie...")
        
        # app_users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_users (
          id INT AUTO_INCREMENT PRIMARY KEY,
          user_uuid VARCHAR(36) NOT NULL UNIQUE,
          email VARCHAR(255),
          device_id VARCHAR(255),
          device_info JSON,
          push_token VARCHAR(500),
          first_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          last_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          INDEX idx_user_uuid (user_uuid)
        )
        """)
        
        # user_sessions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
          id INT AUTO_INCREMENT PRIMARY KEY,
          user_id INT NOT NULL,
          app_id INT NOT NULL,
          session_uuid VARCHAR(36) NOT NULL UNIQUE,
          app_version VARCHAR(20),
          platform VARCHAR(20),
          device_info JSON,
          start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
          end_time DATETIME,
          duration_seconds INT,
          is_active BOOLEAN DEFAULT true,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE CASCADE,
          FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
          INDEX idx_session_uuid (session_uuid)
        )
        """)
        
        # app_error_logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_error_logs (
          id INT AUTO_INCREMENT PRIMARY KEY,
          app_id INT NOT NULL,
          user_id INT,
          session_id INT,
          error_type VARCHAR(100),
          error_message TEXT,
          error_stack TEXT,
          metadata JSON,
          severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
          app_version VARCHAR(20),
          platform VARCHAR(20),
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
          FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE SET NULL,
          FOREIGN KEY (session_id) REFERENCES user_sessions(id) ON DELETE SET NULL,
          INDEX idx_app_errors (app_id, created_at)
        )
        """)
        
        # update_history
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS update_history (
          id INT AUTO_INCREMENT PRIMARY KEY,
          user_id INT NOT NULL,
          app_id INT NOT NULL,
          version_id INT NOT NULL,
          from_version VARCHAR(20),
          to_version VARCHAR(20),
          platform VARCHAR(20),
          update_status ENUM('started', 'downloaded', 'installed', 'failed') DEFAULT 'started',
          error_message TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE CASCADE,
          FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
          FOREIGN KEY (version_id) REFERENCES app_versions(id) ON DELETE CASCADE
        )
        """)
        
        # app_analytics_daily
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_analytics_daily (
          id INT AUTO_INCREMENT PRIMARY KEY,
          app_id INT NOT NULL,
          date DATE NOT NULL,
          active_users INT DEFAULT 0,
          new_users INT DEFAULT 0,
          sessions INT DEFAULT 0,
          errors INT DEFAULT 0,
          critical_errors INT DEFAULT 0,
          updates_started INT DEFAULT 0,
          updates_completed INT DEFAULT 0,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
          UNIQUE KEY unique_app_date (app_id, date)
        )
        """)
        
        connection.commit()
        
        print("\n✅ Migrazione completata con successo!")
        print("\n📊 Riepilogo:")
        
        # Mostra statistiche
        cursor.execute("SELECT COUNT(*) FROM apps")
        print(f"   - Apps registrate: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM app_versions WHERE app_id = 1")
        print(f"   - Versioni esistenti migrate: {cursor.fetchone()[0]}")
        
        print("\n🎉 Il sistema è pronto per l'uso!")
        
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    print("🔧 Migrazione sicura database multi-app v2...")
    print("=" * 50)
    safe_migrate()