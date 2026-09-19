import React, { useState, useEffect } from 'react'
import { X, CheckSquare, Users, Calendar, AlertCircle } from 'lucide-react'
import { studentsAPI } from '../api/client'
import toast from 'react-hot-toast'

// Module-level cache so reopening the modal persists the selected date and period
let lastUsedDate = new Date().toISOString().slice(0, 10)
let lastUsedPeriod = 1

export default function BatchAttendanceModal({ isOpen, onClose, students = [], onAttendanceSubmitted }) {
  const [dateStr, setDateStr] = useState(lastUsedDate)
  const [period, setPeriod] = useState(lastUsedPeriod)
  const [rosterStudents, setRosterStudents] = useState(students)
  const [statuses, setStatuses] = useState({})
  const [loadingAttendance, setLoadingAttendance] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  // Sync date and period with last used when modal opens
  useEffect(() => {
    if (isOpen) {
      setDateStr(lastUsedDate)
      setPeriod(lastUsedPeriod)
    }
  }, [isOpen])

  // Ensure batch register has complete student roster even if main list was filtered
  useEffect(() => {
    if (!isOpen) return
    if (students && students.length >= 40) {
      setRosterStudents(students)
    } else {
      studentsAPI.list({ status: 'all' })
        .then(res => {
          const list = res.data?.students || []
          if (list.length > 0) {
            setRosterStudents(list)
          } else {
            setRosterStudents(students)
          }
        })
        .catch(() => setRosterStudents(students))
    }
  }, [isOpen, students])

  // Fetch saved attendance records whenever modal opens or date/period/roster changes
  useEffect(() => {
    if (!isOpen || !dateStr) return

    let cancelled = false
    setLoadingAttendance(true)

    studentsAPI.getBatchAttendance({
      date: dateStr,
      period: parseInt(period, 10)
    })
      .then(res => {
        if (cancelled) return
        const records = res.data?.records || {}
        const map = {}
        rosterStudents.forEach(s => {
          map[s.student_id] = records[s.student_id] !== undefined ? records[s.student_id] : 'present'
        })
        setStatuses(map)
      })
      .catch(err => {
        if (cancelled) return
        console.error('Failed to load batch attendance:', err)
        const map = {}
        rosterStudents.forEach(s => {
          map[s.student_id] = 'present'
        })
        setStatuses(map)
      })
      .finally(() => {
        if (!cancelled) setLoadingAttendance(false)
      })

    return () => {
      cancelled = true
    }
  }, [isOpen, dateStr, period, rosterStudents])

  const handleDateChange = (val) => {
    setDateStr(val)
    lastUsedDate = val
  }

  const handlePeriodChange = (val) => {
    const p = parseInt(val, 10)
    setPeriod(p)
    lastUsedPeriod = p
  }

  const handleSetAll = (status) => {
    const updated = {}
    rosterStudents.forEach(s => { updated[s.student_id] = status })
    setStatuses(updated)
  }

  const handleToggle = (id, status) => {
    setStatuses(prev => ({ ...prev, [id]: status }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      const records = Object.entries(statuses).map(([student_id, status]) => ({
        student_id,
        status
      }))
      const res = await studentsAPI.batchAttendance({
        date: dateStr,
        period: parseInt(period, 10),
        records
      })
      lastUsedDate = dateStr
      lastUsedPeriod = period
      toast.success(`Updated attendance for ${res.data.updated_count} students! ${res.data.alerts_triggered > 0 ? `(${res.data.alerts_triggered} new alerts triggered)` : ''}`)
      if (onAttendanceSubmitted) onAttendanceSubmitted()
      onClose()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit batch attendance')
    } finally {
      setSubmitting(false)
    }
  }

  if (!isOpen) return null

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
        maxWidth: 680,
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
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
              <CheckSquare size={18} color="var(--brand-glow)" />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 15, color: '#f8fafc' }}>
                Batch Attendance Register
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Mark daily attendance for your classroom cohort in one view
              </div>
            </div>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        {/* Date & Batch Controls */}
        <div style={{
          padding: '12px 20px',
          background: 'rgba(0, 0, 0, 0.25)',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 12
        }}>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <div>
              <input
                type="date"
                className="input"
                value={dateStr}
                onChange={(e) => handleDateChange(e.target.value)}
                style={{ padding: '6px 10px', fontSize: 12 }}
              />
            </div>
            <div>
              <select
                className="input"
                value={period}
                onChange={(e) => handlePeriodChange(e.target.value)}
                style={{ padding: '6px 10px', fontSize: 12 }}
              >
                {[1, 2, 3, 4, 5, 6].map(p => (
                  <option key={p} value={p}>Period {p} {p === 1 ? '(Morning)' : ''}</option>
                ))}
              </select>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 6 }}>
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => handleSetAll('present')}
              style={{ fontSize: 11, color: 'var(--color-normal)' }}
            >
              All Present
            </button>
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => handleSetAll('absent')}
              style={{ fontSize: 11, color: '#ef4444' }}
            >
              All Absent
            </button>
          </div>
        </div>

        {/* Student Table */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '12px 20px' }}>
          {rosterStudents.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 30, color: 'var(--text-muted)' }}>
              No students available in this cohort.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {rosterStudents.map((s, idx) => {
                const cur = statuses[s.student_id] || 'present'
                return (
                  <div
                    key={s.student_id}
                    style={{
                      background: 'rgba(255, 255, 255, 0.02)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 8,
                      padding: '8px 12px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 13, color: '#fff' }}>
                        {idx + 1}. {s.name}
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                        {s.roll_no} · {s.section} · Current DVI: {s.dvi}
                      </div>
                    </div>

                    <div style={{ display: 'flex', gap: 4 }}>
                      {[
                        { id: 'present', label: 'P', color: 'var(--color-normal)' },
                        { id: 'absent', label: 'A', color: '#ef4444' },
                        { id: 'late', label: 'L', color: '#f59e0b' },
                        { id: 'excused', label: 'E', color: '#a855f7' }
                      ].map(btn => (
                        <button
                          key={btn.id}
                          type="button"
                          onClick={() => handleToggle(s.student_id, btn.id)}
                          style={{
                            width: 30,
                            height: 28,
                            borderRadius: 6,
                            border: cur === btn.id ? `2px solid ${btn.color}` : '1px solid var(--border-subtle)',
                            background: cur === btn.id ? 'rgba(255, 255, 255, 0.12)' : 'transparent',
                            color: cur === btn.id ? '#fff' : 'var(--text-muted)',
                            fontWeight: 800,
                            fontSize: 12,
                            cursor: 'pointer'
                          }}
                        >
                          {btn.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '14px 20px',
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          background: 'rgba(255, 255, 255, 0.02)',
          display: 'flex',
          justifyContent: 'flex-end',
          gap: 10
        }}>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClose}>
            Cancel
          </button>
          <button
            type="button"
            className="btn btn-primary btn-sm"
            disabled={submitting || loadingAttendance || rosterStudents.length === 0}
            onClick={handleSubmit}
            style={{ minWidth: 140 }}
          >
            {submitting ? 'Saving...' : loadingAttendance ? 'Loading...' : `Save (${rosterStudents.length} Records)`}
          </button>
        </div>
      </div>
    </div>
  )
}
