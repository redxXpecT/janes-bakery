import { Link } from 'react-router-dom'
import { AlertCircle, CheckCircle2, LoaderCircle, PackageOpen } from 'lucide-react'

export function PageLoader({ label = 'Loading...' }) { return <div className="loader-wrap"><LoaderCircle className="spin" size={25}/><span>{label}</span></div> }
export function EmptyState({ title = 'Nothing here yet', text = 'When there is something to show, it will appear here.' }) { return <div className="empty-state"><PackageOpen size={32}/><h3>{title}</h3><p>{text}</p></div> }
export function Notice({ type = 'success', children, onClose }) { const Icon = type === 'error' ? AlertCircle : CheckCircle2; return <div className={`notice ${type}`}><Icon size={18}/><span>{children}</span>{onClose && <button className="notice-close" onClick={onClose}>×</button>}</div> }
export function PageTitle({ eyebrow, title, subtitle, action }) { return <div className="page-title"><div>{eyebrow && <span className="eyebrow">{eyebrow}</span>}<h1>{title}</h1>{subtitle && <p>{subtitle}</p>}</div>{action}</div> }
export function Price({ value, className = '' }) { return <span className={className}>GH₵ {Number(value || 0).toFixed(2)}</span> }
export function StatusPill({ value }) { const kind = String(value || '').toLowerCase().replaceAll(' ', '-'); return <span className={`status-pill ${kind}`}>{value || 'Unknown'}</span> }
export function ProductImage({ src, name, className = '' }) { return <div className={`product-image ${className}`}>{src ? <img src={src} alt={name} onError={(event) => { event.currentTarget.style.display = 'none'; event.currentTarget.parentElement.classList.add('image-fallback') }}/> : <span>{(name || 'B').slice(0, 1).toUpperCase()}</span>}</div> }
export function AuthRequired({ children }) { return <div className="auth-required"><h2>Sign in to continue</h2><p>Create an account or sign in to use this feature.</p><Link className="btn btn-primary" to="/login">Sign in</Link>{children}</div> }
