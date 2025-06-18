#!/usr/bin/env python3
"""
Recreate all tables with correct structure for multi_app_api.py
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

def recreate_tables():
    """Recreate all tables with correct structure"""
    
    print("🔄 Recreating all tables with correct structure...")
    
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        
        # Drop all tables in correct order
        print("🗑️  Dropping existing tables...")
        tables_to_drop = [
            'user_app_installations',
            'app_error_logs', 
            'user_sessions',
            'app_users',
            'app_versions',
            'apps'
        ]
        
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"   ✅ Dropped {table}")
            except:
                pass
        
        # Create apps table with correct structure
        print("\n🔨 Creating apps table...")
        cursor.execute("""
            CREATE TABLE apps (
                id INT AUTO_INCREMENT PRIMARY KEY,
                app_identifier VARCHAR(100) UNIQUE NOT NULL,
                app_name VARCHAR(255) NOT NULL,
                description TEXT,
                platform_support JSON,
                is_active BOOLEAN DEFAULT true,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_apps_identifier (app_identifier)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Create app_versions table
        print("🔨 Creating app_versions table...")
        cursor.execute("""
            CREATE TABLE app_versions (
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
                INDEX idx_app_versions_platform (app_id, platform)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Create app_users table
        print("🔨 Creating app_users table...")
        cursor.execute("""
            CREATE TABLE app_users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                app_id INT NOT NULL,
                device_id VARCHAR(255) NOT NULL,
                device_info JSON,
                platform VARCHAR(20),
                app_version VARCHAR(50),
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
                UNIQUE KEY unique_app_device (app_id, device_id),
                INDEX idx_users_last_seen (last_seen),
                INDEX idx_users_platform (platform)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Create user_sessions table
        print("🔨 Creating user_sessions table...")
        cursor.execute("""
            CREATE TABLE user_sessions (
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
                INDEX idx_sessions_start (start_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Create app_error_logs table
        print("🔨 Creating app_error_logs table...")
        cursor.execute("""
            CREATE TABLE app_error_logs (
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
        """)
        
        # Create user_app_installations table
        print("🔨 Creating user_app_installations table...")
        cursor.execute("""
            CREATE TABLE user_app_installations (
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
        """)
        
        connection.commit()
        
        # Insert default app
        print("\n📝 Inserting nexa-timesheet app...")
        cursor.execute("""
            INSERT INTO apps (app_identifier, app_name, description, platform_support) 
            VALUES (
                'nexa-timesheet',
                'Nexa Timesheet',
                'Mobile app for managing employee timesheets at NEXA DATA Srl',
                '["android", "ios"]'
            )
        """)
        
        connection.commit()
        
        # Show final status
        print("\n📋 Tables created:")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   - {table[0]}: {count} record")
        
        cursor.close()
        connection.close()
        
        print("\n✅ All tables recreated successfully!")
        print("\n🚀 Now you can start:")
        print("1. Backend: python multi_app_api.py")
        print("2. Frontend: cd frontend/version-manager && npm start")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    recreate_tables()