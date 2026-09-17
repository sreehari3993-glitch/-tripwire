import React, { useState, useEffect } from 'react'
import { analyticsAPI } from '../api/client'
import { X, CheckCircle2, AlertCircle, BarChart3, ShieldCheck, Scale, Award, Info } from 'lucide-react'

export default function ModelValidationModal({ isOpen, onClose }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isOpen) {
      setLoading(true)
      analyticsAPI.weightValidation()
        .then(res => setData(res.data))
        .catch(err => console.error('Failed to load weight validation:', err))
        .finally(() => setLoading(false))
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div className="modal-overlay" style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      background: 'rgba(5, 10, 24, 0.85)',
      backdropFilter: 'blur(10px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: '24px'
    }} onClick={onClose}>
      <div
        className="card"
        style={{
          width: '100%', maxWidth: '980px', maxHeight: '90vh',
          background: 'var(--bg-elevated)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '16px',
          display: 'flex', flexDirection: 'column',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
          overflow: 'hidden'
        }}
        onClick={e => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          background: 'rgba(255,255,255,0.02)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 40, height: 40, borderRadius: 10,
              background: 'rgba(99, 102, 241, 0.15)',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <Scale size={20} color="var(--color-brand)" />
            </div>
            <div>
              <h2 style={{ fontSize: 18, fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
                DVI Model Validation & Sensitivity Analysis
              </h2>
              <p style={{ fontSize: 12, margin: '2px 0 0', color: 'var(--text-muted)' }}>
                Defensible empirical derivation of DVI weights vs. alternative candidate configurations
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="btn btn-ghost"
            style={{ padding: 8, borderRadius: 8 }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: '24px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: 20 }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
              Loading empirical separation analysis...
            </div>
          ) : data ? (
            <>
              {/* Executive Recommendation Callout */}
              <div style={{
                background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(6, 182, 212, 0.08))',
                border: '1px solid rgba(99, 102, 241, 0.3)',
                borderRadius: 12,
                padding: '16px 20px',
                display: 'flex', gap: 16, alignItems: 'flex-start'
              }}>
                <Award size={24} color="var(--color-brand)" style={{ flexShrink: 0, marginTop: 2 }} />
                <div>
                  <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--color-brand)', marginBottom: 4 }}>
                    Empirical Defense: Optimal Separation of Disengaged Cohorts
                  </div>
                  <div style={{ fontSize: 12, lineHeight: 1.6, color: 'var(--text-secondary)' }}>
                    {data.recommendation}
                  </div>
                </div>
              </div>

              {/* Sensitivity Comparison Table */}
              <div>
                <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <BarChart3 size={15} color="var(--color-brand)" /> Weight Candidate Comparison (Threshold DVI ≥ 70)
                </div>
                <div style={{ overflowX: 'auto', border: '1px solid var(--border-subtle)', borderRadius: 10 }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12, textAlign: 'left' }}>
                    <thead>
                      <tr style={{ background: 'rgba(255,255,255,0.03)', borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
                        <th style={{ padding: '10px 14px' }}>Candidate Configuration</th>
                        <th style={{ padding: '10px 14px' }}>Att / Sub / LMS</th>
                        <th style={{ padding: '10px 14px', textAlign: 'center' }}>Rapid Decline</th>
                        <th style={{ padding: '10px 14px', textAlign: 'center' }}>Normal</th>
                        <th style={{ padding: '10px 14px', textAlign: 'center' }}>Excused</th>
                        <th style={{ padding: '10px 14px', textAlign: 'center' }}>Separation Gap</th>
                        <th style={{ padding: '10px 14px', textAlign: 'center' }}>F1 Score</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.candidates.map((c, idx) => {
                        const isTop = c.id === data.best_candidate
                        return (
                          <tr
                            key={c.id}
                            style={{
                              borderBottom: '1px solid var(--border-subtle)',
                              background: isTop ? 'rgba(99, 102, 241, 0.07)' : 'transparent'
                            }}
                          >
                            <td style={{ padding: '12px 14px', fontWeight: isTop ? 700 : 500, color: isTop ? 'var(--color-brand)' : 'var(--text-primary)' }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                {isTop && <CheckCircle2 size={14} color="var(--color-brand)" />}
                                {c.name}
                              </div>
                              <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>{c.rationale}</div>
                            </td>
                            <td style={{ padding: '12px 14px', fontFamily: 'var(--font-mono)' }}>
                              {Math.round(c.weights.attendance * 100)} / {Math.round(c.weights.submission * 100)} / {Math.round(c.weights.engagement * 100)}
                            </td>
                            <td style={{ padding: '12px 14px', textAlign: 'center', fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--color-tripwire)' }}>
                              {c.mean_rapid_decline}
                            </td>
                            <td style={{ padding: '12px 14px', textAlign: 'center', fontFamily: 'var(--font-mono)', color: 'var(--color-normal)' }}>
                              {c.mean_normal}
                            </td>
                            <td style={{ padding: '12px 14px', textAlign: 'center', fontFamily: 'var(--font-mono)', color: 'var(--color-normal)' }}>
                              {c.mean_excused}
                            </td>
                            <td style={{ padding: '12px 14px', textAlign: 'center' }}>
                              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                                <div style={{
                                  width: 80, height: 6, background: 'rgba(255,255,255,0.1)', borderRadius: 3, overflow: 'hidden'
                                }}>
                                  <div style={{
                                    width: `${(c.separation_gap / 70) * 100}%`,
                                    height: '100%',
                                    background: isTop ? 'var(--color-brand)' : 'rgba(255,255,255,0.4)',
                                    borderRadius: 3
                                  }} />
                                </div>
                                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: isTop ? 'var(--color-brand)' : 'var(--text-primary)' }}>
                                  +{c.separation_gap}
                                </span>
                              </div>
                            </td>
                            <td style={{ padding: '12px 14px', textAlign: 'center', fontFamily: 'var(--font-mono)', fontWeight: 700, color: c.f1_score >= 80 ? 'var(--color-normal)' : 'var(--color-monitor)' }}>
                              {c.f1_score}%
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Viva Defense Guide */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
                <div style={{ background: 'var(--bg-card)', padding: '14px 16px', borderRadius: 10, border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Info size={14} color="#f59e0b" /> Why not 33/33/33 Equal Weights?
                  </div>
                  <div style={{ fontSize: 11, lineHeight: 1.5, color: 'var(--text-muted)' }}>
                    Equal weighting dilutes the high-diagnostic early signal of assignment latency (+18h late submission), reducing the separation gap from 65.1 down to 62.0 pts.
                  </div>
                </div>

                <div style={{ background: 'var(--bg-card)', padding: '14px 16px', borderRadius: 10, border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Info size={14} color="#6366f1" /> Why not Attendance-Heavy (50/30/20)?
                  </div>
                  <div style={{ fontSize: 11, lineHeight: 1.5, color: 'var(--text-muted)' }}>
                    Heavy attendance weighting misses <em>silent</em> disengagement where students attend physical lectures while completely abandoning coursework and portal study.
                  </div>
                </div>

                <div style={{ background: 'var(--bg-card)', padding: '14px 16px', borderRadius: 10, border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <ShieldCheck size={14} color="#10b981" /> Excused Leave Protection
                  </div>
                  <div style={{ fontSize: 11, lineHeight: 1.5, color: 'var(--text-muted)' }}>
                    Approved medical leaves score an average DVI of only 16.8 (well below 50), confirming human overrides prevent false alarms on legitimate absences.
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div style={{ color: 'var(--color-tripwire)' }}>Failed to load validation report.</div>
          )}
        </div>

        {/* Modal Footer */}
        <div style={{
          padding: '14px 24px',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          background: 'rgba(255,255,255,0.02)'
        }}>
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            Artifact generated by <code>backend/scripts/validate_weights.py</code>
          </span>
          <button onClick={onClose} className="btn btn-secondary" style={{ padding: '8px 18px' }}>
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
