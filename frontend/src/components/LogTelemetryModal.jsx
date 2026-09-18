import React, { useState } from 'react'
import { X, Activity, Calendar, Clock, BookOpen, CheckCircle, AlertTriangle } from 'lucide-react'
import { studentsAPI } from '../api/client'
import toast from 'react-hot-toast'

export default function LogTelemetryModal({ isOpen, onClose, student, onTelemetryLogged }) {
  if (!isOpen || !student) return null

  const [activeTab, setActiveTab] = useState('attendance') // attendance, assignment, lms
  const [submitting, setSubmitting] = useState(false)
  const [resultData, setResultData] = useState(null)

  // Attendance Form
  const [attDate, setAttDate] = useState(new Date().toISOString().slice(0, 10))
  const [attPeriod, setAttPeriod] = useState(1)
  const [attStatus, setAttStatus] = useState('absent')

  // Assignment Form
  const [asgId, setAsgId] = useState('Lab Assignment 4')
  const [asgStatus, setAsgStatus] = useState('late_2d') // on_time, late_1d, late_2d, late_5d, missing

  // LMS Form
  const [lmsDate, setLmsDate] = useState(new Date().toISOString().slice(0, 10))
  const [lmsCount, setLmsCount] = useState(1)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setResultData(null)

    try {
      let res
      if (activeTab === 'attendance') {
        res = await studentsAPI.logAttendance(student.student_id, {
          date: attDate,
          period: parseInt(attPeriod, 10),
          status: attStatus
        })
      } else if (activeTab === 'assignment') {
        const now = new Date()
        let submitted_at = null
        if (asgStatus === 'on_time') {
          submitted_at = new Date(now.getTime() - 2 * 3600 * 1000).toISOString()
        } else if (asgStatus === 'late_1d') {
          submitted_at = new Date(now.getTime() + 24 * 3600 * 1000).toISOString()
        } else if (asgStatus === 'late_2d') {
          submitted_at = new Date(now.getTime() + 48 * 3600 * 1000).toISOString()
        } else if (asgStatus === 'late_5d') {
          submitted_at = new Date(now.getTime() + 120 * 3600 * 1000).toISOString()
        } // 'missing' keeps submitted_at = null

        res = await studentsAPI.logAssignment(student.student_id, {
          assignment_id: asgId,
          due_date: now.toISOString(),
          submitted_at
        })
      } else if (activeTab === 'lms') {
        res = await studentsAPI.logLMS(student.student_id, {
          date: lmsDate,
          activity_count: parseInt(lmsCount, 10)
        })
      }

      setResultData(res.data)
      toast.success(res.data.message || 'Telemetry updated and DVI recalculated!')
      if (onTelemetryLogged) onTelemetryLogged()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to record telemetry')
    } finally {
      setSubmitting(false)
    }
  }

  return (
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
        background: 'linear-gradient(180deg, #0f172a 0%, #090d16 100%)',
        border: '1px solid rgba(99, 102, 241, 0.3)',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.8)',
        borderRadius: 16,
        width: '100%',
        maxWidth: 520,
        overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{
          padding: '16px 20px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'rgba(255, 255, 255, 0.02)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              background: 'rgba(99, 102, 241, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Activity size={18} color="var(--brand-glow)" />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 15, color: '#f8fafc' }}>
                Log Telemetry: {student.name}
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                {student.student_id} · {student.roll_no} · Current DVI: <strong>{student.dvi}</strong>
              </div>
            </div>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        {/* Tab Selection */}
        <div style={{
          display: 'flex',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          background: 'rgba(0, 0, 0, 0.2)'
        }}>
          {[
            { id: 'attendance', label: 'Attendance', icon: Calendar },
            { id: 'assignment', label: 'Assignment', icon: Clock },
            { id: 'lms', label: 'LMS Activity', icon: BookOpen }
          ].map(tab => {
            const Icon = tab.icon
            const isSel = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => { setActiveTab(tab.id); setResultData(null) }}
                style={{
                  flex: 1,
                  padding: '10px 14px',
                  background: isSel ? 'rgba(99, 102, 241, 0.1)' : 'none',
                  border: 'none',
                  borderBottom: isSel ? '2px solid var(--brand-glow)' : '2px solid transparent',
                  color: isSel ? '#f8fafc' : 'var(--text-muted)',
                  fontSize: 12,
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 6
                }}
              >
                <Icon size={14} color={isSel ? 'var(--brand-glow)' : 'currentColor'} />
                {tab.label}
              </button>
            )
          })}
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 14 }}>
          {activeTab === 'attendance' && (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 12 }}>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                    Date
                  </label>
                  <input
                    type="date"
                    className="input"
                    value={attDate}
                    onChange={(e) => setAttDate(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                    Period (1–6)
                  </label>
                  <select
                    className="input"
                    value={attPeriod}
                    onChange={(e) => setAttPeriod(e.target.value)}
                  >
                    {[1, 2, 3, 4, 5, 6].map(p => (
                      <option key={p} value={p}>Period {p} {p === 1 ? '(Morning)' : ''}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  Attendance Status
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8 }}>
                  {[
                    { id: 'present', label: 'Present', color: 'var(--color-normal)' },
                    { id: 'absent', label: 'Absent', color: '#ef4444' },
                    { id: 'late', label: 'Late', color: '#f59e0b' },
                    { id: 'excused', label: 'Excused', color: '#a855f7' }
                  ].map(st => (
                    <button
                      key={st.id}
                      type="button"
                      onClick={() => setAttStatus(st.id)}
                      style={{
                        padding: '10px 6px',
                        borderRadius: 8,
                        border: attStatus === st.id ? `2px solid ${st.color}` : '1px solid var(--border-subtle)',
                        background: attStatus === st.id ? 'rgba(255, 255, 255, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                        color: attStatus === st.id ? '#fff' : 'var(--text-muted)',
                        fontWeight: 700,
                        fontSize: 11,
                        cursor: 'pointer',
                        textAlign: 'center'
                      }}
                    >
                      {st.label}
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}

          {activeTab === 'assignment' && (
            <>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  Assignment Title / ID
                </label>
                <input
                  className="input"
                  value={asgId}
                  onChange={(e) => setAsgId(e.target.value)}
                  placeholder="e.g. Operating Systems Lab 3"
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  Submission Timeliness
                </label>
                <select
                  className="input"
                  value={asgStatus}
                  onChange={(e) => setAsgStatus(e.target.value)}
                >
                  <option value="on_time">✅ Submitted On Time</option>
                  <option value="late_1d">⚠️ 1 Day Late (24h Delay)</option>
                  <option value="late_2d">⚠️ 2 Days Late (48h Delay)</option>
                  <option value="late_5d">🔴 5 Days Late (120h Delay)</option>
                  <option value="missing">❌ Missing / Not Submitted</option>
                </select>
              </div>
            </>
          )}

          {activeTab === 'lms' && (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 12 }}>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                    Date
                  </label>
                  <input
                    type="date"
                    className="input"
                    value={lmsDate}
                    onChange={(e) => setLmsDate(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                    Logins / Module Views
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="50"
                    className="input"
                    value={lmsCount}
                    onChange={(e) => setLmsCount(e.target.value)}
                    required
                  />
                </div>
              </div>
            </>
          )}

          {/* Real-Time Recalculation Result Card */}
          {resultData && (
            <div style={{
              background: resultData.alert_created ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.1)',
              border: `1px solid ${resultData.alert_created ? 'rgba(239, 68, 68, 0.4)' : 'rgba(16, 185, 129, 0.3)'}`,
              borderRadius: 10,
              padding: '12px 16px',
              display: 'flex',
              flexDirection: 'column',
              gap: 6
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, fontWeight: 700, color: '#fff' }}>
                  {resultData.alert_created ? (
                    <>
                      <AlertTriangle size={16} color="#ef4444" />
                      <span>Tripwire Triggered! Alert Created</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle size={16} color="var(--color-normal)" />
                      <span>DVI Dynamically Recalculated</span>
                    </>
                  )}
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 15, fontWeight: 800, color: resultData.dvi >= 70 ? '#ef4444' : (resultData.dvi >= 50 ? '#f59e0b' : 'var(--color-normal)') }}>
                  DVI: {resultData.dvi} ({resultData.status?.toUpperCase()})
                </div>
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                {resultData.alert_created
                  ? 'Accumulated risk score crossed the 70.0 threshold. This student is now highlighted with an active flag.'
                  : 'Behavioral drift metrics smoothly updated across individual baselines.'}
              </div>
            </div>
          )}

          {/* Footer Buttons */}
          <div style={{
            marginTop: 6,
            display: 'flex',
            justifyContent: 'flex-end',
            gap: 10,
            borderTop: '1px solid rgba(255, 255, 255, 0.08)',
            paddingTop: 16
          }}>
            <button type="button" className="btn btn-ghost btn-sm" onClick={onClose}>
              {resultData ? 'Close' : 'Cancel'}
            </button>
            <button
              id="submit-telemetry-btn"
              type="submit"
              className="btn btn-primary btn-sm"
              disabled={submitting}
              style={{ minWidth: 140 }}
            >
              {submitting ? 'Calculating...' : 'Save & Recalculate'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
