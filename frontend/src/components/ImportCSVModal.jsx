import React, { useState } from 'react'
import { X, Upload, FileText, Download, CheckCircle2, AlertCircle } from 'lucide-react'
import { studentsAPI } from '../api/client'
import toast from 'react-hot-toast'

export default function ImportCSVModal({ isOpen, onClose, onImportSuccess }) {
  if (!isOpen) return null

  const [csvText, setCsvText] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (event) => {
      const content = event.target?.result
      if (typeof content === 'string') {
        setCsvText(content)
      }
    }
    reader.readAsText(file)
  }

  const handleImport = async () => {
    if (!csvText.trim()) {
      toast.error('Please upload a CSV file or paste CSV content')
      return
    }

    setSubmitting(true)
    try {
      const res = await studentsAPI.importCSV(csvText.trim())
      toast.success(res.data.message || `Successfully imported ${res.data.imported_count} students!`)
      if (onImportSuccess) onImportSuccess()
      onClose()
      setCsvText('')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to import CSV')
    } finally {
      setSubmitting(false)
    }
  }

  // Parse preview rows
  const lines = csvText.trim().split('\n').filter(l => l.trim().length > 0)
  const previewRows = lines.slice(1, 6).map(line => line.split(',').map(s => s.trim()))

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
        maxWidth: 620,
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
              <Upload size={18} color="var(--brand-glow)" />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 15, color: '#f8fafc' }}>
                Bulk Import Students (CSV)
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Import your classroom roster directly from an Excel or Google Sheets export
              </div>
            </div>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 14 }}>
          {/* Instructions + Template link */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 10,
            padding: '12px 16px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 12
          }}>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
              Required CSV headers: <code style={{ color: 'var(--brand-glow)' }}>name,roll_no,section</code> (optional: <code style={{ color: 'var(--brand-glow)' }}>student_id</code>)
            </div>
            <a
              href={studentsAPI.getTemplateUrl()}
              download="tripwire_roster_template.csv"
              className="btn btn-ghost btn-sm"
              style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 11, flexShrink: 0 }}
            >
              <Download size={13} /> Sample CSV
            </a>
          </div>

          {/* File input dropzone */}
          <div style={{
            border: '2px dashed var(--border-subtle)',
            borderRadius: 10,
            padding: '20px',
            textAlign: 'center',
            background: 'rgba(0, 0, 0, 0.2)',
            cursor: 'pointer'
          }}>
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
              id="csv-file-input"
            />
            <label htmlFor="csv-file-input" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
              <FileText size={28} color="var(--brand-glow)" />
              <div style={{ fontSize: 13, fontWeight: 600, color: '#f8fafc' }}>
                Click to browse CSV file or drag and drop here
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Supports standard comma-separated text files (.csv)
              </div>
            </label>
          </div>

          {/* Or Paste Text Area */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
              <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>
                Or Paste CSV Text Directly:
              </label>
              {lines.length > 1 && (
                <span style={{ fontSize: 11, color: 'var(--color-normal)' }}>
                  ✓ {lines.length - 1} student rows detected
                </span>
              )}
            </div>
            <textarea
              className="input"
              rows={4}
              placeholder="name,roll_no,section&#10;Aravind Krishnan,CSE24101,CSE S2&#10;Diya Menon,CSE24102,CSE S2"
              value={csvText}
              onChange={(e) => setCsvText(e.target.value)}
              style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}
            />
          </div>

          {/* Live Preview of first 5 rows */}
          {previewRows.length > 0 && (
            <div style={{
              background: 'rgba(0, 0, 0, 0.3)',
              borderRadius: 8,
              border: '1px solid var(--border-subtle)',
              padding: 10,
              fontSize: 11
            }}>
              <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: 6 }}>
                Preview (First {previewRows.length} students):
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {previewRows.map((r, i) => (
                  <div key={i} style={{ display: 'flex', gap: 12, color: 'var(--text-muted)' }}>
                    <span style={{ color: '#fff', fontWeight: 600 }}>{r[0] || 'Unknown'}</span>
                    <span>{r[1] || 'No Roll'}</span>
                    <span>{r[2] || 'No Section'}</span>
                  </div>
                ))}
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
              Cancel
            </button>
            <button
              id="submit-import-csv-btn"
              type="button"
              className="btn btn-primary btn-sm"
              disabled={submitting || lines.length <= 1}
              onClick={handleImport}
              style={{ minWidth: 140 }}
            >
              {submitting ? 'Importing...' : `Import ${Math.max(0, lines.length - 1)} Students`}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
