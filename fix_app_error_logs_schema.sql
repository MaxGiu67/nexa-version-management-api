-- =====================================================
-- Fix app_error_logs table schema
-- This migration aligns the table with the actual schema in production
-- =====================================================

-- First, let's check what columns exist
SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE() 
AND TABLE_NAME = 'app_error_logs'
ORDER BY ORDINAL_POSITION;

-- If the table has the wrong schema, we need to migrate it
-- Step 1: Create a new table with the correct schema
CREATE TABLE IF NOT EXISTS app_error_logs_new (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_id INT NOT NULL,
    user_id INT,
    session_id INT,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    error_stack TEXT,
    metadata JSON,  -- This replaces device_info and context
    severity ENUM('low', 'medium', 'high', 'critical') NOT NULL DEFAULT 'medium',
    app_version VARCHAR(20) NOT NULL,
    platform ENUM('android', 'ios', 'web') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE SET NULL,
    FOREIGN KEY (session_id) REFERENCES user_sessions(id) ON DELETE SET NULL,
    INDEX idx_app_errors (app_id, created_at),
    INDEX idx_error_type (error_type, severity),
    INDEX idx_severity (severity),
    INDEX idx_session_errors (session_id),
    INDEX idx_user_errors (user_id),
    INDEX idx_version_platform (app_version, platform)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Step 2: Migrate data from old table to new table (if old table exists)
-- Check if old table exists and has data
SET @old_table_exists = 0;
SELECT COUNT(*) INTO @old_table_exists 
FROM information_schema.tables 
WHERE table_schema = DATABASE() 
AND table_name = 'app_error_logs';

-- Only migrate if old table exists
SET @sql = IF(@old_table_exists > 0,
    'INSERT INTO app_error_logs_new (
        id, app_id, user_id, error_type, error_message, error_stack, 
        metadata, severity, app_version, platform, created_at
    )
    SELECT 
        id, 
        app_id, 
        user_id, 
        error_type, 
        error_message, 
        error_stack,
        JSON_OBJECT(
            "device_info", IFNULL(device_info, JSON_OBJECT()),
            "context", IFNULL(context, JSON_OBJECT())
        ) as metadata,
        severity, 
        app_version, 
        platform, 
        created_at
    FROM app_error_logs',
    'SELECT "No data to migrate" as message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Step 3: Rename tables
DROP TABLE IF EXISTS app_error_logs_old;
RENAME TABLE app_error_logs TO app_error_logs_old;
RENAME TABLE app_error_logs_new TO app_error_logs;

-- Step 4: Create a migration log
CREATE TABLE IF NOT EXISTS schema_migrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    migration_name VARCHAR(255) NOT NULL,
    executed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_migrations (migration_name) 
VALUES ('fix_app_error_logs_schema_2025_01_15');

-- Report the migration status
SELECT 
    'Migration completed' as status,
    COUNT(*) as records_migrated
FROM app_error_logs;