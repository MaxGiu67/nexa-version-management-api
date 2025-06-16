-- Aggiorna schema database per supportare upload file

-- Aggiungi colonne per gestione file alla tabella app_versions
ALTER TABLE app_versions 
ADD COLUMN file_size BIGINT DEFAULT NULL COMMENT 'Dimensione file in bytes',
ADD COLUMN file_hash VARCHAR(64) DEFAULT NULL COMMENT 'Hash SHA256 del file',
ADD COLUMN download_count INT DEFAULT 0 COMMENT 'Numero di download';

-- Crea tabella per tracciare i download
CREATE TABLE IF NOT EXISTS app_downloads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version_id INT NOT NULL,
    user_id INT DEFAULT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    platform VARCHAR(20),
    download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_size BIGINT,
    success BOOLEAN DEFAULT true,
    
    INDEX idx_version_id (version_id),
    INDEX idx_download_date (download_date),
    INDEX idx_platform (platform),
    
    FOREIGN KEY (version_id) REFERENCES app_versions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Log download file app';

-- Aggiorna le versioni esistenti con URL fittizi per test
UPDATE app_versions 
SET download_url = CASE 
    WHEN platform = 'android' THEN CONCAT('/download/android/nexa-timesheet-v', version, '-android.apk')
    WHEN platform = 'ios' THEN CONCAT('/download/ios/nexa-timesheet-v', version, '-ios.ipa')
    ELSE NULL
END
WHERE download_url IS NULL AND platform IN ('android', 'ios');

-- Mostra struttura aggiornata
DESCRIBE app_versions;