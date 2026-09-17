import axios from 'axios'

export const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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
  summary: () => api.get('/dashboard/summary')
}

export const studentsAPI = {
  list: (params = {}) => api.get('/students', { params }),
  profile: (id) => api.get(`/students/${id}`),
  dviHistory: (id, days = 28) => api.get(`/students/${id}/dvi-history`, { params: { days } }),
  timeline: (id) => api.get(`/students/${id}/timeline`),
  excuse: (id, data) => api.post(`/students/${id}/excuse`, data),
  submitPulse: (id, data) => api.post(`/students/${id}/pulse`, data),
  getPulses: (id) => api.get(`/students/${id}/pulse`)
}

export const alertsAPI = {
  list: () => api.get('/alerts'),
  get: (id) => api.get(`/alerts/${id}`),
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
