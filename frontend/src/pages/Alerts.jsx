import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { alertsAPI } from '../api/client'
import { StatusBadge, LoadingScreen, PrototypeThresholdBadge, HumanOverrideNote } from '../components/Shared'
import { Bell, AlertTriangle, Clock, ChevronRight, ShieldOff } from 'lucide-react'

export default function Alerts() {
  const navigate = useNavigate()
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    alertsAPI.list()
      .then(res => setAlerts(res.data.alerts))
      .finally(() => setLoading(false))
  }, [])

  const active   = alerts.filter(a => a.status === 'active')
  const resolved = alerts.filter(a => a.status !== 'active')

  if (loading) return <LoadingScreen text="Loading alerts..." />

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 className="page-title">Tripwire Alerts</h1>
          <p className="page-subtitle">Students whose behavioral patterns have crossed the intervention threshold</p>
        </div>
        <PrototypeThresholdBadge />
      </div>

      <div className="page-body">
        <HumanOverrideNote />

        {alerts.length === 0 && (
          <div className="empty-state">
            <div style={{ fontSize: 48, marginBottom: 12 }}>✅</div>
            <div style={{ fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>No active alerts</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>All students are within normal behavioral ranges</div>
          </div>
        )}

        {active.length > 0 && (
          <>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--color-tripwire)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
              <AlertTriangle size={12} /> Active Tripwires ({active.length})
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 28 }}>
              {active.map(alert => (
                <AlertCard key={alert.alert_id} alert={alert} navigate={navigate} />
              ))}
            </div>
          </>
        )}

        {resolved.length > 0 && (
          <>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 12 }}>
              Resolved Interventions ({resolved.length})
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {resolved.map(alert => (
                <AlertCard key={alert.alert_id} alert={alert} navigate={navigate} resolved />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function AlertCard({ alert, navigate, resolved = false }) {
  const isActive = !resolved && alert.status === 'active'

  return (
    <div
      id={`alert-card-${alert.alert_id}`}
      className="card card-p"
      style={{
        cursor: 'pointer',
        border: isActive ? '1px solid rgba(239,68,68,0.25)' : '1px solid var(--border-subtle)',
        background: isActive ? 'linear-gradient(135deg, rgba(239,68,68,0.05), rgba(220,38,38,0.03))' : 'var(--bg-card)',
        transition: 'all 0.2s ease',
        animation: isActive ? 'pulse-glow 3s ease-in-out infinite' : 'none'
      }}
      onClick={() => navigate(`/alerts/${alert.alert_id}`)}
      onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-2px)'}
      onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        {/* Left: Student info */}
        <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
          <div style={{
            width: 44, height: 44, borderRadius: 12,
            background: isActive ? 'rgba(239,68,68,0.15)' : 'var(--bg-elevated)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexShrink: 0
          }}>
            {isActive
              ? <AlertTriangle size={20} color="var(--color-tripwire)" />
              : <ShieldOff size={20} color="var(--text-muted)" />
            }
          </div>
          <div>
            <div style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: 15 }}>
              {alert.student_name}
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
              {alert.section} · Alert #{alert.alert_id}
            </div>
          </div>
        </div>

        {/* Center: DVI + factors */}
        <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 28, fontWeight: 800, fontFamily: 'var(--font-mono)', color: isActive ? 'var(--color-tripwire)' : 'var(--text-muted)', lineHeight: 1 }}>
              {Math.round(alert.dvi_score)}
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>DVI</div>
          </div>

          <div style={{ display: 'flex', gap: 8 }}>
            {[
              { label: 'Att', score: alert.attendance_drift, color: '#6366f1' },
              { label: 'Sub', score: alert.submission_drift, color: '#f59e0b' },
              { label: 'LMS', score: alert.engagement_drift, color: '#06b6d4' }
            ].map(({ label, score, color }) => (
              <div key={label} style={{ textAlign: 'center' }}>
                <div style={{ width: 4, height: Math.max(4, score * 0.4), background: color, borderRadius: 2, margin: '0 auto 3px', maxHeight: 40 }} />
                <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{label}</div>
                <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color, fontWeight: 600 }}>{Math.round(score)}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Status + date */}
        <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', gap: 6, alignItems: 'flex-end' }}>
          <StatusBadge status={resolved ? 'resolved' : alert.status} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 11, color: 'var(--text-muted)' }}>
            <Clock size={11} />
            {new Date(alert.trigger_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
          </div>
          {alert.excused_flag && (
            <span style={{ fontSize: 10, color: 'var(--color-monitor)', background: 'rgba(245,158,11,0.1)', padding: '2px 6px', borderRadius: 4 }}>
              Partially excused
            </span>
          )}
          <ChevronRight size={16} color="var(--text-muted)" />
        </div>
      </div>
    </div>
  )
}
