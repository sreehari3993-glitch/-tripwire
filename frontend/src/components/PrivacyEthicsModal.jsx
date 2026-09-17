import React from 'react'
import { X, ShieldCheck, EyeOff, Lock, UserCheck, HeartHandshake, Database, Sliders, FileText } from 'lucide-react'

export default function PrivacyEthicsModal({ isOpen, onClose }) {
  if (!isOpen) return null

  const ETHICAL_PRINCIPLES = [
    {
      icon: EyeOff,
      title: "Zero Invasive Surveillance",
      desc: "Tripwire strictly prohibits webcam monitoring, eye-tracking, keystroke logging, device screen recording, or location tracking. Only non-invasive, coarse-grained administrative logs (attendance, assignment timestamps, LMS login counts) are processed."
    },
    {
      icon: Lock,
      title: "Confidential, Private Alerts",
      desc: "Risk indicators and DVI scores are strictly confidential to authorized faculty mentors. Students are never shown anxiety-inducing labels such as 'HIGH RISK' or 'DISENGAGED', preventing stereotype threat and learned helplessness."
    },
    {
      icon: HeartHandshake,
      title: "Strictly Non-Diagnostic",
      desc: "Tripwire does NOT diagnose mental health, depression, neurodivergence, or cognitive ability. It merely flags observable academic temporal drift and assists the mentor in starting an empathetic, supportive conversation."
    },
    {
      icon: UserCheck,
      title: "Human-in-the-Loop Decision Support",
      desc: "AI never automatically penalizes, sanctions, or disciplines a student. The workflow is always: Telemetry → Decision Support → Faculty Mentor → Empathetic Outreach → Human Intervention Outcome → Recovery."
    },
    {
      icon: Sliders,
      title: "Human Override & False-Positive Safeguards",
      desc: "Faculty mentors can mark any data point or alert as 'EXCUSED' (e.g. for approved medical leave, sports events, family bereavement), instantly recalibrating or overriding the DVI calculation."
    },
    {
      icon: Database,
      title: "DPDP Act 2023 Compliance & Data Minimization",
      desc: "Designed in strict alignment with India's Digital Personal Data Protection Act 2023. Adheres to strict purpose limitation, data minimization, role-based access control (RBAC), and uses 100% synthetic data for prototype demonstrations."
    }
  ]

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
        border: '1px solid rgba(16, 185, 129, 0.25)',
        boxShadow: '0 24px 60px rgba(0, 0, 0, 0.8), 0 0 30px rgba(16, 185, 129, 0.1)',
        borderRadius: 20,
        width: '100%',
        maxWidth: 860,
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Modal Header */}
        <div style={{
          padding: '18px 24px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'rgba(255, 255, 255, 0.02)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 10,
              background: 'linear-gradient(135deg, #10b981, #059669)',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <ShieldCheck size={18} color="#fff" />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: 16, color: '#f8fafc' }}>
                Privacy, Ethics & Student Safeguards
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Responsible AI framework and student-first governance commitments
              </div>
            </div>
          </div>

          <button
            id="privacy-modal-close"
            className="btn btn-ghost btn-sm"
            onClick={onClose}
            style={{ borderRadius: 8, padding: '6px 10px' }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: 24, overflowY: 'auto', flex: 1 }}>
          {/* Manifesto Callout Banner */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(6, 182, 212, 0.08))',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: 12,
            padding: '16px 20px',
            marginBottom: 24,
            textAlign: 'center'
          }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--color-normal)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 4 }}>
              Core Institutional Guarantee
            </div>
            <div style={{ fontSize: 16, fontWeight: 800, color: '#fff', fontStyle: 'italic', lineHeight: 1.5 }}>
              "Tripwire is a decision-support system, not a student-labeling or diagnostic system."
            </div>
          </div>

          {/* 6 Principles Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16 }}>
            {ETHICAL_PRINCIPLES.map(({ icon: Icon, title, desc }) => (
              <div
                key={title}
                style={{
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 12,
                  padding: 16,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 8
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{
                    width: 28, height: 28, borderRadius: 8,
                    background: 'rgba(16, 185, 129, 0.15)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center'
                  }}>
                    <Icon size={15} color="var(--color-normal)" />
                  </div>
                  <div style={{ fontWeight: 700, fontSize: 13, color: '#f8fafc' }}>
                    {title}
                  </div>
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {desc}
                </div>
              </div>
            ))}
          </div>

          {/* Viva Defense Note */}
          <div style={{
            marginTop: 20,
            background: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: 10,
            padding: '12px 16px',
            fontSize: 11,
            color: 'var(--text-muted)',
            lineHeight: 1.6
          }}>
            <strong style={{ color: 'var(--text-primary)' }}>Viva Defense Checklist:</strong> If asked whether Tripwire surveils students or predicts mental health, state clearly: <em>"No. Tripwire only analyzes non-invasive academic time-stamps relative to individual baselines to give human faculty timely notice for supportive advising."</em>
          </div>
        </div>

        {/* Modal Footer */}
        <div style={{
          padding: '14px 24px',
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          background: 'rgba(255, 255, 255, 0.02)',
          display: 'flex',
          justifyContent: 'flex-end'
        }}>
          <button className="btn btn-ghost btn-sm" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
