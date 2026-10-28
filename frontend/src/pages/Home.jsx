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
        <span className="version-label">SENTINAL / 1.0</span>
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
