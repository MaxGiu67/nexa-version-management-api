-- Script completo per creare tutte le tabelle del Version Management System
-- Database: MySQL 8.0+ su Railway

-- 1. Tabella delle applicazioni
CREATE TABLE IF NOT EXISTS apps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    package_name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_apps_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Tabella delle versioni app con BLOB storage
CREATE TABLE IF NOT EXISTS app_versions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_id INT NOT NULL,
    version VARCHAR(50) NOT NULL,
    version_code INT NOT NULL,
    platform ENUM('android', 'ios') NOT NULL,
    app_file LONGBLOB,                      -- File APK/IPA (max 4GB)
    file_name VARCHAR(255),
    file_size BIGINT,
    file_hash VARCHAR(64),                  -- SHA256 hash
    changelog JSON,                         -- Changelog multi-lingua
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Tabella degli utenti delle app
CREATE TABLE IF NOT EXISTS app_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_id INT NOT NULL,
    device_id VARCHAR(255) NOT NULL,
    device_info JSON,                       -- Info dispositivo
    platform VARCHAR(20),
    app_version VARCHAR(50),
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
    UNIQUE KEY unique_app_device (app_id, device_id),
    INDEX idx_users_last_seen (last_seen),
    INDEX idx_users_platform (platform)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Tabella delle sessioni utente
CREATE TABLE IF NOT EXISTS user_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    duration_seconds INT,
    app_version VARCHAR(50),
    metadata JSON,                          -- Dati aggiuntivi sessione
    
    FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE CASCADE,
    INDEX idx_sessions_user (user_id),
    INDEX idx_sessions_start (start_time),
    INDEX idx_sessions_duration (duration_seconds)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Tabella dei log degli errori
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
    metadata JSON,                          -- Context aggiuntivo
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE SET NULL,
    INDEX idx_errors_app (app_id),
    INDEX idx_errors_severity (severity),
    INDEX idx_errors_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Tabella delle installazioni per utente
CREATE TABLE IF NOT EXISTS user_app_installations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    app_version_id INT NOT NULL,
    installed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    install_source VARCHAR(50),             -- 'update', 'fresh', 'rollback'
    previous_version VARCHAR(50),
    
    FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE CASCADE,
    FOREIGN KEY (app_version_id) REFERENCES app_versions(id) ON DELETE CASCADE,
    INDEX idx_installations_user (user_id),
    INDEX idx_installations_date (installed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Inserimento app di default (Nexa Timesheet)
INSERT INTO apps (name, package_name, description) 
VALUES (
    'nexa-timesheet', 
    'com.nexadata.timesheet',
    'Mobile app for managing employee timesheets at NEXA DATA Srl'
) ON DUPLICATE KEY UPDATE description = VALUES(description);

-- 8. Vista per statistiche versioni
CREATE OR REPLACE VIEW version_stats AS
SELECT 
    av.id,
    a.name as app_name,
    av.version,
    av.platform,
    av.version_code,
    av.is_active,
    av.is_mandatory,
    av.download_count,
    av.file_size,
    av.created_at,
    COUNT(DISTINCT uai.user_id) as unique_installs,
    COUNT(DISTINCT CASE 
        WHEN au.last_seen > DATE_SUB(NOW(), INTERVAL 30 DAY) 
        THEN au.id 
    END) as active_users_30d
FROM app_versions av
JOIN apps a ON av.app_id = a.id
LEFT JOIN user_app_installations uai ON av.id = uai.app_version_id
LEFT JOIN app_users au ON uai.user_id = au.id
GROUP BY av.id;

-- 9. Vista per utenti attivi
CREATE OR REPLACE VIEW active_users AS
SELECT 
    au.id,
    a.name as app_name,
    au.device_id,
    au.platform,
    au.app_version,
    au.last_seen,
    COUNT(DISTINCT us.id) as total_sessions,
    SUM(us.duration_seconds) as total_usage_seconds,
    MAX(us.start_time) as last_session_start
FROM app_users au
JOIN apps a ON au.app_id = a.id
LEFT JOIN user_sessions us ON au.id = us.user_id
WHERE au.last_seen > DATE_SUB(NOW(), INTERVAL 90 DAY)
GROUP BY au.id;

-- Verifica creazione tabelle
SHOW TABLES;

-- Mostra struttura delle tabelle principali
DESCRIBE app_versions;
DESCRIBE app_users;