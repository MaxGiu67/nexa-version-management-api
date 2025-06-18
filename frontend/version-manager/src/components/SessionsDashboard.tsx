import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { Users, Clock, TrendingUp, Calendar, Activity, Smartphone, Globe, RefreshCw, User } from 'lucide-react';
import api from '../services/api';
import UsersDashboard from './UsersDashboard';

interface SessionStats {
  total_users: number;
  daily_active_users: number;
  weekly_active_users: number;
  monthly_active_users: number;
  new_users_today: number;
  avg_session_duration: number;
  total_sessions: number;
}

interface UserSession {
  id: number;
  user_id: number;
  email?: string;
  session_start: string;
  session_end?: string;
  duration_seconds?: number;
  app_version: string;
  platform: string;
  device_info?: any;
}

interface DailyStats {
  date: string;
  unique_users: number;
  total_sessions: number;
  avg_duration: number;
}

interface Props {
  appIdentifier: string;
}

const SessionsDashboard: React.FC<Props> = ({ appIdentifier }) => {
  const [stats, setStats] = useState<SessionStats | null>(null);
  const [recentSessions, setRecentSessions] = useState<UserSession[]>([]);
  const [dailyStats, setDailyStats] = useState<DailyStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<number>(7); // giorni
  const [view, setView] = useState<'overview' | 'sessions' | 'daily' | 'users'>('overview');

  useEffect(() => {
    fetchSessionData();
  }, [appIdentifier, timeRange]);

  const fetchSessionData = async () => {
    try {
      setLoading(true);
      
      // Fetch statistiche generali
      const statsResponse = await api.get(`/api/v2/analytics/${appIdentifier}/sessions`, {
        params: { days: timeRange }
      });
      setStats(statsResponse.data.stats);

      // Fetch sessioni recenti
      const sessionsResponse = await api.get(`/api/v2/sessions/recent/${appIdentifier}`, {
        params: { limit: 20 }
      });
      setRecentSessions(sessionsResponse.data.sessions || []);

      // Fetch statistiche giornaliere
      const dailyResponse = await api.get(`/api/v2/analytics/${appIdentifier}/sessions/daily`, {
        params: { days: timeRange }
      });
      setDailyStats(dailyResponse.data.daily_stats || []);

    } catch (error) {
      console.error('Error fetching session data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (seconds: number | undefined) => {
    if (!seconds) return 'N/A';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    }
    return `${secs}s`;
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

  const formatShortDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('it-IT', {
      day: '2-digit',
      month: 'short'
    });
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'android':
        return '🤖';
      case 'ios':
        return '🍎';
      case 'web':
        return '🌐';
      default:
        return '📱';
    }
  };

  const getDeviceInfo = (deviceInfo: any) => {
    if (!deviceInfo) return 'Dispositivo sconosciuto';
    return `${deviceInfo.brand || ''} ${deviceInfo.model || ''}`.trim() || 'Dispositivo sconosciuto';
  };

  if (loading) {
    return <LoadingContainer>Caricamento dati sessioni...</LoadingContainer>;
  }

  return (
    <Container>
      <Header>
        <Title>
          <Users size={24} />
          Monitoraggio Sessioni
        </Title>
        <Controls>
          <ViewTabs>
            <TabButton $active={view === 'overview'} onClick={() => setView('overview')}>
              Panoramica
            </TabButton>
            <TabButton $active={view === 'sessions'} onClick={() => setView('sessions')}>
              Sessioni Recenti
            </TabButton>
            <TabButton $active={view === 'daily'} onClick={() => setView('daily')}>
              Andamento Giornaliero
            </TabButton>
            <TabButton $active={view === 'users'} onClick={() => setView('users')}>
              Utenti
            </TabButton>
          </ViewTabs>
          <Select value={timeRange} onChange={(e) => setTimeRange(Number(e.target.value))}>
            <option value={1}>Oggi</option>
            <option value={7}>Ultimi 7 giorni</option>
            <option value={30}>Ultimi 30 giorni</option>
            <option value={90}>Ultimi 90 giorni</option>
          </Select>
          <RefreshButton onClick={fetchSessionData}>
            <RefreshCw size={18} />
          </RefreshButton>
        </Controls>
      </Header>

      {view === 'overview' && stats && (
        <>
          <StatsGrid>
            <StatCard highlight>
              <StatIcon color="#3b82f6">
                <Activity size={24} />
              </StatIcon>
              <StatContent>
                <StatValue>{stats.daily_active_users}</StatValue>
                <StatLabel>Utenti Attivi Oggi</StatLabel>
                <StatChange positive={stats.new_users_today > 0}>
                  +{stats.new_users_today} nuovi
                </StatChange>
              </StatContent>
            </StatCard>

            <StatCard>
              <StatIcon color="#10b981">
                <Calendar size={24} />
              </StatIcon>
              <StatContent>
                <StatValue>{stats.weekly_active_users}</StatValue>
                <StatLabel>Utenti Settimana</StatLabel>
              </StatContent>
            </StatCard>

            <StatCard>
              <StatIcon color="#6366f1">
                <TrendingUp size={24} />
              </StatIcon>
              <StatContent>
                <StatValue>{stats.monthly_active_users}</StatValue>
                <StatLabel>Utenti Mese</StatLabel>
              </StatContent>
            </StatCard>

            <StatCard>
              <StatIcon color="#f59e0b">
                <Clock size={24} />
              </StatIcon>
              <StatContent>
                <StatValue>{formatDuration(stats.avg_session_duration)}</StatValue>
                <StatLabel>Durata Media</StatLabel>
              </StatContent>
            </StatCard>
          </StatsGrid>

          <MetricsSection>
            <SectionTitle>Metriche Chiave</SectionTitle>
            <MetricsGrid>
              <MetricCard>
                <MetricLabel>Totale Utenti Registrati</MetricLabel>
                <MetricValue>{stats.total_users}</MetricValue>
              </MetricCard>
              <MetricCard>
                <MetricLabel>Sessioni Totali</MetricLabel>
                <MetricValue>{stats.total_sessions}</MetricValue>
              </MetricCard>
              <MetricCard>
                <MetricLabel>Retention Rate (7 giorni)</MetricLabel>
                <MetricValue>
                  {stats.total_users > 0 
                    ? `${Math.round((stats.weekly_active_users / stats.total_users) * 100)}%`
                    : 'N/A'
                  }
                </MetricValue>
              </MetricCard>
              <MetricCard>
                <MetricLabel>Sessioni per Utente</MetricLabel>
                <MetricValue>
                  {stats.total_users > 0 
                    ? (stats.total_sessions / stats.total_users).toFixed(1)
                    : 'N/A'
                  }
                </MetricValue>
              </MetricCard>
            </MetricsGrid>
          </MetricsSection>
        </>
      )}

      {view === 'sessions' && (
        <Section>
          <SectionTitle>Sessioni Recenti</SectionTitle>
          <SessionsList>
            {recentSessions.map((session) => (
              <SessionItem key={session.id}>
                <SessionHeader>
                  <UserInfo>
                    <UserEmail>{session.email || `Utente ${session.user_id}`}</UserEmail>
                    <SessionMeta>
                      <PlatformBadge>{getPlatformIcon(session.platform)} {session.platform}</PlatformBadge>
                      <VersionBadge>v{session.app_version}</VersionBadge>
                    </SessionMeta>
                  </UserInfo>
                  <SessionTiming>
                    <SessionDuration>
                      {session.duration_seconds 
                        ? formatDuration(session.duration_seconds)
                        : 'In corso...'
                      }
                    </SessionDuration>
                  </SessionTiming>
                </SessionHeader>
                <SessionDetails>
                  <DetailItem>
                    <DetailLabel>Inizio:</DetailLabel>
                    <DetailValue>{formatDate(session.session_start)}</DetailValue>
                  </DetailItem>
                  {session.session_end && (
                    <DetailItem>
                      <DetailLabel>Fine:</DetailLabel>
                      <DetailValue>{formatDate(session.session_end)}</DetailValue>
                    </DetailItem>
                  )}
                  <DetailItem>
                    <DetailLabel>Dispositivo:</DetailLabel>
                    <DetailValue>{getDeviceInfo(session.device_info)}</DetailValue>
                  </DetailItem>
                </SessionDetails>
              </SessionItem>
            ))}
          </SessionsList>
        </Section>
      )}

      {view === 'daily' && (
        <Section>
          <SectionTitle>Andamento Giornaliero</SectionTitle>
          <DailyStatsContainer>
            {dailyStats.map((day) => (
              <DailyStatCard key={day.date}>
                <DayLabel>{formatShortDate(day.date)}</DayLabel>
                <DailyMetrics>
                  <DailyMetric>
                    <DailyMetricValue>{day.unique_users}</DailyMetricValue>
                    <DailyMetricLabel>Utenti</DailyMetricLabel>
                  </DailyMetric>
                  <DailyMetric>
                    <DailyMetricValue>{day.total_sessions}</DailyMetricValue>
                    <DailyMetricLabel>Sessioni</DailyMetricLabel>
                  </DailyMetric>
                  <DailyMetric>
                    <DailyMetricValue>{formatDuration(day.avg_duration)}</DailyMetricValue>
                    <DailyMetricLabel>Durata Media</DailyMetricLabel>
                  </DailyMetric>
                </DailyMetrics>
                <ProgressBar>
                  <ProgressFill width={(day.unique_users / Math.max(...dailyStats.map(d => d.unique_users))) * 100} />
                </ProgressBar>
              </DailyStatCard>
            ))}
          </DailyStatsContainer>
        </Section>
      )}

      {view === 'users' && (
        <UsersDashboard appIdentifier={appIdentifier} />
      )}
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
  flex-wrap: wrap;
  gap: 16px;
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
  flex-wrap: wrap;
`;

const ViewTabs = styled.div`
  display: flex;
  background: #f3f4f6;
  border-radius: 8px;
  padding: 4px;
`;

const TabButton = styled.button<{ $active: boolean }>`
  padding: 8px 16px;
  background: ${props => props.$active ? 'white' : 'transparent'};
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: ${props => props.$active ? '#1f2937' : '#6b7280'};
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    color: #1f2937;
  }
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

const StatCard = styled.div<{ highlight?: boolean }>`
  background: ${props => props.highlight ? 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' : 'white'};
  border: 1px solid ${props => props.highlight ? 'transparent' : '#e5e7eb'};
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  color: ${props => props.highlight ? 'white' : '#1f2937'};
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
`;

const StatLabel = styled.div`
  font-size: 14px;
  margin-top: 4px;
  opacity: 0.9;
`;

const StatChange = styled.div<{ positive: boolean }>`
  font-size: 12px;
  margin-top: 4px;
  color: ${props => props.positive ? '#10b981' : '#ef4444'};
  font-weight: 500;
`;

const Section = styled.div`
  margin-bottom: 32px;
`;

const MetricsSection = styled.div`
  margin-bottom: 32px;
`;

const SectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
`;

const MetricCard = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
`;

const MetricLabel = styled.div`
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
`;

const MetricValue = styled.div`
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
`;

const SessionsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const SessionItem = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
`;

const SessionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
`;

const UserInfo = styled.div``;

const UserEmail = styled.div`
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
`;

const SessionMeta = styled.div`
  display: flex;
  gap: 8px;
  align-items: center;
`;

const PlatformBadge = styled.span`
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
`;

const VersionBadge = styled.span`
  background: #e0e7ff;
  color: #4f46e5;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
`;

const SessionTiming = styled.div`
  text-align: right;
`;

const SessionDuration = styled.div`
  font-size: 18px;
  font-weight: 600;
  color: #10b981;
`;

const SessionDetails = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
`;

const DetailItem = styled.div`
  display: flex;
  gap: 8px;
  font-size: 14px;
`;

const DetailLabel = styled.span`
  color: #6b7280;
`;

const DetailValue = styled.span`
  color: #1f2937;
  font-weight: 500;
`;

const DailyStatsContainer = styled.div`
  display: grid;
  gap: 16px;
`;

const DailyStatCard = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
`;

const DayLabel = styled.div`
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12px;
`;

const DailyMetrics = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 12px;
`;

const DailyMetric = styled.div`
  text-align: center;
`;

const DailyMetricValue = styled.div`
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
`;

const DailyMetricLabel = styled.div`
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
`;

const ProgressBar = styled.div`
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
`;

const ProgressFill = styled.div<{ width: number }>`
  height: 100%;
  width: ${props => props.width}%;
  background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
  transition: width 0.3s ease;
`;

export default SessionsDashboard;