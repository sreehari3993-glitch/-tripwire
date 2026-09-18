import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useModals } from '../context/ModalContext'
import {
  LayoutDashboard, Users, Bell, LogOut, Shield, Activity,
  Sparkles, Layers, ShieldCheck, Scale
} from 'lucide-react'

export default function Sidebar() {
  const { mentor, logout } = useAuth()
  const { openDemo, openComparison, openPrivacy, openValidation } = useModals()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/students', icon: Users, label: 'Students' },
    { to: '/alerts', icon: Bell, label: 'Tripwire Alerts' },
  ]

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="logo">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 10,
            background: 'linear-gradient(135deg, #6366f1, #4338ca)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 16px rgba(99, 102, 241, 0.4)',
            flexShrink: 0
          }}>
            <Activity size={17} color="#fff" />
          </div>
          <div>
            <span className="logo-title" style={{ letterSpacing: '1px' }}>TRIPWIRE</span>
          </div>
        </div>
        <div className="logo-sub">Silent Disengagement Early-Warning System</div>
      </div>

      {/* Main Navigation */}
      <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 4 }}>
        <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.8, padding: '8px 12px 4px' }}>
          Monitoring Workspace
        </div>
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
            id={`nav-${label.toLowerCase().replace(/\s+/g, '-')}`}
          >
            <Icon className="nav-icon" size={16} />
            {label}
          </NavLink>
        ))}

        {/* Hackathon Features / Modal Triggers */}
        <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.8, padding: '16px 12px 4px' }}>
          Interactive & Research
        </div>

        {/* Highlighted Demo Mode Action Button */}
        <button
          id="sidebar-demo-btn"
          onClick={openDemo}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            width: '100%',
            padding: '10px 12px',
            borderRadius: 'var(--radius-md)',
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.18), rgba(139, 92, 246, 0.12))',
            border: '1px solid rgba(99, 102, 241, 0.35)',
            color: '#c7d2fe',
            fontSize: 13,
            fontWeight: 700,
            cursor: 'pointer',
            textAlign: 'left',
            transition: 'all 0.2s ease',
            boxShadow: '0 0 12px rgba(99, 102, 241, 0.15)'
          }}
          onMouseEnter={e => {
            e.currentTarget.style.background = 'linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(139, 92, 246, 0.2))'
            e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.6)'
          }}
          onMouseLeave={e => {
            e.currentTarget.style.background = 'linear-gradient(135deg, rgba(99, 102, 241, 0.18), rgba(139, 92, 246, 0.12))'
            e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.35)'
          }}
        >
          <Sparkles size={16} color="var(--brand-glow)" />
          <span>Interactive Demo Mode</span>
        </button>

        {/* System Comparison */}
        <button
          id="sidebar-comparison-btn"
          onClick={openComparison}
          className="nav-item"
          style={{ width: '100%', background: 'transparent', border: 'none', cursor: 'pointer', textAlign: 'left' }}
        >
          <Layers className="nav-icon" size={16} />
          System Comparison
        </button>

        {/* Privacy & Ethics */}
        <button
          id="sidebar-privacy-btn"
          onClick={openPrivacy}
          className="nav-item"
          style={{ width: '100%', background: 'transparent', border: 'none', cursor: 'pointer', textAlign: 'left' }}
        >
          <ShieldCheck className="nav-icon" size={16} />
          Privacy & Ethics
        </button>

        {/* Model Validation (Weights) */}
        <button
          id="sidebar-validation-btn"
          onClick={openValidation}
          className="nav-item"
          style={{ width: '100%', background: 'transparent', border: 'none', cursor: 'pointer', textAlign: 'left' }}
        >
          <Scale className="nav-icon" size={16} />
          Model Validation (Weights)
        </button>
      </nav>


      {/* Mentor Profile / Bottom */}
      {mentor && (
        <div style={{ padding: '0 16px 16px', borderTop: '1px solid var(--border-subtle)', paddingTop: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
            <div style={{
              width: 32, height: 32, borderRadius: '50%',
              background: 'linear-gradient(135deg, #6366f1, #4338ca)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 13, fontWeight: 700, color: '#fff', flexShrink: 0
            }}>
              {mentor.name?.charAt(0) || 'M'}
            </div>
            <div style={{ overflow: 'hidden' }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {mentor.name}
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{mentor.mentor_id} · Faculty</div>
            </div>
          </div>

          <div style={{
            background: 'rgba(16,185,129,0.08)',
            border: '1px solid rgba(16,185,129,0.15)',
            borderRadius: 8, padding: '8px 10px',
            display: 'flex', alignItems: 'center', gap: 6,
            marginBottom: 10
          }}>
            <Shield size={12} color="var(--color-normal)" />
            <span style={{ fontSize: 11, color: 'var(--color-normal)', fontWeight: 600 }}>
              Authorized Mentor
            </span>
          </div>

          <button
            id="logout-btn"
            className="btn btn-ghost"
            style={{ width: '100%', fontSize: 12, padding: '8px 12px' }}
            onClick={handleLogout}
          >
            <LogOut size={14} />
            Sign out
          </button>
        </div>
      )}
    </aside>
  )
}
