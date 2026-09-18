import axios from 'axios'

export const BASE_URL = (
  import.meta.env.VITE_API_URL ||
  (typeof window !== 'undefined' && window.location.hostname
    ? `http://${window.location.hostname}:8000`
    : 'http://localhost:8000')
).replace(/\/+$/, '')

const api = axios.create({ baseURL: BASE_URL })

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('tripwire_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Redirect to login on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('tripwire_token')
      localStorage.removeItem('tripwire_mentor')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const authAPI = {
  login: (username, password) => {
    const form = new URLSearchParams()
    form.append('username', username)
    form.append('password', password)
    return api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
  },
  me: () => api.get('/auth/me')
}

export const dashboardAPI = {
  summary: () => api.get('/dashboard/summary'),
  cohortHeatmap: () => api.get('/dashboard/cohort-heatmap')
}

export const studentsAPI = {
  list: (params = {}) => api.get('/students', { params }),
  profile: (id) => api.get(`/students/${id}`),
  create: (data) => api.post('/students', data),
  delete: (id) => api.delete(`/students/${id}`),
  importCSV: (csv_text) => api.post('/students/import-csv', { csv_text }),
  getTemplateUrl: () => `${BASE_URL}/students/template-csv`,
  logAttendance: (id, data) => api.post(`/students/${id}/attendance`, data),
  logAssignment: (id, data) => api.post(`/students/${id}/assignments`, data),
  logLMS: (id, data) => api.post(`/students/${id}/lms`, data),
  batchAttendance: (data) => api.post('/students/batch-attendance', data),
  resetCohort: (mode = 'empty') => api.post('/students/reset-cohort', { mode }),
  dviHistory: (id, days = 28) => api.get(`/students/${id}/dvi-history`, { params: { days } }),
  timeline: (id) => api.get(`/students/${id}/timeline`),
  excuse: (id, data) => api.post(`/students/${id}/excuse`, data),
  submitPulse: (id, data) => api.post(`/students/${id}/pulse`, data),
  getPulses: (id) => api.get(`/students/${id}/pulse`),
  simulateDrift: (id) => api.post(`/students/${id}/simulate-drift`),
  simulateRecovery: (id) => api.post(`/students/${id}/simulate-recovery`),
  simulateReset: (id) => api.post(`/students/${id}/simulate-reset`)
}

export const alertsAPI = {
  list: () => api.get('/alerts'),
  get: (id) => api.get(`/alerts/${id}`),
  unreadCount: () => api.get('/alerts/unread-count'),
  markAllRead: () => api.post('/alerts/mark-all-read'),
  markRead: (id) => api.post(`/alerts/${id}/mark-read`),
  aiExplain: (id) => api.post(`/alerts/${id}/ai-explain`),
  excuse: (id) => api.post(`/alerts/${id}/excuse`),
  submitFeedback: (id, data) => api.post(`/alerts/${id}/feedback`, data),
  getFeedback: (id) => api.get(`/alerts/${id}/feedback`)
}

export const interventionsAPI = {
  create: (data) => api.post('/interventions', data),
  get: (alertId) => api.get(`/interventions/${alertId}`),
  studentHistory: (studentId) => api.get(`/interventions/student/${studentId}`)
}

export const analyticsAPI = {
  weightValidation: () => api.get('/analytics/weight-validation'),
  modelValidation: () => api.get('/analytics/model-validation'),
  trustScore: () => api.get('/analytics/trust-score')
}

export const demoAPI = {
  stages: () => api.get('/demo/stages')
}



export default api
