import { NavLink, Link } from 'react-router-dom';
import { Activity, ArrowUpRight, Fingerprint, LayoutDashboard, Layers3, LogOut, ScanLine, Shield, ShieldCheck, History, X } from 'lucide-react';
import { useAuth } from '../../auth';

const navigation = [
  ['/', 'Overview', LayoutDashboard],
  ['/analyze/nsfw', 'Safety Analyzer', ShieldCheck],
  ['/analyze/similarity', 'Similarity Checker', Fingerprint],
  ['/analyze/combined', 'Combined Analysis', Layers3],
  ['/history', 'Analysis History', History]
];

export default function Sidebar({ open, onClose }) {
  const { user, logout } = useAuth();

  return (
    <>
      <button
        className={`nav-backdrop ${open ? 'visible' : ''}`}
        onClick={onClose}
        aria-label="Close navigation"
        tabIndex={open ? 0 : -1}
      />
      <aside className={`sidebar ${open ? 'open' : ''}`}>
        <Link className="brand" to="/" onClick={onClose}>
          <span className="brand-mark">
            <Shield size={20} />
          </span>
          <span>
            Sentinel
            <span className="brand-caption">CONTENT INTELLIGENCE</span>
          </span>
        </Link>
        <button className="icon-button mobile-close" onClick={onClose} aria-label="Close navigation">
          <X size={18} />
        </button>

        <div className="workspace-label">
          <span className="workspace-icon">S</span>
          <div>
            Sentinel Workspace
            <small>Trust & Safety Console</small>
          </div>
        </div>

        <p className="nav-label">WORKSPACE</p>
        <nav aria-label="Main navigation">
          {navigation.map(([to, label, Icon]) => (
            <NavLink key={to} to={to} end={to === '/'} onClick={onClose}>
              <Icon size={17} />
              <span>{label}</span>
              {to === '/analyze/combined' && <span className="nav-tag">UNIFIED</span>}
            </NavLink>
          ))}
          {user?.role === 'ADMIN' && (
            <NavLink to="/admin" onClick={onClose}>
              <Shield size={17} />
              <span>Admin Control</span>
            </NavLink>
          )}
        </nav>

        <div className="sidebar-bottom">
          <div className="pipeline-note">
            <Activity size={16} />
            <span>
              Engineered for precision
              <small>Evidence. Context. Human oversight.</small>
            </span>
          </div>

          {user ? (
            <div className="account">
              <div className="avatar">{user.username.slice(0, 2).toUpperCase()}</div>
              <div>
                {user.username}
                <small>{user.role === 'ADMIN' ? 'Administrator' : 'Verified Member'}</small>
              </div>
              <button className="icon-button" onClick={logout} aria-label="Sign out" title="Sign out">
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <Link className="account guest" to="/login" onClick={onClose}>
              <ScanLine size={18} />
              <span>
                Connect Account
                <small>Save and inspect your scans</small>
              </span>
              <ArrowUpRight size={15} />
            </Link>
          )}
        </div>
      </aside>
    </>
  );
}
