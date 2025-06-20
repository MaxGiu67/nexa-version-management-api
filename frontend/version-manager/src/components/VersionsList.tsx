import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import { 
  Download, 
  Trash2, 
  Smartphone, 
  Tablet, 
  Calendar,
  CheckCircle,
  XCircle,
  Loader,
  Eye,
  Hash,
  Clock,
  FileText
} from 'lucide-react';
import { listFiles, deleteFile, getDownloadUrl, formatFileSize, formatDate, parseChangelog } from '../services/api';
import { FileInfo, App } from '../types';
import api from '../services/api';

const Container = styled.div`
  max-width: 1200px;
  margin: 2rem auto;
  padding: 2rem;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  
  h2 {
    color: #1a237e;
    margin: 0;
  }
  
  .actions {
    display: flex;
    gap: 1rem;
  }
`;

const FilterBar = styled.div`
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
  
  select {
    padding: 0.5rem;
    border: 1px solid #e1e5e9;
    border-radius: 4px;
    background: white;
  }
  
  input {
    padding: 0.5rem;
    border: 1px solid #e1e5e9;
    border-radius: 4px;
    flex: 1;
    min-width: 200px;
  }
`;

const StatsBar = styled.div`
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
  display: flex;
  gap: 2rem;
  align-items: center;
  
  .stat {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    
    .value {
      font-weight: bold;
      color: #1a237e;
    }
    
    .label {
      color: #666;
      font-size: 0.9rem;
    }
  }
`;

const VersionGrid = styled.div`
  display: grid;
  gap: 1rem;
`;

const VersionCard = styled.div<{ platform: string }>`
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  border-left: 4px solid ${props => props.platform === 'android' ? '#a4c639' : '#007aff'};
  
  .card-header {
    padding: 1rem 1.5rem;
    background: ${props => props.platform === 'android' ? '#f8fff8' : '#f0f8ff'};
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .title {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      
      .platform-icon {
        color: ${props => props.platform === 'android' ? '#a4c639' : '#007aff'};
      }
      
      .version-info {
        .version {
          font-size: 1.1rem;
          font-weight: bold;
          color: #333;
        }
        
        .platform {
          font-size: 0.9rem;
          color: #666;
          text-transform: uppercase;
        }
      }
    }
    
    .status {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      
      .active {
        color: #28a745;
      }
      
      .inactive {
        color: #dc3545;
      }
      
      .mandatory {
        background: #ff6b35;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
      }
    }
  }
  
  .card-body {
    padding: 1.5rem;
  }
  
  .card-footer {
    padding: 1rem 1.5rem;
    background: #f8f9fa;
    border-top: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
`;

const MetaGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
  
  .meta-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #666;
    font-size: 0.9rem;
    
    .icon {
      color: #1a237e;
    }
  }
`;

const ChangelogBox = styled.div`
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1rem;
  
  .changelog-title {
    font-weight: 600;
    color: #333;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .changelog-list {
    list-style: none;
    padding: 0;
    margin: 0;
    
    li {
      padding: 0.25rem 0;
      color: #555;
      
      &::before {
        content: '•';
        color: #1a237e;
        margin-right: 0.5rem;
      }
    }
  }
  
  .no-changelog {
    color: #999;
    font-style: italic;
  }
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 0.5rem;
`;

const Button = styled.button<{ $variant?: 'danger' | 'primary' | 'secondary' }>`
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  ${props => {
    switch (props.$variant) {
      case 'danger':
        return `
          background: #dc3545;
          color: white;
          &:hover { background: #c82333; }
        `;
      case 'secondary':
        return `
          background: #6c757d;
          color: white;
          &:hover { background: #5a6268; }
        `;
      default:
        return `
          background: #1a237e;
          color: white;
          &:hover { background: #151b69; }
        `;
    }
  }}
  
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
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

const EmptyState = styled.div`
  background: white;
  border-radius: 12px;
  padding: 3rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  color: #666;
  
  .icon {
    margin-bottom: 1rem;
    color: #ccc;
  }
  
  h3 {
    margin-bottom: 0.5rem;
    color: #333;
  }
`;

const Alert = styled.div<{ type: 'success' | 'error' }>`
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  ${props => props.type === 'success' ? `
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  ` : `
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  `}
`;

interface Props {
  refreshTrigger?: number;
  appIdentifier?: string;
}

export const VersionsList: React.FC<Props> = ({ refreshTrigger, appIdentifier }) => {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [filteredFiles, setFilteredFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [apps, setApps] = useState<App[]>([]);
  const [filter, setFilter] = useState({
    platform: 'all',
    search: '',
    status: 'all',
    appId: appIdentifier || 'all'
  });

  // Carica la lista delle app
  const loadApps = async () => {
    try {
      const response = await api.get('/api/v2/apps');
      setApps(response.data.apps || []);
    } catch (error) {
      console.error('Error loading apps:', error);
    }
  };

  const applyFilters = useCallback(() => {
    let filtered = [...files];

    // Filtro app
    if (filter.appId !== 'all') {
      filtered = filtered.filter(file => (file as any).app_identifier === filter.appId);
    }

    // Filtro piattaforma
    if (filter.platform !== 'all') {
      filtered = filtered.filter(file => file.platform === filter.platform);
    }

    // Filtro stato
    if (filter.status !== 'all') {
      if (filter.status === 'active') {
        filtered = filtered.filter(file => file.is_active);
      } else {
        filtered = filtered.filter(file => !file.is_active);
      }
    }

    // Filtro ricerca
    if (filter.search) {
      const searchLower = filter.search.toLowerCase();
      filtered = filtered.filter(file => 
        file.filename?.toLowerCase().includes(searchLower) ||
        file.version.toLowerCase().includes(searchLower) ||
        (file as any).app_name?.toLowerCase().includes(searchLower)
      );
    }

    setFilteredFiles(filtered);
  }, [files, filter]);

  const loadFiles = async () => {
    try {
      setLoading(true);
      // Usa il nuovo endpoint v2
      const response = await api.get('/api/v2/versions');
      const versions = response.data.versions || [];
      
      // Trasforma i dati per compatibilità con FileInfo
      const files: FileInfo[] = versions.map((v: any) => ({
        version: v.version,
        platform: v.platform,
        filename: v.file_name,
        size: v.file_size,
        size_mb: v.file_size ? v.file_size / (1024 * 1024) : 0,
        hash: v.file_hash,
        download_count: v.download_count,
        is_active: v.is_active,
        is_mandatory: v.is_mandatory,
        changelog: v.changelog,
        created_at: v.created_at,
        updated_at: v.updated_at,
        download_url: `/api/v2/download/${v.app_identifier}/${v.platform}/${v.version}`,
        app_identifier: v.app_identifier,
        app_name: v.app_name
      }));
      
      setFiles(files);
    } catch (error: any) {
      console.error('Error loading versions:', error);
      setAlert({
        type: 'error',
        message: `Errore durante il caricamento: ${error.message}`
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApps();
    loadFiles();
  }, [refreshTrigger]);

  useEffect(() => {
    applyFilters();
  }, [applyFilters]);
  
  useEffect(() => {
    if (appIdentifier) {
      setFilter(prev => ({ ...prev, appId: appIdentifier }));
    }
  }, [appIdentifier]);

  const handleDelete = async (file: FileInfo) => {
    const appIdentifier = (file as any).app_identifier;
    const appName = (file as any).app_name;
    
    if (!window.confirm(`Sei sicuro di voler eliminare ${appName || 'questa app'} ${file.platform} v${file.version}?`)) {
      return;
    }

    try {
      // Usa il nuovo endpoint per eliminare la versione specifica
      await api.delete(`/api/v2/versions/${appIdentifier}/${file.platform}/${file.version}`);
      setAlert({
        type: 'success',
        message: `Versione ${file.platform} v${file.version} eliminata con successo`
      });
      loadFiles(); // Ricarica la lista
    } catch (error: any) {
      setAlert({
        type: 'error',
        message: `Errore durante l'eliminazione: ${error.response?.data?.detail || error.message}`
      });
    }
  };

  const handleDownload = (file: FileInfo) => {
    const appIdentifier = (file as any).app_identifier;
    const url = `/api/v2/download/${appIdentifier}/${file.platform}/${file.version}`;
    const link = document.createElement('a');
    // Usa l'API base URL configurata invece di localhost
    const apiBaseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    link.href = `${apiBaseUrl}${url}`;
    link.download = file.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <Container>
        <LoadingCard>
          <Loader className="animate-spin" size={24} />
          <p>Caricamento versioni...</p>
        </LoadingCard>
      </Container>
    );
  }

  const stats = {
    total: files.length,
    android: files.filter(f => f.platform === 'android').length,
    ios: files.filter(f => f.platform === 'ios').length,
    active: files.filter(f => f.is_active).length,
    totalSize: files.reduce((sum, f) => sum + f.size_mb, 0),
    totalDownloads: files.reduce((sum, f) => sum + f.download_count, 0)
  };

  return (
    <Container>
      <Header>
        <h2>📱 Gestione Versioni</h2>
        <div className="actions">
          <Button onClick={loadFiles}>
            <Clock size={16} />
            Aggiorna
          </Button>
        </div>
      </Header>

      {alert && (
        <Alert type={alert.type}>
          {alert.type === 'success' ? <CheckCircle size={20} /> : <XCircle size={20} />}
          {alert.message}
        </Alert>
      )}

      <StatsBar>
        <div className="stat">
          <FileText className="icon" size={16} />
          <span className="value">{stats.total}</span>
          <span className="label">file totali</span>
        </div>
        <div className="stat">
          <Smartphone className="icon" size={16} />
          <span className="value">{stats.android}</span>
          <span className="label">Android</span>
        </div>
        <div className="stat">
          <Tablet className="icon" size={16} />
          <span className="value">{stats.ios}</span>
          <span className="label">iOS</span>
        </div>
        <div className="stat">
          <CheckCircle className="icon" size={16} />
          <span className="value">{stats.active}</span>
          <span className="label">attivi</span>
        </div>
        <div className="stat">
          <Download className="icon" size={16} />
          <span className="value">{stats.totalDownloads}</span>
          <span className="label">download</span>
        </div>
        <div className="stat">
          <Hash className="icon" size={16} />
          <span className="value">{stats.totalSize.toFixed(1)} MB</span>
          <span className="label">storage</span>
        </div>
      </StatsBar>

      <FilterBar>
        <label>
          Applicazione:
          <select 
            value={filter.appId} 
            onChange={(e) => setFilter({...filter, appId: e.target.value})}
          >
            <option value="all">Tutte le app</option>
            {apps.map(app => (
              <option key={app.app_identifier} value={app.app_identifier}>
                {app.app_name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Piattaforma:
          <select 
            value={filter.platform} 
            onChange={(e) => setFilter({...filter, platform: e.target.value})}
          >
            <option value="all">Tutte</option>
            <option value="android">Android</option>
            <option value="ios">iOS</option>
          </select>
        </label>

        <label>
          Stato:
          <select 
            value={filter.status} 
            onChange={(e) => setFilter({...filter, status: e.target.value})}
          >
            <option value="all">Tutti</option>
            <option value="active">Attivi</option>
            <option value="inactive">Inattivi</option>
          </select>
        </label>

        <input
          type="text"
          placeholder="Cerca per nome file, versione o app..."
          value={filter.search}
          onChange={(e) => setFilter({...filter, search: e.target.value})}
        />
      </FilterBar>

      <VersionGrid>
        {filteredFiles.length === 0 ? (
          <EmptyState>
            <FileText className="icon" size={64} />
            <h3>Nessun file trovato</h3>
            <p>Non ci sono file che corrispondono ai filtri selezionati</p>
          </EmptyState>
        ) : (
          filteredFiles.map((file, index) => {
            const changelog = parseChangelog(file.changelog);
            
            return (
              <VersionCard key={index} platform={file.platform}>
                <div className="card-header">
                  <div className="title">
                    {file.platform === 'android' ? 
                      <Smartphone className="platform-icon" size={24} /> : 
                      <Tablet className="platform-icon" size={24} />
                    }
                    <div className="version-info">
                      <div className="version">v{file.version}</div>
                      <div className="platform">{file.platform}</div>
                      {(file as any).app_name && (
                        <div className="app-name" style={{ fontSize: '0.8rem', color: '#666', marginTop: '2px' }}>
                          {(file as any).app_name}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="status">
                    {file.is_active ? 
                      <CheckCircle className="active" size={20} /> : 
                      <XCircle className="inactive" size={20} />
                    }
                    {file.is_mandatory && (
                      <span className="mandatory">OBBLIGATORIO</span>
                    )}
                  </div>
                </div>

                <div className="card-body">
                  <MetaGrid>
                    <div className="meta-item">
                      <FileText className="icon" size={16} />
                      {file.filename}
                    </div>
                    <div className="meta-item">
                      <Hash className="icon" size={16} />
                      {formatFileSize(file.size)}
                    </div>
                    <div className="meta-item">
                      <Download className="icon" size={16} />
                      {file.download_count} download
                    </div>
                    <div className="meta-item">
                      <Calendar className="icon" size={16} />
                      {formatDate(file.created_at)}
                    </div>
                  </MetaGrid>

                  {changelog.length > 0 ? (
                    <ChangelogBox>
                      <div className="changelog-title">
                        <Eye size={16} />
                        Changelog
                      </div>
                      <ul className="changelog-list">
                        {changelog.map((change, idx) => (
                          <li key={idx}>{change}</li>
                        ))}
                      </ul>
                    </ChangelogBox>
                  ) : (
                    <ChangelogBox>
                      <div className="no-changelog">Nessun changelog disponibile</div>
                    </ChangelogBox>
                  )}
                </div>

                <div className="card-footer">
                  <div style={{ fontSize: '0.8rem', color: '#666' }}>
                    Hash: {file.hash?.substring(0, 16)}...
                  </div>
                  <ActionButtons>
                    <Button 
                      onClick={() => handleDownload(file)}
                    >
                      <Download size={16} />
                      Download
                    </Button>
                    <Button 
                      $variant="danger"
                      onClick={() => handleDelete(file)}
                    >
                      <Trash2 size={16} />
                      Elimina
                    </Button>
                  </ActionButtons>
                </div>
              </VersionCard>
            );
          })
        )}
      </VersionGrid>
    </Container>
  );
};