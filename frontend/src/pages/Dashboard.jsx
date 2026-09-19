import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import { dashboardAPI, studentsAPI, analyticsAPI } from '../api/client'
import { StatusBadge, DVIBar, VelocityLabel, LoadingScreen, PrototypeThresholdBadge } from '../components/Shared'
import { useAuth } from '../context/AuthContext'
import { useModals } from '../context/ModalContext'
import {
  Users, AlertTriangle, CheckCircle, Activity, ChevronRight,
  TrendingDown, Sparkles, Layers, ShieldCheck, Clock, BookOpen,
  Award, TrendingUp, HelpCircle, MessageSquare, UserPlus, Upload
} from 'lucide-react'
import AddStudentModal from '../components/AddStudentModal'
import ImportCSVModal from '../components/ImportCSVModal'

export default function Dashboard() {
  const { mentor } = useAuth()
  const { openDemo, openComparison, openPrivacy } = useModals()
  const navigate = useNavigate()
  const [summary, setSummary] = useState(null)
  const [students, setStudents] = useState([])
  const [trustData, setTrustData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isAddOpen, setIsAddOpen] = useState(false)
  const [isImportOpen, setIsImportOpen] = useState(false)

  const fetchDashboardData = () => {
    return Promise.all([
      dashboardAPI.summary(),
      studentsAPI.list(),
      analyticsAPI.trustScore()
    ]).then(([sumRes, stuRes, trustRes]) => {
      setSummary(sumRes.data)
      setStudents(stuRes.data.students || [])
      setTrustData(trustRes.data)
    }).finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchDashboardData()
  }, [])

  if (loading) return <LoadingScreen text="Loading Tripwire analytics dashboard..." />

  const tripwireStudents = students.filter(s => s.status === 'tripwire')
  const monitoringStudents = students.filter(s => s.status === 'monitoring')
  const recoveringStudents = students.filter(s => s.status === 'recovering')

  // Prepare DVI distribution data
  const distData = summary?.distribution ? [
    { range: '0–20', count: summary.distribution['0_20'] || 0, fill: '#10b981' },
    { range: '21–40', count: summary.distribution['21_40'] || 0, fill: '#10b981' },
    { range: '41–60', count: summary.distribution['41_60'] || 0, fill: '#f59e0b' },
    { range: '61–80', count: summary.distribution['61_80'] || 0, fill: '#ef4444' },
    { range: '81–100', count: summary.distribution['81_100'] || 0, fill: '#dc2626' },
  ] : []

  // Synthetic cohort timeline trends over last 14 days
  const cohortTrendData = [
    { day: 'Sep 2', normal: 36, monitor: 10, tripwire: 2, recovering: 2 },
    { day: 'Sep 4', normal: 35, monitor: 11, tripwire: 2, recovering: 2 },
    { day: 'Sep 7', normal: 32, monitor: 13, tripwire: 3, recovering: 2 },
    { day: 'Sep 9', normal: 30, monitor: 14, tripwire: 4, recovering: 2 },
    { day: 'Sep 11', normal: 28, monitor: 16, tripwire: 4, recovering: 2 },
    { day: 'Sep 14', normal: 27, monitor: 17, tripwire: 4, recovering: 2 },
    { day: 'Sep 16', normal: summary?.normal || 26, monitor: summary?.monitoring || 19, tripwire: summary?.tripwire || 3, recovering: summary?.recovering || 2 },
  ]

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--brand-glow)', textTransform: 'uppercase', letterSpacing: '0.8px' }}>
                TRIPWIRE ANALYTICS SUITE
              </span>
              <span style={{ color: 'var(--border-default)' }}>·</span>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                "Detect behavioral drift. Enable timely human intervention."
              </span>
            </div>
            <h1 className="page-title">
              Good {getGreeting()}, {mentor?.name?.split(' ')[0] || 'Faculty'} 👋
            </h1>
            <p className="page-subtitle">
              Cohort Telemetry for {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
            </p>
          </div>

          {/* Quick Action Buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <button
              id="dash-demo-btn"
              className="btn btn-primary btn-sm"
              onClick={openDemo}
              style={{ display: 'flex', alignItems: 'center', gap: 6, boxShadow: '0 0 16px rgba(99,102,241,0.35)' }}
            >
              <Sparkles size={14} />
              Launch Demo Mode
            </button>
            <button
              id="dash-comparison-btn"
              className="btn btn-ghost btn-sm"
              onClick={openComparison}
              style={{ display: 'flex', alignItems: 'center', gap: 6 }}
            >
              <Layers size={14} />
              System Comparison
            </button>
            <button
              id="dash-privacy-btn"
              className="btn btn-ghost btn-sm"
              onClick={openPrivacy}
              style={{ display: 'flex', alignItems: 'center', gap: 6 }}
            >
              <ShieldCheck size={14} />
              Privacy & Ethics
            </button>
          </div>
        </div>
      </div>

      <div className="page-body">
        {/* 5 Core Stat Cards */}
        <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(5, 1fr)', marginBottom: 20 }}>
          {/* Total */}
          <div className="stat-card brand" id="stat-card-total">
            <div className="stat-label">TOTAL STUDENTS</div>
            <div className="stat-value">{summary?.total_students ?? 50}</div>
            <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-muted)' }}>Assigned Mentorship Cohort</div>
          </div>

          {/* Normal */}
          <div className="stat-card normal" id="stat-card-normal">
            <div className="stat-label">NORMAL</div>
            <div className="stat-value">{summary?.normal ?? '—'}</div>
            <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-muted)' }}>DVI &lt; 50 · Good Standing</div>
          </div>

          {/* Monitoring */}
          <div className="stat-card monitor" id="stat-card-monitoring">
            <div className="stat-label">MONITORING</div>
            <div className="stat-value">{summary?.monitoring ?? '—'}</div>
            <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-muted)' }}>DVI 50–69 · Mild Drift</div>
          </div>

          {/* Tripwire Alerts */}
          <div
            className="stat-card tripwire"
            id="stat-card-tripwire"
            style={{ animation: summary?.tripwire > 0 ? 'pulse-glow 2.5s ease-in-out infinite' : 'none' }}
          >
            <div className="stat-label">🚨 TRIPWIRE ALERTS</div>
            <div className="stat-value">{summary?.tripwire ?? '—'}</div>
            <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-muted)' }}>DVI &ge; 70 · Action Needed</div>
          </div>

          {/* Recovering */}
          <div
            className="stat-card"
            id="stat-card-recovering"
            style={{
              background: 'linear-gradient(135deg, rgba(168,85,247,0.1), rgba(147,51,234,0.05))',
              border: '1px solid rgba(168,85,247,0.3)'
            }}
          >
            <div className="stat-label" style={{ color: '#c084fc' }}>🟣 RECOVERING</div>
            <div className="stat-value" style={{ color: '#c084fc' }}>{summary?.recovering ?? '—'}</div>
            <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-muted)' }}>Post-Intervention Turnaround</div>
          </div>
        </div>

        {/* Prototype Threshold Disclaimer Banner */}
        <div style={{
          background: 'rgba(99, 102, 241, 0.05)',
          border: '1px solid rgba(99, 102, 241, 0.2)',
          borderRadius: 'var(--radius-lg)',
          padding: '12px 18px',
          marginBottom: 20,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 12
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Activity size={16} color="var(--brand-glow)" />
            <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
              <strong>DVI Operationalization:</strong> DVI = 0.30(Series Exam Mark Drift) + 0.30(Attendance Drift) + 0.30(Submission Delay Drift) + 0.10(Engagement Decline).
              Thresholds: <span style={{ color: '#ef4444', fontWeight: 700 }}>&ge;70 Tripwire</span>, <span style={{ color: '#f59e0b', fontWeight: 700 }}>50–69 Monitoring</span>, <span style={{ color: '#fb923c', fontWeight: 700 }}>35–49 Watch</span>, <span style={{ color: '#10b981', fontWeight: 700 }}>&lt;35 Normal</span> · <strong style={{ color: '#c7d2fe' }}>Academic Criteria:</strong> <span style={{ color: '#ec4899', fontWeight: 700 }}>&ge;45% Series Exam</span>, <span style={{ color: '#38bdf8', fontWeight: 700 }}>&ge;75% Attendance</span> &amp; <span style={{ color: '#38bdf8', fontWeight: 700 }}>&ge;40% CIE Pass Mark</span> (DVI &ge;50 flags Exam Risk).
            </div>
          </div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', fontStyle: 'italic' }}>
            *Prototype thresholds — decision-support indicator, not a diagnostic verdict.
          </div>
        </div>

        {/* Active Tripwires Banner (if any) */}
        {tripwireStudents.length > 0 && (
          <div style={{
            background: 'linear-gradient(135deg, rgba(239,68,68,0.1), rgba(220,38,38,0.04))',
            border: '1px solid rgba(239,68,68,0.25)',
            borderRadius: 'var(--radius-lg)',
            padding: '14px 20px',
            marginBottom: 12,
            display: 'flex',
            alignItems: 'center',
            gap: 14
          }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: 'rgba(239,68,68,0.2)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0
            }}>
              <AlertTriangle size={20} color="var(--color-tripwire)" />
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--color-tripwire)' }}>
                {tripwireStudents.length} Student{tripwireStudents.length > 1 ? 's' : ''} Crossed Tripwire Threshold (Semester Exam Debarment &amp; CIE Risk)
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                Critical behavioral drift detected relative to personal baseline (breaching statutory 75% attendance / 40% passing mark cutoffs): {tripwireStudents.map(s => `${s.name} (${s.section})`).join(', ')}
              </div>
            </div>
            <button
              id="view-active-alerts-btn"
              className="btn btn-danger btn-sm"
              onClick={() => navigate('/alerts')}
            >
              Review Alerts &rarr;
            </button>
          </div>
        )}

        {/* Pulse Alert Card — students who self-reported low wellbeing */}
        {(() => {
          const lowPulseStudents = students.filter(s => s.pulse && s.pulse.rating <= 2)
          if (lowPulseStudents.length === 0) return null
          return (
            <div style={{
              background: 'linear-gradient(135deg, rgba(168,85,247,0.08), rgba(99,102,241,0.04))',
              border: '1px solid rgba(168,85,247,0.3)',
              borderRadius: 'var(--radius-lg)',
              padding: '14px 20px',
              marginBottom: 12,
              display: 'flex',
              alignItems: 'center',
              gap: 14
            }}>
              <div style={{
                width: 36, height: 36, borderRadius: 10,
                background: 'rgba(168,85,247,0.2)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0, fontSize: 18
              }}>
                😟
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 700, fontSize: 14, color: '#c084fc' }}>
                  💭 {lowPulseStudents.length} Student{lowPulseStudents.length > 1 ? 's' : ''} Self-Reported Low Wellbeing This Week
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                  Qualitative signal corroborating behavioral drift — consider a private check-in:{' '}
                  {lowPulseStudents.map(s => (
                    <button
                      key={s.student_id}
                      onClick={() => navigate(`/students/${s.student_id}`)}
                      style={{
                        background: 'rgba(168,85,247,0.15)', border: '1px solid rgba(168,85,247,0.3)',
                        borderRadius: 4, padding: '1px 6px', fontSize: 11, cursor: 'pointer',
                        color: '#d8b4fe', marginRight: 4
                      }}
                    >
                      {s.name} ({s.pulse.rating === 1 ? '😫 Critical' : '😟 Struggling'})
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )
        })()}



        {/* Charts Row */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>
          {/* Chart 1: DVI Score Distribution */}
          <div className="card card-p">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <div>
                <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-primary)' }}>Cohort DVI Score Distribution</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Count of students across DVI score brackets</div>
              </div>
              <span style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>50 Students</span>
            </div>

            <div style={{ height: 190 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={distData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="range" tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} />
                  <Tooltip
                    contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }}
                  />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {distData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-around', fontSize: 10, color: 'var(--text-muted)', marginTop: 8, borderTop: '1px solid var(--border-subtle)', paddingTop: 8 }}>
              <span>🟢 Normal: 0–40</span>
              <span>🟡 Monitoring: 41–60</span>
              <span>🔴 Tripwire: 61–100</span>
            </div>
          </div>

          {/* Chart 2: Cohort Behavioral Trajectory Over Time */}
          <div className="card card-p">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <div>
                <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-primary)' }}>14-Day Cohort State Trajectory</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Status population trends through active September monitoring</div>
              </div>
              <div style={{ display: 'flex', gap: 10, fontSize: 11 }}>
                <span style={{ color: '#ef4444' }}>● Tripwire</span>
                <span style={{ color: '#f59e0b' }}>● Monitor</span>
                <span style={{ color: '#a855f7' }}>● Recovering</span>
              </div>
            </div>

            <div style={{ height: 190 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={cohortTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} />
                  <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }} />
                  <Area type="monotone" dataKey="tripwire" stroke="#ef4444" fill="rgba(239,68,68,0.15)" strokeWidth={2} />
                  <Area type="monotone" dataKey="monitor" stroke="#f59e0b" fill="rgba(245,158,11,0.15)" strokeWidth={2} />
                  <Area type="monotone" dataKey="recovering" stroke="#a855f7" fill="rgba(168,85,247,0.15)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', textAlign: 'center', marginTop: 8, fontStyle: 'italic' }}>
              Shows early rise in drift during early September, followed by mentor interventions stabilizing the cohort.
            </div>
          </div>
        </div>

        {/* System Trust & Self-Monitoring Section (Expectation-Disconfirmation Loop) */}
        <div className="card card-p" style={{
          marginBottom: 20,
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(13, 19, 34, 0.95) 100%)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)'
        }}>
          {/* Section Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                <span style={{
                  fontSize: 10, fontWeight: 800, textTransform: 'uppercase', letterSpacing: 0.8,
                  padding: '2px 8px', borderRadius: 6, background: 'rgba(99, 102, 241, 0.2)', color: 'var(--brand-glow)', border: '1px solid rgba(99, 102, 241, 0.4)'
                }}>
                  Core Differentiator · Closed-Loop Telemetry
                </span>
                <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  Bhattacherjee & Premkumar (2004) Expectation-Disconfirmation Model
                </span>
              </div>
              <h2 style={{ fontSize: 18, fontWeight: 800, color: '#fff', margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Award size={20} color="var(--brand-glow)" /> System Trust & Self-Monitoring
              </h2>
              <p style={{ fontSize: 12, color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
                "The first early-warning system that monitors its own perceived accuracy and trust over time, not just the student."
              </p>
            </div>

            {trustData?.recovery_diff != null ? (
              <div style={{
                background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)',
                borderRadius: 10, padding: '8px 14px', display: 'flex', alignItems: 'center', gap: 10
              }}>
                <TrendingUp size={18} color="var(--color-normal)" />
                <div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Semester Trust Trend</div>
                  <div style={{ fontSize: 13, fontWeight: 800, color: 'var(--color-normal)' }}>
                    +{trustData.recovery_diff}% Since Earliest Week
                  </div>
                </div>
              </div>
            ) : (
              <div style={{
                background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-subtle)',
                borderRadius: 10, padding: '8px 14px', display: 'flex', alignItems: 'center', gap: 10
              }}>
                <HelpCircle size={18} color="var(--text-muted)" />
                <div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Telemetry Status</div>
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)' }}>
                    Awaiting Faculty Feedback
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Empty State vs Live Trust Telemetry */}
          {(!trustData?.overall_trust_score || trustData?.status === 'no_feedback_yet' || trustData?.total_feedback_count === 0) ? (
            <div style={{
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px dashed var(--border-subtle)',
              borderRadius: 12,
              padding: '48px 24px',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 12
            }}>
              <div style={{
                width: 52,
                height: 52,
                borderRadius: '50%',
                background: 'rgba(99, 102, 241, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <MessageSquare size={24} color="var(--brand-glow)" />
              </div>
              <div style={{ fontSize: 16, fontWeight: 700, color: '#f8fafc' }}>
                Not Enough Feedback Yet
              </div>
              <div style={{ fontSize: 13, color: 'var(--text-muted)', maxWidth: 540, lineHeight: 1.6 }}>
                Faculty feedback tracking is waiting for mentor verifications. Once faculty members review alerts and submit verification feedback (accurate, false positive, too late, or unclear), empirical trust tracking and longitudinal curves will automatically render here.
              </div>
              <div style={{
                marginTop: 6,
                fontSize: 11,
                color: 'var(--text-muted)',
                background: 'rgba(255, 255, 255, 0.04)',
                padding: '6px 14px',
                borderRadius: 20,
                border: '1px solid var(--border-subtle)'
              }}>
                Grounding: Expectation-Disconfirmation Model in EWS (Bhattacherjee &amp; Premkumar, 2004)
              </div>
            </div>
          ) : (
            <>
              {/* Top Metric Cards Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 20 }}>
                {/* Metric 1: Trust Score */}
                <div style={{
                  background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-subtle)', borderRadius: 10, padding: '14px 16px'
                }}>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, marginBottom: 4 }}>
                    Current System Trust Score
                  </div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
                    <span style={{ fontSize: 32, fontWeight: 900, fontFamily: 'var(--font-mono)', color: 'var(--brand-glow)' }}>
                      {trustData.overall_trust_score}
                    </span>
                    <span style={{ fontSize: 14, color: 'var(--text-muted)' }}>/ 100</span>
                    <span style={{ fontSize: 12, color: 'var(--color-normal)', fontWeight: 700, marginLeft: 'auto' }}>
                      Empirical
                    </span>
                  </div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
                    Composite: 50% flag accuracy + 50% usefulness
                  </div>
                </div>

                {/* Metric 2: False Positive Rate */}
                <div style={{
                  background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-subtle)', borderRadius: 10, padding: '14px 16px'
                }}>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, marginBottom: 4 }}>
                    False Positive Rate
                  </div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
                    <span style={{ fontSize: 32, fontWeight: 900, fontFamily: 'var(--font-mono)', color: '#f59e0b' }}>
                      {trustData.false_positive_rate}%
                    </span>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 'auto' }}>
                      {trustData.total_feedback_count} flag(s) reviewed
                    </span>
                  </div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4, lineHeight: 1.3 }}>
                    Empirical faculty disconfirmation rate
                  </div>
                </div>

                {/* Metric 3: Accuracy Rate */}
                <div style={{
                  background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-subtle)', borderRadius: 10, padding: '14px 16px'
                }}>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, marginBottom: 4 }}>
                    Flag Accuracy Consensus
                  </div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
                    <span style={{ fontSize: 32, fontWeight: 900, fontFamily: 'var(--font-mono)', color: 'var(--color-normal)' }}>
                      {trustData.accurate_rate}%
                    </span>
                    <span style={{ fontSize: 11, color: 'var(--color-normal)', fontWeight: 700, marginLeft: 'auto' }}>
                      Verified
                    </span>
                  </div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
                    Verified as genuine disengagement by faculty
                  </div>
                </div>

                {/* Metric 4: Mean Usefulness */}
                <div style={{
                  background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-subtle)', borderRadius: 10, padding: '14px 16px'
                }}>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, marginBottom: 4 }}>
                    Mentor Actionability Rating
                  </div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
                    <span style={{ fontSize: 32, fontWeight: 900, fontFamily: 'var(--font-mono)', color: '#fbbf24' }}>
                      {trustData.avg_useful}
                    </span>
                    <span style={{ fontSize: 14, color: 'var(--text-muted)' }}>/ 5.0 ⭐</span>
                  </div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
                    Average Likert score across faculty feedback
                  </div>
                </div>
              </div>

              {/* Chart + DVI Breakdown Split */}
              <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 16, marginBottom: 16 }}>
                {/* The Disconfirmation Curve Line Chart */}
                <div style={{ background: 'rgba(0, 0, 0, 0.25)', borderRadius: 10, padding: 14, border: '1px solid var(--border-subtle)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 700, color: '#fff' }}>
                        Semester Trust Trajectory (The Disconfirmation Curve)
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                        Observed weekly faculty trust progression over time
                      </div>
                    </div>
                    <span style={{ fontSize: 10, color: '#818cf8', fontWeight: 700, background: 'rgba(99, 102, 241, 0.1)', padding: '2px 8px', borderRadius: 4 }}>
                      N = {trustData.total_feedback_count} reviews
                    </span>
                  </div>

                  <div style={{ height: 180 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={trustData.trust_score_trend || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <defs>
                          <linearGradient id="trustGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                        <XAxis dataKey="week" tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} />
                        <YAxis domain={[30, 100]} tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} />
                        <Tooltip
                          contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }}
                          formatter={(val, name, item) => [`${val}% (Phase: ${item.payload.phase})`, 'Trust Score']}
                        />
                        <Area type="monotone" dataKey="trust_score" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#trustGrad)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Breakdown by DVI Severity Range */}
                <div style={{ background: 'rgba(0, 0, 0, 0.25)', borderRadius: 10, padding: 14, border: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 700, color: '#fff', marginBottom: 4 }}>
                      Trust by DVI Severity Range
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 12 }}>
                      Verifies that higher-confidence flags generate higher faculty trust
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                      {(trustData.breakdown_by_dvi_range || []).map((row, idx) => (
                        <div key={idx} style={{ background: 'rgba(255,255,255,0.03)', padding: '8px 10px', borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginBottom: 4 }}>
                            <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{row.range}</span>
                            <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 800, color: (row.trust_score || 0) >= 85 ? 'var(--color-normal)' : 'var(--color-monitor)' }}>
                              {row.trust_score != null ? `${row.trust_score}% Trust` : 'No reviews'}
                            </span>
                          </div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-muted)' }}>
                            <span>{row.count} alerts · {row.accurate_pct != null ? `${row.accurate_pct}% accurate` : 'N/A'}</span>
                            <span>{row.false_positive_rate != null ? `${row.false_positive_rate}% FP` : 'N/A'}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Auto-Generated Narrative Card */}
              {trustData.narrative && (
                <div style={{
                  background: 'rgba(99, 102, 241, 0.1)',
                  border: '1px solid rgba(99, 102, 241, 0.3)',
                  borderRadius: 8,
                  padding: '10px 14px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10
                }}>
                  <Sparkles size={16} color="var(--brand-glow)" style={{ flexShrink: 0 }} />
                  <div style={{ fontSize: 12, color: 'var(--text-primary)', lineHeight: 1.5 }}>
                    <strong>Self-Monitoring Narrative:</strong> {trustData.narrative}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Class Engagement Overview Table */}
        <div className="card">
          <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span>Class Engagement Overview</span>
              <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 400 }}>
                ({students.length} students enrolled)
              </span>
            </div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <button
                id="dash-add-student-btn"
                className="btn btn-primary btn-sm"
                onClick={() => setIsAddOpen(true)}
                style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 11 }}
              >
                <UserPlus size={13} /> Add Student
              </button>
              <button
                id="dash-import-csv-btn"
                className="btn btn-ghost btn-sm"
                onClick={() => setIsImportOpen(true)}
                style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 11 }}
              >
                <Upload size={13} /> Import CSV
              </button>
              <button
                className="btn btn-ghost btn-sm"
                onClick={() => navigate('/students')}
              >
                View Full Table &rarr;
              </button>
            </div>
          </div>

          <table className="data-table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Section</th>
                <th>Attendance</th>
                <th>Submission Delay</th>
                <th>LMS Logins</th>
                <th style={{ width: 170 }}>DVI Score</th>
                <th>Trend</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {students.slice(0, 10).map(student => (
                <tr
                  key={student.student_id}
                  onClick={() => navigate(`/students/${student.student_id}`)}
                  id={`student-row-${student.student_id}`}
                  style={{ cursor: 'pointer' }}
                >
                  <td>
                    <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{student.name}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{student.roll_no} · {student.student_id}</div>
                  </td>
                  <td style={{ fontSize: 12 }}>{student.section}</td>
                  <td style={{ fontSize: 12, fontFamily: 'var(--font-mono)' }}>{student.attendance}</td>
                  <td style={{ fontSize: 12, fontFamily: 'var(--font-mono)' }}>{student.assignment_delay}</td>
                  <td style={{ fontSize: 12, fontFamily: 'var(--font-mono)' }}>{student.lms_engagement}</td>
                  <td><DVIBar dvi={student.dvi} /></td>
                  <td><VelocityLabel velocity={student.velocity} /></td>
                  <td><StatusBadge status={student.status} /></td>
                  <td>
                    <ChevronRight size={16} color="var(--text-muted)" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Dynamic Data Modals */}
      <AddStudentModal
        isOpen={isAddOpen}
        onClose={() => setIsAddOpen(false)}
        onStudentAdded={() => fetchDashboardData()}
      />

      <ImportCSVModal
        isOpen={isImportOpen}
        onClose={() => setIsImportOpen(false)}
        onImportSuccess={() => fetchDashboardData()}
      />
    </div>
  )
}

function getGreeting() {
  const h = new Date().getHours()
  if (h < 12) return 'morning'
  if (h < 17) return 'afternoon'
  return 'evening'
}
