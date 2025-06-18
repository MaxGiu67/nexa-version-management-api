import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { User, Mail, Calendar, Activity, Smartphone, Clock, ArrowLeft, Eye, TrendingUp } from 'lucide-react';
import api from '../services/api';

interface AppUser {
  id: number;
  user_uuid: string;
  email?: string;
  name?: string;
  first_seen_at: string;
  last_seen_at: string;
  total_sessions: number;
  app_count: number;
  apps?: Array<{
    app_identifier: string;
    app_name: string;
    current_version: string;
    platform: string;
    last_update_date: string;
  }>;
}

interface UserSession {
  id: number;
  session_start: string;
  session_end?: string;
  duration_seconds?: number;
  app_version: string;
  platform: string;
  app_name: string;
  app_identifier: string;
}

interface UserDetails extends AppUser {
  installations: Array<{
    app_id: number;
    app_name: string;
    app_identifier: string;
    platform: string;
    current_version: string;
    install_date: string;
    last_update_date: string;
    is_active: boolean;
    device_model?: string;
    os_version?: string;
  }>;
  recent_sessions: UserSession[];
  error_count: number;
  device_info?: any;
}

interface Props {
  appIdentifier?: string;
}

const UsersDashboard: React.FC<Props> = ({ appIdentifier }) => {
  const [users, setUsers] = useState<AppUser[]>([]);
  const [selectedUser, setSelectedUser] = useState<UserDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [userDetailsLoading, setUserDetailsLoading] = useState(false);
  const [page, setPage] = useState(0);
  const [totalUsers, setTotalUsers] = useState(0);
  const pageSize = 20;

  useEffect(() => {
    fetchUsers();
  }, [page]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v2/users', {
        params: {
          limit: pageSize,
          offset: page * pageSize
        }
      });
      
      setUsers(response.data.users || []);
      setTotalUsers(response.data.total || 0);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserDetails = async (userId: number) => {
    try {
      setUserDetailsLoading(true);
      const response = await api.get(`/api/v2/users/${userId}`);
      setSelectedUser(response.data);
    } catch (error) {
      console.error('Error fetching user details:', error);
    } finally {
      setUserDetailsLoading(false);
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

  const formatDuration = (seconds: number | undefined) => {
    if (!seconds) return 'N/A';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
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

  const getActivityStatus = (lastSeen: string) => {
    const lastSeenDate = new Date(lastSeen);
    const now = new Date();
    const diffHours = (now.getTime() - lastSeenDate.getTime()) / (1000 * 3600);
    
    if (diffHours < 1) return { status: 'online', label: 'Online', color: '#10b981' };
    if (diffHours < 24) return { status: 'recent', label: 'Attivo oggi', color: '#f59e0b' };
    if (diffHours < 168) return { status: 'week', label: 'Questa settimana', color: '#6366f1' };
    return { status: 'inactive', label: 'Inattivo', color: '#6b7280' };
  };

  const totalPages = Math.ceil(totalUsers / pageSize);

  if (selectedUser) {
    return (
      <UserDetailContainer>
        <UserDetailHeader>
          <BackButton onClick={() => setSelectedUser(null)}>
            <ArrowLeft size={20} />
            Torna alla lista utenti
          </BackButton>
          <UserDetailTitle>
            <User size={24} />
            Dettagli Utente
          </UserDetailTitle>
        </UserDetailHeader>

        {userDetailsLoading ? (
          <LoadingContainer>Caricamento dettagli utente...</LoadingContainer>
        ) : (
          <UserDetailContent>
            <UserDetailCard>
              <UserDetailInfo>
                <UserAvatar>
                  <User size={32} />
                </UserAvatar>
                <UserDetailMeta>
                  <UserDetailName>
                    {selectedUser.name || selectedUser.email || `Utente ${selectedUser.id}`}
                  </UserDetailName>
                  <UserDetailEmail>{selectedUser.email}</UserDetailEmail>
                  <UserDetailStats>
                    <StatItem>
                      <Activity size={16} />
                      {selectedUser.total_sessions} sessioni
                    </StatItem>
                    <StatItem>
                      <Calendar size={16} />
                      Registrato il {formatDate(selectedUser.first_seen_at)}
                    </StatItem>
                    <StatItem>
                      <Clock size={16} />
                      Ultimo accesso: {formatDate(selectedUser.last_seen_at)}
                    </StatItem>
                  </UserDetailStats>
                </UserDetailMeta>
              </UserDetailInfo>
            </UserDetailCard>

            <UserDetailGrid>
              <UserDetailSection>
                <SectionTitle>
                  <Smartphone size={20} />
                  Installazioni App ({selectedUser.installations?.length || 0})
                </SectionTitle>
                <InstallationsList>
                  {selectedUser.installations?.map((install, index) => (
                    <InstallationCard key={index}>
                      <InstallationHeader>
                        <InstallationInfo>
                          <InstallationName>{install.app_name}</InstallationName>
                          <InstallationMeta>
                            <PlatformBadge>
                              {getPlatformIcon(install.platform)} {install.platform}
                            </PlatformBadge>
                            <VersionBadge>v{install.current_version}</VersionBadge>
                            <StatusBadge active={install.is_active}>
                              {install.is_active ? 'Attiva' : 'Inattiva'}
                            </StatusBadge>
                          </InstallationMeta>
                        </InstallationInfo>
                      </InstallationHeader>
                      <InstallationDetails>
                        <DetailRow>
                          <DetailLabel>Installata:</DetailLabel>
                          <DetailValue>{formatDate(install.install_date)}</DetailValue>
                        </DetailRow>
                        <DetailRow>
                          <DetailLabel>Ultimo aggiornamento:</DetailLabel>
                          <DetailValue>{formatDate(install.last_update_date)}</DetailValue>
                        </DetailRow>
                        {install.device_model && (
                          <DetailRow>
                            <DetailLabel>Dispositivo:</DetailLabel>
                            <DetailValue>{install.device_model}</DetailValue>
                          </DetailRow>
                        )}
                      </InstallationDetails>
                    </InstallationCard>
                  ))}
                </InstallationsList>
              </UserDetailSection>

              <UserDetailSection>
                <SectionTitle>
                  <TrendingUp size={20} />
                  Sessioni Recenti ({selectedUser.recent_sessions?.length || 0})
                </SectionTitle>
                <SessionsList>
                  {selectedUser.recent_sessions?.map((session) => (
                    <SessionCard key={session.id}>
                      <SessionHeader>
                        <SessionInfo>
                          <SessionApp>{session.app_name}</SessionApp>
                          <SessionMeta>
                            <PlatformBadge>
                              {getPlatformIcon(session.platform)} {session.platform}
                            </PlatformBadge>
                            <VersionBadge>v{session.app_version}</VersionBadge>
                          </SessionMeta>
                        </SessionInfo>
                        <SessionDuration>
                          {session.duration_seconds 
                            ? formatDuration(session.duration_seconds)
                            : 'In corso...'
                          }
                        </SessionDuration>
                      </SessionHeader>
                      <SessionTiming>
                        <TimingItem>
                          <TimingLabel>Inizio:</TimingLabel>
                          <TimingValue>{formatDate(session.session_start)}</TimingValue>
                        </TimingItem>
                        {session.session_end && (
                          <TimingItem>
                            <TimingLabel>Fine:</TimingLabel>
                            <TimingValue>{formatDate(session.session_end)}</TimingValue>
                          </TimingItem>
                        )}
                      </SessionTiming>
                    </SessionCard>
                  ))}
                </SessionsList>
              </UserDetailSection>
            </UserDetailGrid>
          </UserDetailContent>
        )}
      </UserDetailContainer>
    );
  }

  return (
    <Container>
      <Header>
        <Title>
          <User size={24} />
          Gestione Utenti
        </Title>
        <UserStats>
          <StatBadge>
            <User size={16} />
            {totalUsers} utenti totali
          </StatBadge>
        </UserStats>
      </Header>

      {loading ? (
        <LoadingContainer>Caricamento utenti...</LoadingContainer>
      ) : (
        <>
          <UsersGrid>
            {users.map((user) => {
              const activity = getActivityStatus(user.last_seen_at);
              
              return (
                <UserCard key={user.id}>
                  <UserCardHeader>
                    <UserInfo>
                      <UserAvatar>
                        <User size={20} />
                      </UserAvatar>
                      <UserMeta>
                        <UserName>
                          {user.name || user.email || `Utente ${user.id}`}
                        </UserName>
                        <UserEmail>{user.email}</UserEmail>
                      </UserMeta>
                    </UserInfo>
                    <ActivityStatus color={activity.color}>
                      {activity.label}
                    </ActivityStatus>
                  </UserCardHeader>
                  
                  <UserStats>
                    <UserStat>
                      <Activity size={14} />
                      <span>{user.total_sessions} sessioni</span>
                    </UserStat>
                    <UserStat>
                      <Smartphone size={14} />
                      <span>{user.app_count} app</span>
                    </UserStat>
                    <UserStat>
                      <Calendar size={14} />
                      <span>Ultimo: {formatDate(user.last_seen_at)}</span>
                    </UserStat>
                  </UserStats>

                  <ViewDetailsButton onClick={() => fetchUserDetails(user.id)}>
                    <Eye size={16} />
                    Vedi Dettagli
                  </ViewDetailsButton>
                </UserCard>
              );
            })}
          </UsersGrid>

          {totalPages > 1 && (
            <Pagination>
              <PaginationButton 
                disabled={page === 0} 
                onClick={() => setPage(page - 1)}
              >
                Precedente
              </PaginationButton>
              
              <PaginationInfo>
                Pagina {page + 1} di {totalPages} ({totalUsers} utenti totali)
              </PaginationInfo>
              
              <PaginationButton 
                disabled={page >= totalPages - 1} 
                onClick={() => setPage(page + 1)}
              >
                Successiva
              </PaginationButton>
            </Pagination>
          )}
        </>
      )}
    </Container>
  );
};

// Styled Components
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

const UserStats = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
`;

const StatBadge = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f3f4f6;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
  color: #6b7280;
`;

const UsersGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
`;

const UserCard = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s;

  &:hover {
    border-color: #3b82f6;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
  }
`;

const UserCardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const UserAvatar = styled.div`
  width: 40px;
  height: 40px;
  background: #f3f4f6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
`;

const UserMeta = styled.div``;

const UserName = styled.div`
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 2px;
`;

const UserEmail = styled.div`
  font-size: 14px;
  color: #6b7280;
`;

const ActivityStatus = styled.div<{ color: string }>`
  font-size: 12px;
  font-weight: 500;
  color: ${props => props.color};
  background: ${props => props.color}20;
  padding: 4px 8px;
  border-radius: 4px;
`;

const UserStat = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #6b7280;
`;

const ViewDetailsButton = styled.button`
  width: 100%;
  background: #f3f4f6;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
  transition: all 0.2s;

  &:hover {
    background: #3b82f6;
    color: white;
  }
`;

const Pagination = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-top: 1px solid #e5e7eb;
`;

const PaginationButton = styled.button`
  background: white;
  border: 1px solid #e5e7eb;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &:hover:not(:disabled) {
    background: #f9fafb;
  }
`;

const PaginationInfo = styled.div`
  font-size: 14px;
  color: #6b7280;
`;

// User Detail Styles
const UserDetailContainer = styled.div`
  padding: 20px;
`;

const UserDetailHeader = styled.div`
  margin-bottom: 24px;
`;

const BackButton = styled.button`
  background: none;
  border: none;
  color: #3b82f6;
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

const UserDetailTitle = styled.h2`
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
`;

const UserDetailContent = styled.div``;

const UserDetailCard = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
`;

const UserDetailInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const UserDetailMeta = styled.div`
  flex: 1;
`;

const UserDetailName = styled.h3`
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
`;

const UserDetailEmail = styled.div`
  color: #6b7280;
  margin-bottom: 12px;
`;

const UserDetailStats = styled.div`
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
`;

const StatItem = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #6b7280;
`;

const UserDetailGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const UserDetailSection = styled.div``;

const SectionTitle = styled.h4`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
`;

const InstallationsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const InstallationCard = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
`;

const InstallationHeader = styled.div`
  margin-bottom: 12px;
`;

const InstallationInfo = styled.div``;

const InstallationName = styled.div`
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 6px;
`;

const InstallationMeta = styled.div`
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
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

const StatusBadge = styled.span<{ active: boolean }>`
  background: ${props => props.active ? '#dcfce7' : '#fee2e2'};
  color: ${props => props.active ? '#166534' : '#991b1b'};
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
`;

const InstallationDetails = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
`;

const DetailRow = styled.div`
  display: flex;
  gap: 8px;
  font-size: 14px;
`;

const DetailLabel = styled.span`
  color: #6b7280;
  min-width: 120px;
`;

const DetailValue = styled.span`
  color: #1f2937;
  font-weight: 500;
`;

const SessionsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const SessionCard = styled.div`
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

const SessionInfo = styled.div``;

const SessionApp = styled.div`
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 6px;
`;

const SessionMeta = styled.div`
  display: flex;
  gap: 8px;
  align-items: center;
`;

const SessionDuration = styled.div`
  font-size: 16px;
  font-weight: 600;
  color: #10b981;
`;

const SessionTiming = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const TimingItem = styled.div`
  display: flex;
  gap: 8px;
  font-size: 14px;
`;

const TimingLabel = styled.span`
  color: #6b7280;
  min-width: 50px;
`;

const TimingValue = styled.span`
  color: #1f2937;
  font-weight: 500;
`;

export default UsersDashboard;