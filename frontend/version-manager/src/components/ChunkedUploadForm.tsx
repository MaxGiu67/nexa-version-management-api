import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import { Upload, Loader, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import api from '../services/api';

const UploadContainer = styled.div`
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
`;

const Card = styled.div`
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 2rem;
  
  h2 {
    color: #1a237e;
    margin-bottom: 0.5rem;
  }
  
  p {
    color: #666;
  }
`;

const FileDropZone = styled.div<{ $isDragging: boolean; $hasFile: boolean }>`
  border: 2px dashed ${props => 
    props.$hasFile ? '#28a745' : 
    props.$isDragging ? '#1a237e' : '#e1e5e9'
  };
  border-radius: 8px;
  padding: 3rem;
  text-align: center;
  background: ${props => 
    props.$hasFile ? '#f8fff8' : 
    props.$isDragging ? '#f5f5ff' : '#fafafa'
  };
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    border-color: #1a237e;
    background: #f5f5ff;
  }
`;

const ProgressContainer = styled.div`
  margin-top: 2rem;
`;

const ProgressBar = styled.div<{ $progress: number }>`
  width: 100%;
  height: 20px;
  background: #e1e5e9;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
  
  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #1a237e 0%, #2196f3 100%);
    width: ${props => props.$progress}%;
    transition: width 0.3s ease;
    position: relative;
    
    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(
        90deg,
        transparent 0%,
        rgba(255, 255, 255, 0.3) 50%,
        transparent 100%
      );
      animation: shimmer 1.5s infinite;
    }
  }
  
  @keyframes shimmer {
    0% {
      transform: translateX(-100%);
    }
    100% {
      transform: translateX(100%);
    }
  }
`;

const ProgressText = styled.div`
  text-align: center;
  margin-top: 0.5rem;
  font-size: 14px;
  color: #666;
`;

const ChunkInfo = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
  font-size: 12px;
  color: #999;
`;

const Alert = styled.div<{ type: 'success' | 'error' | 'info' }>`
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  ${props => {
    switch (props.type) {
      case 'success':
        return 'background: #d4edda; color: #155724; border: 1px solid #c3e6cb;';
      case 'error':
        return 'background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;';
      case 'info':
        return 'background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb;';
      default:
        return '';
    }
  }}
`;

interface Props {
  appIdentifier: string;
  onSuccess?: () => void;
}

export const ChunkedUploadForm: React.FC<Props> = ({ appIdentifier, onSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentChunk, setCurrentChunk] = useState(0);
  const [totalChunks, setTotalChunks] = useState(0);
  const [alert, setAlert] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    setAlert(null);
    setProgress(0);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect(droppedFile);
    }
  };

  const uploadFileChunked = async (
    file: File,
    formData: any,
    onProgress: (progress: number, chunk: number, total: number) => void
  ) => {
    const CHUNK_SIZE = 5 * 1024 * 1024; // 5MB chunks
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
    
    // Start upload session
    const startResponse = await api.post('/api/v2/version/upload-chunked/start', {
      ...formData,
      file_size: file.size,
      file_name: file.name
    }, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    
    const { upload_id } = startResponse.data;
    
    // Upload chunks
    for (let i = 0; i < totalChunks; i++) {
      const start = i * CHUNK_SIZE;
      const end = Math.min(start + CHUNK_SIZE, file.size);
      const chunk = file.slice(start, end);
      
      const chunkFormData = new FormData();
      chunkFormData.append('chunk', chunk);
      
      await api.post(`/api/v2/version/upload-chunked/${upload_id}/chunk/${i}`, chunkFormData);
      
      const progress = ((i + 1) / totalChunks) * 100;
      onProgress(progress, i + 1, totalChunks);
    }
    
    // Complete upload
    const completeResponse = await api.post(`/api/v2/version/upload-chunked/${upload_id}/complete`);
    
    return completeResponse.data;
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setUploading(true);
    setAlert(null);
    
    try {
      // Prepare form data
      const formData = {
        app_identifier: appIdentifier,
        version: '1.0.0', // You should get this from a form input
        version_code: 1, // You should get this from a form input
        platform: file.name.endsWith('.apk') ? 'android' : 'ios',
        is_mandatory: false,
        changelog: JSON.stringify(['Uploaded via chunked upload'])
      };
      
      const result = await uploadFileChunked(
        file,
        formData,
        (progress, chunk, total) => {
          setProgress(progress);
          setCurrentChunk(chunk);
          setTotalChunks(total);
        }
      );
      
      setAlert({
        type: 'success',
        message: `✅ File uploaded successfully! Version ${result.version} for ${result.platform}`
      });
      
      setFile(null);
      setProgress(0);
      setCurrentChunk(0);
      setTotalChunks(0);
      
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
      onSuccess?.();
      
    } catch (error: any) {
      console.error('Upload error:', error);
      setAlert({
        type: 'error',
        message: `Error: ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
  };

  return (
    <UploadContainer>
      <Card>
        <Header>
          <h2>📤 Chunked Upload (Large Files)</h2>
          <p>Upload APK/IPA files larger than 50MB using chunked upload</p>
        </Header>

        {alert && (
          <Alert type={alert.type}>
            {alert.type === 'success' && <CheckCircle size={20} />}
            {alert.type === 'error' && <XCircle size={20} />}
            {alert.type === 'info' && <AlertCircle size={20} />}
            {alert.message}
          </Alert>
        )}

        <FileDropZone
          $isDragging={isDragging}
          $hasFile={!!file}
          onClick={() => fileInputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
        >
          {file ? (
            <>
              <CheckCircle size={48} style={{ color: '#28a745', marginBottom: '1rem' }} />
              <h3>{file.name}</h3>
              <p>{formatFileSize(file.size)}</p>
            </>
          ) : (
            <>
              <Upload size={48} style={{ color: '#666', marginBottom: '1rem' }} />
              <h3>Drop your APK/IPA file here</h3>
              <p>or click to browse (supports files up to 500MB)</p>
            </>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept=".apk,.ipa"
            onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
            style={{ display: 'none' }}
          />
        </FileDropZone>

        {file && !uploading && (
          <button
            onClick={handleUpload}
            style={{
              marginTop: '2rem',
              padding: '1rem 2rem',
              background: '#1a237e',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              cursor: 'pointer',
              width: '100%'
            }}
          >
            Start Chunked Upload
          </button>
        )}

        {uploading && (
          <ProgressContainer>
            <ProgressBar $progress={progress}>
              <div className="progress-fill" />
            </ProgressBar>
            <ProgressText>
              {progress.toFixed(1)}% - Uploading chunk {currentChunk} of {totalChunks}
            </ProgressText>
            <ChunkInfo>
              <span>Speed: Calculating...</span>
              <span>Time remaining: Calculating...</span>
            </ChunkInfo>
          </ProgressContainer>
        )}
      </Card>
    </UploadContainer>
  );
};