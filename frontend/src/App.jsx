import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './context/AuthContext'
import { ModalProvider } from './context/ModalContext'
import Sidebar from './components/Sidebar'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import StudentList from './pages/StudentList'
import StudentProfile from './pages/StudentProfile'
import Alerts from './pages/Alerts'
import AlertDetail from './pages/AlertDetail'

function ProtectedLayout({ children }) {
  const { mentor } = useAuth()
  if (!mentor) return <Navigate to="/login" replace />
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">{children}</main>
    </div>
  )
}

function AppRoutes() {
  const { mentor } = useAuth()
  return (
    <Routes>
      <Route
        path="/login"
        element={mentor ? <Navigate to="/dashboard" replace /> : <Login />}
      />
      <Route path="/dashboard" element={
        <ProtectedLayout><Dashboard /></ProtectedLayout>
      } />
      <Route path="/students" element={
        <ProtectedLayout><StudentList /></ProtectedLayout>
      } />
      <Route path="/students/:id" element={
        <ProtectedLayout><StudentProfile /></ProtectedLayout>
      } />
      <Route path="/alerts" element={
        <ProtectedLayout><Alerts /></ProtectedLayout>
      } />
      <Route path="/alerts/:id" element={
        <ProtectedLayout><AlertDetail /></ProtectedLayout>
      } />
      <Route path="*" element={<Navigate to={mentor ? '/dashboard' : '/login'} replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <ModalProvider>
        <BrowserRouter>
          <AppRoutes />
          <Toaster
            position="top-right"
            toastOptions={{
              style: {
                background: '#1e293b',
                color: '#f1f5f9',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '10px',
                fontSize: '13px',
              },
              success: { iconTheme: { primary: '#10b981', secondary: '#1e293b' } },
              error: { iconTheme: { primary: '#ef4444', secondary: '#1e293b' } },
            }}
          />
        </BrowserRouter>
      </ModalProvider>
    </AuthProvider>
  )
}

