import axios from 'axios'

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, ''),
  headers: { 'Content-Type': 'application/json' },
  timeout: 20000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jb_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const path = window.location.pathname
      if (!path.startsWith('/login') && !path.startsWith('/admin/login')) {
        localStorage.removeItem('jb_token')
        localStorage.removeItem('jb_user')
      }
    }
    return Promise.reject(error)
  }
)

export const getErrorMessage = (error) => {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((item) => item.msg).join(', ')
  return error?.message || 'Something went wrong. Please try again.'
}

export default api
