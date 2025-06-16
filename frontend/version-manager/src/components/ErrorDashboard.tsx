import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { AlertCircle, AlertTriangle, XCircle, Info, TrendingUp, Users, Clock, RefreshCw } from 'lucide-react';
import api from '../services/api';

interface ErrorSummary {
  error_type: string;
  severity: string;
  error_count: number;
  last_occurrence: string;
  affected_users: number;
  first_version: string;
  last_version: string;
}

interface ErrorDetail {
  id: number;
  error_type: string;
  error_message: string;
  error_stack?: string;
  severity: string;
  user_id?: number;
  app_version: string;
  platform: string;
  device_info?: any;
  context?: any;
  created_at: string;
}

interface Props {
  appIdentifier: string;
}

const ErrorDashboard: React.FC<Props> = ({ appIdentifier }) => {
  const [errors, setErrors] = useState<ErrorSummary[]>([]);
  const [recentErrors, setRecentErrors] = useState<ErrorDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [timeRange, setTimeRange] = useState<number>(7); // giorni

  useEffect(() => {
    fetchErrors();
  }, [appIdentifier, selectedSeverity, timeRange]);

  const fetchErrors = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/v2/analytics/${appIdentifier}/errors`, {
        params: {
          severity: selectedSeverity !== 'all' ? selectedSeverity : undefined,
          days: timeRange
        }
      });
      setErrors(response.data.errors || []);

      // Fetch anche gli errori recenti
      const recentResponse = await api.get(`/api/v2/errors/recent/${appIdentifier}`, {
        params: { limit: 10 }
      });
      setRecentErrors(recentResponse.data.errors || []);
    } catch (error) {
      console.error('Error fetching error data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <XCircle size={20} />;
      case 'high':
        return <AlertCircle size={20} />;
      case 'medium':
        return <AlertTriangle size={20} />;
      case 'low':
        return <Info size={20} />;
      default:
        return <Info size={20} />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '#dc2626';
      case 'high':
        return '#ea580c';
      case 'medium':
        return '#f59e0b';
      case 'low':
        return '#10b981';
      default:
        return '#6b7280';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const calculateErrorStats = () => {
    const totalErrors = errors.reduce((sum, err) => sum + err.error_count, 0);
    const totalUsers = errors.reduce((sum, err) => sum + err.affected_users, 0);
    const criticalErrors = errors.filter(err => err.severity === 'critical').length;
    
    return { totalErrors, totalUsers, criticalErrors };
  };

  const stats = calculateErrorStats();

  if (loading) {
    return <LoadingContainer>Caricamento dati errori...</LoadingContainer>;
  }

  return (
    <Container>
      <Header>
        <Title>
          <AlertCircle size={24} />
          Monitoraggio Errori
        </Title>
        <Controls>
          <Select value={timeRange} onChange={(e) => setTimeRange(Number(e.target.value))}>
            <option value={1}>Ultimo giorno</option>
            <option value={7}>Ultimi 7 giorni</option>
            <option value={30}>Ultimi 30 giorni</option>
            <option value={90}>Ultimi 90 giorni</option>
          </Select>
          <Select value={selectedSeverity} onChange={(e) => setSelectedSeverity(e.target.value)}>
            <option value="all">Tutte le severità</option>
            <option value="critical">Critici</option>
            <option value="high">Alti</option>
            <option value="medium">Medi</option>
            <option value="low">Bassi</option>
          </Select>
          <RefreshButton onClick={fetchErrors}>
            <RefreshCw size={18} />
          </RefreshButton>
        </Controls>
      </Header>

      <StatsGrid>
        <StatCard>
          <StatIcon color="#dc2626">
            <TrendingUp size={24} />
          </StatIcon>
          <StatContent>
            <StatValue>{stats.totalErrors}</StatValue>
            <StatLabel>Errori Totali</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon color="#ea580c">
            <Users size={24} />
          </StatIcon>
          <StatContent>
            <StatValue>{stats.totalUsers}</StatValue>
            <StatLabel>Utenti Coinvolti</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon color="#dc2626">
            <XCircle size={24} />
          </StatIcon>
          <StatContent>
            <StatValue>{stats.criticalErrors}</StatValue>
            <StatLabel>Errori Critici</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon color="#10b981">
            <Clock size={24} />
          </StatIcon>
          <StatContent>
            <StatValue>{timeRange}d</StatValue>
            <StatLabel>Periodo Analisi</StatLabel>
          </StatContent>
        </StatCard>
      </StatsGrid>

      <Section>
        <SectionTitle>Errori per Tipo e Severità</SectionTitle>
        <ErrorGrid>
          {errors.map((error, index) => (
            <ErrorCard key={index} severity={error.severity}>
              <ErrorHeader>
                <ErrorType>
                  {getSeverityIcon(error.severity)}
                  {error.error_type}
                </ErrorType>
                <ErrorCount>{error.error_count}</ErrorCount>
              </ErrorHeader>
              <ErrorDetails>
                <DetailRow>
                  <DetailLabel>Utenti coinvolti:</DetailLabel>
                  <DetailValue>{error.affected_users}</DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Prima occorrenza:</DetailLabel>
                  <DetailValue>{error.first_version}</DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Ultima occorrenza:</DetailLabel>
                  <DetailValue>{formatDate(error.last_occurrence)}</DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Versioni:</DetailLabel>
                  <DetailValue>{error.first_version} → {error.last_version}</DetailValue>
                </DetailRow>
              </ErrorDetails>
            </ErrorCard>
          ))}
        </ErrorGrid>
      </Section>

      <Section>
        <SectionTitle>Errori Recenti</SectionTitle>
        <RecentErrorsList>
          {recentErrors.map((error) => (
            <RecentErrorItem key={error.id}>
              <ErrorInfo>
                <ErrorMeta>
                  <SeverityBadge color={getSeverityColor(error.severity)}>
                    {error.severity}
                  </SeverityBadge>
                  <ErrorPlatform>{error.platform}</ErrorPlatform>
                  <ErrorVersion>v{error.app_version}</ErrorVersion>
                  <ErrorTime>{formatDate(error.created_at)}</ErrorTime>
                </ErrorMeta>
                <ErrorMessage>{error.error_message}</ErrorMessage>
                {error.error_stack && (
                  <ErrorStack>
                    <pre>{error.error_stack.substring(0, 200)}...</pre>
                  </ErrorStack>
                )}
              </ErrorInfo>
            </RecentErrorItem>
          ))}
        </RecentErrorsList>
      </Section>
    </Container>
  );
};

const Container = styled.div`
  padding: 20px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const Title = styled.h2`
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
`;

const Controls = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
`;

const Select = styled.select`
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: #3b82f6;
  }
`;

const RefreshButton = styled.button`
  padding: 8px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: #f9fafb;
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
  color: #6b7280;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
`;

const StatCard = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
`;

const StatIcon = styled.div<{ color: string }>`
  width: 48px;
  height: 48px;
  background: ${props => props.color}20;
  color: ${props => props.color};
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const StatContent = styled.div`
  flex: 1;
`;

const StatValue = styled.div`
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
`;

const StatLabel = styled.div`
  font-size: 14px;
  color: #6b7280;
  margin-top: 4px;
`;

const Section = styled.div`
  margin-bottom: 32px;
`;

const SectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
`;

const ErrorGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
`;

const ErrorCard = styled.div<{ severity: string }>`
  background: white;
  border: 1px solid #e5e7eb;
  border-left: 4px solid ${props => getSeverityColor(props.severity)};
  border-radius: 8px;
  padding: 16px;
`;

const ErrorHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
`;

const ErrorType = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1f2937;
`;

const ErrorCount = styled.div`
  font-size: 20px;
  font-weight: 700;
  color: #dc2626;
`;

const ErrorDetails = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const DetailRow = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 14px;
`;

const DetailLabel = styled.span`
  color: #6b7280;
`;

const DetailValue = styled.span`
  color: #1f2937;
  font-weight: 500;
`;

const RecentErrorsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const RecentErrorItem = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
`;

const ErrorInfo = styled.div``;

const ErrorMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
`;

const SeverityBadge = styled.span<{ color: string }>`
  background: ${props => props.color}20;
  color: ${props => props.color};
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
`;

const ErrorPlatform = styled.span`
  color: #6b7280;
  font-size: 14px;
`;

const ErrorVersion = styled.span`
  color: #6b7280;
  font-size: 14px;
`;

const ErrorTime = styled.span`
  color: #6b7280;
  font-size: 14px;
  margin-left: auto;
`;

const ErrorMessage = styled.div`
  font-size: 14px;
  color: #1f2937;
  margin-bottom: 8px;
`;

const ErrorStack = styled.div`
  background: #f9fafb;
  padding: 8px;
  border-radius: 4px;
  overflow: hidden;

  pre {
    margin: 0;
    font-size: 12px;
    color: #6b7280;
    white-space: pre-wrap;
    word-break: break-all;
  }
`;

// Helper function per ottenere il colore della severità
function getSeverityColor(severity: string): string {
  switch (severity) {
    case 'critical':
      return '#dc2626';
    case 'high':
      return '#ea580c';
    case 'medium':
      return '#f59e0b';
    case 'low':
      return '#10b981';
    default:
      return '#6b7280';
  }
}

export default ErrorDashboard;