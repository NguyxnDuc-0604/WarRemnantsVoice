import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Header from './components/Header'
import HomePage from './pages/HomePage'
import ExhibitVisitorPage from './pages/ExhibitVisitorPage'
import MuseumQRStandeePage from './pages/MuseumQRStandeePage'
import AdminDashboardPage from './pages/AdminDashboardPage'
import TranslatePage from './pages/TranslatePage'

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header />
        <Routes>
          {/* Trang chủ giới thiệu */}
          <Route path="/" element={<HomePage />} />

          {/* TRỤ CỘT KHÁCH THAM QUAN: Quét QR bằng Camera điện thoại -> Mở bài thuyết minh */}
          <Route path="/exhibit/:code" element={<ExhibitVisitorPage />} />

          {/* Bảng Biển Mã QR Hiện Vật Chuẩn Bảo Tàng */}
          <Route path="/qr-stands" element={<MuseumQRStandeePage />} />
          <Route path="/qr-codes" element={<Navigate to="/qr-stands" replace />} />
          <Route path="/qr-scan" element={<Navigate to="/qr-stands" replace />} />

          {/* TRANG ADMIN: Thêm mã QR hiện vật & Thống kê số người đang truy cập thời gian thực */}
          <Route path="/admin" element={<AdminDashboardPage />} />

          {/* Trang công cụ AI dịch tự do */}
          <Route path="/translate" element={<TranslatePage />} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <footer style={{
          textAlign: 'center',
          padding: '1.5rem',
          borderTop: '1px solid rgba(255,255,255,0.06)',
          color: 'var(--color-text-muted)',
          fontSize: '0.75rem',
          marginTop: 'auto',
        }}>
          WarRemnantsVoice © 2026 — Bảo tàng Chứng tích Chiến tranh TP.HCM · Smart Audio Guide PWA & Admin CMS
        </footer>
      </div>
    </BrowserRouter>
  )
}
