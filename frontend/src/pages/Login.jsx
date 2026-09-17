import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Activity, Eye, EyeOff, Shield } from 'lucide-react'

export default function Login() {
  const { login, loading } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    const result = await login(username, password)
    if (result.success) {
      navigate('/dashboard')
    } else {
      setError(result.error)
    }
  }

  return (
    <div className="login-root">
      {/* Background orbs */}
      <div className="login-bg-orb" style={{
        width: 600, height: 600,
        background: 'radial-gradient(circle, #6366f1, #4338ca)',
        top: '-200px', left: '-200px'
      }} />
      <div className="login-bg-orb" style={{
        width: 400, height: 400,
        background: 'radial-gradient(circle, #ef4444, #dc2626)',
        bottom: '-150px', right: '-100px'
      }} />

      <div className="login-card">
        <div className="login-logo">
          <div style={{
            width: 56, height: 56,
            borderRadius: 16,
            background: 'linear-gradient(135deg, #6366f1, #4338ca)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 16px',
            boxShadow: '0 8px 24px rgba(99,102,241,0.35)'
          }}>
            <Activity size={24} color="#fff" />
          </div>
          <div className="login-title">TRIPWIRE</div>
          <div className="login-tagline">
            Faculty Early-Intervention Dashboard<br />
            <span style={{ color: 'var(--text-muted)', fontSize: 11, fontStyle: 'italic' }}>
              Detects patterns, not personalities.
            </span>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="faculty-id">Faculty ID</label>
            <input
              id="faculty-id"
              className="input"
              type="text"
              placeholder="e.g. FAC001"
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <div style={{ position: 'relative' }}>
              <input
                id="password"
                className="input"
                type={showPass ? 'text' : 'password'}
                placeholder="Enter password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                style={{ paddingRight: 44 }}
              />
              <button
                type="button"
                onClick={() => setShowPass(!showPass)}
                style={{
                  position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)',
                  background: 'none', border: 'none', cursor: 'pointer',
                  color: 'var(--text-muted)', display: 'flex', alignItems: 'center'
                }}
              >
                {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {error && (
            <div style={{
              background: 'rgba(239,68,68,0.1)',
              border: '1px solid rgba(239,68,68,0.3)',
              borderRadius: 8, padding: '10px 14px',
              color: 'var(--color-tripwire)',
              fontSize: 13, marginBottom: 16
            }}>
              {error}
            </div>
          )}

          <button
            id="login-submit"
            className="btn btn-primary w-full"
            type="submit"
            disabled={loading}
            style={{ justifyContent: 'center', marginTop: 8 }}
          >
            {loading ? (
              <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin 0.7s linear infinite' }} />
                Signing in...
              </span>
            ) : 'Sign In'}
          </button>
        </form>

        <div className="login-hint">
          <Shield size={11} style={{ display: 'inline', marginRight: 4 }} />
          Demo credentials: <strong>FAC001</strong> / <strong>tripwire123</strong>
        </div>

        <div style={{
          marginTop: 24,
          padding: '12px',
          background: 'rgba(99,102,241,0.05)',
          border: '1px solid rgba(99,102,241,0.15)',
          borderRadius: 8,
          fontSize: 11,
          color: 'var(--text-muted)',
          textAlign: 'center',
          lineHeight: 1.6
        }}>
          🔒 Student behavioral data is confidential.<br />
          Tripwire alerts are visible only to assigned mentors.
        </div>
      </div>
    </div>
  )
}
