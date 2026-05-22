import { BrowserRouter, Link, Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { type ReactElement, useEffect, useState } from 'react';

import { getCurrentUser, getStoredToken, setAuthToken, type LoginResponse, type User } from './api/client';
import { HomePage } from './pages/HomePage';
import { LoginPage } from './pages/LoginPage';
import { PlayerPage } from './pages/PlayerPage';
import { SeriesPage } from './pages/SeriesPage';

function AppLayout({
  user,
  onLogout,
  onLogin,
}: {
  user: User | null;
  onLogout: () => void;
  onLogin: (result: LoginResponse) => void;
}) {
  const location = useLocation();
  const isLoginScreen = location.pathname === '/login';

  return (
    <div className="app-shell">
      {!isLoginScreen && (
        <header className="app-header">
          <div className="app-header__cluster">
            <Link className="brand" to="/">
              <span className="brand__mark">N</span>
              <span>
                <strong>Nastenka Flix</strong>
                <small>My little place for the stories I always return to</small>
              </span>
            </Link>
            <span className="nav-pill">Nastenka&apos;s collection</span>
          </div>
          <div className="app-header__actions">
            {user ? <span className="user-pill">Welcome back, {user.display_name}</span> : null}
            {user ? (
              <button className="ghost-button" onClick={onLogout} type="button">
                Leave for now
              </button>
            ) : null}
          </div>
        </header>
      )}
      <main className={isLoginScreen ? 'page page--login' : 'page'}>
        <Routes>
          <Route path="/login" element={user ? <Navigate to="/" replace /> : <LoginRoute onLogin={onLogin} />} />
          <Route path="/" element={<RequireAuth user={user}><HomePage /></RequireAuth>} />
          <Route path="/series/:seriesSlug" element={<RequireAuth user={user}><SeriesPage /></RequireAuth>} />
          <Route path="/player/:episodeId" element={<RequireAuth user={user}><PlayerPage /></RequireAuth>} />
          <Route path="*" element={<Navigate to={user ? '/' : '/login'} replace />} />
        </Routes>
      </main>
    </div>
  );
}

function LoginRoute({ onLogin }: { onLogin: (result: LoginResponse) => void }) {
  const navigate = useNavigate();

  return (
    <LoginPage
      onLogin={async (result: LoginResponse) => {
        onLogin(result);
        navigate('/', { replace: true });
      }}
    />
  );
}

function RequireAuth({ user, children }: { user: User | null; children: ReactElement }) {
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem('nastenka-flix-user');
    return stored ? (JSON.parse(stored) as User) : null;
  });
  const [isCheckingSession, setIsCheckingSession] = useState(Boolean(getStoredToken()));

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      setIsCheckingSession(false);
      return;
    }

    getCurrentUser()
      .then((currentUser) => {
        setUser(currentUser);
        localStorage.setItem('nastenka-flix-user', JSON.stringify(currentUser));
      })
      .catch(() => {
        setAuthToken(null);
        localStorage.removeItem('nastenka-flix-user');
        setUser(null);
      })
      .finally(() => setIsCheckingSession(false));
  }, []);

  const handleLogout = () => {
    setAuthToken(null);
    localStorage.removeItem('nastenka-flix-user');
    setUser(null);
  };

  const handleLogin = (result: LoginResponse) => {
    setAuthToken(result.access_token);
    localStorage.setItem('nastenka-flix-user', JSON.stringify(result.user));
    setUser(result.user);
  };

  if (isCheckingSession) {
    return <div className="loading-screen">Opening my corner of Nastenka Flix...</div>;
  }

  return (
    <BrowserRouter>
      <AppLayout onLogin={handleLogin} user={user} onLogout={handleLogout} />
    </BrowserRouter>
  );
}
