import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ArrowRight, Check, Eye, EyeOff, ShieldCheck } from 'lucide-react';
import { useAuth } from '../auth';
import { errorMessage } from '../api';
import { ErrorNotice } from '../components/common/Ui';

export default function Login() {
  const [register, setRegister] = useState(false);
  const [visible, setVisible] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  const { authenticate, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setPending(true);
    const form = new FormData(e.currentTarget);
    try {
      await authenticate(register ? 'register' : 'login', Object.fromEntries(form));
      navigate(location.state?.from || '/analyze/combined', { replace: true });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setPending(false);
    }
  };

  return (
    <section className="auth-layout">
      <div className="auth-intro">
        <div className="auth-shield">
          <ShieldCheck size={40} strokeWidth={1.5} />
        </div>
        <p className="eyebrow">Better Signals. Better Decisions.</p>
        <h1>
          Clarity starts
          <br />
          with context.
        </h1>
        <p>Your secure workspace for automated content safety and vector-indexed visual intelligence.</p>
        <ul>
          {[
            'Analyze images and video in a unified studio',
            'Inspect multimodal evidence behind every assessment',
            'Maintain a private, searchable history of your decisions'
          ].map((text) => (
            <li key={text}>
              <Check size={16} />
              <span>{text}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="auth-card">
        <div className="auth-tabs" role="group" aria-label="Account access">
          <button
            type="button"
            className={!register ? 'selected' : ''}
            onClick={() => {
              setRegister(false);
              setError('');
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            className={register ? 'selected' : ''}
            onClick={() => {
              setRegister(true);
              setError('');
            }}
          >
            Create Account
          </button>
        </div>

        <h2>{register ? 'Your workspace awaits.' : 'Welcome back.'}</h2>
        <p>{register ? 'Create your Sentinel credentials to begin.' : 'Sign in to access your content intelligence console.'}</p>

        {user ? (
          <>
            <div className="notice">You are currently signed in as {user.username}.</div>
            <Link className="button primary full-width" to="/analyze/combined">
              <span>Open Analysis Studio</span>
              <ArrowRight size={16} />
            </Link>
          </>
        ) : (
          <form onSubmit={submit}>
            <label htmlFor="username">Username</label>
            <input
              id="username"
              name="username"
              autoComplete="username"
              required
              minLength={3}
              maxLength={50}
              placeholder="Username"
            />

            {register && (
              <>
                <label htmlFor="email">Email Address</label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  maxLength={100}
                  placeholder="name@apple.com"
                />
              </>
            )}

            <label htmlFor="password">Password</label>
            <div className="password-field">
              <input
                id="password"
                name="password"
                type={visible ? 'text' : 'password'}
                autoComplete={register ? 'new-password' : 'current-password'}
                required
                minLength={register ? 12 : 1}
                maxLength={128}
                placeholder={register ? 'At least 12 characters' : 'Your password'}
              />
              <button
                type="button"
                className="icon-button"
                onClick={() => setVisible(!visible)}
                aria-label={visible ? 'Hide password' : 'Show password'}
              >
                {visible ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>

            <ErrorNotice>{error}</ErrorNotice>

            <button type="submit" className="button primary full-width" disabled={pending}>
              <span>{pending ? 'Connecting…' : register ? 'Create Account' : 'Sign In'}</span>
              <ArrowRight size={16} />
            </button>
          </form>
        )}

        <div className="auth-note">
          <ShieldCheck size={14} />
          <span>Analysis records and vectors are strictly scoped to your account.</span>
        </div>
      </div>
    </section>
  );
}
