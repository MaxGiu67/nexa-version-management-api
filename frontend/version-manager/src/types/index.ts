// Types per il sistema di gestione versioni

export interface AppVersion {
  id: number;
  version: string;
  version_code: number;
  platform: 'android' | 'ios' | 'all';
  release_date: string;
  is_mandatory: boolean;
  is_active: boolean;
  changelog?: string;
  download_url?: string;
  file_name?: string;
  file_size?: number;
  file_hash?: string;
  download_count: number;
  created_at: string;
  updated_at?: string;
}

export interface FileInfo {
  version: string;
  platform: string;
  filename: string;
  size: number;
  size_mb: number;
  hash: string;
  download_count: number;
  is_active: boolean;
  is_mandatory: boolean;
  changelog?: string;
  created_at: string;
  updated_at?: string;
  download_url: string;
}

export interface StorageInfo {
  total_files: number;
  total_size_bytes: number;
  total_size_mb: number;
  average_size_mb: number;
  max_size_mb: number;
  total_downloads: number;
  platform_breakdown: PlatformStats[];
}

export interface PlatformStats {
  platform: string;
  files: number;
  size_mb: number;
  downloads: number;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  version_id: number;
  // v1 format - with file_info
  file_info?: {
    filename: string;
    size: number;
    size_mb: number;
    hash: string;
    mime_type: string;
    download_url: string;
  };
  // v2 format - direct properties
  version?: string;
  platform?: string;
  file_size?: number;
  download_url?: string;
}

export interface CheckUpdateResponse {
  hasUpdate: boolean;
  latestVersion: string;
  versionCode: number;
  isMandatory: boolean;
  downloadUrl?: string;
  changelog: string[];
  releaseDate?: string;
  fileSize?: number;
}

export interface UploadFormData {
  file: File;
  version: string;
  platform: 'android' | 'ios';
  version_code: number;
  is_mandatory: boolean;
  changelog?: string;
}

export interface App {
  id: number;
  app_identifier: string;
  app_name: string;
  description?: string;
  platform_support: string[];
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}