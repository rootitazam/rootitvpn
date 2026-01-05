import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_BASE = `${API_URL}/api/v1`

const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Redirect to login if unauthorized
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
  check: () => api.get('/auth/check'),
}

// Users API
export const usersAPI = {
  getAll: (params) => api.get('/users', { params }),
  getById: (id) => api.get(`/users/${id}`),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
  resetData: (id) => api.post(`/users/${id}/reset-data`),
  getStats: () => api.get('/users/stats'),
}

// Monitoring API
export const monitoringAPI = {
  getOnlineUsers: () => api.get('/monitoring/online-users'),
  getStats: () => api.get('/monitoring/stats'),
  getDevices: (userId) => api.get('/monitoring/devices', { params: { user_id: userId } }),
  getAccessLogs: (params) => api.get('/monitoring/access-logs', { params }),
  getTopDomains: (params) => api.get('/monitoring/top-domains', { params }),
}

// Subscriptions API
export const subscriptionsAPI = {
  getUserSubscription: (userId, serverIp) => 
    api.get(`/subscriptions/${userId}`, { params: { server_ip: serverIp } }),
  getV2rayNG: (userId, serverIp) => 
    api.get(`/subscriptions/${userId}/v2rayng`, { params: { server_ip: serverIp } }),
  getShadowrocket: (userId, serverIp) => 
    api.get(`/subscriptions/${userId}/shadowrocket`, { params: { server_ip: serverIp } }),
  getNekoray: (userId, serverIp) => 
    api.get(`/subscriptions/${userId}/nekoray`, { params: { server_ip: serverIp } }),
}

// Xray API
export const xrayAPI = {
  getConfig: () => api.get('/xray/config'),
  updateConfig: (data) => api.put('/xray/config', data),
  rotateReality: () => api.post('/xray/config/rotate'),
  reload: () => api.post('/xray/reload'),
}

export default api

