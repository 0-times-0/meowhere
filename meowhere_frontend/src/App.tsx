import React, { useState } from 'react';
import { BrowserRouter, Link, Route, Routes } from 'react-router-dom';
import 'leaflet/dist/leaflet.css';
import './App.css';
import {
  clearSession,
  getStoredSession,
  loginMunicipal,
  loginResident,
  registerResident,
} from './api';
import CreateReportPage from './pages/CreateReportPage';
import HomePage from './pages/HomePage';
import ReportDetailsPage from './pages/ReportDetailsPage';
import type { AuthSession } from './types';

export const App: React.FC = () => {
  const [session, setSession] = useState<AuthSession | null>(() => getStoredSession());
  const [showAuthModal, setShowAuthModal] = useState<boolean>(false);
  const [authTab, setAuthTab] = useState<'resident-login' | 'resident-register' | 'municipal'>(
    'resident-login'
  );

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [badgeNumber, setBadgeNumber] = useState('SM-101');
  const [authError, setAuthError] = useState<string | null>(null);

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    try {
      let newSession: AuthSession;
      if (authTab === 'resident-login') {
        newSession = await loginResident(email, password);
      } else if (authTab === 'resident-register') {
        newSession = await registerResident({
          email,
          password,
          full_name: fullName,
          phone_number: phone || undefined,
        });
      } else {
        newSession = await loginMunicipal(badgeNumber, password);
      }
      setSession(newSession);
      setShowAuthModal(false);
      setPassword('');
    } catch (err: any) {
      setAuthError(err.message || 'Błąd uwierzytelniania.');
    }
  };

  const handleLogout = () => {
    clearSession();
    setSession(null);
    window.location.reload();
  };

  return (
    <BrowserRouter>
      <header className="top-navbar">
        <div className="navbar-inner">
          <Link to="/" className="brand-logo">
            🐾 MEOWHERE
          </Link>
          <nav className="nav-links">
            <Link to="/">Mapa</Link>
            <Link to="/search">Wyszukiwarka</Link>
            <Link to="/post">Dodaj zgłoszenie</Link>
          </nav>
          <div className="nav-auth">
            {session ? (
              <div className="user-pill">
                <span>
                  {session.role === 'municipal' ? '🛡️ ' : '👤 '}
                  <strong>{session.display_name}</strong>
                </span>
                <button onClick={handleLogout} className="btn btn-outline btn-sm">
                  Wyloguj
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowAuthModal(true)}
                className="btn btn-primary btn-sm"
              >
                Zaloguj / Rejestracja
              </button>
            )}
          </div>
        </div>
      </header>

      {showAuthModal && (
        <div className="modal-backdrop" onClick={() => setShowAuthModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-tabs">
              <button
                className={authTab === 'resident-login' ? 'active' : ''}
                onClick={() => setAuthTab('resident-login')}
              >
                Mieszkaniec
              </button>
              <button
                className={authTab === 'resident-register' ? 'active' : ''}
                onClick={() => setAuthTab('resident-register')}
              >
                Rejestracja
              </button>
              <button
                className={authTab === 'municipal' ? 'active' : ''}
                onClick={() => setAuthTab('municipal')}
              >
                Straż Miejska
              </button>
            </div>

            {authError && <div className="alert alert-error">{authError}</div>}

            <form onSubmit={handleAuthSubmit} className="report-form">
              {authTab === 'municipal' ? (
                <label>
                  Numer odznaki (demo: SM-101)
                  <input
                    type="text"
                    required
                    value={badgeNumber}
                    onChange={(e) => setBadgeNumber(e.target.value)}
                  />
                </label>
              ) : (
                <label>
                  E-mail (demo: anna.kowalska@example.com)
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </label>
              )}

              {authTab === 'resident-register' && (
                <>
                  <label>
                    Imię i nazwisko
                    <input
                      type="text"
                      required
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                    />
                  </label>
                  <label>
                    Telefon
                    <input
                      type="text"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                    />
                  </label>
                </>
              )}

              <label>
                Hasło {authTab === 'municipal' ? '(demo: StrazMiejska123!)' : ''}
                <input
                  type="password"
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </label>

              <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => setShowAuthModal(false)}
                  className="btn btn-outline"
                >
                  Anuluj
                </button>
                <button type="submit" className="btn btn-primary">
                  Kontynuuj
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<HomePage />} />
          <Route path="/post" element={<CreateReportPage />} />
          <Route path="/reports/new" element={<CreateReportPage />} />
          <Route path="/listing" element={<ReportDetailsPage />} />
          <Route path="/reports/:id" element={<ReportDetailsPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
};

export default App;