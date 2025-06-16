#!/usr/bin/env python3
"""
Script di migrazione database per sistema multi-app v2
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

def execute_migration():
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    try:
        # 1. Crea tabella apps
        print("Creating apps table...")
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
        
        # 2. Verifica se app_versions esiste già
        cursor.execute("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'railway' AND table_name = 'app_versions'
        """)
        app_versions_exists = cursor.fetchone()[0] > 0
        
        if app_versions_exists:
            print("app_versions exists, adding app_id column if missing...")
            # Aggiungi colonna app_id se non esiste
            cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_schema = 'railway' 
            AND table_name = 'app_versions' 
            AND column_name = 'app_id'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("ALTER TABLE app_versions ADD COLUMN app_id INT DEFAULT 1")
                cursor.execute("ALTER TABLE app_versions ADD FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE")
        else:
            print("Creating app_versions table...")
            cursor.execute("""
            CREATE TABLE app_versions (
              id INT AUTO_INCREMENT PRIMARY KEY,
              app_id INT NOT NULL,
              version VARCHAR(20) NOT NULL,
              platform ENUM('android', 'ios', 'web', 'all') NOT NULL,
              version_code INT NOT NULL,
              app_file LONGBLOB,
              file_name VARCHAR(255),
              file_size BIGINT,
              file_hash VARCHAR(64),
              changelog JSON,
              is_active BOOLEAN DEFAULT true,
              is_mandatory BOOLEAN DEFAULT false,
              min_supported_version VARCHAR(20),
              release_date DATETIME DEFAULT CURRENT_TIMESTAMP,
              download_count INT DEFAULT 0,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
              updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
              INDEX idx_app_platform_version (app_id, platform, version),
              INDEX idx_active_versions (app_id, is_active, version_code),
              UNIQUE KEY unique_app_platform_version (app_id, platform, version)
            )
            """)
        
        # 3. Crea tabella app_users
        print("Creating app_users table...")
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
          INDEX idx_user_uuid (user_uuid),
          INDEX idx_email (email),
          INDEX idx_device_id (device_id)
        )
        """)
        
        # 4. Crea tabella user_sessions
        print("Creating user_sessions table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
          id INT AUTO_INCREMENT PRIMARY KEY,
          user_id INT NOT NULL,
          app_id INT NOT NULL,
          session_uuid VARCHAR(36) NOT NULL UNIQUE,
          app_version VARCHAR(20),
          platform VARCHAR(20),
          device_info JSON,
          ip_address VARCHAR(45),
          start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
          end_time DATETIME,
          duration_seconds INT,
          is_active BOOLEAN DEFAULT true,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE CASCADE,
          FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
          INDEX idx_user_sessions (user_id, app_id),
          INDEX idx_session_uuid (session_uuid),
          INDEX idx_active_sessions (is_active, start_time)
        )
        """)
        
        # 5. Crea tabella app_error_logs
        print("Creating app_error_logs table...")
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
          device_info JSON,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
          FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE SET NULL,
          FOREIGN KEY (session_id) REFERENCES user_sessions(id) ON DELETE SET NULL,
          INDEX idx_app_errors (app_id, created_at),
          INDEX idx_error_severity (severity, created_at),
          INDEX idx_error_type (error_type)
        )
        """)
        
        # 6. Crea tabella update_history
        print("Creating update_history table...")
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
          metadata JSON,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE CASCADE,
          FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
          FOREIGN KEY (version_id) REFERENCES app_versions(id) ON DELETE CASCADE,
          INDEX idx_user_updates (user_id, app_id),
          INDEX idx_update_status (update_status, created_at)
        )
        """)
        
        # 7. Crea tabella app_analytics_daily
        print("Creating app_analytics_daily table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_analytics_daily (
          id INT AUTO_INCREMENT PRIMARY KEY,
          app_id INT NOT NULL,
          date DATE NOT NULL,
          active_users INT DEFAULT 0,
          new_users INT DEFAULT 0,
          sessions INT DEFAULT 0,
          avg_session_duration INT DEFAULT 0,
          errors INT DEFAULT 0,
          critical_errors INT DEFAULT 0,
          updates_started INT DEFAULT 0,
          updates_completed INT DEFAULT 0,
          updates_failed INT DEFAULT 0,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
          UNIQUE KEY unique_app_date (app_id, date),
          INDEX idx_app_date (app_id, date)
        )
        """)
        
        # 8. Inserisci app di default se non esiste
        print("Inserting default app...")
        cursor.execute("""
        INSERT IGNORE INTO apps (app_identifier, app_name, description, platform_support)
        VALUES (
            'com.nexa.timesheet',
            'Nexa Timesheet',
            'App gestione timesheet per dipendenti NEXA DATA',
            '["android", "ios"]'
        )
        """)
        
        # 9. Se esistono versioni, collegale all'app di default
        if app_versions_exists:
            print("Linking existing versions to default app...")
            cursor.execute("""
            UPDATE app_versions 
            SET app_id = (SELECT id FROM apps WHERE app_identifier = 'com.nexa.timesheet')
            WHERE app_id IS NULL OR app_id = 0 OR app_id = 1
            """)
        
        connection.commit()
        print("\n✅ Migrazione completata con successo!")
        print("📱 App di default creata: com.nexa.timesheet")
        
    except Exception as e:
        print(f"\n❌ Errore durante la migrazione: {e}")
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    print("🚀 Avvio migrazione database verso sistema multi-app v2...")
    print("=" * 50)
    execute_migration()
    print("\n🎉 Puoi ora avviare il backend con: python multi_app_api.py")