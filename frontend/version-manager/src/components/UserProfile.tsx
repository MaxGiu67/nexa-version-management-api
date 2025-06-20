import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import api from '../services/api';
import { User, Shield, Key, AlertCircle, Check, X } from 'lucide-react';

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
`;

const Card = styled.div`
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
`;

const Title = styled.h2`
  color: #1a1f3a;
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const InfoItem = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const Label = styled.span`
  color: #666;
  font-size: 14px;
`;

const Value = styled.span`
  color: #333;
  font-size: 16px;
  font-weight: 500;
`;

const TwoFASection = styled.div`
  border-top: 1px solid #eee;
  padding-top: 25px;
  margin-top: 25px;
`;

const TwoFAStatus = styled.div<{ enabled: boolean }>`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  background: ${props => props.enabled ? '#e8f5e9' : '#fff3e0'};
  border-radius: 8px;
  margin-bottom: 20px;
`;

const StatusIcon = styled.div<{ enabled: boolean }>`
  color: ${props => props.enabled ? '#4caf50' : '#ff9800'};
`;

const Button = styled.button`
  padding: 10px 20px;
  background: #4a69bd;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s;

  &:hover:not(:disabled) {
    background: #3c5aa6;
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

const DangerButton = styled(Button)`
  background: #f44336;

  &:hover:not(:disabled) {
    background: #d32f2f;
  }
`;

const QRCodeContainer = styled.div`
  text-align: center;
  margin: 20px 0;
`;

const QRCode = styled.img`
  max-width: 300px;
  border: 1px solid #ddd;
  padding: 10px;
  background: white;
  border-radius: 8px;
`;

const Secret = styled.div`
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  margin: 15px 0;
  font-family: monospace;
  font-size: 16px;
  text-align: center;
  letter-spacing: 2px;
`;

const BackupCodes = styled.div`
  background: #fff8e1;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
`;

const CodeGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  margin-top: 15px;
`;

const BackupCode = styled.div`
  background: white;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: monospace;
  font-size: 14px;
  text-align: center;
`;

const Warning = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #ffebee;
  padding: 15px;
  border-radius: 8px;
  margin: 15px 0;
  color: #c62828;
`;

interface UserProfileProps {
  user: any;
  authToken: string;
}

export const UserProfile: React.FC<UserProfileProps> = ({ user, authToken }) => {
  const [loading, setLoading] = useState(false);
  const [has2FA, setHas2FA] = useState(false);
  const [qrCode, setQrCode] = useState('');
  const [secret, setSecret] = useState('');
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [showEnable2FA, setShowEnable2FA] = useState(false);

  useEffect(() => {
    // Set initial 2FA status from user data
    setHas2FA(user?.has_2fa || false);
  }, [user]);

  const handleEnable2FA = async () => {
    setLoading(true);
    try {
      const response = await api.post('/api/v2/auth/enable-2fa', {}, {
        headers: { Authorization: `Bearer ${authToken}` }
      });

      setQrCode(response.data.qr_code);
      setSecret(response.data.secret);
      setBackupCodes(response.data.backup_codes);
      setShowEnable2FA(true);
    } catch (error) {
      console.error('Failed to enable 2FA:', error);
      alert('Errore durante l\'abilitazione 2FA');
    } finally {
      setLoading(false);
    }
  };

  const handleDisable2FA = async () => {
    if (!window.confirm('Sei sicuro di voler disabilitare la verifica a due fattori? Questo ridurrà la sicurezza del tuo account.')) {
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/v2/auth/disable-2fa', {}, {
        headers: { Authorization: `Bearer ${authToken}` }
      });

      setHas2FA(false);
      setShowEnable2FA(false);
      alert('2FA disabilitato con successo');
    } catch (error) {
      console.error('Failed to disable 2FA:', error);
      alert('Errore durante la disabilitazione 2FA');
    } finally {
      setLoading(false);
    }
  };

  const handleComplete2FASetup = () => {
    setHas2FA(true);
    setShowEnable2FA(false);
    alert('2FA abilitato con successo! Assicurati di salvare i codici di backup.');
  };

  return (
    <Container>
      <Card>
        <Title>
          <User size={24} />
          Profilo Utente
        </Title>

        <InfoGrid>
          <InfoItem>
            <Label>Username</Label>
            <Value>{user?.username || 'N/A'}</Value>
          </InfoItem>
          <InfoItem>
            <Label>Email</Label>
            <Value>{user?.email || 'N/A'}</Value>
          </InfoItem>
          <InfoItem>
            <Label>Nome</Label>
            <Value>{user?.first_name || 'N/A'} {user?.last_name || ''}</Value>
          </InfoItem>
          <InfoItem>
            <Label>Ruolo</Label>
            <Value>{user?.is_superadmin ? 'Super Admin' : 'Admin'}</Value>
          </InfoItem>
        </InfoGrid>

        <TwoFASection>
          <Title>
            <Shield size={24} />
            Verifica a Due Fattori (2FA)
          </Title>

          <TwoFAStatus enabled={has2FA}>
            <StatusIcon enabled={has2FA}>
              {has2FA ? <Check size={24} /> : <X size={24} />}
            </StatusIcon>
            <div>
              <div style={{ fontWeight: 500 }}>
                2FA {has2FA ? 'Abilitato' : 'Disabilitato'}
              </div>
              <div style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
                {has2FA 
                  ? 'Il tuo account è protetto con verifica a due fattori'
                  : 'Abilita 2FA per maggiore sicurezza'}
              </div>
            </div>
          </TwoFAStatus>

          {!has2FA && !showEnable2FA && (
            <Button onClick={handleEnable2FA} disabled={loading}>
              {loading ? 'Caricamento...' : 'Abilita 2FA'}
            </Button>
          )}

          {has2FA && (
            <DangerButton onClick={handleDisable2FA} disabled={loading}>
              {loading ? 'Caricamento...' : 'Disabilita 2FA'}
            </DangerButton>
          )}

          {showEnable2FA && (
            <div>
              <Warning>
                <AlertCircle size={20} />
                <div>
                  <strong>Importante:</strong> Scansiona il QR code con Google Authenticator o un'app simile prima di procedere.
                </div>
              </Warning>

              <QRCodeContainer>
                <QRCode src={qrCode} alt="2FA QR Code" />
              </QRCodeContainer>

              <div>
                <Label>Oppure inserisci manualmente questo codice:</Label>
                <Secret>{secret}</Secret>
              </div>

              <BackupCodes>
                <h4 style={{ marginTop: 0 }}>
                  <Key size={18} style={{ verticalAlign: 'middle', marginRight: '5px' }} />
                  Codici di Backup
                </h4>
                <p style={{ fontSize: '14px', color: '#666' }}>
                  Salva questi codici in un posto sicuro. Potrai usarli per accedere se perdi l'accesso alla tua app di autenticazione.
                </p>
                <CodeGrid>
                  {backupCodes.map((code, index) => (
                    <BackupCode key={index}>{code}</BackupCode>
                  ))}
                </CodeGrid>
              </BackupCodes>

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
                <Button onClick={handleComplete2FASetup}>
                  Ho configurato l'app
                </Button>
                <Button 
                  onClick={() => setShowEnable2FA(false)}
                  style={{ background: '#666' }}
                >
                  Annulla
                </Button>
              </div>
            </div>
          )}
        </TwoFASection>
      </Card>
    </Container>
  );
};