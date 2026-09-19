import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine
} from 'recharts'
import { studentsAPI, interventionsAPI } from '../api/client'
import { StatusBadge, VelocityLabel, Spinner, LoadingScreen, HumanOverrideNote, PrototypeThresholdBadge } from '../components/Shared'
import LogTelemetryModal from '../components/LogTelemetryModal'
import {
  ArrowLeft, AlertTriangle, TrendingDown, TrendingUp, Clock,
  BookOpen, Sunrise, Activity, Shield, ShieldCheck, HelpCircle,
  CheckCircle2, Plus, Calendar, UserCheck, AlertCircle, Zap, RotateCcw
} from 'lucide-react'
import toast from 'react-hot-toast'


// ── DVI Gauge (SVG radial) ─────────────────────────────────────
function DVIGauge({ dvi }) {
  const size = 160
  const strokeWidth = 14
  const radius = (size - strokeWidth) / 2
  const circumference = Math.PI * radius
  const progress = Math.min(Math.max(dvi || 0, 0), 100) / 100
  const offset = circumference - progress * circumference

  const color =
    dvi >= 70 ? '#ef4444' :
      dvi >= 50 ? '#f59e0b' : '#10b981'

  return (
    <div style={{ textAlign: 'center' }}>
      <svg width={size} height={size / 2 + 32} viewBox={`0 0 ${size} ${size / 2 + 20}`}>
        {/* Background arc */}
        <path
          d={`M ${strokeWidth / 2} ${size / 2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${size / 2}`}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        {/* Foreground arc */}
        <path
          d={`M ${strokeWidth / 2} ${size / 2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${size / 2}`}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 1s cubic-bezier(0.4,0,0.2,1), stroke 0.5s ease' }}
          filter={`drop-shadow(0 0 8px ${color}50)`}
        />
        <text
          x={size / 2} y={size / 2 + 4}
          textAnchor="middle"
          fontSize="28"
          fontWeight="900"
          fill={color}
          fontFamily="var(--font-mono)"
        >
          {Math.round(dvi)}
        </text>
        <text
          x={size / 2} y={size / 2 + 20}
          textAnchor="middle"
          fontSize="10"
          fill="#64748b"
          fontFamily="Inter, sans-serif"
          textTransform="uppercase"
          letterSpacing="1"
          fontWeight="600"
        >
          DVI / 100
        </text>
      </svg>
    </div>
  )
}

// ── Timeline ────────────────────────────────────────────────────
function Timeline({ events }) {
  if (!events || events.length === 0) {
    return <div style={{ color: 'var(--text-muted)', fontSize: 13, padding: 16 }}>No notable events in this period.</div>
  }

  const dotClass = {
    low: 'dot-low', medium: 'dot-medium',
    high: 'dot-high', critical: 'dot-critical', tripwire: 'dot-tripwire'
  }

  return (
    <div className="timeline">
      {events.map((evt, i) => (
        <div key={i} className="timeline-item" style={{
          animationDelay: `${i * 50}ms`,
          background: evt.type === 'tripwire' ? 'rgba(239,68,68,0.06)' : 'transparent',
          borderRadius: evt.type === 'tripwire' ? 8 : 0,
          padding: evt.type === 'tripwire' ? '8px 12px' : '4px 0'
        }}>
          <div className={`timeline-dot ${dotClass[evt.severity] || 'dot-low'}`} />
          <div className="timeline-date">{formatDate(evt.date)}</div>
          <div className="timeline-label" style={{
            color: evt.type === 'tripwire' ? 'var(--color-tripwire)' : 'var(--text-secondary)',
            fontWeight: evt.type === 'tripwire' ? 700 : 400
          }}>
            {evt.label}
          </div>
        </div>
      ))}
    </div>
  )
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
}

export default function StudentProfile() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [profile, setProfile] = useState(null)
  const [history, setHistory] = useState([])
  const [timeline, setTimeline] = useState([])
  const [interventions, setInterventions] = useState([])
  const [loading, setLoading] = useState(true)

  // Temporal Smoothing mode: 'smoothed' (EWMA alpha=0.3) vs 'raw' (daily telemetry)
  const [smoothingMode, setSmoothingMode] = useState('smoothed')

  // Excuse Modal state
  const [showExcuseModal, setShowExcuseModal] = useState(false)
  const [excuseStart, setExcuseStart] = useState('2026-09-08')
  const [excuseEnd, setExcuseEnd] = useState('2026-09-11')
  const [excuseReason, setExcuseReason] = useState('medical')
  const [excuseNotes, setExcuseNotes] = useState('')
  const [submittingExcuse, setSubmittingExcuse] = useState(false)

  // Pulse Modal state
  const [showPulseModal, setShowPulseModal] = useState(false)
  const [pulseRating, setPulseRating] = useState(2)
  const [pulseNote, setPulseNote] = useState('')
  const [submittingPulse, setSubmittingPulse] = useState(false)

  // Live Telemetry Modal state
  const [showTelemetryModal, setShowTelemetryModal] = useState(false)

  // Live Pitch Simulation state
  const [isSimulating, setIsSimulating] = useState(false)

  const handleSimulateDrift = async () => {
    try {
      setIsSimulating(true)
      const res = await studentsAPI.simulateDrift(id)
      toast.error(res.data.summary || 'Simulated behavioral drift: DVI crossed Tripwire!')
      await reloadData()
    } catch (e) {
      toast.error('Failed to simulate drift.')
    } finally {
      setIsSimulating(false)
    }
  }

  const handleSimulateRecovery = async () => {
    try {
      setIsSimulating(true)
      const res = await studentsAPI.simulateRecovery(id)
      toast.success(res.data.summary || 'Simulated mentor recovery: DVI normalized.')
      await reloadData()
    } catch (e) {
      toast.error('Failed to simulate recovery.')
    } finally {
      setIsSimulating(false)
    }
  }

  const handleSimulateReset = async () => {
    try {
      setIsSimulating(true)
      const res = await studentsAPI.simulateReset(id)
      toast.success(res.data.message || 'Simulation reset to baseline.')
      await reloadData()
    } catch (e) {
      toast.error('Failed to reset simulation.')
    } finally {
      setIsSimulating(false)
    }
  }

  const reloadData = () => {
    return Promise.all([
      studentsAPI.profile(id),
      studentsAPI.dviHistory(id, 28),
      studentsAPI.timeline(id),
      interventionsAPI.studentHistory(id)
    ]).then(([pRes, hRes, tRes, iRes]) => {
      setProfile(pRes.data)
      setHistory(hRes.data.history)
      setTimeline(tRes.data.events)
      setInterventions(iRes.data.interventions || [])
    })
  }

  useEffect(() => {
    setLoading(true)
    reloadData().finally(() => setLoading(false))
  }, [id])

  const handleApplyExcuse = async () => {
    setSubmittingExcuse(true)
    try {
      await studentsAPI.excuse(id, {
        start_date: excuseStart,
        end_date: excuseEnd,
        reason: excuseReason,
        notes: excuseNotes
      })
      toast.success('Human override applied: Leave marked as EXCUSED.')
      setShowExcuseModal(false)
      reloadData()
    } catch (e) {
      toast.error('Failed to apply human override.')
    } finally {
      setSubmittingExcuse(false)
    }
  }

  const handleApplyPulse = async () => {
    setSubmittingPulse(true)
    try {
      await studentsAPI.submitPulse(id, {
        rating: pulseRating,
        stuck_on: pulseNote
      })
      toast.success('Weekly pulse check logged successfully.')
      setShowPulseModal(false)
      reloadData()
    } catch (e) {
      toast.error('Failed to log pulse check.')
    } finally {
      setSubmittingPulse(false)
    }
  }

  if (loading) return <LoadingScreen text="Loading student behavioral profile..." />
  if (!profile) return <div className="page-body" style={{ padding: 32 }}>Student not found.</div>

  const { signals, baselines, what_changed, counterfactual } = profile

  const chartData = history.map((h, i) => ({
    date: i % 3 === 0 ? new Date(h.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : '',
    rawDate: h.date,
    dvi: smoothingMode === 'raw' ? (h.raw_dvi ?? h.dvi) : (h.smoothed_dvi ?? h.dvi),
    rawDvi: h.raw_dvi ?? h.dvi,
    smoothedDvi: h.smoothed_dvi ?? h.dvi,
    status: h.status
  }))

  const dviColor =
    profile.dvi >= 70 ? '#ef4444' :
      profile.dvi >= 50 ? '#f59e0b' :
        profile.status === 'recovering' ? '#a855f7' : '#10b981'

  return (
    <div>
      {/* Header */}
      <div className="page-header">
        <button className="back-btn" onClick={() => navigate(-1)}>
          <ArrowLeft size={14} /> Back to Directory
        </button>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <h1 className="page-title" style={{ margin: 0 }}>{profile.name}</h1>
              <StatusBadge status={profile.status} />
            </div>
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginTop: 6, flexWrap: 'wrap' }}>
              <span className="text-sm text-muted">Class: <strong style={{ color: '#fff' }}>{profile.section}</strong></span>
              <span style={{ color: 'var(--border-default)' }}>·</span>
              <span className="text-sm text-muted">Roll No: {profile.roll_no}</span>
              <span style={{ color: 'var(--border-default)' }}>·</span>
              <span className="text-sm text-muted" style={{ fontFamily: 'var(--font-mono)' }}>{profile.student_id}</span>
            </div>

            {/* Badges: Baseline Confidence + Status Duration + Pulse */}
            <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 8, flexWrap: 'wrap' }}>
              {profile.is_cold_start ? (
                <span style={{ padding: '3px 8px', borderRadius: 6, fontSize: 11, background: 'rgba(245,158,11,0.15)', color: '#f59e0b', border: '1px solid rgba(245,158,11,0.3)', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                  <AlertCircle size={11} /> Baseline: {profile.baseline_confidence}
                </span>
              ) : (
                <span style={{ padding: '3px 8px', borderRadius: 6, fontSize: 11, background: 'rgba(16,185,129,0.15)', color: '#10b981', border: '1px solid rgba(16,185,129,0.3)', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                  <CheckCircle2 size={11} /> Baseline: Established (100% Individual)
                </span>
              )}

              <span style={{ padding: '3px 8px', borderRadius: 6, fontSize: 11, background: 'rgba(99,102,241,0.15)', color: '#a5b4fc', border: '1px solid rgba(99,102,241,0.3)', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                <Clock size={11} /> {profile.weeks_in_status || 1} wk(s) in {profile.status.toUpperCase()}
              </span>

              {profile.pulse && (
                <span style={{ padding: '3px 8px', borderRadius: 6, fontSize: 11, background: 'rgba(168,85,247,0.15)', color: '#d8b4fe', border: '1px solid rgba(168,85,247,0.3)', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                  <span>{profile.pulse.rating <= 2 ? '😟' : profile.pulse.rating === 3 ? '😐' : '🙂'}</span> Pulse: {profile.pulse.rating}/5
                </span>
              )}
            </div>
          </div>

          <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
            <button
              id="log-telemetry-btn"
              className="btn btn-primary btn-sm"
              onClick={() => setShowTelemetryModal(true)}
              style={{ display: 'flex', alignItems: 'center', gap: 6 }}
            >
              <Activity size={14} /> Log Activity / Attendance
            </button>

            <button
              id="pulse-check-btn"
              className="btn btn-ghost btn-sm"
              onClick={() => setShowPulseModal(true)}
              style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#c084fc', border: '1px solid rgba(168,85,247,0.3)' }}
            >
              <span>💭</span> Weekly Pulse Check
            </button>

            <button
              id="excuse-leave-btn"
              className="btn btn-ghost btn-sm"
              onClick={() => setShowExcuseModal(true)}
              style={{ display: 'flex', alignItems: 'center', gap: 6 }}
            >
              <ShieldCheck size={14} color="var(--color-normal)" />
              Record Excused Leave
            </button>

            {profile.dvi < 70 ? (
              <button
                id="simulate-drift-btn"
                className="btn btn-ghost btn-sm"
                onClick={handleSimulateDrift}
                disabled={isSimulating}
                style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#ef4444', border: '1px solid rgba(239,68,68,0.35)' }}
                title="Inject live multi-day absences and delayed submissions to demonstrate instant early warning to judges"
              >
                <Zap size={13} /> {isSimulating ? 'Simulating...' : '⚡ Simulate Crisis (Demo)'}
              </button>
            ) : (
              <button
                id="simulate-recovery-btn"
                className="btn btn-ghost btn-sm"
                onClick={handleSimulateRecovery}
                disabled={isSimulating}
                style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#10b981', border: '1px solid rgba(16,185,129,0.35)' }}
                title="Log simulated faculty mentoring intervention and positive attendance rebound"
              >
                <Zap size={13} /> {isSimulating ? 'Simulating...' : '⚡ Simulate Recovery (Demo)'}
              </button>
            )}

            <button
              id="simulate-reset-btn"
              className="btn btn-ghost btn-sm"
              onClick={handleSimulateReset}
              disabled={isSimulating}
              style={{ display: 'flex', alignItems: 'center', gap: 6 }}
              title="Reset simulated data and restore baseline standing"
            >
              <RotateCcw size={13} /> Reset Baseline
            </button>

            {profile.alert_id && (
              <button
                className="btn btn-danger btn-sm"
                id="view-alert-btn"
                onClick={() => navigate(`/alerts/${profile.alert_id}`)}
                style={{ display: 'flex', alignItems: 'center', gap: 6 }}
              >
                <AlertTriangle size={13} />
                View Alert #{profile.alert_id}
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="page-body">
        {/* Hysteresis Anti-Flapping Banner */}
        <div style={{
          background: 'rgba(99,102,241,0.06)', border: '1px solid rgba(99,102,241,0.2)',
          borderRadius: 8, padding: '10px 16px', marginBottom: 20, fontSize: 11, color: 'var(--text-secondary)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Shield size={14} color="#818cf8" />
            <span>
              <strong>Hysteresis Anti-Flapping Engine:</strong> Once flagged as TRIPWIRE, student must sustain <strong>DVI &lt; 55 for 2 consecutive weeks</strong> to enter RECOVERING, and <strong>DVI &lt; 40 for 2 weeks</strong> to return to NORMAL.
            </span>
          </div>
          <span style={{ color: '#c7d2fe', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
            Current Status: {profile.weeks_in_status || 1} / 2 wks sustained
          </span>
        </div>

        {/* Top Section: Gauge & 28-Day Trend */}
        <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', gap: 20, marginBottom: 20 }}>
          {/* DVI Radial Card */}
          <div className="card card-p" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <DVIGauge dvi={profile.dvi} />
            <div style={{ marginTop: 10, textAlign: 'center' }}>
              <VelocityLabel velocity={profile.velocity} />
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
                Relative to {profile.name}'s Normal Baseline
              </div>
            </div>
          </div>

          {/* DVI 28-Day History Chart with Temporal Smoothing Toggle */}
          <div className="card">
            <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span>DVI Behavioral Trajectory — 28 Day Rolling Window</span>
                {/* Temporal Smoothing toggle */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'rgba(0,0,0,0.3)', padding: '2px 4px', borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
                  <button
                    onClick={() => setSmoothingMode('smoothed')}
                    style={{
                      border: 'none', borderRadius: 6, padding: '3px 8px', fontSize: 10, fontWeight: 700, cursor: 'pointer',
                      background: smoothingMode === 'smoothed' ? 'var(--color-brand)' : 'transparent',
                      color: smoothingMode === 'smoothed' ? '#fff' : 'var(--text-muted)'
                    }}
                  >
                    Smoothed (EWMA α=0.3)
                  </button>
                  <button
                    onClick={() => setSmoothingMode('raw')}
                    style={{
                      border: 'none', borderRadius: 6, padding: '3px 8px', fontSize: 10, fontWeight: 700, cursor: 'pointer',
                      background: smoothingMode === 'raw' ? 'var(--color-brand)' : 'transparent',
                      color: smoothingMode === 'raw' ? '#fff' : 'var(--text-muted)'
                    }}
                  >
                    Raw Telemetry
                  </button>
                </div>
              </div>
              <div style={{ display: 'flex', gap: 16, fontSize: 11, color: 'var(--text-muted)' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <div style={{ width: 8, height: 2, background: '#ef4444' }} /> Tripwire Threshold (70)
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <div style={{ width: 8, height: 2, background: '#f59e0b' }} /> Monitoring Threshold (50)
                </span>
              </div>
            </div>
            <div style={{ padding: '16px 16px 8px', height: 180 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 6, right: 8, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#64748b' }} tickLine={false} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#64748b' }} tickLine={false} />
                  <Tooltip
                    content={({ active, payload, label }) => {
                      if (!active || !payload?.length) return null
                      const v = payload[0].value
                      return (
                        <div style={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', padding: '6px 10px', borderRadius: 6, fontSize: 11 }}>
                          <div>{label || 'Date'}</div>
                          <div style={{ color: dviColor, fontWeight: 700 }}>DVI ({smoothingMode}): {Math.round(v)}</div>
                        </div>
                      )
                    }}
                  />
                  <ReferenceLine y={70} stroke="rgba(239,68,68,0.5)" strokeDasharray="4 4" />
                  <ReferenceLine y={50} stroke="rgba(245,158,11,0.5)" strokeDasharray="4 4" />
                  <Line
                    type="monotone" dataKey="dvi"
                    stroke={dviColor}
                    strokeWidth={2.5}
                    dot={false}
                    activeDot={{ r: 4, fill: dviColor }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div style={{ padding: '8px 16px', fontSize: 11, color: 'var(--text-muted)', borderTop: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between' }}>
              <span>Baseline Established: Aug 1–31</span>
              <span>Active Monitoring: Sep 1–15 (Mode: {smoothingMode === 'smoothed' ? 'EWMA α=0.3 Noise Dampened' : 'Raw Telemetry'})</span>
            </div>
          </div>
        </div>

        {/* 🌟 MAJOR SECTION: "WHAT CHANGED?" 🌟 */}

        <div className="card card-p" style={{ marginBottom: 20, border: '1px solid rgba(99, 102, 241, 0.3)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Activity size={18} color="var(--brand-glow)" />
              <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800, color: '#f8fafc', letterSpacing: '0.3px' }}>
                WHAT CHANGED? — INDIVIDUAL BEHAVIORAL DRIFT ANALYSIS
              </h3>
            </div>
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              Compared with <strong style={{ color: '#fff' }}>{profile.name}'s normal behavior</strong> (not class average)
            </span>
          </div>

          {/* 3 Metric Comparison Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 20 }}>
            {/* Card 1: Attendance */}
            <div style={{
              background: 'var(--bg-elevated)',
              border: '1px solid rgba(99,102,241,0.2)',
              borderRadius: 12,
              padding: '16px 18px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>Attendance Rate</span>
                <span style={{
                  fontSize: 12, fontWeight: 800, fontFamily: 'var(--font-mono)',
                  color: what_changed?.attendance?.negative ? '#ef4444' : '#10b981'
                }}>
                  {what_changed?.attendance?.formatted_change}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 6 }}>
                <div style={{ fontSize: 26, fontWeight: 800, fontFamily: 'var(--font-mono)', color: what_changed?.attendance?.negative ? '#ef4444' : '#f8fafc' }}>
                  {what_changed?.attendance?.current}%
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>current</div>
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Baseline: <strong style={{ color: 'var(--text-secondary)' }}>{what_changed?.attendance?.baseline}%</strong>
              </div>
            </div>

            {/* Card 2: Assignment Delay */}
            <div style={{
              background: 'var(--bg-elevated)',
              border: '1px solid rgba(245,158,11,0.2)',
              borderRadius: 12,
              padding: '16px 18px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>Assignment Submission Latency</span>
                <span style={{
                  fontSize: 12, fontWeight: 800, fontFamily: 'var(--font-mono)',
                  color: what_changed?.submission_delay?.negative ? '#ef4444' : '#10b981'
                }}>
                  {what_changed?.submission_delay?.formatted_change}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 6 }}>
                <div style={{ fontSize: 26, fontWeight: 800, fontFamily: 'var(--font-mono)', color: what_changed?.submission_delay?.negative ? '#ef4444' : '#f8fafc' }}>
                  {what_changed?.submission_delay?.current}h
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>current delay</div>
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Baseline: <strong style={{ color: 'var(--text-secondary)' }}>{what_changed?.submission_delay?.baseline}h</strong>
              </div>
            </div>

            {/* Card 3: LMS Activity */}
            <div style={{
              background: 'var(--bg-elevated)',
              border: '1px solid rgba(6,182,212,0.2)',
              borderRadius: 12,
              padding: '16px 18px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>LMS / Course Engagement</span>
                <span style={{
                  fontSize: 12, fontWeight: 800, fontFamily: 'var(--font-mono)',
                  color: what_changed?.lms_activity?.negative ? '#ef4444' : '#10b981'
                }}>
                  {what_changed?.lms_activity?.formatted_change}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 6 }}>
                <div style={{ fontSize: 26, fontWeight: 800, fontFamily: 'var(--font-mono)', color: what_changed?.lms_activity?.negative ? '#ef4444' : '#f8fafc' }}>
                  {what_changed?.lms_activity?.current}/wk
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>current logins</div>
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Baseline: <strong style={{ color: 'var(--text-secondary)' }}>{what_changed?.lms_activity?.baseline}/wk</strong>
              </div>
            </div>
          </div>

          {/* Counterfactual Explanation Box */}
          {counterfactual && (
            <div style={{
              background: 'rgba(99, 102, 241, 0.08)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              borderRadius: 12,
              padding: '16px 20px',
              marginBottom: 16
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                <HelpCircle size={16} color="var(--brand-glow)" />
                <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--brand-glow)', textTransform: 'uppercase', letterSpacing: 0.5 }}>
                  Counterfactual Reasoner ("What If?")
                </span>
              </div>

              <div style={{ fontSize: 14, color: 'var(--text-primary)', fontStyle: 'italic', lineHeight: 1.6, marginBottom: 12 }}>
                "{counterfactual.summary}"
              </div>

              {/* Counterfactual chips */}
              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                <div style={{ background: 'var(--bg-elevated)', borderRadius: 8, padding: '8px 12px', fontSize: 11, border: '1px solid var(--border-subtle)' }}>
                  <span style={{ color: 'var(--text-muted)' }}>If Submission was at baseline:</span>{' '}
                  <strong style={{ color: counterfactual.scenarios.if_submission_baseline.clears_tripwire ? '#10b981' : '#f59e0b', fontFamily: 'var(--font-mono)' }}>
                    DVI &rarr; {counterfactual.scenarios.if_submission_baseline.hypothetical_dvi}
                  </strong>{' '}
                  ({counterfactual.scenarios.if_submission_baseline.clears_tripwire ? 'Clears Tripwire' : 'Leaves in Monitoring'})
                </div>

                <div style={{ background: 'var(--bg-elevated)', borderRadius: 8, padding: '8px 12px', fontSize: 11, border: '1px solid var(--border-subtle)' }}>
                  <span style={{ color: 'var(--text-muted)' }}>If LMS was at baseline:</span>{' '}
                  <strong style={{ color: counterfactual.scenarios.if_lms_baseline.clears_tripwire ? '#10b981' : '#f59e0b', fontFamily: 'var(--font-mono)' }}>
                    DVI &rarr; {counterfactual.scenarios.if_lms_baseline.hypothetical_dvi}
                  </strong>
                </div>

                <div style={{ background: 'var(--bg-elevated)', borderRadius: 8, padding: '8px 12px', fontSize: 11, border: '1px solid var(--border-subtle)' }}>
                  <span style={{ color: 'var(--text-muted)' }}>If Both Sub & LMS restored:</span>{' '}
                  <strong style={{ color: '#10b981', fontFamily: 'var(--font-mono)' }}>
                    DVI &rarr; {counterfactual.scenarios.if_submission_and_lms_baseline.hypothetical_dvi} (Normal)
                  </strong>
                </div>
              </div>

              <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 10 }}>
                {counterfactual.disclaimer}
              </div>
            </div>
          )}

          {/* DVI Formula Exact Breakdown Bar */}
          <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: 16 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 12 }}>
              DVI Additive Point Composition
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
              <div style={{ background: 'var(--bg-elevated)', borderRadius: 8, padding: '10px 12px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>
                  Attendance Drift ({Math.round((profile?.weights?.attendance ?? 0.50) * 100)}%)
                </div>
                <div style={{ fontSize: 16, fontWeight: 700, color: '#6366f1', fontFamily: 'var(--font-mono)' }}>
                  {signals.attendance.score} pts &times; {(profile?.weights?.attendance ?? 0.50).toFixed(2)} = {profile.dvi_breakdown?.attendance_component}
                </div>
              </div>

              <div style={{ background: 'var(--bg-elevated)', borderRadius: 8, padding: '10px 12px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>
                  Submission Delay Drift ({Math.round((profile?.weights?.submission ?? 0.30) * 100)}%)
                </div>
                <div style={{ fontSize: 16, fontWeight: 700, color: '#f59e0b', fontFamily: 'var(--font-mono)' }}>
                  {signals.submission.score} pts &times; {(profile?.weights?.submission ?? 0.30).toFixed(2)} = {profile.dvi_breakdown?.submission_component}
                </div>
              </div>

              <div style={{ background: 'var(--bg-elevated)', borderRadius: 8, padding: '10px 12px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>
                  Engagement Drop ({Math.round((profile?.weights?.engagement ?? 0.20) * 100)}%)
                </div>
                <div style={{ fontSize: 16, fontWeight: 700, color: '#06b6d4', fontFamily: 'var(--font-mono)' }}>
                  {signals.engagement.score} pts &times; {(profile?.weights?.engagement ?? 0.20).toFixed(2)} = {profile.dvi_breakdown?.engagement_component}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Self-Reported Signal Card (Qualitative Corroborating Evidence) */}
        {profile.pulse && (
          <div className="card card-p" style={{
            background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.08), rgba(99, 102, 241, 0.04))',
            border: '1px solid rgba(168, 85, 247, 0.3)',
            marginBottom: 20
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 18 }}>💭</span>
                <span style={{ fontSize: 13, fontWeight: 700, color: '#c084fc', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Self-Reported Student Pulse (Qualitative Corroborating Signal)
                </span>
              </div>
              <span style={{ fontSize: 10, color: '#d8b4fe', background: 'rgba(168,85,247,0.15)', padding: '2px 8px', borderRadius: 4, fontWeight: 700 }}>
                Non-Weighted Contextual Evidence
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <span style={{ fontSize: 28 }}>
                {profile.pulse.rating === 1 ? '😫' :
                  profile.pulse.rating === 2 ? '😟' :
                    profile.pulse.rating === 3 ? '😐' :
                      profile.pulse.rating === 4 ? '🙂' : '🌟'}
              </span>
              <div>
                <div style={{ fontSize: 13, fontWeight: 700, color: profile.pulse.rating <= 2 ? '#ef4444' : '#10b981' }}>
                  Student Self-Rating: {profile.pulse.rating}/5 — {profile.pulse.rating <= 2 ? 'Struggling' : 'Manageable'} ({profile.pulse.date ? new Date(profile.pulse.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : 'Recent'})
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', fontStyle: 'italic', marginTop: 2 }}>
                  "{profile.pulse.stuck_on || 'No feedback text submitted.'}"
                </div>
              </div>
            </div>
            <div style={{ marginTop: 10, fontSize: 11, color: 'var(--text-muted)', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: 8 }}>
              💡 <strong>Human-in-the-Loop Integration:</strong> Provides subjective student context to corroborate telemetry drift without altering the deterministic, transparent 40/35/25 DVI weights.
            </div>
          </div>
        )}

        {/* Human Override Active Note if any excused leaves */}
        {profile.excused_leaves && profile.excused_leaves.length > 0 && (

          <div style={{ marginBottom: 20 }}>
            <HumanOverrideNote />
          </div>
        )}

        {/* Past Interventions Log (if student was previously intervened) */}
        {interventions.length > 0 && (
          <div className="card card-p" style={{ marginBottom: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
              <UserCheck size={16} color="var(--color-normal)" />
              <h3 style={{ margin: 0, fontSize: 14, fontWeight: 700, color: '#f8fafc' }}>
                Intervention & Recovery History ({interventions.length})
              </h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {interventions.map(inv => (
                <div key={inv.id} style={{
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 10,
                  padding: '12px 16px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                    <span style={{ fontWeight: 700, color: 'var(--color-normal)' }}>
                      Outcome: {inv.outcome}
                    </span>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                      {new Date(inv.contact_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                    </span>
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 8 }}>
                    <strong>Method:</strong> {inv.contact_method} · <strong>Notes:</strong> {inv.notes}
                  </div>
                  {inv.pre_dvi && inv.post_dvi && (
                    <div style={{ fontSize: 11, color: 'var(--brand-glow)', fontWeight: 600 }}>
                      Trajectory: DVI {Math.round(inv.pre_dvi)} &rarr; {Math.round(inv.post_dvi)} (Behavioral turnaround detected)
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Behavioral Event Timeline */}
        <div className="card">
          <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Chronological Behavioral Event Log</span>
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              Identifies exact dates when behavioral latency or absence emerged
            </span>
          </div>
          <div style={{ padding: 24 }}>
            <Timeline events={timeline} />
          </div>
        </div>
      </div>

      {/* Human Override / Excused Leave Modal */}
      {showExcuseModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(5, 8, 16, 0.85)',
          backdropFilter: 'blur(12px)',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 20
        }}>
          <div style={{
            background: '#0f172a',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: 16,
            width: '100%',
            maxWidth: 520,
            padding: 24,
            boxShadow: '0 20px 50px rgba(0,0,0,0.8)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <ShieldCheck size={20} color="var(--color-normal)" />
                <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: '#f8fafc' }}>
                  Record Excused Absence (Human Override)
                </h3>
              </div>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowExcuseModal(false)}>
                &times;
              </button>
            </div>

            <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 16, lineHeight: 1.5 }}>
              Faculty mentors can mark specific date ranges as excused (medical leave, approved sports, college event). This removes attendance penalties from the student's DVI calculation.
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 14 }}>
              <div>
                <label className="form-label">Start Date</label>
                <input
                  type="date"
                  className="input"
                  value={excuseStart}
                  onChange={e => setExcuseStart(e.target.value)}
                />
              </div>
              <div>
                <label className="form-label">End Date</label>
                <input
                  type="date"
                  className="input"
                  value={excuseEnd}
                  onChange={e => setExcuseEnd(e.target.value)}
                />
              </div>
            </div>

            <div style={{ marginBottom: 14 }}>
              <label className="form-label">Reason</label>
              <select
                className="input"
                value={excuseReason}
                onChange={e => setExcuseReason(e.target.value)}
              >
                <option value="medical">Medical / Health Leave</option>
                <option value="official">Official Academic / College Event</option>
                <option value="personal">Approved Personal Exemption</option>
              </select>
            </div>

            <div style={{ marginBottom: 20 }}>
              <label className="form-label">Mentor Notes (Optional)</label>
              <textarea
                className="input"
                rows={2}
                placeholder="Doctor's note submitted, dean approval received..."
                value={excuseNotes}
                onChange={e => setExcuseNotes(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowExcuseModal(false)}>
                Cancel
              </button>
              <button
                className="btn btn-primary btn-sm"
                onClick={handleApplyExcuse}
                disabled={submittingExcuse}
              >
                {submittingExcuse ? 'Applying Override...' : 'Apply Human Override'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Quick Pulse Check Modal */}
      {showPulseModal && (
        <div className="modal-overlay" style={{
          position: 'fixed', inset: 0, zIndex: 9999,
          background: 'rgba(5,10,24,0.85)', backdropFilter: 'blur(8px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24
        }} onClick={() => setShowPulseModal(false)}>
          <div className="card card-p" style={{
            width: '100%', maxWidth: '440px', background: 'var(--bg-elevated)',
            border: '1px solid rgba(168,85,247,0.4)', borderRadius: 16
          }} onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 20 }}>💭</span>
                <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>
                  Weekly Self-Report Pulse Check
                </h3>
              </div>
              <button className="btn btn-ghost" style={{ padding: 6 }} onClick={() => setShowPulseModal(false)}>
                &times;
              </button>
            </div>

            <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 16, lineHeight: 1.5 }}>
              A 1-tap weekly check-in allowing the student to report how they feel. This qualitative evidence corroborates drift without polluting deterministic DVI weights.
            </p>

            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: 8 }}>
                How are you feeling this week? (1 = Critical, 5 = Thriving)
              </label>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
                {[
                  { r: 1, e: '😫', l: 'Critical' },
                  { r: 2, e: '😟', l: 'Struggling' },
                  { r: 3, e: '😐', l: 'Okay' },
                  { r: 4, e: '🙂', l: 'Good' },
                  { r: 5, e: '🌟', l: 'Thriving' },
                ].map(({ r, e, l }) => (
                  <button
                    key={r}
                    type="button"
                    onClick={() => setPulseRating(r)}
                    style={{
                      flex: 1, padding: '8px 4px', borderRadius: 8,
                      border: pulseRating === r ? '2px solid #a855f7' : '1px solid var(--border-subtle)',
                      background: pulseRating === r ? 'rgba(168,85,247,0.2)' : 'var(--bg-card)',
                      cursor: 'pointer', textAlign: 'center'
                    }}
                  >
                    <div style={{ fontSize: 18 }}>{e}</div>
                    <div style={{ fontSize: 9, color: pulseRating === r ? '#d8b4fe' : 'var(--text-muted)', marginTop: 2 }}>{l}</div>
                  </button>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: 20 }}>
              <label className="form-label">What are you currently stuck on? (Optional)</label>
              <textarea
                className="input"
                rows={3}
                value={pulseNote}
                onChange={e => setPulseNote(e.target.value)}
                placeholder="e.g. Lab assignment deadline, commuting delays, exam pressure..."
                style={{ width: '100%', fontSize: 12, resize: 'none' }}
              />
            </div>

            <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
              <button type="button" className="btn btn-secondary btn-sm" onClick={() => setShowPulseModal(false)}>
                Cancel
              </button>
              <button
                type="button"
                className="btn btn-primary btn-sm"
                onClick={handleApplyPulse}
                disabled={submittingPulse}
                style={{ background: 'linear-gradient(135deg, #a855f7, #6366f1)', border: 'none' }}
              >
                {submittingPulse ? 'Saving...' : 'Submit Pulse Check'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Live Telemetry Logger Modal */}
      <LogTelemetryModal
        isOpen={showTelemetryModal}
        onClose={() => setShowTelemetryModal(false)}
        student={profile ? { ...profile, student_id: profile.student_id || id } : null}
        onTelemetryLogged={() => reloadData()}
      />
    </div>
  )
}

