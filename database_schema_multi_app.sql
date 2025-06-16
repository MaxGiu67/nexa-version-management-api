-- Schema Database Multi-App Version Management
-- Supporta multiple applicazioni, tracking utenti e error reporting

-- 1. Tabella Apps (nuova)
CREATE TABLE IF NOT EXISTS apps (
  id INT AUTO_INCREMENT PRIMARY KEY,
  app_identifier VARCHAR(100) NOT NULL UNIQUE, -- es: com.nexa.timesheet
  app_name VARCHAR(255) NOT NULL,              -- es: Nexa Timesheet
  description TEXT,
  platform_support JSON,                        -- ["android", "ios", "web"]
  is_active BOOLEAN DEFAULT true,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_app_identifier (app_identifier)
);

-- 2. Tabella App Versions (modificata)
CREATE TABLE IF NOT EXISTS app_versions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  app_id INT NOT NULL,                          -- FK to apps table
  version VARCHAR(20) NOT NULL,
  platform ENUM('android', 'ios', 'web', 'all') NOT NULL,
  version_code INT NOT NULL,
  app_file LONGBLOB,                            -- File binario APK/IPA
  file_name VARCHAR(255),
  file_size BIGINT,
  file_hash VARCHAR(64),                        -- SHA256 hash
  changelog JSON,                               -- Lista modifiche
  is_active BOOLEAN DEFAULT true,
  is_mandatory BOOLEAN DEFAULT false,
  min_supported_version VARCHAR(20),            -- Versione minima supportata
  release_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  download_count INT DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
  INDEX idx_app_platform_version (app_id, platform, version),
  INDEX idx_active_versions (app_id, is_active, version_code),
  UNIQUE KEY unique_app_platform_version (app_id, platform, version)
);

-- 3. Tabella Users (nuova)
CREATE TABLE IF NOT EXISTS app_users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_uuid VARCHAR(36) NOT NULL UNIQUE,        -- UUID generato dall'app
  email VARCHAR(255),
  device_id VARCHAR(255),
  device_info JSON,                             -- {os, model, manufacturer, etc}
  push_token VARCHAR(500),
  first_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_uuid (user_uuid),
  INDEX idx_email (email),
  INDEX idx_last_seen (last_seen_at)
);

-- 4. Tabella User App Installations (nuova)
CREATE TABLE IF NOT EXISTS user_app_installations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  app_id INT NOT NULL,
  current_version VARCHAR(20),
  current_version_code INT,
  platform VARCHAR(20),
  install_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_update_date DATETIME,
  is_active BOOLEAN DEFAULT true,
  FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE CASCADE,
  FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
  UNIQUE KEY unique_user_app (user_id, app_id),
  INDEX idx_app_version (app_id, current_version)
);

-- 5. Tabella User Sessions (nuova)
CREATE TABLE IF NOT EXISTS user_sessions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  app_id INT NOT NULL,
  session_start DATETIME NOT NULL,
  session_end DATETIME,
  duration_seconds INT,
  app_version VARCHAR(20),
  device_info JSON,
  ip_address VARCHAR(45),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE CASCADE,
  FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
  INDEX idx_user_sessions (user_id, session_start),
  INDEX idx_app_sessions (app_id, session_start),
  INDEX idx_session_dates (session_start, session_end)
);

-- 6. Tabella Error Logs (nuova)
CREATE TABLE IF NOT EXISTS app_error_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  app_id INT NOT NULL,
  user_id INT,
  error_type VARCHAR(100),                      -- crash, api_error, js_error, etc
  error_message TEXT,
  error_stack TEXT,
  app_version VARCHAR(20),
  platform VARCHAR(20),
  device_info JSON,
  context JSON,                                 -- Additional context data
  severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
  is_resolved BOOLEAN DEFAULT false,
  resolved_at DATETIME,
  resolved_by VARCHAR(255),
  error_count INT DEFAULT 1,                    -- For grouping similar errors
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE SET NULL,
  INDEX idx_app_errors (app_id, created_at),
  INDEX idx_error_type (error_type, severity),
  INDEX idx_unresolved (is_resolved, severity, created_at)
);

-- 7. Tabella Update History (nuova)
CREATE TABLE IF NOT EXISTS update_history (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  app_id INT NOT NULL,
  from_version VARCHAR(20),
  to_version VARCHAR(20),
  update_status ENUM('started', 'downloaded', 'installed', 'failed') NOT NULL,
  failure_reason TEXT,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE CASCADE,
  FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
  INDEX idx_user_updates (user_id, updated_at),
  INDEX idx_app_updates (app_id, updated_at)
);

-- 8. Tabella Analytics Summary (nuova - per dashboard)
CREATE TABLE IF NOT EXISTS app_analytics_daily (
  id INT AUTO_INCREMENT PRIMARY KEY,
  app_id INT NOT NULL,
  date DATE NOT NULL,
  active_users INT DEFAULT 0,
  new_users INT DEFAULT 0,
  sessions_count INT DEFAULT 0,
  avg_session_duration INT DEFAULT 0,
  errors_count INT DEFAULT 0,
  updates_count INT DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
  UNIQUE KEY unique_app_date (app_id, date),
  INDEX idx_date (date)
);

-- Insert sample data for Nexa Timesheet
INSERT INTO apps (app_identifier, app_name, description, platform_support) VALUES
('com.nexa.timesheet', 'Nexa Timesheet', 'Gestione timesheet per dipendenti NEXA DATA', '["android", "ios"]');

-- Views per reporting
CREATE VIEW v_app_user_stats AS
SELECT 
  a.app_name,
  COUNT(DISTINCT uai.user_id) as total_users,
  COUNT(DISTINCT CASE WHEN DATE(us.session_start) = CURDATE() THEN us.user_id END) as daily_active_users,
  COUNT(DISTINCT CASE WHEN DATE(us.session_start) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) THEN us.user_id END) as weekly_active_users,
  COUNT(DISTINCT CASE WHEN DATE(us.session_start) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) THEN us.user_id END) as monthly_active_users
FROM apps a
LEFT JOIN user_app_installations uai ON a.id = uai.app_id
LEFT JOIN user_sessions us ON a.id = us.app_id
GROUP BY a.id, a.app_name;

CREATE VIEW v_error_summary AS
SELECT 
  a.app_name,
  el.error_type,
  el.severity,
  COUNT(*) as error_count,
  MAX(el.created_at) as last_occurrence,
  COUNT(DISTINCT el.user_id) as affected_users
FROM app_error_logs el
JOIN apps a ON el.app_id = a.id
WHERE el.is_resolved = false
GROUP BY a.id, a.app_name, el.error_type, el.severity
ORDER BY el.severity DESC, error_count DESC;