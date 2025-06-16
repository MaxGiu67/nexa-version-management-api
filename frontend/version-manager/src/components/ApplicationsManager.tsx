import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Plus, Package, Edit, Trash2, Eye, Smartphone, Globe } from 'lucide-react';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';

const Container = styled.div`
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
`;

const Title = styled.h1`
  color: #333;
  margin: 0;
`;

const AddButton = styled.button`
  background: #1976d2;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background 0.3s;

  &:hover {
    background: #1565c0;
  }
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
`;

const AppCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }
`;

const AppHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

const AppInfo = styled.div`
  flex: 1;
`;

const AppName = styled.h2`
  color: #1976d2;
  margin: 0 0 8px 0;
  font-size: 22px;
`;

const AppIdentifier = styled.p`
  color: #666;
  margin: 0;
  font-size: 14px;
  font-family: monospace;
`;

const AppDescription = styled.p`
  color: #555;
  margin: 12px 0;
  font-size: 14px;
  line-height: 1.5;
`;

const PlatformContainer = styled.div`
  display: flex;
  gap: 8px;
  margin: 16px 0;
`;

const PlatformBadge = styled.span<{ platform: string }>`
  background: ${props => {
    switch(props.platform) {
      case 'android': return '#3DDC84';
      case 'ios': return '#007AFF';
      case 'web': return '#FF6B35';
      default: return '#666';
    }
  }};
  color: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
`;

const Stats = styled.div`
  display: flex;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
  margin-top: 16px;
`;

const Stat = styled.div`
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 24px;
  font-weight: 600;
  color: #333;
`;

const StatLabel = styled.div`
  font-size: 12px;
  color: #666;
  margin-top: 4px;
`;

const Actions = styled.div`
  display: flex;
  gap: 8px;
`;

const ActionButton = styled.button<{ variant?: 'danger' }>`
  background: ${props => props.variant === 'danger' ? '#f44336' : '#f5f5f5'};
  color: ${props => props.variant === 'danger' ? 'white' : '#666'};
  border: none;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: ${props => props.variant === 'danger' ? '#d32f2f' : '#e0e0e0'};
  }
`;

const StatusBadge = styled.span<{ active: boolean }>`
  background: ${props => props.active ? '#4CAF50' : '#f44336'};
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  margin-left: 8px;
`;

// Modal for creating/editing app
const Modal = styled.div<{ isOpen: boolean }>`
  display: ${props => props.isOpen ? 'flex' : 'none'};
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  padding: 32px;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
`;

const ModalHeader = styled.h2`
  margin: 0 0 24px 0;
  color: #333;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Label = styled.label`
  color: #555;
  font-weight: 500;
  font-size: 14px;
`;

const Input = styled.input`
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  
  &:focus {
    outline: none;
    border-color: #1976d2;
  }
`;

const TextArea = styled.textarea`
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  resize: vertical;
  min-height: 80px;
  
  &:focus {
    outline: none;
    border-color: #1976d2;
  }
`;

const CheckboxGroup = styled.div`
  display: flex;
  gap: 16px;
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  
  ${props => props.variant === 'primary' ? `
    background: #1976d2;
    color: white;
    border: none;
    
    &:hover {
      background: #1565c0;
    }
  ` : `
    background: white;
    color: #666;
    border: 1px solid #ddd;
    
    &:hover {
      background: #f5f5f5;
    }
  `}
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: #666;
`;

const EmptyIcon = styled.div`
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.3;
`;

interface App {
  id: number;
  app_identifier: string;
  app_name: string;
  description: string;
  platform_support: string[];
  is_active: boolean;
  created_at: string;
  total_versions?: number;
  active_users?: number;
}

const ApplicationsManager: React.FC = () => {
  const navigate = useNavigate();
  const [apps, setApps] = useState<App[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingApp, setEditingApp] = useState<App | null>(null);
  const [formData, setFormData] = useState({
    app_identifier: '',
    app_name: '',
    description: '',
    platform_support: ['android']
  });

  useEffect(() => {
    loadApps();
  }, []);

  const loadApps = async () => {
    try {
      const response = await api.get('/api/v2/apps');
      setApps(response.data.apps);
    } catch (error) {
      console.error('Error loading apps:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingApp) {
        // Update existing app
        await api.put(`/api/v2/apps/${editingApp.app_identifier}`, formData);
      } else {
        // Create new app
        await api.post('/api/v2/apps', formData);
      }
      setIsModalOpen(false);
      resetForm();
      loadApps();
    } catch (error) {
      console.error('Error saving app:', error);
      alert('Error saving application');
    }
  };

  const resetForm = () => {
    setFormData({
      app_identifier: '',
      app_name: '',
      description: '',
      platform_support: ['android']
    });
    setEditingApp(null);
  };

  const handleDelete = async (app: App) => {
    if (window.confirm(`Are you sure you want to delete ${app.app_name}? This will also delete all versions and related data.`)) {
      try {
        await api.delete(`/api/v2/apps/${app.app_identifier}`);
        loadApps();
      } catch (error) {
        console.error('Error deleting app:', error);
        alert('Failed to delete app. Please try again.');
      }
    }
  };

  const handleCardClick = (app: App) => {
    navigate(`/app/${app.app_identifier}`);
  };

  const handlePlatformChange = (platform: string) => {
    setFormData(prev => ({
      ...prev,
      platform_support: prev.platform_support.includes(platform)
        ? prev.platform_support.filter(p => p !== platform)
        : [...prev.platform_support, platform]
    }));
  };

  const getPlatformIcon = (platform: string) => {
    switch(platform) {
      case 'android': return '🤖';
      case 'ios': return '🍎';
      case 'web': return '🌐';
      default: return '📱';
    }
  };

  return (
    <Container>
      <Header>
        <Title>Gestione Applicazioni</Title>
        <AddButton onClick={() => setIsModalOpen(true)}>
          <Plus size={20} />
          Nuova Applicazione
        </AddButton>
      </Header>

      {loading ? (
        <EmptyState>Caricamento...</EmptyState>
      ) : apps.length === 0 ? (
        <EmptyState>
          <EmptyIcon>📱</EmptyIcon>
          <h2>Nessuna applicazione registrata</h2>
          <p>Clicca su "Nuova Applicazione" per iniziare</p>
        </EmptyState>
      ) : (
        <Grid>
          {apps.map(app => (
            <AppCard key={app.id} onClick={() => handleCardClick(app)}>
              <AppHeader>
                <AppInfo>
                  <AppName>
                    {app.app_name}
                    <StatusBadge active={app.is_active}>
                      {app.is_active ? 'Attiva' : 'Inattiva'}
                    </StatusBadge>
                  </AppName>
                  <AppIdentifier>{app.app_identifier}</AppIdentifier>
                </AppInfo>
                <Actions onClick={(e) => e.stopPropagation()}>
                  <ActionButton onClick={() => {
                    setEditingApp(app);
                    setFormData({
                      app_identifier: app.app_identifier,
                      app_name: app.app_name,
                      description: app.description || '',
                      platform_support: app.platform_support
                    });
                    setIsModalOpen(true);
                  }}>
                    <Edit size={16} />
                  </ActionButton>
                  <ActionButton variant="danger" onClick={() => handleDelete(app)}>
                    <Trash2 size={16} />
                  </ActionButton>
                </Actions>
              </AppHeader>
              
              <AppDescription>
                {app.description || 'Nessuna descrizione disponibile'}
              </AppDescription>
              
              <PlatformContainer>
                {app.platform_support.map(platform => (
                  <PlatformBadge key={platform} platform={platform}>
                    {getPlatformIcon(platform)}
                    {platform.toUpperCase()}
                  </PlatformBadge>
                ))}
              </PlatformContainer>
              
              <Stats>
                <Stat>
                  <StatValue>{app.total_versions || 0}</StatValue>
                  <StatLabel>Versioni</StatLabel>
                </Stat>
                <Stat>
                  <StatValue>{app.active_users || 0}</StatValue>
                  <StatLabel>Utenti Attivi</StatLabel>
                </Stat>
                <Stat>
                  <StatValue>
                    {new Date(app.created_at).toLocaleDateString('it-IT', { 
                      day: '2-digit',
                      month: 'short' 
                    })}
                  </StatValue>
                  <StatLabel>Creata il</StatLabel>
                </Stat>
              </Stats>
            </AppCard>
          ))}
        </Grid>
      )}

      <Modal isOpen={isModalOpen}>
        <ModalContent>
          <ModalHeader>
            {editingApp ? 'Modifica Applicazione' : 'Nuova Applicazione'}
          </ModalHeader>
          <Form onSubmit={handleSubmit}>
            <FormGroup>
              <Label>Identificativo App *</Label>
              <Input
                type="text"
                value={formData.app_identifier}
                onChange={(e) => setFormData({...formData, app_identifier: e.target.value})}
                placeholder="com.company.appname"
                required
                disabled={!!editingApp}
              />
            </FormGroup>
            
            <FormGroup>
              <Label>Nome Applicazione *</Label>
              <Input
                type="text"
                value={formData.app_name}
                onChange={(e) => setFormData({...formData, app_name: e.target.value})}
                placeholder="Nome App"
                required
              />
            </FormGroup>
            
            <FormGroup>
              <Label>Descrizione</Label>
              <TextArea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="Descrizione dell'applicazione..."
              />
            </FormGroup>
            
            <FormGroup>
              <Label>Piattaforme Supportate *</Label>
              <CheckboxGroup>
                <CheckboxLabel>
                  <input
                    type="checkbox"
                    checked={formData.platform_support.includes('android')}
                    onChange={() => handlePlatformChange('android')}
                  />
                  🤖 Android
                </CheckboxLabel>
                <CheckboxLabel>
                  <input
                    type="checkbox"
                    checked={formData.platform_support.includes('ios')}
                    onChange={() => handlePlatformChange('ios')}
                  />
                  🍎 iOS
                </CheckboxLabel>
                <CheckboxLabel>
                  <input
                    type="checkbox"
                    checked={formData.platform_support.includes('web')}
                    onChange={() => handlePlatformChange('web')}
                  />
                  🌐 Web
                </CheckboxLabel>
              </CheckboxGroup>
            </FormGroup>
            
            <ButtonGroup>
              <Button type="button" onClick={() => {
                setIsModalOpen(false);
                resetForm();
              }}>
                Annulla
              </Button>
              <Button type="submit" variant="primary">
                {editingApp ? 'Salva Modifiche' : 'Crea Applicazione'}
              </Button>
            </ButtonGroup>
          </Form>
        </ModalContent>
      </Modal>
    </Container>
  );
};

export default ApplicationsManager;