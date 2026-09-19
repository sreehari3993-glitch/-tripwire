import React from 'react'
import { ShieldCheck, AlertCircle, Info } from 'lucide-react'

export function StatusBadge({ status }) {
  const norm = (status || '').toLowerCase()
  const map = {
    tripwire: { cls: 'badge-tripwire', label: '🔴 TRIPWIRE', color: '#ef4444' },
    monitoring: { cls: 'badge-monitor', label: '🟡 MONITORING', color: '#f59e0b' },
    watch: { cls: 'badge-monitor', label: '🟠 WATCH', color: '#fb923c' },
    recovering: { cls: 'badge-recovering', label: '🟣 RECOVERING', color: '#a855f7' },
    normal: { cls: 'badge-normal', label: '🟢 NORMAL', color: '#10b981' },
    resolving: { cls: 'badge-recovering', label: '🟣 RECOVERING', color: '#a855f7' },
    resolved: { cls: 'badge-normal', label: '✅ RESOLVED', color: '#10b981' },
    active: { cls: 'badge-tripwire', label: '🔴 ACTIVE', color: '#ef4444' },
  }
  const info = map[norm] || { cls: 'badge-normal', label: status?.toUpperCase() || 'NORMAL', color: '#10b981' }
  return (
    <span
      className={`badge ${info.cls}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 5,
        padding: '3px 9px',
        borderRadius: 6,
        fontSize: '11px',
        fontWeight: 700,
        letterSpacing: '0.4px',
        textTransform: 'uppercase'
      }}
    >
      {info.label}
    </span>
  )
}

export function VelocityLabel({ velocity }) {
  const up2 = velocity === '↗↗'
  const up1 = velocity === '↗'
  const flat = velocity === '→'
  const dn1 = velocity === '↘'
  const dn2 = velocity === '↘↘'

  let cls = 'velocity-flat'
  let label = 'Stable'
  if (up2) { cls = 'velocity-up'; label = 'Strong Recovery' }
  else if (up1) { cls = 'velocity-up'; label = 'Improving' }
  else if (dn2) { cls = 'velocity-down2'; label = 'Rapid Drift' }
  else if (dn1) { cls = 'velocity-down'; label = 'Mild Drift' }

  return (
    <span className={`velocity ${cls}`} title={`Trajectory: ${label}`} style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
      <span>{velocity}</span>
      <span style={{ fontSize: 10, opacity: 0.75, fontWeight: 500 }}>{label}</span>
    </span>
  )
}

export function DVIBar({ dvi }) {
  const val = Math.min(Math.max(Number(dvi) || 0, 0), 100)
  const color =
    val >= 70 ? '#ef4444' :
      val >= 50 ? '#f59e0b' : '#10b981'

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, minWidth: 140 }}>
      <div style={{
        flex: 1,
        height: 6,
        background: 'rgba(255,255,255,0.06)',
        borderRadius: 3,
        overflow: 'hidden',
        position: 'relative'
      }}>
        {/* Monitoring tick at 50% */}
        <div style={{ position: 'absolute', left: '50%', top: 0, bottom: 0, width: 1, background: 'rgba(245,158,11,0.4)', zIndex: 1 }} />
        {/* Tripwire tick at 70% */}
        <div style={{ position: 'absolute', left: '70%', top: 0, bottom: 0, width: 1, background: 'rgba(239,68,68,0.5)', zIndex: 1 }} />
        <div
          style={{
            width: `${val}%`,
            height: '100%',
            background: color,
            borderRadius: 3,
            boxShadow: `0 0 6px ${color}60`,
            transition: 'width 0.6s cubic-bezier(0.4,0,0.2,1)'
          }}
        />
      </div>
      <span style={{
        fontSize: 12,
        fontWeight: 800,
        color,
        fontFamily: 'var(--font-mono)',
        width: 32,
        textAlign: 'right'
      }}>
        {Math.round(val)}
      </span>
    </div>
  )
}

export function PrototypeThresholdBadge() {
  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 6,
      background: 'rgba(99,102,241,0.08)',
      border: '1px solid rgba(99,102,241,0.25)',
      borderRadius: 6,
      padding: '4px 10px',
      fontSize: 11,
      color: 'var(--brand-glow)',
      fontWeight: 500
    }}>
      <Info size={12} />
      <span>Prototype Threshold: <strong style={{ color: '#ef4444' }}>&ge;70 Tripwire</strong> · <strong style={{ color: '#f59e0b' }}>50–69 Monitor</strong> · <strong style={{ color: '#10b981' }}>&lt;50 Normal</strong></span>
    </div>
  )
}

export function HumanOverrideNote() {
  return (
    <div style={{
      background: 'rgba(16,185,129,0.06)',
      border: '1px solid rgba(16,185,129,0.2)',
      borderRadius: 8,
      padding: '10px 14px',
      fontSize: 12,
      color: 'var(--text-secondary)',
      display: 'flex',
      alignItems: 'center',
      gap: 8,
      lineHeight: 1.5
    }}>
      <ShieldCheck size={16} color="var(--color-normal)" style={{ flexShrink: 0 }} />
      <span>
        <strong>Human Override Active:</strong> Tripwire supports human override because behavioral signals can have legitimate explanations (medical leave, approved college activity).
      </span>
    </div>
  )
}

export function Spinner({ size = 24 }) {
  return (
    <div
      style={{
        width: size, height: size,
        border: '2px solid rgba(99,102,241,0.2)',
        borderTopColor: 'var(--brand-primary)',
        borderRadius: '50%',
        animation: 'spin 0.7s linear infinite'
      }}
    />
  )
}

export function LoadingScreen({ text = 'Loading...' }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 300, gap: 16 }}>
      <Spinner size={32} />
      <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>{text}</span>
    </div>
  )
}
