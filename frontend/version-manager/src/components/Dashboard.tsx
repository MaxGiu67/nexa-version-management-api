import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Activity, Download, Smartphone, Tablet, HardDrive, TrendingUp } from 'lucide-react';
import { getStorageInfo, listFiles } from '../services/api';
import { StorageInfo, FileInfo } from '../types';
import { formatFileSize, formatDate } from '../services/api';

const DashboardContainer = styled.div`
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  margin-bottom: 2rem;
  h1 {
    color: #1a237e;
    margin-bottom: 0.5rem;
  }
  p {
    color: #666;
    font-size: 1.1rem;
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const StatCard = styled.div<{ color?: string }>`
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-left: 4px solid ${props => props.color || '#1a237e'};
  
  .stat-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
    
    .icon {
      color: ${props => props.color || '#1a237e'};
    }
  }
  
  .stat-value {
    font-size: 2rem;
    font-weight: bold;
    color: #333;
    margin-bottom: 0.5rem;
  }
  
  .stat-label {
    color: #666;
    font-size: 0.9rem;
  }
  
  .stat-trend {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.5rem;
    font-size: 0.8rem;
    color: #28a745;
  }
`;

const PlatformGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const PlatformCard = styled.div<{ platform: string }>`
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  
  .platform-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
    
    .icon {
      color: ${props => props.platform === 'android' ? '#a4c639' : '#007aff'};
    }
    
    h3 {
      margin: 0;
      color: #333;
    }
  }
  
  .platform-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    
    .stat {
      text-align: center;
      
      .value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
      }
      
      .label {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.25rem;
      }
    }
  }
`;

const RecentFiles = styled.div`
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  
  h3 {
    margin-bottom: 1rem;
    color: #333;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
`;

const FileList = styled.div`
  .file-item {
    display: flex;
    align-items: center;
    justify-content: between;
    padding: 0.75rem;
    border-bottom: 1px solid #eee;
    
    &:last-child {
      border-bottom: none;
    }
    
    .file-info {
      flex: 1;
      
      .filename {
        font-weight: 500;
        color: #333;
        margin-bottom: 0.25rem;
      }
      
      .meta {
        font-size: 0.8rem;
        color: #666;
      }
    }
    
    .file-stats {
      text-align: right;
      font-size: 0.8rem;
      color: #666;
    }
  }
`;

const LoadingCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  color: #666;
`;

const ErrorCard = styled.div`
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 12px;
  padding: 1rem;
  color: #c33;
  margin-bottom: 1rem;
`;

export const Dashboard: React.FC = () => {
  const [storageInfo, setStorageInfo] = useState<StorageInfo | null>(null);
  const [recentFiles, setRecentFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [storage, files] = await Promise.all([
        getStorageInfo(),
        listFiles()
      ]);
      
      setStorageInfo(storage);
      setRecentFiles(files.files.slice(0, 5)); // Ultimi 5 file
      
    } catch (err: any) {
      setError(err.message || 'Errore durante il caricamento dati');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <DashboardContainer>
        <LoadingCard>
          <Activity className="animate-spin" size={24} />
          <p>Caricamento dashboard...</p>
        </LoadingCard>
      </DashboardContainer>
    );
  }

  if (error) {
    return (
      <DashboardContainer>
        <ErrorCard>
          <strong>Errore:</strong> {error}
          <button onClick={loadDashboardData} style={{ marginLeft: '1rem' }}>
            Riprova
          </button>
        </ErrorCard>
      </DashboardContainer>
    );
  }

  const androidStats = storageInfo?.platform_breakdown.find(p => p.platform === 'android');
  const iosStats = storageInfo?.platform_breakdown.find(p => p.platform === 'ios');

  return (
    <DashboardContainer>
      <Header>
        <h1>🗄️ Dashboard Gestione Versioni</h1>
        <p>Panoramica storage database e versioni app</p>
      </Header>

      <StatsGrid>
        <StatCard color="#1a237e">
          <div className="stat-header">
            <h4>File Totali</h4>
            <HardDrive className="icon" size={24} />
          </div>
          <div className="stat-value">{storageInfo?.total_files || 0}</div>
          <div className="stat-label">nel database</div>
          <div className="stat-trend">
            <TrendingUp size={14} />
            Storage attivo
          </div>
        </StatCard>

        <StatCard color="#28a745">
          <div className="stat-header">
            <h4>Spazio Utilizzato</h4>
            <HardDrive className="icon" size={24} />
          </div>
          <div className="stat-value">{storageInfo?.total_size_mb.toFixed(1)} MB</div>
          <div className="stat-label">dati totali</div>
          <div className="stat-trend">
            <TrendingUp size={14} />
            Avg: {storageInfo?.average_size_mb.toFixed(1)} MB
          </div>
        </StatCard>

        <StatCard color="#ff6b35">
          <div className="stat-header">
            <h4>Download Totali</h4>
            <Download className="icon" size={24} />
          </div>
          <div className="stat-value">{storageInfo?.total_downloads || 0}</div>
          <div className="stat-label">scaricamenti</div>
          <div className="stat-trend">
            <TrendingUp size={14} />
            Tutti i file
          </div>
        </StatCard>

        <StatCard color="#9c27b0">
          <div className="stat-header">
            <h4>File Massimo</h4>
            <Activity className="icon" size={24} />
          </div>
          <div className="stat-value">{storageInfo?.max_size_mb.toFixed(1)} MB</div>
          <div className="stat-label">dimensione max</div>
          <div className="stat-trend">
            <TrendingUp size={14} />
            Limite: 500 MB
          </div>
        </StatCard>
      </StatsGrid>

      <PlatformGrid>
        <PlatformCard platform="android">
          <div className="platform-header">
            <Smartphone className="icon" size={32} />
            <h3>Android</h3>
          </div>
          <div className="platform-stats">
            <div className="stat">
              <div className="value">{androidStats?.files || 0}</div>
              <div className="label">File APK</div>
            </div>
            <div className="stat">
              <div className="value">{androidStats?.size_mb.toFixed(1) || '0.0'} MB</div>
              <div className="label">Storage</div>
            </div>
            <div className="stat">
              <div className="value">{androidStats?.downloads || 0}</div>
              <div className="label">Download</div>
            </div>
            <div className="stat">
              <div className="value">
                {androidStats?.files ? (androidStats.downloads / androidStats.files).toFixed(1) : '0.0'}
              </div>
              <div className="label">Avg/File</div>
            </div>
          </div>
        </PlatformCard>

        <PlatformCard platform="ios">
          <div className="platform-header">
            <Tablet className="icon" size={32} />
            <h3>iOS</h3>
          </div>
          <div className="platform-stats">
            <div className="stat">
              <div className="value">{iosStats?.files || 0}</div>
              <div className="label">File IPA</div>
            </div>
            <div className="stat">
              <div className="value">{iosStats?.size_mb.toFixed(1) || '0.0'} MB</div>
              <div className="label">Storage</div>
            </div>
            <div className="stat">
              <div className="value">{iosStats?.downloads || 0}</div>
              <div className="label">Download</div>
            </div>
            <div className="stat">
              <div className="value">
                {iosStats?.files ? (iosStats.downloads / iosStats.files).toFixed(1) : '0.0'}
              </div>
              <div className="label">Avg/File</div>
            </div>
          </div>
        </PlatformCard>
      </PlatformGrid>

      <RecentFiles>
        <h3>
          <Activity size={20} />
          File Recenti
        </h3>
        <FileList>
          {recentFiles.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>
              Nessun file ancora caricato
            </div>
          ) : (
            recentFiles.map((file, index) => (
              <div key={index} className="file-item">
                <div className="file-info">
                  <div className="filename">{file.filename}</div>
                  <div className="meta">
                    {file.platform.toUpperCase()} v{file.version} • {formatDate(file.created_at)}
                  </div>
                </div>
                <div className="file-stats">
                  <div>{formatFileSize(file.size)}</div>
                  <div>{file.download_count} download</div>
                </div>
              </div>
            ))
          )}
        </FileList>
      </RecentFiles>
    </DashboardContainer>
  );
};