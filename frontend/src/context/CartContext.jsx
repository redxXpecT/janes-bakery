import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import api from '../api/client'
import { useAuth } from './AuthContext'

const CartContext = createContext(null)
export function CartProvider({ children }) {
  const { isAuthenticated, isAdmin } = useAuth()
  const [cart, setCart] = useState({ cart_id: null, items: [], total: 0 })
  const [loading, setLoading] = useState(false)

  const refreshCart = useCallback(async () => {
    if (!isAuthenticated || isAdmin) { setCart({ cart_id: null, items: [], total: 0 }); return }
    setLoading(true)
    try { const { data } = await api.get('/api/cart/'); setCart(data) }
    catch { setCart({ cart_id: null, items: [], total: 0 }) }
    finally { setLoading(false) }
  }, [isAuthenticated, isAdmin])

  useEffect(() => { refreshCart() }, [refreshCart])
  const addItem = async (productId, quantity = 1) => { await api.post('/api/cart/items', { product_id: productId, quantity }); await refreshCart() }
  const updateItem = async (itemId, quantity) => { await api.patch(`/api/cart/items/${itemId}`, { quantity }); await refreshCart() }
  const removeItem = async (itemId) => { await api.delete(`/api/cart/items/${itemId}`); await refreshCart() }
  const value = useMemo(() => ({ cart, loading, refreshCart, addItem, updateItem, removeItem, count: cart.items.reduce((sum, item) => sum + item.quantity, 0) }), [cart, loading, refreshCart])
  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}
export const useCart = () => useContext(CartContext)
