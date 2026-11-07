import { useState } from 'react'
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { Menu, ShoppingBag, UserRound, LogOut, LayoutDashboard, ChevronDown, X } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'

export function SiteLayout() {
  const { user, isAuthenticated, isAdmin, logout } = useAuth()
  const { count } = useCart()
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()
  const signOut = () => { logout(); navigate('/') }
  return <div className="site-shell">
    <div className="announcement">Freshly baked in Ghana, made with care every day</div>
    <header className="site-header"><div className="container nav-wrap">
      <button className="mobile-menu icon-button" onClick={() => setOpen(!open)} aria-label="Toggle menu">{open ? <X/> : <Menu/>}</button>
      <Link to="/" className="brand"><span className="brand-mark">J</span><span>jane's<span className="brand-sub">BAKERY</span></span></Link>
      <nav className={`main-nav ${open ? 'show' : ''}`}>
        <NavLink to="/shop" onClick={() => setOpen(false)}>Shop</NavLink><NavLink to="/custom-order" onClick={() => setOpen(false)}>Custom orders</NavLink><a href="/#story" onClick={() => setOpen(false)}>Our story</a>
      </nav>
      <div className="nav-actions">
        {isAuthenticated ? <>
          {!isAdmin && <Link to="/cart" className="icon-button cart-link" aria-label="Shopping cart"><ShoppingBag size={19}/>{count > 0 && <span className="cart-count">{count}</span>}</Link>}
          <div className="account-menu"><button className="account-trigger"><UserRound size={18}/><span>{isAdmin ? 'Admin' : 'Account'}</span><ChevronDown size={14}/></button><div className="account-dropdown">{isAdmin ? <Link to="/admin">Dashboard</Link> : <><Link to="/account">My account</Link><Link to="/orders">My orders</Link><Link to="/my-custom-orders">My custom orders</Link><Link to="/receipts">Receipts</Link></>}<button onClick={signOut}><LogOut size={15}/> Sign out</button></div></div>
          {isAdmin && <Link to="/admin" className="btn btn-dark btn-small"><LayoutDashboard size={15}/> Dashboard</Link>}
        </> : <><Link to="/login" className="nav-login">Sign in</Link><Link to="/register" className="btn btn-dark btn-small">Create account</Link></>}
      </div>
    </div></header>
    <main><Outlet/></main>
    <footer className="site-footer"><div className="container footer-grid"><div><Link to="/" className="brand footer-brand"><span className="brand-mark">J</span><span>jane's<span className="brand-sub">BAKERY</span></span></Link><p>Small-batch goodness, baked fresh and shared with love.</p></div><div><h4>Explore</h4><Link to="/shop">Shop all</Link><Link to="/custom-order">Custom orders</Link><Link to="/orders">Track an order</Link></div><div><h4>Get in touch</h4><p>Accra, Ghana</p><p>Freshly baked, every day.</p></div></div><div className="container footer-bottom">© {new Date().getFullYear()} Jane's Bakery. All rights reserved.</div></footer>
  </div>
}

export function AdminLayout() {
  const { logout } = useAuth(); const navigate = useNavigate()
  const links = [['Overview','/admin'],['Products','/admin/products'],['Orders','/admin/orders'],['Custom orders','/admin/custom-orders'],['Payments','/admin/payments'],['Fulfilment','/admin/deliveries'],['Reports','/admin/reports']]
  return <div className="admin-shell"><aside className="admin-sidebar"><Link to="/" className="brand admin-brand"><span className="brand-mark">J</span><span>jane's<span className="brand-sub">BAKERY ADMIN</span></span></Link><div className="sidebar-label">WORKSPACE</div><nav>{links.map(([label, path]) => <NavLink key={path} end={path === '/admin'} to={path}>{label}</NavLink>)}</nav><button className="sidebar-logout" onClick={() => { logout(); navigate('/') }}><LogOut size={17}/> Sign out</button></aside><div className="admin-main"><header className="admin-topbar"><span>Administration</span><Link to="/" className="text-link">View storefront ↗</Link></header><div className="admin-content"><Outlet/></div></div></div>
}
