import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Layout from './components/Layout/Layout'
import Login from './components/Login/Login'
import Dashboard from './components/Dashboard/Dashboard'
import UserManagement from './components/UserManagement/UserManagement'
import Monitoring from './components/Monitoring/Monitoring'
import Settings from './components/Settings/Settings'
import { authAPI } from './services/api'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      await authAPI.check()
      setIsAuthenticated(true)
    } catch (error) {
      setIsAuthenticated(false)
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = () => {
    setIsAuthenticated(true)
  }

  const handleLogout = async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setIsAuthenticated(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={
            isAuthenticated ? (
              <Navigate to="/" replace />
            ) : (
              <Login onLogin={handleLogin} />
            )
          }
        />
        <Route
          path="/*"
          element={
            isAuthenticated ? (
              <Layout onLogout={handleLogout}>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/users" element={<UserManagement />} />
                  <Route path="/monitoring" element={<Monitoring />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>
    </Router>
  )
}

export default App

