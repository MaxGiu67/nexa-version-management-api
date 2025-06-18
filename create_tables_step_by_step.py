#!/usr/bin/env python3
"""
Create tables one by one with better error handling
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

def execute_sql(cursor, sql, description):
    """Execute a single SQL statement with error handling"""
    try:
        cursor.execute(sql)
        print(f"✅ {description}")
        return True
    except pymysql.Error as e:
        if 'already exists' in str(e):
            print(f"⚠️  {description} - già esistente")
            return True
        else:
            print(f"❌ {description} - Errore: {e}")
            return False

def create_tables():
    """Create all tables step by step"""
    
    print("🚀 Creazione tabelle MySQL")
    print("=" * 50)
    
    try:
        # Connect
        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        print("✅ Connesso al database\n")
        
        # 1. Create apps table
        execute_sql(cursor, """
            CREATE TABLE IF NOT EXISTS apps (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                package_name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_apps_name (name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """, "Tabella 'apps' creata")
        
        # 2. Create app_versions table
        execute_sql(cursor, """
            CREATE TABLE IF NOT EXISTS app_versions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                app_id INT NOT NULL,
                version VARCHAR(50) NOT NULL,
                version_code INT NOT NULL,
                platform ENUM('android', 'ios') NOT NULL,
                app_file LONGBLOB,
                file_name VARCHAR(255),
                file_size BIGINT,
                file_hash VARCHAR(64),
                changelog JSON,
                is_active BOOLEAN DEFAULT true,
                is_mandatory BOOLEAN DEFAULT false,
                download_count INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
                UNIQUE KEY unique_app_platform_version (app_id, platform, version),
                INDEX idx_app_versions_active (is_active, version_code),
                INDEX idx_app_versions_platform (app_id, platform),
                INDEX idx_app_versions_created (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """, "Tabella 'app_versions' creata")
        
        # 3. Create app_users table
        execute_sql(cursor, """
            CREATE TABLE IF NOT EXISTS app_users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                app_id INT NOT NULL,
                device_id VARCHAR(255) NOT NULL,
                device_info JSON,
                platform VARCHAR(20),
                app_version VARCHAR(50),
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
                UNIQUE KEY unique_app_device (app_id, device_id),
                INDEX idx_users_last_seen (last_seen),
                INDEX idx_users_platform (platform)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """, "Tabella 'app_users' creata")
        
        # 4. Create user_sessions table
        execute_sql(cursor, """
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME,
                duration_seconds INT,
                app_version VARCHAR(50),
                metadata JSON,
                
                FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE CASCADE,
                INDEX idx_sessions_user (user_id),
                INDEX idx_sessions_start (start_time),
                INDEX idx_sessions_duration (duration_seconds)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """, "Tabella 'user_sessions' creata")
        
        # 5. Create app_error_logs table
        execute_sql(cursor, """
            CREATE TABLE IF NOT EXISTS app_error_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                app_id INT NOT NULL,
                user_id INT,
                error_type VARCHAR(100),
                error_message TEXT,
                stack_trace TEXT,
                app_version VARCHAR(50),
                platform VARCHAR(20),
                severity ENUM('debug', 'info', 'warning', 'error', 'critical') DEFAULT 'error',
                metadata JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE SET NULL,
                INDEX idx_errors_app (app_id),
                INDEX idx_errors_severity (severity),
                INDEX idx_errors_created (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """, "Tabella 'app_error_logs' creata")
        
        # 6. Create user_app_installations table
        execute_sql(cursor, """
            CREATE TABLE IF NOT EXISTS user_app_installations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                app_version_id INT NOT NULL,
                installed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                install_source VARCHAR(50),
                previous_version VARCHAR(50),
                
                FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE CASCADE,
                FOREIGN KEY (app_version_id) REFERENCES app_versions(id) ON DELETE CASCADE,
                INDEX idx_installations_user (user_id),
                INDEX idx_installations_date (installed_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """, "Tabella 'user_app_installations' creata")
        
        # Commit all changes
        connection.commit()
        
        # Insert default app
        execute_sql(cursor, """
            INSERT INTO apps (name, package_name, description) 
            VALUES (
                'nexa-timesheet', 
                'com.nexadata.timesheet',
                'Mobile app for managing employee timesheets at NEXA DATA Srl'
            ) ON DUPLICATE KEY UPDATE description = VALUES(description)
        """, "App 'nexa-timesheet' inserita")
        
        connection.commit()
        
        # Show final status
        print("\n📋 Tabelle create:")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   - {table[0]}: {count} record")
        
        cursor.close()
        connection.close()
        
        print("\n✅ Setup completato!")
        print("\n🚀 Ora puoi avviare:")
        print("1. Backend: python multi_app_api.py")
        print("2. Frontend: cd frontend/version-manager && npm start")
        
    except Exception as e:
        print(f"\n❌ Errore: {e}")

if __name__ == "__main__":
    create_tables()