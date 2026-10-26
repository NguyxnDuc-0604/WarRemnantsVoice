import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import HomePage from './pages/HomePage'
import QRScanPage from './pages/QRScanPage'
import TranslatePage from './pages/TranslatePage'
import QRExhibitsPage from './pages/QRExhibitsPage'

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/qr-scan" element={<QRScanPage />} />
          <Route path="/translate" element={<TranslatePage />} />
          <Route path="/qr-codes" element={<QRExhibitsPage />} />
        </Routes>
        <footer style={{
          textAlign: 'center',
          padding: '1.5rem',
          borderTop: '1px solid rgba(255,255,255,0.06)',
          color: 'var(--color-text-muted)',
          fontSize: '0.75rem',
          marginTop: 'auto',
        }}>
          WarRemnantsVoice © 2024 — Bảo tàng Chứng tích Chiến tranh · AI Audio Guide v2.0
        </footer>
      </div>
    </BrowserRouter>
  )
}
