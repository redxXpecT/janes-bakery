import { createContext, useContext, useMemo, useState } from 'react'
import api from '../api/client'

const AuthContext = createContext(null)
export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('jb_token'))
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('jb_user') || 'null') } catch { return null }
  })

  const login = async (email, password, type = 'customer') => {
    const { data } = await api.post(`/api/auth/${type}/login`, { email, password })
    localStorage.setItem('jb_token', data.access_token)
    const nextUser = { user_id: data.user_id, user_type: data.user_type }
    localStorage.setItem('jb_user', JSON.stringify(nextUser))
    setToken(data.access_token)
    setUser(nextUser)
    return nextUser
  }

  const register = async (values) => api.post('/api/customers/register', values)
  const logout = () => {
    localStorage.removeItem('jb_token'); localStorage.removeItem('jb_user')
    setToken(null); setUser(null)
  }

  const value = useMemo(() => ({ token, user, isAuthenticated: Boolean(token && user), isAdmin: user?.user_type === 'ADMIN', login, register, logout }), [token, user])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
export const useAuth = () => useContext(AuthContext)
