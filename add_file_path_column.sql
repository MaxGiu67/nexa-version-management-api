-- Add file_path column to store file location instead of BLOB
ALTER TABLE app_versions 
ADD COLUMN file_path VARCHAR(500) AFTER file_hash;

-- Update existing records to indicate they use BLOB storage
UPDATE app_versions 
SET file_path = 'BLOB_STORAGE' 
WHERE app_file IS NOT NULL;

-- In future, we can migrate existing BLOBs to file storage
-- For now, we'll support both storage methods