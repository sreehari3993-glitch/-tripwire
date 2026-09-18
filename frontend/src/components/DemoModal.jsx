import React, { useState, useEffect, useRef } from 'react'
import {
  Play, Pause, RotateCcw, ChevronRight, ChevronLeft, X,
  Sparkles, AlertTriangle, CheckCircle, Clock, Activity, MessageSquare,
  Shield, TrendingDown, TrendingUp, HelpCircle, ArrowRight
} from 'lucide-react'
import { StatusBadge, VelocityLabel } from './Shared'
import { BASE_URL } from '../api/client'

export default function DemoModal({ isOpen, onClose }) {
  const [stages, setStages] = useState([])
  const [currentIdx, setCurrentIdx] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [speed, setSpeed] = useState(1) // 1x, 1.5x, 2x
  const timerRef = useRef(null)

  useEffect(() => {
    // Fetch stages from backend demo API
    fetch(`${BASE_URL}/demo/stages`)
      .then(r => r.json())
      .then(d => {
        if (d.stages) setStages(d.stages)
      })
      .catch(() => {
        // Fallback demo stages if offline
        setStages(FALLBACK_STAGES)
      })
  }, [])

  // Auto-play timer
  useEffect(() => {
    if (isPlaying) {
      const intervalMs = Math.round(11000 / speed)
      timerRef.current = setInterval(() => {
        setCurrentIdx(prev => {
          if (prev >= stages.length - 1) {
            setIsPlaying(false)
            return prev
          }
          return prev + 1
        })
      }, intervalMs)
    } else {
      if (timerRef.current) clearInterval(timerRef.current)
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [isPlaying, currentIdx, speed, stages.length])

  if (!isOpen || stages.length === 0) return null

  const stage = stages[currentIdx]
  const dvi = stage.dvi
  const dviColor =
    dvi >= 70 ? '#ef4444' :
      dvi >= 50 ? '#f59e0b' :
        stage.status === 'recovering' ? '#a855f7' : '#10b981'

  const handleNext = () => {
    if (currentIdx < stages.length - 1) setCurrentIdx(currentIdx + 1)
  }

  const handlePrev = () => {
    if (currentIdx > 0) setCurrentIdx(currentIdx - 1)
  }

  const handleRestart = () => {
    setCurrentIdx(0)
    setIsPlaying(true)
  }

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(5, 8, 16, 0.88)',
      backdropFilter: 'blur(16px)',
      zIndex: 9999,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 20
    }}>
      <div style={{
        background: 'linear-gradient(180deg, #0d1322 0%, #080c14 100%)',
        border: '1px solid rgba(99, 102, 241, 0.25)',
        boxShadow: '0 24px 60px rgba(0, 0, 0, 0.8), 0 0 40px rgba(99, 102, 241, 0.15)',
        borderRadius: 20,
        width: '100%',
        maxWidth: 1040,
        maxHeight: '92vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Modal Top Bar */}
        <div style={{
          padding: '16px 24px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'rgba(255, 255, 255, 0.02)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 10,
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <Sparkles size={16} color="#fff" />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: 15, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: 8 }}>
                TRIPWIRE DEMO EXPERIENCE
                <span style={{ fontSize: 10, color: 'var(--brand-glow)', background: 'rgba(99,102,241,0.15)', padding: '2px 8px', borderRadius: 4 }}>
                  STUDENT STORY: RAHUL MENON (S5 CSE)
                </span>
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                60–90s Guided Trajectory: Baseline &rarr; Silent Drift &rarr; Tripwire Alert &rarr; Mentorship &rarr; Recovery
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <button
              id="demo-modal-close"
              className="btn btn-ghost btn-sm"
              onClick={onClose}
              style={{ borderRadius: 8, padding: '6px 10px' }}
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Stepper Timeline Bar */}
        <div style={{
          padding: '14px 24px',
          background: 'rgba(0, 0, 0, 0.25)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
          display: 'flex',
          alignItems: 'center',
          gap: 8
        }}>
          {stages.map((stg, i) => {
            const isActive = i === currentIdx
            const isDone = i < currentIdx
            const stepColor =
              stg.dvi >= 70 ? '#ef4444' :
                stg.dvi >= 50 ? '#f59e0b' :
                  stg.status === 'recovering' ? '#a855f7' : '#10b981'

            return (
              <React.Fragment key={stg.stage}>
                <div
                  id={`demo-step-${stg.stage}`}
                  onClick={() => setCurrentIdx(i)}
                  style={{
                    flex: 1,
                    cursor: 'pointer',
                    padding: '8px 10px',
                    borderRadius: 8,
                    background: isActive ? 'rgba(99, 102, 241, 0.15)' : 'rgba(255, 255, 255, 0.02)',
                    border: isActive ? `1px solid ${stepColor}` : '1px solid rgba(255, 255, 255, 0.05)',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ fontSize: 10, fontWeight: 700, color: isActive ? '#fff' : 'var(--text-muted)' }}>
                      STAGE {stg.stage}
                    </span>
                    <span style={{
                      fontSize: 11,
                      fontFamily: 'var(--font-mono)',
                      fontWeight: 800,
                      color: stepColor
                    }}>
                      DVI {stg.dvi}
                    </span>
                  </div>
                  <div style={{ fontSize: 11, fontWeight: 600, color: isActive ? stepColor : 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {stg.phase || stg.title}
                  </div>
                </div>
                {i < stages.length - 1 && (
                  <ArrowRight size={12} color="rgba(255, 255, 255, 0.2)" />
                )}
              </React.Fragment>
            )
          })}
        </div>

        {/* Modal Body */}
        <div style={{ padding: 24, overflowY: 'auto', flex: 1 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: 20 }}>
            {/* Left Column: DVI Gauge & Core Stats */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: 14,
              padding: 20,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>
                {stage.timeframe}
              </div>

              {/* Large Radial DVI display */}
              <div style={{
                width: 140, height: 140, borderRadius: '50%',
                background: `radial-gradient(circle, ${dviColor}18 0%, transparent 70%)`,
                border: `3px solid ${dviColor}`,
                boxShadow: `0 0 24px ${dviColor}40`,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: 16,
                transition: 'all 0.5s ease'
              }}>
                <div style={{ fontSize: 44, fontWeight: 900, fontFamily: 'var(--font-mono)', color: dviColor, lineHeight: 1 }}>
                  {stage.dvi}
                </div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4, letterSpacing: 1 }}>
                  DVI / 100
                </div>
              </div>

              <div style={{ marginBottom: 16 }}>
                <StatusBadge status={stage.status} />
              </div>

              {/* Threshold indicator */}
              <div style={{
                background: 'var(--bg-elevated)',
                borderRadius: 8,
                padding: '8px 12px',
                fontSize: 11,
                color: 'var(--text-muted)',
                width: '100%',
                lineHeight: 1.5
              }}>
                <div>Prototype Threshold:</div>
                <div style={{ color: dvi >= 70 ? '#ef4444' : dvi >= 50 ? '#f59e0b' : '#10b981', fontWeight: 700 }}>
                  {dvi >= 70 ? 'CRITICAL DRIFT (>= 70)' : dvi >= 50 ? 'BORDERLINE DRIFT (50–69)' : 'NORMAL (< 50)'}
                </div>
              </div>
            </div>

            {/* Right Column: Stage Narrative & Interactive Elements */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {/* Title & Badge */}
              <div style={{
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: 14,
                padding: '16px 20px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                  <h3 style={{ margin: 0, fontSize: 18, color: '#f8fafc', fontWeight: 700 }}>
                    {stage.title}
                  </h3>
                  <span style={{
                    fontSize: 12,
                    fontWeight: 700,
                    color: dviColor,
                    background: `${dviColor}15`,
                    border: `1px solid ${dviColor}30`,
                    padding: '3px 10px',
                    borderRadius: 6
                  }}>
                    {stage.badge}
                  </span>
                </div>
                <p style={{ margin: 0, fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {stage.narrative}
                </p>
              </div>

              {/* Metrics Snapshot */}
              {stage.metrics && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
                  <div style={{ background: 'var(--bg-elevated)', borderRadius: 10, padding: '12px 14px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Attendance</div>
                    <div style={{ fontSize: 16, fontWeight: 700, color: '#6366f1', fontFamily: 'var(--font-mono)' }}>
                      {stage.metrics.attendance.current}%
                    </div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Baseline: {stage.metrics.attendance.baseline}%</div>
                  </div>

                  <div style={{ background: 'var(--bg-elevated)', borderRadius: 10, padding: '12px 14px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Submission Latency</div>
                    <div style={{ fontSize: 16, fontWeight: 700, color: '#f59e0b', fontFamily: 'var(--font-mono)' }}>
                      {stage.metrics.submission_delay.current}h
                    </div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Baseline: {stage.metrics.submission_delay.baseline}h</div>
                  </div>

                  <div style={{ background: 'var(--bg-elevated)', borderRadius: 10, padding: '12px 14px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>LMS Activity</div>
                    <div style={{ fontSize: 16, fontWeight: 700, color: '#06b6d4', fontFamily: 'var(--font-mono)' }}>
                      {stage.metrics.lms_activity.current}/wk
                    </div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Baseline: {stage.metrics.lms_activity.baseline}/wk</div>
                  </div>
                </div>
              )}

              {/* Stage 3 Highlight: What Changed & Counterfactual & AI */}
              {stage.stage === 3 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {/* Counterfactual Card */}
                  <div style={{
                    background: 'rgba(99, 102, 241, 0.08)',
                    border: '1px solid rgba(99, 102, 241, 0.25)',
                    borderRadius: 10,
                    padding: '12px 16px'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                      <HelpCircle size={14} color="var(--brand-glow)" />
                      <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--brand-glow)', textTransform: 'uppercase', letterSpacing: 0.5 }}>
                        Counterfactual Explanation
                      </span>
                    </div>
                    <p style={{ margin: 0, fontSize: 13, color: 'var(--text-primary)', fontStyle: 'italic', lineHeight: 1.5 }}>
                      "{stage.counterfactual}"
                    </p>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 6 }}>
                      Note: Explanatory decision-support reasoning; not a guaranteed causal statement.
                    </div>
                  </div>

                  {/* AI Mentor Talking Point */}
                  <div style={{
                    background: 'rgba(16, 185, 129, 0.06)',
                    border: '1px solid rgba(16, 185, 129, 0.2)',
                    borderRadius: 10,
                    padding: '12px 16px'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                      <MessageSquare size={14} color="var(--color-normal)" />
                      <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--color-normal)', textTransform: 'uppercase', letterSpacing: 0.5 }}>
                        Suggested Mentor Conversation Starter
                      </span>
                    </div>
                    <blockquote style={{ margin: 0, fontSize: 13, color: 'var(--text-primary)', fontStyle: 'italic', borderLeft: '3px solid var(--color-normal)', paddingLeft: 10 }}>
                      "{stage.talking_point}"
                    </blockquote>
                  </div>
                </div>
              )}

              {/* Stage 4 Highlight: Intervention Details */}
              {stage.stage === 4 && stage.intervention && (
                <div style={{
                  background: 'rgba(16, 185, 129, 0.05)',
                  border: '1px solid rgba(16, 185, 129, 0.2)',
                  borderRadius: 12,
                  padding: 16
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                    <CheckCircle size={16} color="var(--color-normal)" />
                    <span style={{ fontWeight: 700, fontSize: 13, color: '#f8fafc' }}>
                      Faculty Intervention Record
                    </span>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, marginBottom: 12, fontSize: 12 }}>
                    <div>
                      <span style={{ color: 'var(--text-muted)' }}>Mentor:</span> <strong>{stage.intervention.mentor}</strong>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-muted)' }}>Method:</span> <strong>{stage.intervention.contact_method}</strong>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-muted)' }}>Outcome:</span> <strong style={{ color: 'var(--color-normal)' }}>{stage.intervention.outcome}</strong>
                    </div>
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', background: 'var(--bg-elevated)', padding: 12, borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
                    <strong>Meeting Notes:</strong> {stage.intervention.notes}
                  </div>
                </div>
              )}

              {/* Stage 6 Highlight: Closing Takeaway */}
              {stage.stage === 6 && (
                <div style={{
                  background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(16, 185, 129, 0.08))',
                  border: '1px solid rgba(99, 102, 241, 0.3)',
                  borderRadius: 12,
                  padding: 18,
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--brand-glow)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 }}>
                    Core Hackathon Takeaway
                  </div>
                  <div style={{ fontSize: 16, fontWeight: 800, color: '#fff', fontStyle: 'italic', lineHeight: 1.5 }}>
                    "{stage.final_message || 'Tripwire doesn\'t replace the mentor. It helps the mentor notice the right student at the right time.'}"
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Modal Controls Footer */}
        <div style={{
          padding: '16px 24px',
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          background: 'rgba(255, 255, 255, 0.02)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          {/* Playback Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <button
              id="demo-play-btn"
              className="btn btn-primary btn-sm"
              onClick={() => setIsPlaying(!isPlaying)}
            >
              {isPlaying ? <><Pause size={14} /> Pause</> : <><Play size={14} /> Play Demo</>}
            </button>

            <button
              id="demo-restart-btn"
              className="btn btn-ghost btn-sm"
              onClick={handleRestart}
              title="Restart from Stage 1"
            >
              <RotateCcw size={14} /> Restart
            </button>

            {/* Speed toggle */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginLeft: 8 }}>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Speed:</span>
              {[1, 1.5, 2].map(s => (
                <button
                  key={s}
                  onClick={() => setSpeed(s)}
                  style={{
                    padding: '3px 8px',
                    borderRadius: 4,
                    fontSize: 10,
                    fontWeight: 700,
                    border: 'none',
                    cursor: 'pointer',
                    background: speed === s ? 'var(--brand-primary)' : 'rgba(255,255,255,0.06)',
                    color: speed === s ? '#fff' : 'var(--text-muted)'
                  }}
                >
                  {s}x
                </button>
              ))}
            </div>
          </div>

          {/* Stepper buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <button
              id="demo-prev-btn"
              className="btn btn-ghost btn-sm"
              onClick={handlePrev}
              disabled={currentIdx === 0}
            >
              <ChevronLeft size={16} /> Previous
            </button>

            <span style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              {currentIdx + 1} / {stages.length}
            </span>

            <button
              id="demo-next-btn"
              className="btn btn-primary btn-sm"
              onClick={handleNext}
              disabled={currentIdx === stages.length - 1}
            >
              Next <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

const FALLBACK_STAGES = [
  {
    stage: 1,
    title: "Individual Baseline Established",
    phase: "Baseline Normal",
    timeframe: "August 1 – August 31",
    dvi: 31,
    status: "normal",
    badge: "🟢 Normal Baseline",
    narrative: "Rahul starts with healthy, consistent behavior. Tripwire establishes his personal baseline: 91% attendance, 4.5h assignment delay, 10 LMS interactions/wk. Not compared to class average, but to himself."
  },
  {
    stage: 2,
    title: "Early Behavioral Drift",
    phase: "Monitoring Zone",
    timeframe: "September 1 – September 8",
    dvi: 52,
    status: "monitoring",
    badge: "🟡 Behavioral Drift",
    narrative: "Early September: Rahul misses two morning classes and assignment delay increases to 18h. DVI rises to 52 into MONITORING. Traditional systems notice nothing."
  },
  {
    stage: 3,
    title: "Tripwire Alert Triggered",
    phase: "Active Warning",
    timeframe: "September 9 – September 15",
    dvi: 78,
    status: "tripwire",
    badge: "🔴 TRIPWIRE DETECTED",
    narrative: "Decline accelerates: Assignment SEP03 42h late, LMS collapses to 2/wk. DVI hits 78. A confidential alert triggers to Dr. Pradeep. Rahul sees no alarming risk label."
  },
  {
    stage: 4,
    title: "Faculty Mentor Intervention",
    phase: "Faculty Mentorship",
    timeframe: "September 16",
    dvi: 78,
    status: "tripwire",
    badge: "🤝 Mentor Intervention",
    narrative: "Dr. Pradeep conducts a supportive check-in. Rahul explains lab workload and commute issues. Peer tutoring is arranged and recorded."
  },
  {
    stage: 5,
    title: "Behavioral Recovery Detected",
    phase: "Early Recovery",
    timeframe: "September 17 – September 20",
    dvi: 63,
    status: "recovering",
    badge: "🟣 Behavioral Recovery",
    narrative: "Rahul attends classes and completes coursework. DVI drops to 63. Status updates to RECOVERING. System confirms closed-loop recovery."
  },
  {
    stage: 6,
    title: "Fully Recovered to Normal Baseline",
    phase: "Full Resolution",
    timeframe: "September 21 – September 25",
    dvi: 49,
    status: "normal",
    badge: "🟢 Good Standing Restored",
    final_message: "Tripwire doesn't replace the mentor. It helps the mentor notice the right student at the right time.",
    narrative: "Rahul's DVI returns to 49. Academic disengagement was caught and reversed before exams. Mission accomplished."
  }
]
