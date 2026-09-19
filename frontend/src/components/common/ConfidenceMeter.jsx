export default function ConfidenceMeter({ value, label = 'Safe confidence' }) {
  const hasValue = typeof value === 'number';
  const pct = hasValue ? Math.max(0, Math.min(100, value)) : 0;
  // Circumference: 2 * PI * 64 = 402.12
  const circumference = 402.12;
  const strokeDash = (pct / 100) * circumference;

  const isSafe = pct >= 80;
  const isMid = pct >= 50 && pct < 80;

  return (
    <div className="confidence">
      <svg
        viewBox="0 0 160 160"
        role="img"
        aria-label={hasValue ? `${label}: ${value.toFixed(1)} percent` : `${label}: not evaluated`}
      >
        <defs>
          <linearGradient id="appleRingGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            {isSafe ? (
              <>
                <stop offset="0%" stopColor="#30d158" />
                <stop offset="100%" stopColor="#00c853" />
              </>
            ) : isMid ? (
              <>
                <stop offset="0%" stopColor="#ffd60a" />
                <stop offset="100%" stopColor="#ff9f0a" />
              </>
            ) : (
              <>
                <stop offset="0%" stopColor="#2997ff" />
                <stop offset="100%" stopColor="#0071e3" />
              </>
            )}
          </linearGradient>
        </defs>
        <circle className="dial-track" cx="80" cy="80" r="64" />
        <circle
          className="dial-value"
          cx="80"
          cy="80"
          r="64"
          stroke="url(#appleRingGrad)"
          strokeDasharray={`${hasValue ? strokeDash : 0} ${circumference}`}
          strokeLinecap="round"
        />
      </svg>
      <div>
        <strong>
          {hasValue ? value.toFixed(1) : '—'}
          {hasValue && <small>%</small>}
        </strong>
        <span>{label}</span>
      </div>
    </div>
  );
}
