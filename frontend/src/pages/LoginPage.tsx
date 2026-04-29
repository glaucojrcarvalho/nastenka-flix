import { useState } from 'react';

import { login, type LoginResponse } from '../api/client';

type LoginPageProps = {
  onLogin: (result: LoginResponse) => Promise<void> | void;
};

export function LoginPage({ onLogin }: LoginPageProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  return (
    <section className="login-panel">
      <div className="login-panel__intro">
        <p className="eyebrow">Birthday edition</p>
        <h1>Your private streaming space.</h1>
        <p>
          Three favorite series. Endless rewatch energy. A private little corner of the internet made to feel like her own platform.
        </p>
        <div className="feature-points">
          <div className="feature-point">
            <strong>Curated comfort shows</strong>
            <span>Only the series she genuinely returns to again and again.</span>
          </div>
          <div className="feature-point">
            <strong>Resume without friction</strong>
            <span>Playback progress stays saved, so the next rewatch starts exactly where it should.</span>
          </div>
          <div className="feature-point">
            <strong>Private by design</strong>
            <span>Self-hosted, simple, and meant for one special viewer first.</span>
          </div>
        </div>
      </div>
      <form
        className="login-form"
        onSubmit={async (event) => {
          event.preventDefault();
          setError(null);
          setIsSubmitting(true);
          try {
            const result = await login(username, password);
            await onLogin(result);
          } catch (submissionError) {
            setError(submissionError instanceof Error ? submissionError.message : 'Unable to sign in');
          } finally {
            setIsSubmitting(false);
          }
        }}
      >
        <label>
          Username
          <input placeholder="username" value={username} onChange={(event) => setUsername(event.target.value)} />
        </label>
        <label>
          Password
          <input
            placeholder="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        <div className="login-note">
          <span>Private access only.</span>
        </div>
        {error ? <p className="form-error">{error}</p> : null}
        <button className="primary-button" disabled={isSubmitting} type="submit">
          {isSubmitting ? 'Opening Nastenka Flix...' : 'Enter Nastenka Flix'}
        </button>
      </form>
    </section>
  );
}
