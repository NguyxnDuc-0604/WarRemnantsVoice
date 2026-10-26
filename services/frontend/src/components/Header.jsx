import { Link, useLocation } from 'react-router-dom'
import { Headphones, BookOpen, QrCode, Globe } from 'lucide-react'
import './Header.css'

export default function Header() {
  const location = useLocation()

  return (
    <header className="header">
      <div className="header__inner container">
        {/* Logo */}
        <Link to="/" className="header__logo">
          <div className="header__logo-icon">
            <Headphones size={20} strokeWidth={2.5} />
          </div>
          <div className="header__logo-text">
            <span className="header__logo-name">WarRemnants</span>
            <span className="header__logo-suffix gradient-text">Voice</span>
          </div>
        </Link>

        {/* Navigation */}
        <nav className="header__nav">
          <Link
            to="/"
            className={`header__nav-link ${location.pathname === '/' ? 'header__nav-link--active' : ''}`}
          >
            <BookOpen size={15} />
            <span className="nav-label">Trang chủ</span>
          </Link>

          <Link
            to="/qr-stands"
            className={`header__nav-link header__nav-link--highlight ${location.pathname.startsWith('/qr') ? 'header__nav-link--active' : ''}`}
          >
            <QrCode size={15} />
            <span className="nav-label">Bảng Mã QR Hiện Vật</span>
          </Link>

          <Link
            to="/translate"
            className={`header__nav-link ${location.pathname === '/translate' ? 'header__nav-link--active' : ''}`}
          >
            <Globe size={15} />
            <span className="nav-label">Công cụ Dịch AI</span>
          </Link>
        </nav>

        {/* Status badge */}
        <div className="header__status">
          <span className="header__status-dot" />
          <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>AI Pipeline Active</span>
        </div>
      </div>
    </header>
  )
}
