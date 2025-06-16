// Servizio API per comunicazione con backend
import axios from 'axios';
import { AppVersion, FileInfo, StorageInfo, UploadResponse, CheckUpdateResponse } from '../types';

// Configurazione base API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_KEY = process.env.REACT_APP_API_KEY || 'nexa_internal_app_key_2025';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minuti per upload file grandi
  headers: {
    'X-API-Key': API_KEY
  }
});

// Interceptor per logging
api.interceptors.request.use((config) => {
  console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`API Error: ${error.response?.status} ${error.config?.url}`, error.response?.data);
    return Promise.reject(error);
  }
);

// ======================================================
// API FUNCTIONS
// ======================================================

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

// Ottieni ultima versione
export const getLatestVersion = async (platform: string = 'all'): Promise<AppVersion> => {
  const response = await api.get(`/api/v1/app-version/latest?platform=${platform}`);
  return response.data;
};

// Controlla aggiornamenti
export const checkForUpdates = async (
  currentVersion: string, 
  platform: string = 'all'
): Promise<CheckUpdateResponse> => {
  const response = await api.get(
    `/api/v1/app-version/check?current_version=${currentVersion}&platform=${platform}`
  );
  return response.data;
};

// Upload file app (v1 compatibility and v2)
export const uploadAppFile = async (
  formData: FormData, 
  onProgress?: (progress: number) => void
): Promise<UploadResponse> => {
  // Check if app_identifier is present for v2 API
  const hasAppIdentifier = formData.has('app_identifier');
  const endpoint = hasAppIdentifier ? '/api/v2/version/upload' : '/api/v1/app-version/upload';
  
  const response = await api.post(endpoint, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        console.log(`Upload progress: ${percentCompleted}%`);
        if (onProgress) {
          onProgress(percentCompleted);
        }
      }
    },
  });
  return response.data;
};

// Lista file nel database
export const listFiles = async (): Promise<{ files: FileInfo[]; total: number }> => {
  const response = await api.get('/api/v1/app-version/files');
  return response.data;
};

// Informazioni storage
export const getStorageInfo = async (): Promise<StorageInfo> => {
  const response = await api.get('/api/v1/app-version/storage-info');
  return response.data;
};

// Elimina file
export const deleteFile = async (platform: string, version: string): Promise<{ success: boolean; message: string }> => {
  const response = await api.delete(`/api/v1/app-version/files/${platform}/${version}`);
  return response.data;
};

// Download file (genera URL per download)
export const getDownloadUrl = (platform: string, version: string): string => {
  return `${API_BASE_URL}/download/${platform}/${version}`;
};

// ======================================================
// UTILITY FUNCTIONS
// ======================================================

// Formatta dimensione file
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

// Formatta data
export const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('it-IT', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Valida versione semantica
export const validateVersion = (version: string): boolean => {
  const semverRegex = /^\d+\.\d+\.\d+$/;
  return semverRegex.test(version);
};

// Confronta versioni
export const compareVersions = (version1: string, version2: string): number => {
  const v1parts = version1.split('.').map(Number);
  const v2parts = version2.split('.').map(Number);
  
  for (let i = 0; i < 3; i++) {
    if (v1parts[i] > v2parts[i]) return 1;
    if (v1parts[i] < v2parts[i]) return -1;
  }
  return 0;
};

// Parse changelog JSON
export const parseChangelog = (changelog?: string): string[] => {
  if (!changelog) return [];
  
  try {
    const parsed = JSON.parse(changelog);
    return parsed.changes || [];
  } catch {
    return [];
  }
};

// Crea changelog JSON
export const createChangelog = (changes: string[]): string => {
  return JSON.stringify({ changes });
};

// Export default per retrocompatibilità
export default api;