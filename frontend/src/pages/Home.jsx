import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  ArrowUpRight,
  ScanLine,
  ShieldCheck,
  Fingerprint,
  Layers3,
  Users,
  Flag,
  Check,
  Radar,
  FileImage,
  ScanText
} from 'lucide-react';
import { api } from '../api';
import MetricCard from '../components/common/MetricCard';

const tools = [
  {
    path: 'nsfw',
    number: '01',
    icon: ShieldCheck,
    title: 'Safety Analyzer',
    description: 'Detect visual risks and evaluate text embedded directly inside your media.',
    tags: ['Visual Classification', 'OCR Text Extraction']
  },
  {
    path: 'similarity',
    number: '02',
    icon: Fingerprint,
    title: 'Similarity Checker',
    description: 'Find semantic matches and uncover duplicates across your visual library.',
    tags: ['CLIP Embeddings', 'Vector Search']
  },
  {
    path: 'combined',
    number: '03',
    icon: Layers3,
    title: 'Combined Analysis',
    description: 'Bring safety signals and visual similarity into one unified assessment.',
    tags: ['Full Pipeline', 'Unified Report']
  }
];

export default function Home({ health }) {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    api
      .get('/metrics/public')
      .then((r) => setMetrics(r.data))
      .catch(() => setMetrics(null));
  }, []);

  return (
    <div className="home-page">
      <div className="overview-kicker">
        <span className="eyebrow">Your Content. Understood.</span>
        <span className="version-label">SENTINEL / 1.0</span>
      </div>

      <section className="hero">
        <div className="hero-copy">
          <div className="hero-label">
            <span className="status-dot" />
            <span>MULTIMODAL CONTENT INTELLIGENCE</span>
          </div>
          <h1>
            Intelligent defense.
            <br />
            <span>Unbounded content.</span>
          </h1>
          <p>
            See beyond the pixels. Detect content risks, uncover visual similarities, and turn
            complex signals into confident, accountable decisions.
          </p>
          <div className="hero-actions">
            <Link className="button primary" to="/analyze/combined">
              <span>Start Analysis</span>
              <ArrowRight size={16} />
            </Link>
            <Link className="button secondary" to="/history">
              <span>View History</span>
              <ArrowUpRight size={15} />
            </Link>
          </div>
          <p className="hero-footnote">
            <ShieldCheck size={14} />
            <span>Intelligent defense against unbounded content</span>
          </p>
        </div>

        <div className="sentinel-visual" aria-label="Illustration of Sentinel content pipeline">
          <div className="visual-grid" />
          <span className="visual-coordinate coordinate-top">SNTL / VISION CORE</span>
          <div className="scan-orbit orbit-outer" />
          <div className="scan-orbit orbit-inner" />
          <div className="core-shield">
            <ShieldCheck size={52} strokeWidth={1.5} />
          </div>
          <span className="orbit-node node-one" />
          <span className="orbit-node node-two" />
          <div className="visual-chip chip-top">
            <ScanLine size={16} />
            <div>
              VISUAL SAFETY
              <small>Content Classification</small>
            </div>
          </div>
          <div className="visual-chip chip-bottom">
            <Fingerprint size={16} />
            <div>
              SIMILARITY ENGINE
              <small>Semantic Understanding</small>
            </div>
          </div>
          <span className="visual-coordinate coordinate-bottom">IMAGE + VIDEO + TEXT</span>
        </div>
      </section>

      <section className="metrics-grid" aria-label="Live platform statistics">
        <MetricCard
          label="Total Analyses"
          value={metrics?.total_scans}
          icon={ScanLine}
          caption="Media processed across platform"
        />
        <MetricCard
          label="Flagged Content"
          value={metrics?.flagged_count}
          icon={Flag}
          caption="Signals identified for moderation"
        />
        <MetricCard
          label="Registered Members"
          value={metrics?.registered_users}
          icon={Users}
          caption="Accounts connected to Sentinel"
        />
      </section>

      <section className="tools-section">
        <div className="section-heading">
          <div>
            <h2>Analysis Toolkit</h2>
            <p>Choose a dedicated lens or run the full pipeline.</p>
          </div>
          <span className="subtle-label">THREE TOOLS. ONE WORKSPACE.</span>
        </div>
        <div className="tool-grid">
          {tools.map(({ path, number, icon: Icon, title, description, tags }) => (
            <Link className={`tool-card tool-${path}`} to={`/analyze/${path}`} key={path}>
              <div className="tool-card-top">
                <span className="tool-icon">
                  <Icon size={20} />
                </span>
                <span>{number}</span>
              </div>
              <h3>
                <span>{title}</span>
                <ArrowUpRight size={18} />
              </h3>
              <p>{description}</p>
              <div className="tool-tags">
                {tags.map((tag) => (
                  <span key={tag}>{tag}</span>
                ))}
              </div>
            </Link>
          ))}
        </div>
      </section>

      <section className="workflow-strip">
        <div>
          <Radar size={22} />
          <h2>From media to meaning.</h2>
          <p>A structured path to informed moderation.</p>
        </div>
        <ol>
          <li>
            <FileImage size={18} />
            <span>
              <strong>Upload</strong>
              <small>Image or video file</small>
            </span>
          </li>
          <li>
            <ScanText size={18} />
            <span>
              <strong>Analyze</strong>
              <small>Multimodal safety signals</small>
            </span>
          </li>
          <li>
            <Check size={18} />
            <span>
              <strong>Decide</strong>
              <small>Contextual evidence</small>
            </span>
          </li>
        </ol>
      </section>

      <footer className="page-footer">
        <span>
          <ShieldCheck size={14} />
          <span>Private account history · Human-centered moderation</span>
        </span>
        <span>{health ? 'Connected to Sentinel API' : 'API Standby'}</span>
      </footer>
    </div>
  );
}
