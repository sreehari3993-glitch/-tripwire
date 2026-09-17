import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { studentsAPI } from '../api/client'
import { StatusBadge, DVIBar, VelocityLabel, LoadingScreen, PrototypeThresholdBadge } from '../components/Shared'
import { Search, ChevronRight, Users, Sparkles, Filter } from 'lucide-react'
import { useModals } from '../context/ModalContext'

const STATUS_OPTIONS = [
  { value: 'all',        label: 'All Students' },
  { value: 'tripwire',   label: '🔴 Tripwire' },
  { value: 'monitoring', label: '🟡 Monitoring' },
  { value: 'recovering', label: '🟣 Recovering' },
  { value: 'normal',     label: '🟢 Normal' },
]

export default function StudentList() {
  const navigate = useNavigate()
  const { openDemo } = useModals()
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  const fetchStudents = () => {
    setLoading(true)
    studentsAPI.list({ status: statusFilter, search })
      .then(res => setStudents(res.data.students))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchStudents() }, [statusFilter])

  const handleSearch = (e) => {
    e.preventDefault()
    fetchStudents()
  }

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h1 className="page-title">Students Directory</h1>
            <p className="page-subtitle">
              Continuous behavioral drift monitoring across your mentorship group
            </p>
          </div>
          <PrototypeThresholdBadge />
        </div>
      </div>

      <div className="page-body">
        {/* Filters and Search Bar */}
        <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap', alignItems: 'center' }}>
          <form onSubmit={handleSearch} style={{ display: 'flex', gap: 8, flex: 1, minWidth: 260 }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <Search size={14} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                id="student-search-input"
                className="input"
                placeholder="Search by name, roll no, or student ID..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                style={{ paddingLeft: 36 }}
              />
            </div>
            <button id="search-submit-btn" className="btn btn-primary btn-sm" type="submit">
              Search
            </button>
          </form>

          {/* Status filter buttons */}
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {STATUS_OPTIONS.map(opt => (
              <button
                key={opt.value}
                id={`filter-${opt.value}`}
                className={`btn btn-sm ${statusFilter === opt.value ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setStatusFilter(opt.value)}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <LoadingScreen text="Loading student telemetry..." />
        ) : students.length === 0 ? (
          <div className="empty-state">
            <div style={{ fontSize: 36, marginBottom: 8 }}>👤</div>
            <div style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>No students match this query</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>Try clearing search or changing the filter.</div>
          </div>
        ) : (
          <div className="card">
            <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span>Student Cohort Telemetry</span>
                <span style={{ color: 'var(--text-muted)', fontWeight: 400, fontSize: 11 }}>
                  ({students.length} matching students)
                </span>
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Signals calculated against individual student baselines
              </div>
            </div>

            <table className="data-table">
              <thead>
                <tr>
                  <th>Student ID</th>
                  <th>Name</th>
                  <th>Class</th>
                  <th>Attendance</th>
                  <th>Assignment Delay</th>
                  <th>LMS Engagement</th>
                  <th style={{ width: 170 }}>DVI Score</th>
                  <th>Trend</th>
                  <th>Status</th>
                  <th>Last Activity</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {students.map(student => (
                  <tr
                    key={student.student_id}
                    onClick={() => navigate(`/students/${student.student_id}`)}
                    id={`student-row-${student.student_id}`}
                    style={{ cursor: 'pointer' }}
                  >
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--brand-glow)', fontWeight: 600 }}>
                      {student.student_id}
                    </td>
                    <td>
                      <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{student.name}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Roll: {student.roll_no}</div>
                    </td>
                    <td style={{ fontSize: 12 }}>{student.section}</td>
                    <td style={{ fontSize: 12, fontFamily: 'var(--font-mono)' }}>{student.attendance}</td>
                    <td style={{ fontSize: 12, fontFamily: 'var(--font-mono)' }}>{student.assignment_delay}</td>
                    <td style={{ fontSize: 12, fontFamily: 'var(--font-mono)' }}>{student.lms_engagement}</td>
                    <td><DVIBar dvi={student.dvi} /></td>
                    <td><VelocityLabel velocity={student.velocity} /></td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <StatusBadge status={student.status} />
                        {student.alert_id && student.status === 'tripwire' && (
                          <span style={{ fontSize: 9, color: '#ef4444', background: 'rgba(239,68,68,0.15)', padding: '1px 5px', borderRadius: 4, fontWeight: 800 }}>
                            ALERT
                          </span>
                        )}
                      </div>
                    </td>
                    <td style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                      {student.last_activity}
                    </td>
                    <td>
                      <ChevronRight size={16} color="var(--text-muted)" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
