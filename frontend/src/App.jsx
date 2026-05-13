import { useState } from 'react'

import { loginUser, registerUser } from './api'

function App() {
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('user@example.com')
  const [password, setPassword] = useState('testtest')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setMessage('')
    setError('')
    setIsSubmitting(true)

    try {
      if (mode === 'login') {
        const data = await loginUser({ email, password })
        localStorage.setItem('token', data.token)
        setMessage('login successful. token stored.')
      } else {
        const data = await registerUser({ email, password })
        setMessage(`registered ${data.email}. you can log in now.`)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card" aria-labelledby="auth-title">
        <div className="auth-header">
          <p className="eyebrow">paper trading</p>
          <h1 id="auth-title">{mode === 'login' ? 'log in' : 'register'}</h1>
          <p className="subtitle">
            connect to your local FastAPI backend.
          </p>
        </div>

        <div className="mode-tabs" aria-label="auth mode">
          <button
            className={mode === 'login' ? 'tab active' : 'tab'}
            type="button"
            onClick={() => setMode('login')}
          >
            login
          </button>
          <button
            className={mode === 'register' ? 'tab active' : 'tab'}
            type="button"
            onClick={() => setMode('register')}
          >
            register
          </button>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            email
            <input
              autoComplete="email"
              onChange={(event) => setEmail(event.target.value)}
              placeholder="user@example.com"
              type="email"
              value={email}
            />
          </label>

          <label>
            password
            <input
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              minLength={8}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="at least 8 characters"
              type="password"
              value={password}
            />
          </label>

          <button className="submit-button" disabled={isSubmitting} type="submit">
            {isSubmitting ? 'working...' : mode}
          </button>
        </form>

        {message && <p className="status success">{message}</p>}
        {error && <p className="status error">{error}</p>}
      </section>
    </main>
  )
}

export default App
