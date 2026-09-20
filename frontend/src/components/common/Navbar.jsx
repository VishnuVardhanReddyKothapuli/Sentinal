import { useEffect, useState } from 'react';
import { Menu, Moon, Sun, ShieldCheck, ArrowUpRight, ChevronRight } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../auth';

export default function Navbar({ onMenu, health }) {
  const [dark, setDark] = useState(() => document.documentElement.dataset.theme === 'dark');
  useEffect(() => {
    const theme = dark ? 'dark' : 'light';
    document.documentElement.dataset.theme = theme;
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', dark ? '#080809' : '#f5f5f7');
    try { localStorage.setItem('sentinel-theme', theme); } catch { /* Storage may be disabled. */ }
  }, [dark]);
  const { user } = useAuth();
  const location = useLocation();
  const section = location.pathname.startsWith('/analyze')
    ? 'Analysis Studio'
    : location.pathname === '/history'
    ? 'Analysis History'
    : location.pathname === '/admin'
    ? 'Administration'
    : location.pathname === '/login'
    ? 'Account Access'
    : 'Overview';

  return (
    <header className="topbar">
      <div className="breadcrumb">
        <button className="icon-button mobile-menu" onClick={onMenu} aria-label="Open navigation">
          <Menu size={20} />
        </button>
        <span className="text-[var(--text-secondary)] font-medium">Sentinel</span>
        <ChevronRight size={13} className="slash opacity-40" />
        <strong>{section}</strong>
      </div>
      <div className="top-actions">
        <button type="button" className="theme-switch" aria-label="Black theme" aria-pressed={dark} onClick={() => setDark(!dark)} title={dark ? 'Switch to white theme' : 'Switch to black theme'}>
          {dark ? <Moon size={15} /> : <Sun size={15} />}
          <span>{dark ? 'Black' : 'White'}</span>
          <span className="theme-switch-track" aria-hidden="true"><span /></span>
        </button>
        <span className={`connection ${health ? 'online' : ''}`}>
          <span className="status-dot" />
          <span>{health ? 'API Connected' : 'API Standby'}</span>
        </span>
        {user ? (
          <span className="top-account">
            <ShieldCheck size={15} />
            <span>{user.username}</span>
          </span>
        ) : (
          <Link to="/login" className="button secondary small">
            <span>Sign In</span>
            <ArrowUpRight size={13} />
          </Link>
        )}
      </div>
    </header>
  );
}
