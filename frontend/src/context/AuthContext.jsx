import React, { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [mentor, setMentor] = useState(() => {
    const stored = localStorage.getItem('tripwire_mentor')
    return stored ? JSON.parse(stored) : null
  })
  const [loading, setLoading] = useState(false)

  const login = async (username, password) => {
    setLoading(true)
    try {
      const res = await authAPI.login(username, password)
      const { access_token, mentor: mentorData } = res.data
      localStorage.setItem('tripwire_token', access_token)
      localStorage.setItem('tripwire_mentor', JSON.stringify(mentorData))
      setMentor(mentorData)
      return { success: true }
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || 'Login failed' }
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('tripwire_token')
    localStorage.removeItem('tripwire_mentor')
    setMentor(null)
  }

  return (
    <AuthContext.Provider value={{ mentor, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
