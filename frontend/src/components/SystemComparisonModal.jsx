import React from 'react'
import { X, Layers, CheckCircle2, AlertTriangle, Shield, Check } from 'lucide-react'

export default function SystemComparisonModal({ isOpen, onClose }) {
  if (!isOpen) return null

  const systems = [
    {
      system: "Traditional Academic Audits",
      namedExample: "University Academic Standing Notices / SAP Audits (Higher Education Act)",
      data: "Term GPA, midterm/final exam scores, cumulative absences",
      prediction: "Static administrative cutoffs (e.g. GPA < 2.0 or attendance < 75%)",
      intervention: "Formal probation notices, late administrative advisories",
      privacy: "Low telemetry collection; but carries post-hoc academic probation stigma",
      limitation: "Severely lagging — alerts trigger only after coursework failure has already occurred",
      isTripwire: false
    },
    {
      system: "LMS Portal Analytics",
      namedExample: "Canvas Course Analytics / Moodle Engagement Analytics (Moodle HQ)",
      data: "Gross pageviews, content download counts, discussion post volume",
      prediction: "Cohort-relative participation volume (e.g., student vs. class average)",
      intervention: "Automated student portal reminder or instructor summary chart",
      privacy: "Moderate; logs platform clickstreams without qualitative context",
      limitation: "Measures compliance rather than genuine cognitive engagement; high false alarm rate",
      isTripwire: false
    },
    {
      system: "Predictive Analytics Platforms",
      namedExample: "Civitas Learning Illume / EAB Navigate Student Success Platform",
      data: "Demographics, historical course completion, prior GPA, portal clicks",
      prediction: "Proprietary predictive classifiers (Random Forest, Logistic Regression, XGBoost)",
      intervention: "Central advisor ticketing, automated retention campaigns",
      privacy: "Elevated risk of demographic stereotyping and historical cohort bias",
      limitation: "Opaque 'black-box' reasoning; low faculty trust; cannot provide actionable 'why'",
      isTripwire: false
    },
    {
      system: "Traffic-Light Nudge Systems",
      namedExample: "Purdue Course Signals (Arnold & Pistilli, ACM LAK 2012)",
      data: "Prior GPA, LMS login volume, standardized test percentiles, quiz scores",
      prediction: "Regression model mapping student risk into Red / Yellow / Green signals",
      intervention: "Direct automated email to student with traffic light visual badge",
      privacy: "Public student risk labels can induce learned helplessness and test anxiety",
      limitation: "Cohort-normed; lacks individual baseline trajectory; assumes student acts without mentor",
      isTripwire: false
    },
    {
      system: "Deep Learning Sequence Models",
      namedExample: "Sequential Dropout Recurrent Networks (e.g. Kuzilek et al. 2017, OULAD)",
      data: "High-resolution time-series clickstreams, assessment timing, interaction sequences",
      prediction: "Deep Sequential models (LSTM, GRU, Transformers)",
      intervention: "Central analytics alert or automated institutional flag",
      privacy: "High telemetry collection; dense longitudinal tracking across student life",
      limitation: "Prohibitive training complexity; lacks local faculty interpretability; difficult to audit",
      isTripwire: false
    },
    {
      system: "TRIPWIRE (Our Work)",
      namedExample: "TRIPWIRE (Idiographic Behavioral Drift & Mentorship Decision-Support)",
      data: "Non-invasive logs: Attendance drift, Submission delay drift, LMS login rhythm, voluntary pulse",
      prediction: "Transparent Disengagement Velocity Index (DVI) + EWMA Temporal Smoothing (α=0.3)",
      intervention: "Private faculty mentor decision support with structured outcomes, counterfactuals & recovery tracking",
      privacy: "Privacy-first (DPDP Act 2023 compliant); zero surveillance (no camera/keystroke tracking); private to mentors",
      limitation: "Requires baseline calibration (addressed via Bayesian cohort blending for cold-start students)",
      isTripwire: true
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
        border: '1px solid rgba(99, 102, 241, 0.25)',
        boxShadow: '0 24px 60px rgba(0, 0, 0, 0.8)',
        borderRadius: 20,
        width: '100%',
        maxWidth: 1100,
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
              background: 'linear-gradient(135deg, #06b6d4, #6366f1)',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <Layers size={16} color="#fff" />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: 16, color: '#f8fafc' }}>
                Competitive & Architectural System Comparison
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                How Tripwire differentiates from legacy, commercial, and research early-warning systems
              </div>
            </div>
          </div>

          <button
            id="comparison-modal-close"
            className="btn btn-ghost btn-sm"
            onClick={onClose}
            style={{ borderRadius: 8, padding: '6px 10px' }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Modal Content */}
        <div style={{ padding: 24, overflowY: 'auto', flex: 1 }}>
          {/* Key differentiation statement banner */}
          <div style={{
            background: 'rgba(99, 102, 241, 0.08)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            borderRadius: 12,
            padding: '14px 18px',
            marginBottom: 20,
            display: 'flex',
            alignItems: 'center',
            gap: 12
          }}>
            <Shield size={20} color="var(--brand-glow)" style={{ flexShrink: 0 }} />
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              <strong style={{ color: '#fff' }}>Tripwire does not claim to be completely unique.</strong> Rather, its core innovation is the synergistic combination of:
              <span style={{ color: 'var(--brand-glow)', fontWeight: 600 }}>
                {' '}Individual Baselines + Behavioral Velocity + Transparent DVI + "What Changed?" Counterfactuals + Private Mentor Alerts + Intervention Tracking + Recovery Detection.
              </span>
            </div>
          </div>

          {/* Comparison Table */}
          <div style={{ overflowX: 'auto', borderRadius: 12, border: '1px solid var(--border-subtle)' }}>
            <table className="data-table" style={{ width: '100%', fontSize: 12, margin: 0 }}>
              <thead>
                <tr style={{ background: 'rgba(255,255,255,0.03)' }}>
                  <th style={{ width: 180 }}>Approach</th>
                  <th>Data Telemetry</th>
                  <th>Prediction Paradigm</th>
                  <th>Intervention Model</th>
                  <th>Privacy & Stigma</th>
                  <th>Primary Limitation</th>
                </tr>
              </thead>
              <tbody>
                {systems.map((row, idx) => (
                  <tr
                    key={row.system}
                    style={{
                      background: row.isTripwire ? 'rgba(99, 102, 241, 0.08)' : 'transparent',
                      borderLeft: row.isTripwire ? '3px solid #6366f1' : 'none'
                    }}
                  >
                    <td>
                      <div style={{ fontWeight: 700, color: row.isTripwire ? '#fff' : 'var(--text-primary)' }}>
                        {row.system}
                      </div>
                      {row.namedExample && (
                        <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2, fontStyle: 'italic' }}>
                          {row.namedExample}
                        </div>
                      )}
                      {row.isTripwire && (
                        <span style={{ fontSize: 9, background: '#6366f1', color: '#fff', padding: '1px 6px', borderRadius: 4, textTransform: 'uppercase', fontWeight: 800, marginTop: 4, display: 'inline-block' }}>
                          Proposed System
                        </span>
                      )}
                    </td>
                    <td style={{ color: 'var(--text-secondary)' }}>{row.data}</td>
                    <td style={{ color: 'var(--text-secondary)' }}>{row.prediction}</td>
                    <td style={{ color: 'var(--text-secondary)' }}>{row.intervention}</td>
                    <td style={{ color: 'var(--text-secondary)' }}>{row.privacy}</td>
                    <td style={{ color: row.isTripwire ? 'var(--text-muted)' : '#f87171' }}>{row.limitation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* 7 Differentiators Highlights */}
          <div style={{ marginTop: 24 }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 12 }}>
              The 7 Core Tripwire Pillars
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10 }}>
              {[
                { title: "Individual Baseline", desc: "Compares Rahul to his own historical norm, not class average" },
                { title: "Behavioral Velocity", desc: "Tracks rate of drift (d/dt) across rolling windows" },
                { title: "Transparent DVI", desc: "40% Att + 35% Sub + 25% Eng = Exact additive score" },
                { title: "What Changed?", desc: "Actionable itemization with counterfactual 'what-if' analysis" },
                { title: "Private Mentor Alert", desc: "Zero student stigma; decision support for authorized educators" },
                { title: "Closed-Loop Intervention", desc: "Tracks mentor contact method, notes, and outcome" },
                { title: "Recovery Tracking", desc: "Detects positive velocity after intervention (78 → 63 → 49)" },
                { title: "Human Override", desc: "Allows marking data as EXCUSED for medical/approved leaves" },
              ].map(p => (
                <div key={p.title} style={{
                  background: 'var(--bg-elevated)',
                  borderRadius: 8,
                  padding: '10px 12px',
                  border: '1px solid var(--border-subtle)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                    <Check size={12} color="#10b981" />
                    <span style={{ fontWeight: 700, fontSize: 11, color: '#f8fafc' }}>{p.title}</span>
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.4 }}>{p.desc}</div>
                </div>
              ))}
            </div>
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
