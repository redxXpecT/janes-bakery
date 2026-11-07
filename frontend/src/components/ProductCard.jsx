import { Link } from 'react-router-dom'
import { ArrowUpRight, ShoppingBag } from 'lucide-react'
import { ProductImage, Price } from './Shared'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import { useState } from 'react'

export default function ProductCard({ product }) {
  const { isAuthenticated, isAdmin } = useAuth(); const { addItem } = useCart(); const [busy, setBusy] = useState(false); const [message, setMessage] = useState('')
  const add = async () => { if (!isAuthenticated || isAdmin) { setMessage('Sign in as a customer to add items.'); return } setBusy(true); setMessage(''); try { await addItem(product.product_id, 1); setMessage('Added to bag') } catch (error) { setMessage(error.response?.data?.detail || 'Could not add this item') } finally { setBusy(false) } }
  return <article className="product-card"><Link to={`/product/${product.product_id}`} className="product-card-image"><ProductImage src={product.image_url} name={product.product_name}/><span className="product-view">View <ArrowUpRight size={15}/></span></Link><div className="product-card-body"><div className="product-card-top"><h3><Link to={`/product/${product.product_id}`}>{product.product_name}</Link></h3><Price value={product.selling_price}/></div><p>{product.description || 'Freshly prepared by our bakery team.'}</p><div className="product-card-bottom"><span className="stock-label">{product.stock_quantity > 0 ? 'Freshly available' : 'Currently unavailable'}</span><button className="add-button" onClick={add} disabled={busy || product.stock_quantity < 1}>{busy ? 'Adding…' : <><ShoppingBag size={15}/> Add</>}</button></div>{message && <small className="inline-message">{message}</small>}</div></article>
}
