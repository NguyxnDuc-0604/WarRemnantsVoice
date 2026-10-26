import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Header from './components/Header'
import HomePage from './pages/HomePage'
import ExhibitVisitorPage from './pages/ExhibitVisitorPage'
import MuseumQRStandeePage from './pages/MuseumQRStandeePage'
import TranslatePage from './pages/TranslatePage'

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header />
        <Routes>
          {/* Trang chủ giới thiệu */}
          <Route path="/" element={<HomePage />} />

          {/* TRỤ CỘT CHÍNH PRD: Du khách quét QR bằng Camera điện thoại -> Mở thẳng trang này */}
          <Route path="/exhibit/:code" element={<ExhibitVisitorPage />} />

          {/* Bảng Biển Mã QR Hiện Vật Chuẩn Bảo Tàng (Hiển thị trên PC để điện thoại quét, hoặc in ấn) */}
          <Route path="/qr-stands" element={<MuseumQRStandeePage />} />
          <Route path="/qr-codes" element={<Navigate to="/qr-stands" replace />} />
          <Route path="/qr-scan" element={<Navigate to="/qr-stands" replace />} />

          {/* Trang công cụ AI dịch tự do & quản lý */}
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
          WarRemnantsVoice © 2026 — Bảo tàng Chứng tích Chiến tranh TP.HCM · Smart Audio Guide PWA
        </footer>
      </div>
    </BrowserRouter>
  )
}
