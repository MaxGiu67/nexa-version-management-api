import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Package, Users, AlertCircle, Download, TrendingUp, Activity, Smartphone, Globe, Database, Clock, User, Mail, Calendar } from 'lucide-react';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';

const Container = styled.div`
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
`;

const Header = styled.div`
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
`;

const Title = styled.h1`
  color: #333;
  margin: 0 0 10px 0;
  font-size: 32px;
`;

const Subtitle = styled.p`
  color: #666;
  margin: 0;
  font-size: 16px;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const StatCard = styled.div`
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
`;

const StatInfo = styled.div`
  flex: 1;
`;

const StatLabel = styled.p`
  color: #666;
  margin: 0 0 5px 0;
  font-size: 14px;
`;

const StatValue = styled.h2`
  color: #333;
  margin: 0;
  font-size: 28px;
`;

const IconWrapper = styled.div<{ color?: string; iconColor?: string }>`
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${props => props.color || '#e3f2fd'};
  color: ${props => props.iconColor || '#1976d2'};
`;

const Section = styled.div`
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
`;

const SectionTitle = styled.h2`
  color: #333;
  margin: 0 0 20px 0;
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const AppGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
`;

const AppCard = styled.div`
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: #f5f5f5;
    border-color: #1976d2;
  }
`;

const AppHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
`;

const AppName = styled.h3`
  color: #1976d2;
  margin: 0;
  font-size: 18px;
`;

const AppStats = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e0e0e0;
`;

const AppStat = styled.div`
  text-align: center;
`;

const AppStatValue = styled.div`
  font-weight: 600;
  color: #333;
`;

const AppStatLabel = styled.div`
  font-size: 12px;
  color: #666;
  margin-top: 2px;
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
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  margin-right: 4px;
`;

const ErrorsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
`;

const ErrorCard = styled.div<{ severity: string }>`
  padding: 15px;
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

const ErrorApp = styled.div`
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
`;

const ErrorCount = styled.div`
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
`;

const ErrorType = styled.div`
  font-size: 12px;
  color: #666;
`;

const NoData = styled.p`
  text-align: center;
  color: #999;
  padding: 40px 0;
`;

const SessionsGrid = styled.div`
  display: grid;
  gap: 15px;
`;

const SessionCard = styled.div`
  padding: 15px;
  border-radius: 8px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const SessionInfo = styled.div`
  flex: 1;
`;

const SessionApp = styled.div`
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
`;

const SessionUser = styled.div`
  font-size: 14px;
  color: #666;
`;

const SessionTime = styled.div`
  text-align: right;
  font-size: 14px;
  color: #666;
`;

const SessionDuration = styled.div`
  font-size: 16px;
  font-weight: 600;
  color: #10b981;
  margin-bottom: 4px;
`;

const UsersGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 15px;
`;

const UserCard = styled.div`
  padding: 20px;
  border-radius: 8px;
  background: white;
  border: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  gap: 15px;
  transition: all 0.2s;
  
  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transform: translateY(-1px);
  }
`;

const UserAvatar = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #e3f2fd;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1976d2;
  font-weight: 600;
  font-size: 20px;
`;

const UserInfo = styled.div`
  flex: 1;
`;

const UserEmail = styled.div`
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
`;

const UserMeta = styled.div`
  font-size: 13px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const UserApps = styled.div`
  display: flex;
  gap: 4px;
  align-items: center;
  flex-wrap: wrap;
`;

const UserAppBadge = styled.span`
  background: #f5f5f5;
  color: #666;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  white-space: nowrap;
`;

interface AppSummary {
  id: number;
  app_identifier: string;
  app_name: string;
  platform_support: string[];
  total_users?: number;
  active_users?: number;
  total_versions?: number;
  latest_version?: string;
  error_count?: number;
}

interface SystemStats {
  total_apps: number;
  total_users: number;
  total_errors: number;
  active_users_today: number;
  total_versions: number;
  total_downloads: number;
}

interface ErrorSummary {
  app_name: string;
  app_identifier: string;
  severity: string;
  count: number;
  error_type: string;
}

interface RecentSession {
  id: number;
  app_name: string;
  app_identifier: string;
  user_email?: string;
  session_start: string;
  session_end?: string;
  duration_seconds?: number;
  platform: string;
}

interface AppUser {
  id: number;
  user_uuid: string;
  email?: string;
  first_seen_at: string;
  last_seen_at: string;
  total_sessions: number;
  apps: Array<{
    app_name: string;
    app_identifier: string;
    platform: string;
    current_version: string;
  }>;
}

const MainDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [apps, setApps] = useState<AppSummary[]>([]);
  const [systemStats, setSystemStats] = useState<SystemStats>({
    total_apps: 0,
    total_users: 0,
    total_errors: 0,
    active_users_today: 0,
    total_versions: 0,
    total_downloads: 0
  });
  const [criticalErrors, setCriticalErrors] = useState<ErrorSummary[]>([]);
  const [recentSessions, setRecentSessions] = useState<RecentSession[]>([]);
  const [appUsers, setAppUsers] = useState<AppUser[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load apps
      const appsResponse = await api.get('/api/v2/apps');
      const appsData = appsResponse.data.apps;
      
      // For each app, load basic stats (in a real app, this would be a single endpoint)
      const appsWithStats = await Promise.all(
        appsData.map(async (app: any) => {
          try {
            const analyticsResponse = await api.get(`/api/v2/analytics/${app.app_identifier}/overview`);
            const analytics = analyticsResponse.data;
            
            return {
              ...app,
              total_users: analytics.user_stats?.total_users || 0,
              active_users: analytics.user_stats?.daily_active_users || 0,
              error_count: analytics.error_stats?.unresolved_errors || 0,
              total_versions: analytics.version_distribution?.length || 0,
              latest_version: analytics.version_distribution?.[0]?.current_version || 'N/A'
            };
          } catch (error) {
            return app;
          }
        })
      );
      
      setApps(appsWithStats);
      
      // Calculate system stats
      const stats = appsWithStats.reduce((acc: SystemStats, app: any) => ({
        total_apps: acc.total_apps + 1,
        total_users: acc.total_users + (app.total_users || 0),
        total_errors: acc.total_errors + (app.error_count || 0),
        active_users_today: acc.active_users_today + (app.active_users || 0),
        total_versions: acc.total_versions + (app.total_versions || 0),
        total_downloads: acc.total_downloads + 0 // Would need to sum from versions
      }), {
        total_apps: 0,
        total_users: 0,
        total_errors: 0,
        active_users_today: 0,
        total_versions: 0,
        total_downloads: 0
      });
      
      setSystemStats(stats);
      
      // Load critical errors from all apps
      const errorsPromises = appsData.map((app: any) => 
        api.get(`/api/v2/analytics/${app.app_identifier}/errors?severity=critical&limit=5`)
          .then((res: any) => res.data.errors.map((err: any) => ({
            ...err,
            app_name: app.app_name,
            app_identifier: app.app_identifier
          })))
          .catch(() => [])
      );
      
      const allErrors = await Promise.all(errorsPromises);
      const flatErrors = allErrors.flat().slice(0, 6);
      setCriticalErrors(flatErrors);
      
      // Load recent sessions from all apps
      const sessionsPromises = appsData.map((app: any) => 
        api.get(`/api/v2/sessions/recent/${app.app_identifier}?limit=3`)
          .then((res: any) => res.data.sessions.map((session: any) => ({
            ...session,
            app_name: app.app_name,
            app_identifier: app.app_identifier
          })))
          .catch(() => [])
      );
      
      const allSessions = await Promise.all(sessionsPromises);
      const flatSessions = allSessions.flat()
        .sort((a, b) => new Date(b.session_start).getTime() - new Date(a.session_start).getTime())
        .slice(0, 5);
      setRecentSessions(flatSessions);
      
      // Load recent users using the new users endpoint
      try {
        const usersResponse = await api.get('/api/v2/users?limit=10');
        const usersData = usersResponse.data.users;
        
        // Transform the data to match our AppUser interface
        const users: AppUser[] = usersData.map((user: any) => ({
          id: user.id,
          user_uuid: user.user_uuid,
          email: user.email,
          first_seen_at: user.first_seen_at,
          last_seen_at: user.last_seen_at,
          total_sessions: user.total_sessions,
          apps: user.apps || []
        }));
        
        setAppUsers(users);
      } catch (error) {
        console.error('Error loading user data:', error);
        // Fallback to aggregating from sessions if the new endpoint is not available
        try {
          const userMap = new Map<string, AppUser>();
          
          for (const app of appsData) {
            try {
              const sessionsResponse = await api.get(`/api/v2/sessions/recent/${app.app_identifier}?limit=20`);
              const sessions = sessionsResponse.data.sessions;
              
              sessions.forEach((session: any) => {
                if (session.email && !userMap.has(session.email)) {
                  userMap.set(session.email, {
                    id: session.user_id,
                    user_uuid: session.user_id.toString(),
                    email: session.email,
                    first_seen_at: session.session_start,
                    last_seen_at: session.session_start,
                    total_sessions: 1,
                    apps: [{
                      app_name: app.app_name,
                      app_identifier: app.app_identifier,
                      platform: session.platform,
                      current_version: session.app_version
                    }]
                  });
                } else if (session.email && userMap.has(session.email)) {
                  const user = userMap.get(session.email)!;
                  user.total_sessions++;
                  user.last_seen_at = new Date(session.session_start) > new Date(user.last_seen_at) 
                    ? session.session_start 
                    : user.last_seen_at;
                  
                  const appExists = user.apps.some(a => 
                    a.app_identifier === app.app_identifier && 
                    a.platform === session.platform
                  );
                  
                  if (!appExists) {
                    user.apps.push({
                      app_name: app.app_name,
                      app_identifier: app.app_identifier,
                      platform: session.platform,
                      current_version: session.app_version
                    });
                  }
                }
              });
            } catch (error) {
              console.error(`Error loading user data for ${app.app_identifier}:`, error);
            }
          }
          
          const users = Array.from(userMap.values())
            .sort((a, b) => new Date(b.last_seen_at).getTime() - new Date(a.last_seen_at).getTime())
            .slice(0, 10);
          
          setAppUsers(users);
        } catch (fallbackError) {
          console.error('Fallback user loading also failed:', fallbackError);
        }
      }
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
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

  const formatDuration = (seconds: number | undefined): string => {
    if (!seconds) return 'In corso';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) return `${hours}h ${minutes}m`;
    if (minutes > 0) return `${minutes}m`;
    return '<1m';
  };

  const formatTimeAgo = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Ora';
    if (diffMins < 60) return `${diffMins}m fa`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h fa`;
    return date.toLocaleDateString('it-IT');
  };
  
  const getInitials = (email?: string): string => {
    if (!email) return '?';
    const parts = email.split('@')[0].split('.');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return email.substring(0, 2).toUpperCase();
  };

  if (loading) {
    return (
      <Container>
        <NoData>Caricamento dashboard...</NoData>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <Title>Dashboard Multi-App</Title>
        <Subtitle>Panoramica completa di tutte le applicazioni gestite</Subtitle>
      </Header>

      <StatsGrid>
        <StatCard>
          <StatInfo>
            <StatLabel>Applicazioni</StatLabel>
            <StatValue>{systemStats.total_apps}</StatValue>
          </StatInfo>
          <IconWrapper color="#e3f2fd" iconColor="#1976d2">
            <Package size={30} />
          </IconWrapper>
        </StatCard>

        <StatCard>
          <StatInfo>
            <StatLabel>Utenti Totali</StatLabel>
            <StatValue>{formatNumber(systemStats?.total_users)}</StatValue>
          </StatInfo>
          <IconWrapper color="#e8f5e9" iconColor="#4CAF50">
            <Users size={30} />
          </IconWrapper>
        </StatCard>

        <StatCard>
          <StatInfo>
            <StatLabel>Utenti Attivi Oggi</StatLabel>
            <StatValue>{formatNumber(systemStats?.active_users_today)}</StatValue>
          </StatInfo>
          <IconWrapper color="#f3e5f5" iconColor="#9c27b0">
            <Activity size={30} />
          </IconWrapper>
        </StatCard>

        <StatCard>
          <StatInfo>
            <StatLabel>Errori Non Risolti</StatLabel>
            <StatValue>{formatNumber(systemStats?.total_errors)}</StatValue>
          </StatInfo>
          <IconWrapper color="#ffebee" iconColor="#f44336">
            <AlertCircle size={30} />
          </IconWrapper>
        </StatCard>
      </StatsGrid>

      <Section>
        <SectionTitle>
          <Package size={24} />
          Applicazioni Registrate
        </SectionTitle>
        {apps.length === 0 ? (
          <NoData>Nessuna applicazione registrata</NoData>
        ) : (
          <AppGrid>
            {apps.map(app => (
              <AppCard key={app.id} onClick={() => navigate(`/app/${app.app_identifier}`)}>
                <AppHeader>
                  <AppName>{app.app_name}</AppName>
                  <div>
                    {app.platform_support.map(platform => (
                      <PlatformBadge key={platform} platform={platform}>
                        {platform.toUpperCase()}
                      </PlatformBadge>
                    ))}
                  </div>
                </AppHeader>
                <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
                  {app.app_identifier}
                </div>
                <AppStats>
                  <AppStat>
                    <AppStatValue>{formatNumber(app.total_users || 0)}</AppStatValue>
                    <AppStatLabel>Utenti</AppStatLabel>
                  </AppStat>
                  <AppStat>
                    <AppStatValue>{app.total_versions || 0}</AppStatValue>
                    <AppStatLabel>Versioni</AppStatLabel>
                  </AppStat>
                  <AppStat>
                    <AppStatValue>{app.error_count || 0}</AppStatValue>
                    <AppStatLabel>Errori</AppStatLabel>
                  </AppStat>
                </AppStats>
              </AppCard>
            ))}
          </AppGrid>
        )}
      </Section>

      {criticalErrors.length > 0 && (
        <Section>
          <SectionTitle>
            <AlertCircle size={24} />
            Errori Critici Recenti
          </SectionTitle>
          <ErrorsGrid>
            {criticalErrors.map((error, index) => (
              <ErrorCard key={index} severity={error.severity}>
                <ErrorApp>{error.app_name}</ErrorApp>
                <ErrorCount>{error.count}</ErrorCount>
                <ErrorType>{error.error_type}</ErrorType>
              </ErrorCard>
            ))}
          </ErrorsGrid>
        </Section>
      )}

      {recentSessions.length > 0 && (
        <Section>
          <SectionTitle>
            <Activity size={24} />
            Sessioni Utente Recenti
          </SectionTitle>
          <SessionsGrid>
            {recentSessions.map((session) => (
              <SessionCard key={session.id}>
                <SessionInfo>
                  <SessionApp>{session.app_name}</SessionApp>
                  <SessionUser>
                    {session.user_email || 'Utente anonimo'} • {session.platform}
                  </SessionUser>
                </SessionInfo>
                <SessionTime>
                  <SessionDuration>{formatDuration(session.duration_seconds)}</SessionDuration>
                  {formatTimeAgo(session.session_start)}
                </SessionTime>
              </SessionCard>
            ))}
          </SessionsGrid>
          
          <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <button 
              onClick={() => navigate('/sessions')}
              style={{
                background: '#1976d2',
                color: 'white',
                border: 'none',
                padding: '10px 20px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              Visualizza Tutte le Sessioni
            </button>
          </div>
        </Section>
      )}

      {appUsers.length > 0 && (
        <Section>
          <SectionTitle>
            <Users size={24} />
            Utenti delle Applicazioni
          </SectionTitle>
          <UsersGrid>
            {appUsers.map((user) => (
              <UserCard key={user.id}>
                <UserAvatar>{getInitials(user.email)}</UserAvatar>
                <UserInfo>
                  <UserEmail>{user.email || 'Utente anonimo'}</UserEmail>
                  <UserMeta>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Activity size={12} />
                      {user.total_sessions} sessioni
                    </span>
                    <span>•</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Clock size={12} />
                      {formatTimeAgo(user.last_seen_at)}
                    </span>
                  </UserMeta>
                  <UserApps>
                    {user.apps.slice(0, 3).map((app, index) => (
                      <UserAppBadge key={index}>
                        {app.app_name} ({app.platform})
                      </UserAppBadge>
                    ))}
                    {user.apps.length > 3 && (
                      <UserAppBadge>+{user.apps.length - 3} altre</UserAppBadge>
                    )}
                  </UserApps>
                </UserInfo>
              </UserCard>
            ))}
          </UsersGrid>
          
          <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <button 
              onClick={() => navigate('/users')}
              style={{
                background: '#1976d2',
                color: 'white',
                border: 'none',
                padding: '10px 20px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              Visualizza Tutti gli Utenti
            </button>
          </div>
        </Section>
      )}
    </Container>
  );
};

export default MainDashboard;