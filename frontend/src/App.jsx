import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import { SiteLayout, AdminLayout } from './components/Layout'
import { PageLoader } from './components/Shared'
import { HomePage, ShopPage, ProductPage, CartPage, CheckoutPage, CustomOrderPage, PaymentCallbackPage, AccountPage, OrdersPage, OrderDetailPage, ReceiptsPage, MyCustomOrdersPage } from './pages/StorePages'
import { LoginPage, RegisterPage } from './pages/AuthPages'
import { AdminDashboardPage, AdminProductsPage, AdminOrdersPage, AdminCustomOrdersPage, AdminPaymentsPage, AdminDeliveriesPage, AdminReportsPage } from './pages/AdminPages'

function RequireAuth({ children, admin = false }) {
  const { isAuthenticated, isAdmin } = useAuth(); const location = useLocation()
  if (!isAuthenticated) return <Navigate to={admin ? '/admin/login' : '/login'} state={{ from: location.pathname }} replace/>
  if (admin && !isAdmin) return <Navigate to="/admin/login" replace/>
  if (!admin && isAdmin) return <Navigate to="/admin" replace/>
  return children
}
function CustomerOnly({ children }) { return <RequireAuth>{children}</RequireAuth> }
function AdminOnly({ children }) { return <RequireAuth admin>{children}</RequireAuth> }

export default function App() {
  const { isAuthenticated, isAdmin } = useAuth()
  return <Routes>
    <Route element={<SiteLayout/>}>
      <Route index element={<HomePage/>}/>
      <Route path="shop" element={<ShopPage/>}/>
      <Route path="product/:id" element={<ProductPage/>}/>
      <Route path="custom-order" element={<CustomerOnly><CustomOrderPage/></CustomerOnly>}/>
      <Route path="login" element={<LoginPage/>}/>
      <Route path="register" element={<RegisterPage/>}/>
      <Route path="admin/login" element={<LoginPage admin/>}/>
      <Route path="payment/callback" element={<CustomerOnly><PaymentCallbackPage/></CustomerOnly>}/>
      <Route path="cart" element={<CustomerOnly><CartPage/></CustomerOnly>}/>
      <Route path="checkout" element={<CustomerOnly><CheckoutPage/></CustomerOnly>}/>
      <Route path="account" element={<CustomerOnly><AccountPage/></CustomerOnly>}/>
      <Route path="orders" element={<CustomerOnly><OrdersPage/></CustomerOnly>}/>
      <Route path="my-custom-orders" element={<CustomerOnly><MyCustomOrdersPage/></CustomerOnly>}/>
      <Route path="orders/:id" element={<CustomerOnly><OrderDetailPage/></CustomerOnly>}/>
      <Route path="receipts" element={<CustomerOnly><ReceiptsPage/></CustomerOnly>}/>
    </Route>
    <Route path="admin" element={<AdminOnly><AdminLayout/></AdminOnly>}>
      <Route index element={<AdminDashboardPage/>}/>
      <Route path="products" element={<AdminProductsPage/>}/>
      <Route path="orders" element={<AdminOrdersPage/>}/>
      <Route path="custom-orders" element={<AdminCustomOrdersPage/>}/>
      <Route path="payments" element={<AdminPaymentsPage/>}/>
      <Route path="deliveries" element={<AdminDeliveriesPage/>}/>
      <Route path="reports" element={<AdminReportsPage/>}/>
    </Route>
    <Route path="*" element={<Navigate to={isAuthenticated && isAdmin ? '/admin' : '/'} replace/>}/>
  </Routes>
}
