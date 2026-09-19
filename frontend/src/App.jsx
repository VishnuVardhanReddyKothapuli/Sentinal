import { useEffect, useState } from 'react';
import { Link, Route, Routes, useLocation } from 'react-router-dom';
import { api } from './api';
import Navbar from './components/common/Navbar';
import Sidebar from './components/common/Sidebar';
import ProtectedRoutes from './components/common/ProtectedRoutes';
import Home from './pages/Home';
import Login from './pages/Login';
import NsfwAnalyzer from './pages/NsfwAnalyzer';
import SimilarityChecker from './pages/SimilarityChecker';
import CombinedChecker from './pages/CombinedChecker';
import History from './pages/History';
import AdminDashboard from './pages/AdminDashboard';

export default function App() {
  const [open, setOpen] = useState(false);
  const [health, setHealth] = useState(null);
  const location = useLocation();

  useEffect(() => {
    api
      .get('/health')
      .then((r) => setHealth(r.data))
      .catch(() => setHealth(null));
  }, []);

  useEffect(() => {
    window.scrollTo(0, 0);
    setOpen(false);
  }, [location.pathname]);

  return (
    <>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <Sidebar open={open} onClose={() => setOpen(false)} />
      <div className="app-shell">
        <Navbar onMenu={() => setOpen(true)} health={health} />
        <main id="main-content" className="main-content">
          <Routes>
            <Route path="/" element={<Home health={health} />} />
            <Route path="/login" element={<Login />} />
            <Route element={<ProtectedRoutes />}>
              <Route path="/analyze/nsfw" element={<NsfwAnalyzer />} />
              <Route path="/analyze/similarity" element={<SimilarityChecker />} />
              <Route path="/analyze/combined" element={<CombinedChecker />} />
              <Route path="/history" element={<History />} />
            </Route>
            <Route element={<ProtectedRoutes admin />}>
              <Route path="/admin" element={<AdminDashboard />} />
            </Route>
            <Route
              path="*"
              element={
                <div className="table-empty">
                  <h1>Page not found</h1>
                  <p>This address doesn’t point to a Sentinel workspace page.</p>
                  <Link className="button primary" to="/">
                    Return to Overview
                  </Link>
                </div>
              }
            />
          </Routes>
        </main>
      </div>
    </>
  );
}
