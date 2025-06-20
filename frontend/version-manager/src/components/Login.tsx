import React, { useState } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Lock, User, Shield } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const LoginContainer = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1f3a 0%, #2d3561 100%);
`;

const LoginCard = styled.div`
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
`;

const Title = styled.h1`
  text-align: center;
  color: #1a1f3a;
  margin-bottom: 10px;
  font-size: 28px;
`;

const Subtitle = styled.p`
  text-align: center;
  color: #666;
  margin-bottom: 30px;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
`;

const InputGroup = styled.div`
  position: relative;
  margin-bottom: 20px;
`;

const InputIcon = styled.div`
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 15px 12px 45px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;

  &:focus {
    outline: none;
    border-color: #4a69bd;
  }

  &::placeholder {
    color: #999;
  }
`;

const Button = styled.button`
  padding: 12px;
  background: #4a69bd;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
  margin-top: 10px;

  &:hover:not(:disabled) {
    background: #3c5aa6;
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  background: #ffe4e4;
  color: #d32f2f;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 14px;
  text-align: center;
`;

const TwoFactorSection = styled.div`
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
`;

const TwoFactorTitle = styled.h3`
  color: #1a1f3a;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const CodeInput = styled(Input)`
  text-align: center;
  font-size: 24px;
  letter-spacing: 8px;
  padding-left: 15px;
`;

const InfoText = styled.p`
  color: #666;
  font-size: 14px;
  text-align: center;
  margin-top: 10px;
`;

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [sessionToken, setSessionToken] = useState('');
  const [requires2FA, setRequires2FA] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await api.post('/api/v2/auth/login', { username, password });
      
      if (response.data.requires_2fa) {
        setSessionToken(response.data.session_token);
        setRequires2FA(true);
      } else {
        // No 2FA required, login complete
        login(response.data.session_token, response.data.user);
        navigate('/');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handle2FAVerification = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await api.post('/api/v2/auth/verify-2fa', {
        session_token: sessionToken,
        totp_code: totpCode
      });

      if (response.data.success) {
        login(sessionToken, response.data.user);
        navigate('/');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '2FA verification failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <LoginContainer>
      <LoginCard>
        <Title>Nexa Version Manager</Title>
        <Subtitle>Accedi al pannello di controllo</Subtitle>

        {error && <ErrorMessage>{error}</ErrorMessage>}

        {!requires2FA ? (
          <Form onSubmit={handleLogin}>
            <InputGroup>
              <InputIcon>
                <User size={20} />
              </InputIcon>
              <Input
                type="text"
                placeholder="Username o Email"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                disabled={loading}
              />
            </InputGroup>

            <InputGroup>
              <InputIcon>
                <Lock size={20} />
              </InputIcon>
              <Input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
              />
            </InputGroup>

            <Button type="submit" disabled={loading}>
              {loading ? 'Accesso in corso...' : 'Accedi'}
            </Button>
          </Form>
        ) : (
          <TwoFactorSection>
            <TwoFactorTitle>
              <Shield size={20} />
              Verifica a due fattori
            </TwoFactorTitle>

            <Form onSubmit={handle2FAVerification}>
              <InputGroup>
                <CodeInput
                  type="text"
                  placeholder="000000"
                  maxLength={6}
                  value={totpCode}
                  onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, ''))}
                  required
                  disabled={loading}
                  autoFocus
                />
              </InputGroup>

              <Button type="submit" disabled={loading || totpCode.length !== 6}>
                {loading ? 'Verifica in corso...' : 'Verifica'}
              </Button>

              <InfoText>
                Inserisci il codice a 6 cifre dalla tua app di autenticazione
              </InfoText>
            </Form>
          </TwoFactorSection>
        )}
      </LoginCard>
    </LoginContainer>
  );
};