import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Upload, Download, Trash2, Package, Users, AlertCircle, TrendingUp, Calendar, FileText, Activity } from 'lucide-react';
import api from '../services/api';
import { UploadForm } from './UploadForm';
import { VersionsList } from './VersionsList';
import ErrorDashboard from './ErrorDashboard';
import SessionsDashboard from './SessionsDashboard';

const Container = styled.div`
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
`;

const Header = styled.div`
  background: white;
  padding: 24px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
`;

const BackButton = styled.button`
  background: none;
  border: none;
  color: #1976d2;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  margin-bottom: 16px;
  padding: 0;
  
  &:hover {
    text-decoration: underline;
  }
`;

const AppHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
`;

const AppInfo = styled.div``;

const AppName = styled.h1`
  color: #333;
  margin: 0 0 8px 0;
  font-size: 28px;
`;

const AppIdentifier = styled.p`
  color: #666;
  margin: 0 0 16px 0;
  font-family: monospace;
  font-size: 14px;
`;

const PlatformContainer = styled.div`
  display: flex;
  gap: 8px;
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
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
`;

const ActionButton = styled.button`
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

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
`;

const StatCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
`;

const StatIcon = styled.div<{ color: string }>`
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: ${props => props.color}20;
  color: ${props => props.color};
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
`;

const StatValue = styled.h3`
  color: #333;
  margin: 0 0 4px 0;
  font-size: 24px;
`;

const StatLabel = styled.p`
  color: #666;
  margin: 0;
  font-size: 14px;
`;

const TabContainer = styled.div`
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const TabHeader = styled.div`
  display: flex;
  border-bottom: 1px solid #e0e0e0;
`;

const Tab = styled.button<{ $active: boolean }>`
  background: none;
  border: none;
  padding: 16px 24px;
  font-size: 16px;
  cursor: pointer;
  color: ${props => props.$active ? '#1976d2' : '#666'};
  border-bottom: ${props => props.$active ? '2px solid #1976d2' : 'none'};
  margin-bottom: -1px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  
  &:hover {
    color: #1976d2;
  }
`;

const TabContent = styled.div`
  padding: 24px;
`;

const ErrorList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const ErrorItem = styled.div<{ severity: string }>`
  padding: 16px;
  border-radius: 8px;
  border: 1px solid ${props => {
    switch(props.severity) {
      case 'critical': return '#ffcdd2';
      case 'high': return '#ffe0b2';
      case 'medium': return '#fff9c4';
      default: return '#e0e0e0';
    }
  }};
  background: ${props => {
    switch(props.severity) {
      case 'critical': return '#ffebee';
      case 'high': return '#fff3e0';
      case 'medium': return '#fffde7';
      default: return '#f5f5f5';
    }
  }};
`;

const ErrorHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
`;

const ErrorType = styled.span`
  font-weight: 600;
  color: #333;
`;

const ErrorCount = styled.span`
  background: rgba(0, 0, 0, 0.1);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
`;

const ErrorDetails = styled.div`
  font-size: 14px;
  color: #666;
  display: flex;
  gap: 20px;
`;

const NoData = styled.p`
  text-align: center;
  color: #999;
  padding: 40px 0;
`;

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
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const ModalTitle = styled.h2`
  margin: 0;
  color: #333;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  
  &:hover {
    color: #333;
  }
`;

interface AppDetails {
  id: number;
  app_identifier: string;
  app_name: string;
  description?: string;
  platform_support: string[];
  is_active: boolean;
}

interface Analytics {
  user_stats: {
    total_users: number;
    daily_active_users: number;
    weekly_active_users: number;
    monthly_active_users: number;
  };
  error_stats: {
    total_errors: number;
    unresolved_errors: number;
    critical_errors: number;
  };
  version_distribution: Array<{
    current_version: string;
    platform: string;
    user_count: number;
  }>;
}

const AppDetail: React.FC = () => {
  const { appIdentifier } = useParams<{ appIdentifier: string }>();
  const navigate = useNavigate();
  const [app, setApp] = useState<AppDetails | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [errors, setErrors] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'versions' | 'analytics' | 'errors' | 'sessions'>('versions');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (appIdentifier) {
      loadAppData();
    }
  }, [appIdentifier]);

  const loadAppData = async () => {
    try {
      setLoading(true);
      
      // Load app details
      const appsResponse = await api.get('/api/v2/apps');
      const appData = appsResponse.data.apps.find((a: any) => a.app_identifier === appIdentifier);
      
      if (!appData) {
        navigate('/apps');
        return;
      }
      
      setApp(appData);
      
      // Load analytics
      const analyticsResponse = await api.get(`/api/v2/analytics/${appIdentifier}/overview`);
      setAnalytics(analyticsResponse.data);
      
      // Load errors
      const errorsResponse = await api.get(`/api/v2/analytics/${appIdentifier}/errors`);
      setErrors(errorsResponse.data.errors);
      
    } catch (error) {
      console.error('Error loading app data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number | undefined | null): string => {
    if (num === undefined || num === null) return '0';
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  if (loading || !app) {
    return (
      <Container>
        <NoData>Caricamento...</NoData>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <BackButton onClick={() => navigate('/apps')}>
          <ArrowLeft size={20} />
          Torna alle applicazioni
        </BackButton>
        
        <AppHeader>
          <AppInfo>
            <AppName>{app.app_name}</AppName>
            <AppIdentifier>{app.app_identifier}</AppIdentifier>
            <PlatformContainer>
              {app.platform_support.map(platform => (
                <PlatformBadge key={platform} platform={platform}>
                  {platform.toUpperCase()}
                </PlatformBadge>
              ))}
            </PlatformContainer>
          </AppInfo>
          
          <ActionButton onClick={() => setShowUploadModal(true)}>
            <Upload size={20} />
            Carica Nuova Versione
          </ActionButton>
        </AppHeader>
      </Header>

      {analytics && (
        <StatsGrid>
          <StatCard>
            <StatIcon color="#1976d2">
              <Users size={24} />
            </StatIcon>
            <StatValue>{formatNumber(analytics.user_stats?.total_users)}</StatValue>
            <StatLabel>Utenti Totali</StatLabel>
          </StatCard>
          
          <StatCard>
            <StatIcon color="#4CAF50">
              <TrendingUp size={24} />
            </StatIcon>
            <StatValue>{formatNumber(analytics.user_stats?.daily_active_users)}</StatValue>
            <StatLabel>Utenti Attivi Oggi</StatLabel>
          </StatCard>
          
          <StatCard>
            <StatIcon color="#f44336">
              <AlertCircle size={24} />
            </StatIcon>
            <StatValue>{formatNumber(analytics.error_stats?.unresolved_errors)}</StatValue>
            <StatLabel>Errori Non Risolti</StatLabel>
          </StatCard>
          
          <StatCard>
            <StatIcon color="#9c27b0">
              <Package size={24} />
            </StatIcon>
            <StatValue>{analytics.version_distribution?.length || 0}</StatValue>
            <StatLabel>Versioni Attive</StatLabel>
          </StatCard>
        </StatsGrid>
      )}

      <TabContainer>
        <TabHeader>
          <Tab $active={activeTab === 'versions'} onClick={() => setActiveTab('versions')}>
            <Package size={18} style={{ marginRight: '8px' }} />
            Versioni
          </Tab>
          <Tab $active={activeTab === 'analytics'} onClick={() => setActiveTab('analytics')}>
            <TrendingUp size={18} style={{ marginRight: '8px' }} />
            Analytics
          </Tab>
          <Tab $active={activeTab === 'errors'} onClick={() => setActiveTab('errors')}>
            <AlertCircle size={18} style={{ marginRight: '8px' }} />
            Errori {errors.length > 0 && `(${errors.length})`}
          </Tab>
          <Tab $active={activeTab === 'sessions'} onClick={() => setActiveTab('sessions')}>
            <Activity size={18} style={{ marginRight: '8px' }} />
            Sessioni
          </Tab>
        </TabHeader>
        
        <TabContent>
          {activeTab === 'versions' && (
            <VersionsList appIdentifier={appIdentifier!} />
          )}
          
          {activeTab === 'analytics' && analytics && (
            <div>
              <h3>Distribuzione Versioni</h3>
              {analytics.version_distribution?.map((version, index) => (
                <div key={index} style={{ padding: '12px', borderBottom: '1px solid #e0e0e0' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <strong>v{version.current_version}</strong> - {version.platform.toUpperCase()}
                    </div>
                    <div>{version.user_count} utenti</div>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {activeTab === 'errors' && (
            <ErrorDashboard appIdentifier={appIdentifier!} />
          )}

          {activeTab === 'sessions' && (
            <SessionsDashboard appIdentifier={appIdentifier!} />
          )}
        </TabContent>
      </TabContainer>

      <Modal isOpen={showUploadModal}>
        <ModalContent>
          <ModalHeader>
            <ModalTitle>Carica Nuova Versione - {app.app_name}</ModalTitle>
            <CloseButton onClick={() => setShowUploadModal(false)}>×</CloseButton>
          </ModalHeader>
          <UploadForm 
            appIdentifier={appIdentifier!}
            onSuccess={() => {
              setShowUploadModal(false);
              setActiveTab('versions');
              loadAppData();
            }}
          />
        </ModalContent>
      </Modal>
    </Container>
  );
};

export default AppDetail;