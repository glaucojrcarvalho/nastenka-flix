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
        <p className="eyebrow">Only for Nastenka</p>
        <h1>This is my place.</h1>
        <p>
          My favorite stories, my comfort rewatches, my own little platform waiting exactly the way I like it.
        </p>
        <div className="feature-points">
          <div className="feature-point">
            <strong>My forever rewatches</strong>
            <span>The series I never get tired of, all in one place.</span>
          </div>
          <div className="feature-point">
            <strong>Right where I left off</strong>
            <span>Every pause is remembered, so the next episode night starts smoothly.</span>
          </div>
          <div className="feature-point">
            <strong>Made just for me</strong>
            <span>A private little streaming world that feels personal from the first click.</span>
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
          <input placeholder="my username" value={username} onChange={(event) => setUsername(event.target.value)} />
        </label>
        <label>
          Password
          <input
            placeholder="my password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        <div className="login-note">
          <span>My private entrance.</span>
        </div>
        {error ? <p className="form-error">{error}</p> : null}
        <button className="primary-button" disabled={isSubmitting} type="submit">
          {isSubmitting ? 'Opening my space...' : 'Enter my Nastenka Flix'}
        </button>
      </form>
    </section>
  );
}
