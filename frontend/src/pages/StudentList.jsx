import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { studentsAPI } from '../api/client'
import { StatusBadge, DVIBar, VelocityLabel, LoadingScreen, PrototypeThresholdBadge } from '../components/Shared'
import { Search, ChevronRight, Users, Sparkles, Filter, UserPlus, Upload, CheckSquare, RotateCcw, Trash2, Activity } from 'lucide-react'
import { useModals } from '../context/ModalContext'
import AddStudentModal from '../components/AddStudentModal'
import ImportCSVModal from '../components/ImportCSVModal'
import LogTelemetryModal from '../components/LogTelemetryModal'
import BatchAttendanceModal from '../components/BatchAttendanceModal'
import toast from 'react-hot-toast'

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

  // Modals state
  const [isAddOpen, setIsAddOpen] = useState(false)
  const [isImportOpen, setIsImportOpen] = useState(false)
  const [isBatchOpen, setIsBatchOpen] = useState(false)
  const [selectedStudentForTelemetry, setSelectedStudentForTelemetry] = useState(null)

  const fetchStudents = () => {
    setLoading(true)
    studentsAPI.list({ status: statusFilter, search })
      .then(res => setStudents(res.data.students || []))
      .catch(() => toast.error('Failed to load students'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchStudents() }, [statusFilter])

  const handleSearch = (e) => {
    e.preventDefault()
    fetchStudents()
  }

  const handleDeleteStudent = async (e, studentId, studentName) => {
    e.stopPropagation()
    if (!window.confirm(`Are you sure you want to delete student '${studentName}'? All associated attendance and alerts will also be deleted.`)) {
      return
    }
    try {
      await studentsAPI.delete(studentId)
      toast.success(`Student '${studentName}' deleted.`)
      fetchStudents()
    } catch (err) {
      toast.error('Failed to delete student')
    }
  }

  const handleResetCohort = async (mode) => {
    const msg = mode === 'seed'
      ? 'Reload the 50-student synthetic demo cohort? This will replace your current roster.'
      : 'Clear all students from your roster to start completely blank?'
    if (!window.confirm(msg)) return

    try {
      await studentsAPI.resetCohort(mode)
      toast.success(mode === 'seed' ? 'Demo cohort loaded.' : 'Cohort cleared.')
      fetchStudents()
    } catch (err) {
      toast.error('Failed to reset cohort')
    }
  }

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 14 }}>
          <div>
            <h1 className="page-title">Students Directory</h1>
            <p className="page-subtitle">
              Continuous behavioral drift monitoring across your mentorship group
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <button
              id="add-student-btn"
              className="btn btn-primary btn-sm"
              onClick={() => setIsAddOpen(true)}
              style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}
            >
              <UserPlus size={14} /> Add Student
            </button>

            <button
              id="import-csv-btn"
              className="btn btn-ghost btn-sm"
              onClick={() => setIsImportOpen(true)}
              style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}
            >
              <Upload size={14} /> Import CSV
            </button>

            <button
              id="batch-attendance-btn"
              className="btn btn-ghost btn-sm"
              onClick={() => setIsBatchOpen(true)}
              style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}
            >
              <CheckSquare size={14} /> Batch Attendance
            </button>

            <button
              id="reset-cohort-btn"
              className="btn btn-ghost btn-sm"
              onClick={() => handleResetCohort(students.length === 0 ? 'seed' : 'empty')}
              title={students.length === 0 ? 'Load Demo Cohort' : 'Clear Roster'}
              style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 11, color: 'var(--text-muted)' }}
            >
              <RotateCcw size={13} /> {students.length === 0 ? 'Load Demo Data' : 'Clear Roster'}
            </button>

            <PrototypeThresholdBadge />
          </div>
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
                  <th style={{ textAlign: 'center' }}>Quick Actions</th>
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
                    <td onClick={(e) => e.stopPropagation()}>
                      <div style={{ display: 'flex', gap: 6, alignItems: 'center', justifyContent: 'center' }}>
                        <button
                          className="btn btn-ghost btn-sm"
                          onClick={(e) => {
                            e.stopPropagation()
                            setSelectedStudentForTelemetry(student)
                          }}
                          title="Log Attendance / Delays"
                          style={{ padding: '4px 8px', fontSize: 11, display: 'inline-flex', alignItems: 'center', gap: 4 }}
                        >
                          <Activity size={13} color="var(--brand-glow)" /> Log
                        </button>
                        <button
                          className="btn btn-ghost btn-sm"
                          onClick={(e) => handleDeleteStudent(e, student.student_id, student.name)}
                          title="Delete Student"
                          style={{ padding: '4px 8px', color: '#ef4444' }}
                        >
                          <Trash2 size={13} />
                        </button>
                      </div>
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

      {/* Dynamic Data Modals */}
      <AddStudentModal
        isOpen={isAddOpen}
        onClose={() => setIsAddOpen(false)}
        onStudentAdded={() => fetchStudents()}
      />

      <ImportCSVModal
        isOpen={isImportOpen}
        onClose={() => setIsImportOpen(false)}
        onImportSuccess={() => fetchStudents()}
      />

      <BatchAttendanceModal
        isOpen={isBatchOpen}
        onClose={() => setIsBatchOpen(false)}
        students={students}
        onAttendanceSubmitted={() => fetchStudents()}
      />

      <LogTelemetryModal
        isOpen={!!selectedStudentForTelemetry}
        onClose={() => setSelectedStudentForTelemetry(null)}
        student={selectedStudentForTelemetry}
        onTelemetryLogged={() => fetchStudents()}
      />
    </div>
  )
}
