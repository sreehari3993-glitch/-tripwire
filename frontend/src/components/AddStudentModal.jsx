import React, { useState } from 'react'
import { X, UserPlus, Sparkles, AlertCircle } from 'lucide-react'
import { studentsAPI } from '../api/client'
import toast from 'react-hot-toast'

export default function AddStudentModal({ isOpen, onClose, onStudentAdded }) {
  if (!isOpen) return null

  const [name, setName] = useState('')
  const [rollNo, setRollNo] = useState('')
  const [section, setSection] = useState('CSE S2')
  const [studentId, setStudentId] = useState('')
  const [baselineAtt, setBaselineAtt] = useState('85')
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!name.trim() || !rollNo.trim() || !section.trim()) {
      toast.error('Please enter name, roll number, and section')
      return
    }

    setSubmitting(true)
    try {
      const payload = {
        name: name.trim(),
        roll_no: rollNo.trim(),
        section: section.trim(),
        student_id: studentId.trim() || undefined,
        baseline_attendance: parseFloat(baselineAtt) || 85.0
      }
      const res = await studentsAPI.create(payload)
      toast.success(res.data.message || 'Student added successfully!')
      if (onStudentAdded) onStudentAdded(res.data.student)
      onClose()
      setName('')
      setRollNo('')
      setStudentId('')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add student')
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
              <UserPlus size={18} color="var(--brand-glow)" />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 15, color: '#f8fafc' }}>
                Add New Student
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Register a student profile in your active mentorship cohort
              </div>
            </div>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
              Student Full Name *
            </label>
            <input
              id="student-name-input"
              className="input"
              placeholder="e.g. Aravind Krishnan"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              autoFocus
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                Roll Number *
              </label>
              <input
                id="student-roll-input"
                className="input"
                placeholder="e.g. CSE24089"
                value={rollNo}
                onChange={(e) => setRollNo(e.target.value)}
                required
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                Class / Section *
              </label>
              <input
                id="student-section-input"
                className="input"
                placeholder="e.g. CSE S2"
                value={section}
                onChange={(e) => setSection(e.target.value)}
                required
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
              Student ID (Optional - Auto-generated if empty)
            </label>
            <input
              id="student-id-input"
              className="input"
              placeholder="e.g. STU1001"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
            />
          </div>

          <div>
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--brand-glow)',
                fontSize: 12,
                cursor: 'pointer',
                padding: 0,
                display: 'inline-flex',
                alignItems: 'center',
                gap: 4
              }}
            >
              {showAdvanced ? '− Hide Initial Baseline Parameters' : '+ Customize Baseline Parameters'}
            </button>

            {showAdvanced && (
              <div style={{
                marginTop: 10,
                background: 'rgba(255, 255, 255, 0.03)',
                padding: 12,
                borderRadius: 8,
                border: '1px solid var(--border-subtle)'
              }}>
                <label style={{ display: 'block', fontSize: 11, color: 'var(--text-secondary)', marginBottom: 4 }}>
                  Historical Baseline Attendance Rate (%)
                </label>
                <input
                  type="number"
                  min="50"
                  max="100"
                  className="input"
                  value={baselineAtt}
                  onChange={(e) => setBaselineAtt(e.target.value)}
                  style={{ width: '100%' }}
                />
                <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
                  Tripwire measures behavioral drift relative to each student's personal historical baseline.
                </div>
              </div>
            )}
          </div>

          {/* Footer Buttons */}
          <div style={{
            marginTop: 10,
            display: 'flex',
            justifyContent: 'flex-end',
            gap: 10,
            borderTop: '1px solid rgba(255, 255, 255, 0.08)',
            paddingTop: 16
          }}>
            <button type="button" className="btn btn-ghost btn-sm" onClick={onClose}>
              Cancel
            </button>
            <button
              id="submit-create-student-btn"
              type="submit"
              className="btn btn-primary btn-sm"
              disabled={submitting}
              style={{ minWidth: 120 }}
            >
              {submitting ? 'Adding...' : 'Add Student'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
