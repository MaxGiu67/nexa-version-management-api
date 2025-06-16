-- Migration script to upgrade from v1 to v2 (Multi-App Support)
-- IMPORTANTE: Fare backup del database prima di eseguire!

-- 1. Create apps table
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
);

-- 2. Insert Nexa Timesheet as the first app
INSERT INTO apps (app_identifier, app_name, description, platform_support) 
VALUES ('com.nexa.timesheet', 'Nexa Timesheet', 'Gestione timesheet per dipendenti NEXA DATA', '["android", "ios"]');

-- 3. Add app_id column to app_versions table
ALTER TABLE app_versions 
ADD COLUMN app_id INT AFTER id,
ADD FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE;

-- 4. Update existing records to use Nexa Timesheet app_id
UPDATE app_versions 
SET app_id = (SELECT id FROM apps WHERE app_identifier = 'com.nexa.timesheet')
WHERE app_id IS NULL;

-- 5. Make app_id NOT NULL after migration
ALTER TABLE app_versions 
MODIFY COLUMN app_id INT NOT NULL;

-- 6. Update unique constraint to include app_id
ALTER TABLE app_versions 
DROP KEY unique_platform_version,
ADD UNIQUE KEY unique_app_platform_version (app_id, platform, version);

-- 7. Create new user tracking tables
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
  INDEX idx_user_uuid (user_uuid),
  INDEX idx_email (email),
  INDEX idx_last_seen (last_seen_at)
);

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

-- 8. Create error tracking tables
CREATE TABLE IF NOT EXISTS app_error_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  app_id INT NOT NULL,
  user_id INT,
  error_type VARCHAR(100),
  error_message TEXT,
  error_stack TEXT,
  app_version VARCHAR(20),
  platform VARCHAR(20),
  device_info JSON,
  context JSON,
  severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
  is_resolved BOOLEAN DEFAULT false,
  resolved_at DATETIME,
  resolved_by VARCHAR(255),
  error_count INT DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE SET NULL,
  INDEX idx_app_errors (app_id, created_at),
  INDEX idx_error_type (error_type, severity),
  INDEX idx_unresolved (is_resolved, severity, created_at)
);

-- 9. Create update history table
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

-- 10. Create analytics summary table
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

-- 11. Create views for reporting
CREATE OR REPLACE VIEW v_app_user_stats AS
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

CREATE OR REPLACE VIEW v_error_summary AS
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

-- Migration completed
SELECT 'Migration to Multi-App Support v2.0 completed successfully!' as status;