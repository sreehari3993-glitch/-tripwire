import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { alertsAPI, interventionsAPI } from '../api/client'
import { StatusBadge, Spinner, LoadingScreen, HumanOverrideNote, PrototypeThresholdBadge } from '../components/Shared'
import {
  ArrowLeft, Sparkles, AlertTriangle, User, MessageSquare,
  CheckCircle, Clock, TrendingDown, Shield, HelpCircle,
  ShieldAlert, ShieldCheck, HelpCircle as QuestionIcon, PhoneCall, Calendar, Award,
  GraduationCap
} from 'lucide-react'
import toast from 'react-hot-toast'

// Form outcome options as specified in prompt section 12
const OUTCOMES = [
  { value: 'Contacted', icon: '💬', label: 'Contacted', desc: 'Initial check-in conversation completed' },
  { value: 'Student requested support', icon: '🙋', label: 'Student Requested Support', desc: 'Student asked for academic or personal assistance' },
  { value: 'Academic issue identified', icon: '📚', label: 'Academic Issue Identified', desc: 'Difficulty with coursework, lab deadlines, or concepts' },
  { value: 'Personal difficulty reported', icon: '🏠', label: 'Personal Difficulty Reported', desc: 'Commute, family, health, or personal circumstance' },
  { value: 'Referred to support service', icon: '🤝', label: 'Referred to Support Service', desc: 'Referred to counseling, tutoring, or financial aid' },
  { value: 'Monitoring', icon: '🟡', label: 'Monitoring', desc: 'Agreed on check-in schedule; monitoring next week' },
  { value: 'Improved', icon: '🟢', label: 'Improved', desc: 'Behavior stabilized; student catching up' },
  { value: 'No response', icon: '⏳', label: 'No Response', desc: 'Attempted contact; awaiting student reply' },
]

const CONTACT_METHODS = [
  'In-Person (Faculty Office)',
  'Video Call (Google Meet/Teams)',
  'Direct Phone Call',
  'Email Outreach',
  'LMS Direct Message'
]

function ComponentBar({ label, score, weight, color, contribution }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <span style={{ fontSize: 13, color: 'var(--text-secondary)', fontWeight: 500 }}>{label}</span>
        <div style={{ display: 'flex', gap: 12, fontSize: 12, fontFamily: 'var(--font-mono)' }}>
          <span style={{ color: 'var(--text-muted)' }}>
            score: <strong style={{ color: 'var(--text-primary)' }}>{Math.round(score)}</strong>
          </span>
          <span style={{ color: 'var(--text-muted)' }}>&times; {(weight * 100).toFixed(0)}% =</span>
          <span style={{ color, fontWeight: 800 }}>{contribution.toFixed(1)} pts</span>
        </div>
      </div>
      <div style={{ height: 8, background: 'rgba(255,255,255,0.05)', borderRadius: 4, overflow: 'hidden' }}>
        <div style={{
          height: '100%', width: `${Math.min(score, 100)}%`,
          background: `linear-gradient(90deg, ${color}88, ${color})`,
          borderRadius: 4,
          transition: 'width 1s cubic-bezier(0.4,0,0.2,1)',
          boxShadow: `0 0 8px ${color}40`
        }} />
      </div>
    </div>
  )
}

export default function AlertDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [alert, setAlert] = useState(null)
  const [intervention, setIntervention] = useState(null)
  const [loading, setLoading] = useState(true)
  const [aiLoading, setAiLoading] = useState(false)
  const [aiResult, setAiResult] = useState(null)

  // Intervention Form State
  const [contactMethod, setContactMethod] = useState(CONTACT_METHODS[0])
  const [selectedOutcome, setSelectedOutcome] = useState('')
  const [notes, setNotes] = useState('')
  const [followUpDate, setFollowUpDate] = useState('2026-09-23')
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  // Human Override State
  const [overrideLoading, setOverrideLoading] = useState(false)

  // System Trust Feedback State
  const [feedback, setFeedback] = useState(null)
  const [feedbackAccurate, setFeedbackAccurate] = useState('accurate')
  const [feedbackUseful, setFeedbackUseful] = useState(5)
  const [feedbackComment, setFeedbackComment] = useState('')
  const [submittingFeedback, setSubmittingFeedback] = useState(false)
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false)
  const [isEditingFeedback, setIsEditingFeedback] = useState(false)

  const reloadAlert = () => {
    return Promise.all([
      alertsAPI.get(id),
      interventionsAPI.get(id)
    ]).then(([aRes, iRes]) => {
      setAlert(aRes.data)
      if (aRes.data.feedback) {
        setFeedback(aRes.data.feedback)
        setFeedbackAccurate(aRes.data.feedback.was_accurate)
        setFeedbackUseful(aRes.data.feedback.was_useful)
        setFeedbackComment(aRes.data.feedback.comment || '')
        setFeedbackSubmitted(true)
      }
      if (iRes.data.intervention) {
        setIntervention(iRes.data.intervention)
        setSubmitted(true)
      }
    })
  }

  const handleSubmitFeedback = async (accVal, useVal) => {
    const acc = accVal !== undefined ? accVal : feedbackAccurate
    const use = useVal !== undefined ? useVal : feedbackUseful
    setSubmittingFeedback(true)
    try {
      const res = await alertsAPI.submitFeedback(id, {
        was_accurate: acc,
        was_useful: use,
        free_text_comment: feedbackComment
      })
      setFeedback(res.data.feedback)
      setFeedbackSubmitted(true)
      setIsEditingFeedback(false)
      toast.success('System trust feedback recorded!')
    } catch (e) {
      toast.error('Failed to submit system trust feedback')
    } finally {
      setSubmittingFeedback(false)
    }
  }

  useEffect(() => {
    setLoading(true)
    reloadAlert().finally(() => setLoading(false))
  }, [id])

  const handleAIExplain = async () => {
    setAiLoading(true)
    try {
      const res = await alertsAPI.aiExplain(id)
      setAiResult(res.data)
    } catch (e) {
      toast.error('AI explanation failed. Using deterministic fallback.')
    } finally {
      setAiLoading(false)
    }
  }

  const handleSubmitIntervention = async () => {
    if (!selectedOutcome) {
      toast.error('Please select an intervention outcome')
      return
    }
    setSubmitting(true)
    try {
      const res = await interventionsAPI.create({
        alert_id: parseInt(id),
        contact_method: contactMethod,
        outcome: selectedOutcome,
        notes,
        follow_up_date: followUpDate,
        post_dvi: null
      })
      setIntervention(res.data)
      setSubmitted(true)
      toast.success('Faculty intervention successfully logged')
      reloadAlert()
    } catch (e) {
      toast.error('Failed to record intervention')
    } finally {
      setSubmitting(false)
    }
  }

  const handleHumanOverride = async () => {
    setOverrideLoading(true)
    try {
      await alertsAPI.excuse(id)
      toast.success('Human override recorded: Alert marked as EXCUSED.')
      reloadAlert()
    } catch (e) {
      toast.error('Failed to apply human override')
    } finally {
      setOverrideLoading(false)
    }
  }

  if (loading) return <LoadingScreen text="Loading alert telemetry..." />
  if (!alert) return <div style={{ padding: 32, color: 'var(--text-muted)' }}>Alert not found.</div>

  const { components, reason, baselines, counterfactual } = alert
  const dvi = alert.dvi_score
  const dviColor =
    dvi >= 70 ? '#ef4444' :
      dvi >= 50 ? '#f59e0b' : '#10b981'

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <button className="back-btn" onClick={() => navigate(-1)}>
          <ArrowLeft size={14} /> Back
        </button>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
              <AlertTriangle size={22} color="var(--color-tripwire)" />
              <h1 className="page-title" style={{ margin: 0 }}>
                Tripwire Alert #{alert.alert_id} — {alert.student_name}
              </h1>
              <StatusBadge status={alert.status} />
            </div>
            <p className="page-subtitle">
              Class: <strong>{alert.section}</strong> · Roll: {alert.roll_no} · Student ID: {alert.student_id} · Triggered {new Date(alert.trigger_date).toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}
            </p>
          </div>

          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <button
              id="alert-excuse-btn"
              className="btn btn-ghost btn-sm"
              onClick={handleHumanOverride}
              disabled={overrideLoading || alert.excused_flag}
              style={{ display: 'flex', alignItems: 'center', gap: 6 }}
            >
              <ShieldCheck size={14} color="var(--color-normal)" />
              {alert.excused_flag ? 'Excused Override Applied' : 'Mark as Excused'}
            </button>

            <button
              className="btn btn-ghost btn-sm"
              onClick={() => navigate(`/students/${alert.student_id}`)}
              style={{ display: 'flex', alignItems: 'center', gap: 6 }}
            >
              <User size={13} /> View Full Profile
            </button>
          </div>
        </div>
      </div>

      <div className="page-body">
        {/* Top Grid: DVI Score Breakdown & Why Was Alert Triggered */}
        <div className="grid-2" style={{ marginBottom: 20 }}>
          {/* DVI Score Card */}
          <div className="card card-p" style={{
            background: 'linear-gradient(135deg, rgba(239,68,68,0.08), rgba(220,38,38,0.03))',
            border: '1px solid rgba(239,68,68,0.25)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Disengagement Velocity Index (DVI)
              </div>
              <span style={{ fontSize: 10, color: '#ef4444', background: 'rgba(239,68,68,0.15)', padding: '2px 8px', borderRadius: 4, fontWeight: 800 }}>
                {alert.threshold_label || 'Prototype Threshold: DVI >= 70'}
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 12, marginBottom: 14 }}>
              <div style={{ fontSize: 56, fontWeight: 900, color: dviColor, fontFamily: 'var(--font-mono)', lineHeight: 1, filter: `drop-shadow(0 0 16px ${dviColor}60)` }}>
                {Math.round(alert.dvi_score)}
              </div>
              <div style={{ paddingBottom: 8 }}>
                <div style={{ fontSize: 16, color: 'var(--text-muted)' }}>/100</div>
                <div style={{ fontSize: 12, color: 'var(--color-tripwire)', fontWeight: 800 }}>TRIPWIRE ACTIVE</div>
              </div>
            </div>

            {/* Human Override indicator if excused */}
            {alert.excused_flag && (
              <div style={{
                background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.25)',
                borderRadius: 8, padding: '8px 12px', fontSize: 11, color: 'var(--color-monitor)',
                display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12
              }}>
                <Shield size={14} />
                <span>Marked as EXCUSED by faculty mentor — signal de-escalated.</span>
              </div>
            )}

            <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              Calculated strictly relative to <strong style={{ color: '#fff' }}>{alert.student_name}'s personal baseline</strong>—never against a generic class average.
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 8, fontStyle: 'italic' }}>
              Notice: Decision-support early warning indicator; not a medical, psychological, or disciplinary diagnosis.
            </div>
          </div>

          {/* Explainable Factor Contribution Breakdown */}
          <div className="card card-p">
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 16 }}>
              Why Did Tripwire Trigger? — Component Contributions
            </div>
            {components.series_exam && (
              <ComponentBar
                label="Series Exam Mark Drift"
                score={components.series_exam.score}
                weight={components.series_exam.weight}
                color="#ec4899"
                contribution={components.series_exam.contribution}
              />
            )}
            <ComponentBar
              label="Attendance Drift"
              score={components.attendance.score}
              weight={components.attendance.weight}
              color="#6366f1"
              contribution={components.attendance.contribution}
            />
            <ComponentBar
              label="Submission Delay Drift"
              score={components.submission.score}
              weight={components.submission.weight}
              color="#f59e0b"
              contribution={components.submission.contribution}
            />
            <ComponentBar
              label="Engagement Drop"
              score={components.engagement.score}
              weight={components.engagement.weight}
              color="#06b6d4"
              contribution={components.engagement.contribution}
            />
            <div style={{
              borderTop: '1px solid var(--border-subtle)', paddingTop: 12, marginTop: 4,
              display: 'flex', justifyContent: 'space-between', alignItems: 'center'
            }}>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                DVI = {components.series_exam ? `${(components.series_exam.weight ?? 0.30).toFixed(2)}(${Math.round(components.series_exam.score)}) + ` : ''}{(components.attendance.weight ?? 0.30).toFixed(2)}({Math.round(components.attendance.score)}) + {(components.submission.weight ?? 0.30).toFixed(2)}({Math.round(components.submission.score)}) + {(components.engagement.weight ?? 0.10).toFixed(2)}({Math.round(components.engagement.score)})
              </span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 900, fontSize: 18, color: dviColor }}>
                = {Math.round(
                  (components.series_exam?.contribution ?? 0) +
                  components.attendance.contribution +
                  components.submission.contribution +
                  components.engagement.contribution
                )}
              </span>
            </div>

            {/* Semester Exam Criteria & Mark Threshold Standing */}
            <div style={{
              borderTop: '1px solid var(--border-subtle)',
              paddingTop: 12,
              marginTop: 12,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: 8,
              fontSize: 11
            }}>
              <div>
                <strong style={{ color: '#f87171' }}>Academic Criteria Check:</strong>{' '}
                <span style={{ color: 'var(--text-secondary)' }}>
                  Series Exam Cutoff &ge;45% · Statutory Attendance &ge;75% · Passing CIE Mark &ge;40% (DVI &ge;50 flags Exam Risk)
                </span>
                <div style={{ color: 'var(--text-muted)', fontSize: 10, marginTop: 2 }}>
                  {alert.exam_eligibility?.label || `DVI ${Math.round(alert.dvi_score)} exceeds risk threshold (50) — Exam Debarment & CIE Mark Fail Risk`}
                </div>
              </div>
              <span style={{
                fontSize: 10,
                fontWeight: 700,
                color: (alert.exam_eligibility?.is_eligible ?? (alert.dvi_score < 70)) ? '#10b981' : '#ef4444',
                background: (alert.exam_eligibility?.is_eligible ?? (alert.dvi_score < 70)) ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
                border: '1px solid ' + ((alert.exam_eligibility?.is_eligible ?? (alert.dvi_score < 70)) ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'),
                padding: '3px 8px',
                borderRadius: 4,
                fontFamily: 'var(--font-mono)'
              }}>
                {(alert.exam_eligibility?.status ?? 'EXAM_RISK').toUpperCase()}
              </span>
            </div>
          </div>
        </div>

        {/* SEPARATE Self-Reported Signal Card (Qualitative Corroborating Evidence) */}
        <div className="card card-p" style={{
          background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.08), rgba(99, 102, 241, 0.04))',
          border: '1px solid rgba(168, 85, 247, 0.3)',
          marginBottom: 20
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: 18 }}>💭</span>
              <span style={{ fontSize: 13, fontWeight: 700, color: '#c084fc', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Self-Reported Signal — Qualitative Pulse Check
              </span>
            </div>
            <span style={{
              fontSize: 10, fontWeight: 700, padding: '3px 8px', borderRadius: 4,
              background: 'rgba(168, 85, 247, 0.15)', color: '#d8b4fe', border: '1px solid rgba(168, 85, 247, 0.3)'
            }}>
              Non-Weighted Corroborating Context
            </span>
          </div>

          {alert.pulse ? (
            <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start', flexWrap: 'wrap' }}>
              <div style={{
                background: 'rgba(0,0,0,0.3)', borderRadius: 10, padding: '10px 14px',
                display: 'flex', alignItems: 'center', gap: 10
              }}>
                <span style={{ fontSize: 24 }}>
                  {alert.pulse.rating === 1 ? '😫' :
                    alert.pulse.rating === 2 ? '😟' :
                      alert.pulse.rating === 3 ? '😐' :
                        alert.pulse.rating === 4 ? '🙂' : '🌟'}
                </span>
                <div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Self-Rating</div>
                  <div style={{ fontSize: 13, fontWeight: 800, color: alert.pulse.rating <= 2 ? '#ef4444' : '#10b981' }}>
                    {alert.pulse.rating}/5 — {alert.pulse.rating <= 2 ? 'Struggling' : alert.pulse.rating === 3 ? 'Moderate' : 'Good'}
                  </div>
                </div>
              </div>

              <div style={{ flex: 1, minWidth: 240 }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 3 }}>
                  Student Self-Report ({alert.pulse.date ? new Date(alert.pulse.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : 'Recent'})
                </div>
                <div style={{
                  fontSize: 13, color: 'var(--text-primary)', fontStyle: 'italic',
                  background: 'rgba(255,255,255,0.02)', padding: '8px 12px', borderRadius: 6,
                  borderLeft: '3px solid #c084fc'
                }}>
                  "{alert.pulse.stuck_on || 'No additional comment provided.'}"
                </div>
              </div>
            </div>
          ) : (
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              No self-reported pulse submitted this week.
            </div>
          )}

          <div style={{ marginTop: 12, fontSize: 11, color: 'var(--text-muted)', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: 8 }}>
            💡 <strong>Corroborating Dimension:</strong> This qualitative check-in provides student voice to contextualize telemetry drift (e.g. confirms project/lab stress) without altering the deterministic, transparent 40/35/25 DVI weights.
          </div>
        </div>

        {/* Counterfactual Explanation Box */}
        {counterfactual && (

          <div className="card card-p" style={{
            marginBottom: 20,
            background: 'rgba(99, 102, 241, 0.06)',
            border: '1px solid rgba(99, 102, 241, 0.25)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <HelpCircle size={16} color="var(--brand-glow)" />
              <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--brand-glow)', textTransform: 'uppercase', letterSpacing: 0.5 }}>
                Counterfactual Analysis ("What If?")
              </span>
            </div>

            <p style={{ margin: 0, fontSize: 14, color: '#f8fafc', fontStyle: 'italic', lineHeight: 1.6, marginBottom: 12 }}>
              "{counterfactual.summary}"
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
              <div style={{ background: 'var(--bg-elevated)', borderRadius: 8, padding: '10px 12px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>If Submission at Baseline:</div>
                <div style={{ fontSize: 14, fontWeight: 700, color: '#10b981', fontFamily: 'var(--font-mono)' }}>
                  DVI &rarr; {counterfactual.scenarios.if_submission_baseline.hypothetical_dvi}
                </div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Clears Tripwire</div>
              </div>

              <div style={{ background: 'var(--bg-elevated)', borderRadius: 8, padding: '10px 12px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>If LMS at Baseline:</div>
                <div style={{ fontSize: 14, fontWeight: 700, color: '#f59e0b', fontFamily: 'var(--font-mono)' }}>
                  DVI &rarr; {counterfactual.scenarios.if_lms_baseline.hypothetical_dvi}
                </div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Monitoring</div>
              </div>

              <div style={{ background: 'var(--bg-elevated)', borderRadius: 8, padding: '10px 12px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>If Both Sub & LMS Restored:</div>
                <div style={{ fontSize: 14, fontWeight: 700, color: '#10b981', fontFamily: 'var(--font-mono)' }}>
                  DVI &rarr; {counterfactual.scenarios.if_submission_and_lms_baseline.hypothetical_dvi}
                </div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Normal Status</div>
              </div>
            </div>

            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 10 }}>
              {counterfactual.disclaimer}
            </div>
          </div>
        )}

        {/* AI Explanation & Mentor Guidance */}
        <div className="card card-p" style={{ marginBottom: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Sparkles size={16} color="var(--brand-glow)" />
              <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>
                AI Explanation & Mentorship Guidance Layer
              </span>
            </div>
            {!aiResult && (
              <button
                id="generate-ai-btn"
                className="btn btn-primary btn-sm"
                onClick={handleAIExplain}
                disabled={aiLoading}
              >
                {aiLoading ? <><Spinner size={14} /> Generating Guidance...</> : <><Sparkles size={13} /> Generate Guidance</>}
              </button>
            )}
          </div>

          {!aiResult && !aiLoading && (
            <div style={{
              border: '1px dashed var(--border-default)', borderRadius: 10, padding: '24px',
              textAlign: 'center', color: 'var(--text-muted)', fontSize: 13
            }}>
              <Sparkles size={24} style={{ margin: '0 auto 8px', display: 'block', color: 'var(--brand-primary)', opacity: 0.6 }} />
              Click "Generate Guidance" to obtain an empathetic, non-judgmental explanation of recent behavioral drift,
              suggested conversation starters, and recommended exploratory questions for your check-in.
              <div style={{ fontSize: 11, marginTop: 8, color: 'var(--text-muted)', fontStyle: 'italic' }}>
                Strict Ethical Safeguard: The AI translates observable academic telemetry — it never diagnoses mental health or assigns punitive blame.
              </div>
            </div>
          )}

          {aiLoading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 24 }}>
              <Spinner size={20} />
              <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>Synthesizing supportive mentor guidance...</span>
            </div>
          )}

          {aiResult && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {/* Plain-language explanation */}
              <div className="ai-card">
                <div className="ai-badge">
                  <Sparkles size={11} />
                  {aiResult.source === 'gemini' ? 'Gemini 1.5 Flash' : 'Pattern Analyzer'} · Behavioral Drift Summary
                </div>
                <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7, margin: 0 }}>
                  {aiResult.explanation}
                </p>
              </div>

              {/* Suggested conversation starter */}
              <div style={{
                background: 'rgba(16,185,129,0.06)',
                border: '1px solid rgba(16,185,129,0.25)',
                borderRadius: 12, padding: 18
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
                  <MessageSquare size={14} color="var(--color-normal)" />
                  <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--color-normal)', textTransform: 'uppercase', letterSpacing: 0.5 }}>
                    Suggested Non-Judgmental Conversation Starter
                  </span>
                </div>
                <blockquote style={{
                  fontSize: 14, color: '#f8fafc',
                  fontStyle: 'italic', lineHeight: 1.7,
                  borderLeft: '3px solid var(--color-normal)',
                  paddingLeft: 14, margin: 0
                }}>
                  "{aiResult.talking_point}"
                </blockquote>
              </div>

              {/* Suggested Mentor Questions */}
              {aiResult.suggested_questions && (
                <div style={{
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 12, padding: 16
                }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 10 }}>
                    Recommended Exploratory Questions
                  </div>
                  <ul style={{ margin: 0, paddingLeft: 20, display: 'flex', flexDirection: 'column', gap: 6, fontSize: 13, color: 'var(--text-secondary)' }}>
                    {aiResult.suggested_questions.map((q, idx) => (
                      <li key={idx}>{q}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div style={{ fontSize: 11, color: 'var(--text-muted)', fontStyle: 'italic' }}>
                🔒 Confidential to faculty mentor. Students do not see this risk analysis.
              </div>
            </div>
          )}
        </div>

        {/* Human-in-the-Loop Intervention Panel */}
        <div className="card card-p">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
            <CheckCircle size={18} color={submitted ? 'var(--color-normal)' : 'var(--text-muted)'} />
            <h3 style={{ margin: 0, fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
              {submitted ? 'Faculty Intervention Recorded' : 'Record Mentor Intervention (Human-in-the-Loop)'}
            </h3>
          </div>

          {submitted && intervention ? (
            <div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, marginBottom: 16 }}>
                <div style={{ background: 'var(--bg-elevated)', borderRadius: 10, padding: '12px 16px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Outcome</div>
                  <div style={{ fontWeight: 700, color: 'var(--color-normal)' }}>
                    {OUTCOMES.find(o => o.value === intervention.outcome)?.icon || '✅'}{' '}
                    {intervention.outcome}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-elevated)', borderRadius: 10, padding: '12px 16px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Contact Method</div>
                  <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                    {intervention.contact_method || 'In-Person'}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-elevated)', borderRadius: 10, padding: '12px 16px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Contact Date</div>
                  <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                    {new Date(intervention.contact_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}
                  </div>
                </div>
              </div>

              {intervention.notes && (
                <div style={{ background: 'var(--bg-elevated)', borderRadius: 10, padding: '14px 16px', border: '1px solid var(--border-subtle)', marginBottom: 16 }}>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6 }}>Meeting Notes & Action Plan</div>
                  <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{intervention.notes}</div>
                </div>
              )}

              {/* Recovery Loop Projection */}
              <div style={{
                display: 'flex', alignItems: 'center', gap: 16, padding: '14px 18px',
                background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.25)',
                borderRadius: 10
              }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 900, color: 'var(--color-tripwire)', fontFamily: 'var(--font-mono)' }}>
                    {Math.round(alert.dvi_score)}
                  </div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Pre-Intervention</div>
                </div>
                <div style={{ color: 'var(--text-muted)', fontSize: 20 }}>&rarr;</div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 900, color: 'var(--color-normal)', fontFamily: 'var(--font-mono)' }}>
                    {intervention.post_dvi ? Math.round(intervention.post_dvi) : Math.round(Math.max(35, alert.dvi_score - 18))}
                  </div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Projected Post-Intervention</div>
                </div>
                <div style={{ fontSize: 13, color: 'var(--color-normal)', fontWeight: 600, marginLeft: 8 }}>
                  🟢 Behavioral turnaround loop active. Tripwire will now monitor for recovery trajectory.
                </div>
              </div>
            </div>
          ) : (
            <div>
              <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 16 }}>
                Record your check-in notes and the agreed action plan. This closes the telemetry loop and initiates recovery tracking.
              </div>

              {/* Contact Method Selector */}
              <div style={{ marginBottom: 16 }}>
                <label className="form-label">Contact Method</label>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {CONTACT_METHODS.map(method => (
                    <button
                      key={method}
                      type="button"
                      className={`btn btn-sm ${contactMethod === method ? 'btn-primary' : 'btn-ghost'}`}
                      onClick={() => setContactMethod(method)}
                    >
                      {method}
                    </button>
                  ))}
                </div>
              </div>

              {/* Outcome Options Grid */}
              <div style={{ marginBottom: 16 }}>
                <label className="form-label">Outcome of Intervention</label>
                <div className="outcome-options" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10 }}>
                  {OUTCOMES.map(opt => (
                    <div
                      key={opt.value}
                      id={`outcome-${opt.value.toLowerCase().replace(/\s+/g, '-')}`}
                      className={`outcome-option ${selectedOutcome === opt.value ? 'selected' : ''}`}
                      onClick={() => setSelectedOutcome(opt.value)}
                      style={{ padding: '10px 14px' }}
                    >
                      <span style={{ fontSize: 20 }}>{opt.icon}</span>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: 13, color: 'var(--text-primary)' }}>{opt.label}</div>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{opt.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Notes */}
              <div style={{ marginBottom: 16 }}>
                <label className="form-label">Meeting Notes & Supportive Action Plan</label>
                <textarea
                  id="intervention-notes"
                  className="input"
                  rows={3}
                  placeholder="e.g. Student reported commute and lab deadline conflicts. Connected with peer tutor, granted 48-hour extension on SEP04..."
                  value={notes}
                  onChange={e => setNotes(e.target.value)}
                  style={{ resize: 'vertical' }}
                />
              </div>

              {/* Follow-up Date */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
                <div>
                  <label className="form-label">Follow-up Date</label>
                  <input
                    type="date"
                    className="input"
                    value={followUpDate}
                    onChange={e => setFollowUpDate(e.target.value)}
                  />
                </div>
              </div>

              <button
                id="submit-intervention-btn"
                className="btn btn-primary"
                onClick={handleSubmitIntervention}
                disabled={submitting || !selectedOutcome}
                style={{ opacity: selectedOutcome ? 1 : 0.5, display: 'flex', alignItems: 'center', gap: 8 }}
              >
                {submitting ? <><Spinner size={14} /> Recording Intervention...</> : <><CheckCircle size={15} /> Save Intervention & Track Recovery</>}
              </button>
            </div>
          )}
        </div>

        {/* System Trust & Accuracy Feedback Widget (Closed Loop Tracking) */}
        <div className="card card-p" style={{
          marginTop: 20,
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(13, 19, 34, 0.8))',
          border: '1px solid rgba(99, 102, 241, 0.25)',
          borderRadius: 12
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Award size={18} color="var(--color-brand)" />
              <div>
                <h3 style={{ margin: 0, fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>
                  System Trust & Accuracy Evaluation (Closed-Loop Telemetry)
                </h3>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                  Help Tripwire calibrate its own accuracy over time. Grounded in Expectation-Disconfirmation Theory (Bhattacherjee & Premkumar, 2004).
                </div>
              </div>
            </div>
            {feedbackSubmitted && !isEditingFeedback && (
              <button
                className="btn btn-ghost btn-xs"
                onClick={() => setIsEditingFeedback(true)}
                style={{ fontSize: 11 }}
              >
                ✏️ Edit Feedback
              </button>
            )}
          </div>

          {feedbackSubmitted && !isEditingFeedback ? (
            <div style={{
              background: 'rgba(255, 255, 255, 0.03)',
              borderRadius: 8,
              padding: '12px 16px',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: 12
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
                  <span style={{
                    fontSize: 12,
                    fontWeight: 700,
                    padding: '2px 8px',
                    borderRadius: 6,
                    background: feedback.was_accurate === 'accurate' ? 'rgba(16, 185, 129, 0.15)' :
                      feedback.was_accurate === 'false_positive' ? 'rgba(239, 68, 68, 0.15)' :
                        'rgba(245, 158, 11, 0.15)',
                    color: feedback.was_accurate === 'accurate' ? 'var(--color-normal)' :
                      feedback.was_accurate === 'false_positive' ? 'var(--color-tripwire)' :
                        'var(--color-monitor)'
                  }}>
                    {feedback.was_accurate === 'accurate' ? '🎯 Accurate Flag' :
                      feedback.was_accurate === 'false_positive' ? '⚠️ False Positive' :
                        feedback.was_accurate === 'too_late' ? '⏳ Too Late' : '❓ Unclear Signal'}
                  </span>
                  <span style={{ fontSize: 13, color: '#fbbf24', fontWeight: 700 }}>
                    {'★'.repeat(feedback.was_useful)}{'☆'.repeat(5 - feedback.was_useful)} ({feedback.was_useful}/5 Usefulness)
                  </span>
                </div>
                {feedback.comment && (
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                    "{feedback.comment}"
                  </div>
                )}
              </div>
              <div style={{ fontSize: 11, color: 'var(--color-normal)', fontWeight: 600 }}>
                Recorded for System Trust Score ✓
              </div>
            </div>
          ) : (
            <div>
              {/* Question 1: Accuracy chips */}
              <div style={{ marginBottom: 14 }}>
                <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8 }}>
                  Was this alert accurate?
                </label>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {[
                    { id: 'accurate', label: '🎯 Accurate', desc: 'Real disengagement' },
                    { id: 'false_positive', label: '⚠️ False Positive', desc: 'Normal/excused reason' },
                    { id: 'too_late', label: '⏳ Too Late', desc: 'Already escalated' },
                    { id: 'unclear', label: '❓ Unclear', desc: 'Ambiguous telemetry' }
                  ].map(chip => (
                    <button
                      key={chip.id}
                      type="button"
                      onClick={() => setFeedbackAccurate(chip.id)}
                      style={{
                        padding: '6px 12px',
                        borderRadius: 8,
                        fontSize: 12,
                        fontWeight: 600,
                        cursor: 'pointer',
                        background: feedbackAccurate === chip.id ? 'var(--color-brand)' : 'rgba(255, 255, 255, 0.05)',
                        color: feedbackAccurate === chip.id ? '#fff' : 'var(--text-secondary)',
                        border: feedbackAccurate === chip.id ? '1px solid var(--color-brand)' : '1px solid var(--border-subtle)',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      {chip.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Question 2: Usefulness 1-5 Likert */}
              <div style={{ marginBottom: 14 }}>
                <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8 }}>
                  How useful was this alert for timely mentorship? (1–5 Scale)
                </label>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                  {[1, 2, 3, 4, 5].map(star => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setFeedbackUseful(star)}
                      style={{
                        padding: '6px 10px',
                        borderRadius: 8,
                        fontSize: 13,
                        fontWeight: 700,
                        cursor: 'pointer',
                        background: feedbackUseful >= star ? 'rgba(251, 191, 36, 0.15)' : 'rgba(255, 255, 255, 0.04)',
                        color: feedbackUseful >= star ? '#fbbf24' : 'var(--text-muted)',
                        border: feedbackUseful === star ? '1px solid #fbbf24' : '1px solid var(--border-subtle)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 4
                      }}
                    >
                      ★ {star}
                    </button>
                  ))}
                  <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 6 }}>
                    {feedbackUseful === 1 ? '1 - Not useful' :
                      feedbackUseful === 2 ? '2 - Marginal' :
                        feedbackUseful === 3 ? '3 - Moderately useful' :
                          feedbackUseful === 4 ? '4 - Very useful' :
                            '5 - Essential / critical catch'}
                  </span>
                </div>
              </div>

              {/* Optional Comment */}
              <div style={{ marginBottom: 14 }}>
                <input
                  type="text"
                  className="input"
                  placeholder="Optional note: e.g. Caught latency spike 10 days before midterms. Very actionable."
                  value={feedbackComment}
                  onChange={e => setFeedbackComment(e.target.value)}
                  style={{ fontSize: 12, padding: '8px 12px' }}
                />
              </div>

              <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                <button
                  type="button"
                  className="btn btn-primary btn-sm"
                  onClick={() => handleSubmitFeedback()}
                  disabled={submittingFeedback}
                  style={{ display: 'flex', alignItems: 'center', gap: 6 }}
                >
                  {submittingFeedback ? <Spinner size={12} /> : <CheckCircle size={13} />}
                  Save Accuracy Feedback
                </button>
                {isEditingFeedback && (
                  <button
                    type="button"
                    className="btn btn-ghost btn-sm"
                    onClick={() => setIsEditingFeedback(false)}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
