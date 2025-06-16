-- Aggiorna schema per salvare file APK/IPA come BLOB nel database

-- Aggiungi colonna BLOB per i file
ALTER TABLE app_versions 
ADD COLUMN app_file LONGBLOB COMMENT 'File APK/IPA binario',
ADD COLUMN file_name VARCHAR(255) COMMENT 'Nome file originale',
ADD COLUMN mime_type VARCHAR(100) COMMENT 'Tipo MIME del file',
ADD COLUMN file_size BIGINT COMMENT 'Dimensione file in bytes' IF NOT EXISTS,
ADD COLUMN file_hash VARCHAR(64) COMMENT 'Hash SHA256 del file' IF NOT EXISTS,
ADD COLUMN download_count INT DEFAULT 0 COMMENT 'Numero di download' IF NOT EXISTS;

-- Aggiorna indici per performance
ALTER TABLE app_versions 
ADD INDEX idx_file_hash (file_hash),
ADD INDEX idx_file_size (file_size);

-- Mostra struttura aggiornata
DESCRIBE app_versions;