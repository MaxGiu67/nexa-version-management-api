"""
File Storage Implementation for Large Files
Uses Railway persistent volume instead of MySQL BLOB
"""
import os
import shutil
from pathlib import Path
from typing import Optional
import hashlib
import json
from datetime import datetime

class FileStorageManager:
    def __init__(self, base_path: str = "/app/storage"):
        """
        Initialize file storage manager
        On Railway, use persistent volume mounted at /app/storage
        """
        self.base_path = Path(base_path)
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directory structure"""
        dirs = [
            self.base_path / "versions",
            self.base_path / "temp",
            self.base_path / "backups"
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_file_path(self, app_id: int, version: str, platform: str, filename: str) -> Path:
        """Generate file path for version file"""
        # Structure: /app/storage/versions/{app_id}/{platform}/{version}/{filename}
        path = self.base_path / "versions" / str(app_id) / platform / version
        path.mkdir(parents=True, exist_ok=True)
        return path / filename
    
    def save_file(self, app_id: int, version: str, platform: str, 
                  filename: str, file_content: bytes) -> dict:
        """Save file to disk and return metadata"""
        file_path = self.get_file_path(app_id, version, platform, filename)
        
        # Write file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Calculate hash
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Create metadata
        metadata = {
            "file_path": str(file_path),
            "relative_path": str(file_path.relative_to(self.base_path)),
            "size": len(file_content),
            "hash": file_hash,
            "created_at": datetime.now().isoformat()
        }
        
        # Save metadata
        metadata_path = file_path.with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata
    
    def read_file(self, relative_path: str) -> bytes:
        """Read file from storage"""
        file_path = self.base_path / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")
        
        with open(file_path, 'rb') as f:
            return f.read()
    
    def delete_file(self, relative_path: str) -> bool:
        """Delete file and its metadata"""
        file_path = self.base_path / relative_path
        metadata_path = file_path.with_suffix('.json')
        
        if file_path.exists():
            file_path.unlink()
        if metadata_path.exists():
            metadata_path.unlink()
        
        # Remove empty directories
        try:
            file_path.parent.rmdir()
            file_path.parent.parent.rmdir()
        except:
            pass  # Directory not empty
        
        return True
    
    def get_storage_stats(self) -> dict:
        """Get storage usage statistics"""
        total_size = 0
        file_count = 0
        
        for file_path in self.base_path.rglob("*"):
            if file_path.is_file() and not file_path.suffix == '.json':
                total_size += file_path.stat().st_size
                file_count += 1
        
        return {
            "total_files": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_size_gb": round(total_size / (1024 * 1024 * 1024), 2)
        }

# Initialize global storage manager
# Use local path for development, /app/storage for production
if os.environ.get('ENVIRONMENT', 'local') == 'local':
    default_path = os.path.join(os.path.dirname(__file__), 'storage')
else:
    default_path = '/app/storage'

storage_manager = FileStorageManager(
    base_path=os.environ.get('STORAGE_PATH', default_path)
)