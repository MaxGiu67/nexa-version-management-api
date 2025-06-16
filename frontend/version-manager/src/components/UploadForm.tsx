import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { Upload, File, CheckCircle, XCircle, AlertCircle, Loader } from 'lucide-react';
import { uploadAppFile, validateVersion, createChangelog } from '../services/api';
import { UploadFormData, App } from '../types';
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

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  
  label {
    font-weight: 600;
    color: #333;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .required {
    color: #e74c3c;
  }
`;

const Input = styled.input`
  padding: 0.75rem;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
  
  &:focus {
    outline: none;
    border-color: #1a237e;
  }
  
  &.error {
    border-color: #e74c3c;
  }
`;

const Select = styled.select`
  padding: 0.75rem;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  transition: border-color 0.2s;
  
  &:focus {
    outline: none;
    border-color: #1a237e;
  }
`;

// const TextArea = styled.textarea`
//   padding: 0.75rem;
//   border: 2px solid #e1e5e9;
//   border-radius: 8px;
//   font-size: 1rem;
//   min-height: 100px;
//   resize: vertical;
//   transition: border-color 0.2s;
//   
//   &:focus {
//     outline: none;
//     border-color: #1a237e;
//   }
// `;

const FileDropZone = styled.div<{ isDragging: boolean; hasFile: boolean }>`
  border: 2px dashed ${props => 
    props.hasFile ? '#28a745' : 
    props.isDragging ? '#1a237e' : '#e1e5e9'
  };
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  background: ${props => 
    props.hasFile ? '#f8fff8' : 
    props.isDragging ? '#f5f5ff' : '#fafafa'
  };
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    border-color: #1a237e;
    background: #f5f5ff;
  }
  
  .upload-icon {
    margin-bottom: 1rem;
    color: ${props => 
      props.hasFile ? '#28a745' : 
      props.isDragging ? '#1a237e' : '#666'
    };
  }
  
  .upload-text {
    color: #333;
    font-weight: 500;
    margin-bottom: 0.5rem;
  }
  
  .upload-hint {
    color: #666;
    font-size: 0.9rem;
  }
`;

const CheckboxGroup = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  input[type="checkbox"] {
    width: 18px;
    height: 18px;
  }
  
  label {
    margin: 0;
    font-weight: normal;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  ${props => props.variant === 'secondary' ? `
    background: #e1e5e9;
    color: #333;
    
    &:hover {
      background: #d1d5d9;
    }
  ` : `
    background: #1a237e;
    color: white;
    
    &:hover {
      background: #151b69;
    }
    
    &:disabled {
      background: #ccc;
      cursor: not-allowed;
    }
  `}
`;

const ChangelogList = styled.div`
  .changelog-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
    
    input {
      flex: 1;
      padding: 0.5rem;
      border: 1px solid #e1e5e9;
      border-radius: 4px;
    }
    
    button {
      padding: 0.25rem 0.5rem;
      background: #e74c3c;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      
      &:hover {
        background: #c0392b;
      }
    }
  }
  
  .add-button {
    padding: 0.5rem 1rem;
    background: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 0.5rem;
    
    &:hover {
      background: #218838;
    }
  }
`;

const Alert = styled.div<{ type: 'success' | 'error' | 'warning' }>`
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
      case 'warning':
        return 'background: #fff3cd; color: #856404; border: 1px solid #ffeaa7;';
      default:
        return '';
    }
  }}
`;

const ProgressBar = styled.div<{ $progress: number }>`
  width: 100%;
  height: 8px;
  background: #e1e5e9;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 0.5rem;
  
  .progress-fill {
    height: 100%;
    background: #1a237e;
    width: ${props => props.$progress}%;
    transition: width 0.3s ease;
  }
`;

interface Props {
  onUploadSuccess?: () => void;
  appIdentifier?: string;
  onSuccess?: () => void;
}

export const UploadForm: React.FC<Props> = ({ onUploadSuccess, appIdentifier, onSuccess }) => {
  const [formData, setFormData] = useState<Partial<UploadFormData>>({
    version: '',
    platform: 'android',
    version_code: 1,
    is_mandatory: false,
  });
  
  const [file, setFile] = useState<File | null>(null);
  const [changelogItems, setChangelogItems] = useState<string[]>(['']);
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState<{ type: 'success' | 'error' | 'warning'; message: string } | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [apps, setApps] = useState<App[]>([]);
  const [selectedApp, setSelectedApp] = useState<App | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  useEffect(() => {
    loadApps();
  }, []);
  
  useEffect(() => {
    // Se viene passato un appIdentifier, seleziona automaticamente l'app
    if (appIdentifier && apps.length > 0) {
      const app = apps.find(a => a.app_identifier === appIdentifier);
      if (app) {
        setSelectedApp(app);
      }
    }
  }, [appIdentifier, apps]);
  
  const loadApps = async () => {
    try {
      const response = await api.get('/api/v2/apps');
      setApps(response.data.apps || []);
    } catch (error) {
      console.error('Error loading apps:', error);
    }
  };

  const handleFileSelect = (selectedFile: File) => {
    // Validazione tipo file
    const isValidFile = 
      (formData.platform === 'android' && selectedFile.name.endsWith('.apk')) ||
      (formData.platform === 'ios' && selectedFile.name.endsWith('.ipa'));
    
    if (!isValidFile) {
      setAlert({
        type: 'error',
        message: `File non valido. Seleziona un file .${formData.platform === 'android' ? 'apk' : 'ipa'} per ${formData.platform === 'android' ? 'Android' : 'iOS'}.`
      });
      return;
    }
    
    // Validazione dimensione (500MB default, configurabile dal backend)
    const maxSizeMB = 500; // Railway Pro supports up to 1GB but we set a reasonable default
    if (selectedFile.size > maxSizeMB * 1024 * 1024) {
      setAlert({
        type: 'error',
        message: `File troppo grande. Dimensione massima: ${maxSizeMB}MB.`
      });
      return;
    }
    
    setFile(selectedFile);
    setAlert(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect(droppedFile);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const addChangelogItem = () => {
    setChangelogItems([...changelogItems, '']);
  };

  const removeChangelogItem = (index: number) => {
    setChangelogItems(changelogItems.filter((_, i) => i !== index));
  };

  const updateChangelogItem = (index: number, value: string) => {
    const updated = [...changelogItems];
    updated[index] = value;
    setChangelogItems(updated);
  };

  const validateForm = (): string[] => {
    const errors: string[] = [];
    
    if (!selectedApp) errors.push('Seleziona un\'applicazione');
    if (!file) errors.push('Seleziona un file');
    if (!formData.version) errors.push('Inserisci la versione');
    if (formData.version && !validateVersion(formData.version)) {
      errors.push('Versione non valida (formato: 1.2.3)');
    }
    if (!formData.version_code || formData.version_code < 1) {
      errors.push('Version code deve essere >= 1');
    }
    
    // Valida che la piattaforma sia supportata dall'app
    if (selectedApp && !selectedApp.platform_support.includes(formData.platform!)) {
      errors.push(`L'app ${selectedApp.app_name} non supporta la piattaforma ${formData.platform}`);
    }
    
    return errors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const errors = validateForm();
    if (errors.length > 0) {
      setAlert({
        type: 'error',
        message: errors.join(', ')
      });
      return;
    }
    
    if (!file) return;
    
    setLoading(true);
    setUploadProgress(0);
    setAlert(null);
    
    try {
      const uploadFormData = new FormData();
      uploadFormData.append('file', file);
      uploadFormData.append('version', formData.version!);
      uploadFormData.append('platform', formData.platform!);
      uploadFormData.append('version_code', formData.version_code!.toString());
      uploadFormData.append('is_mandatory', formData.is_mandatory!.toString());
      
      // Aggiungi app_identifier dall'app selezionata
      if (selectedApp) {
        uploadFormData.append('app_identifier', selectedApp.app_identifier);
      } else if (appIdentifier) {
        uploadFormData.append('app_identifier', appIdentifier);
      } else {
        // Default to nexa-timesheet if no app is selected
        uploadFormData.append('app_identifier', 'com.nexadata.timesheet');
      }
      
      // Crea changelog se ci sono modifiche
      const validChanges = changelogItems.filter(item => item.trim());
      if (validChanges.length > 0) {
        uploadFormData.append('changelog', createChangelog(validChanges));
      }
      
      const result = await uploadAppFile(uploadFormData, (progress) => {
        setUploadProgress(progress);
      });
      
      // Handle both v1 and v2 response formats
      const successMessage = result.message || 'Version uploaded successfully';
      const fileInfo = result.file_info;
      
      if (fileInfo) {
        // v1 format with file_info
        setAlert({
          type: 'success',
          message: `✅ ${successMessage}! File caricato: ${fileInfo.filename} (${fileInfo.size_mb} MB)`
        });
      } else {
        // v2 format without file_info
        const fileSizeMB = result.file_size ? (result.file_size / (1024 * 1024)).toFixed(2) : '';
        setAlert({
          type: 'success',
          message: `✅ ${successMessage}! Versione ${result.version} per ${result.platform} caricata${fileSizeMB ? ` (${fileSizeMB} MB)` : ''}`
        });
      }
      
      // Reset form
      setFile(null);
      setFormData({
        version: '',
        platform: 'android',
        version_code: 1,
        is_mandatory: false,
      });
      setChangelogItems(['']);
      
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
      // Small delay before resetting progress
      setTimeout(() => {
        setUploadProgress(0);
      }, 500);
      
      onUploadSuccess?.();
      onSuccess?.();
      
    } catch (error: any) {
      console.error('Upload error:', error);
      let errorMessage = 'Errore durante l\'upload';
      
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'Timeout durante l\'upload. Il file potrebbe essere troppo grande.';
      }
      
      setAlert({
        type: 'error',
        message: `Errore: ${errorMessage}`
      });
      setUploadProgress(0); // Reset progress on error
    } finally {
      setLoading(false);
    }
  };

  return (
    <UploadContainer>
      <Card>
        <Header>
          <h2>📱 Upload Nuova Versione</h2>
          <p>Carica file APK (Android) o IPA (iOS) nel database</p>
        </Header>

        {alert && (
          <Alert type={alert.type}>
            {alert.type === 'success' && <CheckCircle size={20} />}
            {alert.type === 'error' && <XCircle size={20} />}
            {alert.type === 'warning' && <AlertCircle size={20} />}
            {alert.message}
          </Alert>
        )}

        <Form onSubmit={handleSubmit}>
          {!appIdentifier && (
            <FormGroup>
              <label>
                🏢 Applicazione <span className="required">*</span>
              </label>
              <Select
                value={selectedApp?.app_identifier || ''}
                onChange={(e) => {
                  const app = apps.find(a => a.app_identifier === e.target.value);
                  setSelectedApp(app || null);
                  // Reset piattaforma se non supportata
                  if (app && !app.platform_support.includes(formData.platform!)) {
                    setFormData({ ...formData, platform: app.platform_support[0] as 'android' | 'ios' });
                    setFile(null);
                    if (fileInputRef.current) fileInputRef.current.value = '';
                  }
                }}
              >
                <option value="">-- Seleziona app --</option>
                {apps.map(app => (
                  <option key={app.app_identifier} value={app.app_identifier}>
                    {app.app_name} ({app.platform_support.join(', ')})
                  </option>
                ))}
              </Select>
            </FormGroup>
          )}

          <FormGroup>
            <label>
              📱 Piattaforma <span className="required">*</span>
            </label>
            <Select
              value={formData.platform}
              onChange={(e) => {
                setFormData({ ...formData, platform: e.target.value as 'android' | 'ios' });
                setFile(null); // Reset file quando cambia piattaforma
                if (fileInputRef.current) fileInputRef.current.value = '';
              }}
              disabled={!!(selectedApp && selectedApp.platform_support.length === 1)}
            >
              {selectedApp ? (
                selectedApp.platform_support.map((platform: string) => (
                  <option key={platform} value={platform}>
                    {platform === 'android' ? '🤖 Android (.apk)' : 
                     platform === 'ios' ? '🍎 iOS (.ipa)' : 
                     '🌐 Web'}
                  </option>
                ))
              ) : (
                <>
                  <option value="android">🤖 Android (.apk)</option>
                  <option value="ios">🍎 iOS (.ipa)</option>
                </>
              )}
            </Select>
            {selectedApp && selectedApp.platform_support.length === 1 && (
              <small style={{ color: '#666' }}>
                Questa app supporta solo {selectedApp.platform_support[0]}
              </small>
            )}
          </FormGroup>

          <FormGroup>
            <label>
              📁 File App <span className="required">*</span>
            </label>
            <FileDropZone
              isDragging={isDragging}
              hasFile={!!file}
              onClick={() => fileInputRef.current?.click()}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
            >
              {file ? <CheckCircle className="upload-icon" size={48} /> : <Upload className="upload-icon" size={48} />}
              <div className="upload-text">
                {file ? `✅ ${file.name}` : `Trascina qui il file .${formData.platform === 'android' ? 'apk' : 'ipa'} o clicca per selezionare`}
              </div>
              <div className="upload-hint">
                {file ? 
                  `${(file.size / (1024 * 1024)).toFixed(2)} MB - Clicca per cambiare` :
                  `Massimo 500MB (Railway Pro) - Solo file .${formData.platform === 'android' ? 'apk' : 'ipa'}`
                }
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept={formData.platform === 'android' ? '.apk' : '.ipa'}
                onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
                style={{ display: 'none' }}
              />
            </FileDropZone>
          </FormGroup>

          <FormGroup>
            <label>
              🏷️ Versione <span className="required">*</span>
            </label>
            <Input
              type="text"
              placeholder="1.0.0"
              value={formData.version}
              onChange={(e) => setFormData({ ...formData, version: e.target.value })}
              className={formData.version && !validateVersion(formData.version) ? 'error' : ''}
            />
            <small style={{ color: '#666' }}>Formato versione semantica: major.minor.patch (es. 1.2.3)</small>
          </FormGroup>

          <FormGroup>
            <label>
              🔢 Version Code <span className="required">*</span>
            </label>
            <Input
              type="number"
              min="1"
              placeholder="1"
              value={formData.version_code}
              onChange={(e) => setFormData({ ...formData, version_code: parseInt(e.target.value) || 1 })}
            />
            <small style={{ color: '#666' }}>Numero incrementale per confronto versioni</small>
          </FormGroup>

          <FormGroup>
            <CheckboxGroup>
              <input
                type="checkbox"
                id="mandatory"
                checked={formData.is_mandatory}
                onChange={(e) => setFormData({ ...formData, is_mandatory: e.target.checked })}
              />
              <label htmlFor="mandatory">⚠️ Aggiornamento obbligatorio</label>
            </CheckboxGroup>
            <small style={{ color: '#666' }}>Forza gli utenti ad aggiornare prima di usare l'app</small>
          </FormGroup>

          <FormGroup>
            <label>📋 Changelog (opzionale)</label>
            <ChangelogList>
              {changelogItems.map((item, index) => (
                <div key={index} className="changelog-item">
                  <input
                    type="text"
                    placeholder={`Modifica ${index + 1}...`}
                    value={item}
                    onChange={(e) => updateChangelogItem(index, e.target.value)}
                  />
                  {changelogItems.length > 1 && (
                    <button type="button" onClick={() => removeChangelogItem(index)}>
                      ✕
                    </button>
                  )}
                </div>
              ))}
              <button type="button" className="add-button" onClick={addChangelogItem}>
                + Aggiungi modifica
              </button>
            </ChangelogList>
          </FormGroup>

          {loading && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <Loader className="animate-spin" size={16} />
                Upload in corso...
              </div>
              <ProgressBar $progress={uploadProgress}>
                <div className="progress-fill" />
              </ProgressBar>
            </div>
          )}

          <ButtonGroup>
            <Button type="submit" disabled={loading || !file}>
              {loading ? (
                <>
                  <Loader className="animate-spin" size={16} />
                  Caricamento...
                </>
              ) : (
                <>
                  <Upload size={16} />
                  Carica nel Database
                </>
              )}
            </Button>
            
            <Button 
              type="button" 
              variant="secondary"
              onClick={() => {
                setFile(null);
                setFormData({
                  version: '',
                  platform: 'android',
                  version_code: 1,
                  is_mandatory: false,
                });
                setChangelogItems(['']);
                setAlert(null);
                if (fileInputRef.current) fileInputRef.current.value = '';
              }}
            >
              <XCircle size={16} />
              Reset
            </Button>
          </ButtonGroup>
        </Form>
      </Card>
    </UploadContainer>
  );
};