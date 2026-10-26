import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import QRCode from 'qrcode'
import {
  QrCode, ExternalLink, Printer, Download, Globe,
  MapPin, Check, Copy, Wifi, Share2, Sparkles, Smartphone, CheckCircle2, AlertTriangle
} from 'lucide-react'
import { fetchExhibits } from '../api/pipelineApi'
import './MuseumQRStandeePage.css'

export default function MuseumQRStandeePage() {
  const [exhibits, setExhibits] = useState([])
  const [qrImages, setQrImages] = useState({})
  const [copiedCode, setCopiedCode] = useState(null)

  // Tự động khôi phục link Tunnel đã lưu trước đó nếu có (loại bỏ nếu là api.trycloudflare.com)
  const defaultBaseUrl = window.location.origin
  const [customHost, setCustomHost] = useState(() => {
    const saved = localStorage.getItem('war_remnants_tunnel_host')
    if (saved && !saved.includes('api.trycloudflare.com')) {
      return saved
    }
    return defaultBaseUrl
  })
  const [isEditingHost, setIsEditingHost] = useState(false)

  useEffect(() => {
    fetchExhibits()
      .then((data) => {
        setExhibits(data)
        generateAllQrs(data, customHost)
      })
      .catch((err) => console.warn('Lỗi tải hiện vật:', err))
  }, [])

  // Sinh mã QR khi danh sách hiện vật hoặc customHost thay đổi
  const generateAllQrs = async (exhibitList, baseUrl) => {
    const images = {}
    for (const ex of exhibitList) {
      try {
        const targetUrl = `${baseUrl.replace(/\/+$/, '')}/exhibit/${ex.code}`
        const dataUrl = await QRCode.toDataURL(targetUrl, {
          width: 360,
          margin: 1,
          color: {
            dark: '#0a0c10',
            light: '#ffffff',
          },
          errorCorrectionLevel: 'H',
        })
        images[ex.code] = {
          dataUrl,
          targetUrl,
        }
      } catch (err) {
        console.error('Lỗi tạo QR:', err)
      }
    }
    setQrImages(images)
  }

  const handleHostChange = (newHost) => {
    const cleaned = newHost.trim().replace(/\/+$/, '')
    setCustomHost(cleaned)
    if (!cleaned.includes('api.trycloudflare.com')) {
      localStorage.setItem('war_remnants_tunnel_host', cleaned)
    }
    generateAllQrs(exhibits, cleaned)
  }

  const handleCopyLink = (code, url) => {
    navigator.clipboard.writeText(url)
    setCopiedCode(code)
    setTimeout(() => setCopiedCode(null), 2000)
  }

  const handlePrint = () => {
    window.print()
  }

  const isInvalidApiUrl = customHost.includes('api.trycloudflare.com')
  const isTunnelUrl = customHost.includes('trycloudflare.com') && !isInvalidApiUrl

  return (
    <main className="standee-page">
      <div className="container">
        {/* Header điều khiển */}
        <div className="standee-header">
          <div className="standee-title-group">
            <div className="badge badge-amber" style={{ marginBottom: '0.4rem' }}>
              <QrCode size={13} />
              <span>Bảng Biển Mã QR Chuẩn Bảo Tàng</span>
            </div>
            <h1 className="text-3xl font-bold">
              Biển Thuyết Minh <span className="gradient-text">Quét Mã QR</span>
            </h1>
            <p className="text-sm text-secondary" style={{ marginTop: '0.25rem' }}>
              Du khách chỉ cần dùng <strong>Camera điện thoại</strong> hoặc <strong>Zalo</strong> quét mã QR dưới đây để vào thẳng bài thuyết minh (không cần nhập IP hay mật khẩu)
            </p>
          </div>

          <div className="standee-actions-bar">
            <button type="button" className="btn btn-secondary btn-sm" onClick={handlePrint}>
              <Printer size={15} />
              <span>In Bảng Mica</span>
            </button>
          </div>
        </div>

        {/* Thanh cấu hình Domain / IP cho nhiều điện thoại cùng vào */}
        <div className="host-config-card glass-card">
          <div className="host-config-info">
            <div className="flex items-center gap-2">
              <Share2 size={16} style={{ color: 'var(--color-amber-400)' }} />
              <strong className="text-sm">Đường dẫn mã QR đang liên kết:</strong>
            </div>
            <code className="host-url-badge">{customHost}</code>
            {isTunnelUrl && (
              <span className="badge badge-amber" style={{ fontSize: '0.7rem' }}>
                <CheckCircle2 size={12} /> Cloudflare Tunnel (Vào thẳng 100%)
              </span>
            )}
            {isInvalidApiUrl && (
              <span className="badge" style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#fca5a5', border: '1px solid rgba(239, 68, 68, 0.4)', fontSize: '0.75rem' }}>
                <AlertTriangle size={13} /> Nhầm link API Cloudflare
              </span>
            )}
          </div>

          {/* Cảnh báo nếu dán nhầm api.trycloudflare.com */}
          {isInvalidApiUrl && (
            <div className="error-box glass-card animate-fade-in-up" style={{ padding: '8px 12px', marginTop: '6px' }}>
              <span className="text-xs" style={{ color: '#fca5a5' }}>
                ⚠️ <strong>Bạn đang dán nhầm "api.trycloudflare.com"!</strong> Đây là link máy chủ Cloudflare, không phải website của bạn.
                Đường link đúng phải có tên ngẫu nhiên (ví dụ: <code>https://spin-jewel-garden-adding.trycloudflare.com</code>). Hãy mở lại file <code>start_public_tunnel.bat</code> để lấy link màu vàng đúng nhé!
              </span>
            </div>
          )}

          <div className="host-presets">
            <span className="text-xs text-muted">Chuyển cấu hình:</span>
            <button
              type="button"
              className={`preset-btn ${customHost === defaultBaseUrl ? 'active' : ''}`}
              onClick={() => handleHostChange(defaultBaseUrl)}
            >
              Mặc định ({window.location.hostname})
            </button>
            <button
              type="button"
              className={`preset-btn ${isEditingHost || isTunnelUrl ? 'active' : ''}`}
              onClick={() => setIsEditingHost(!isEditingHost)}
            >
              {isEditingHost ? 'Đóng ô nhập' : '🔗 Dán Link Cloudflare Tunnel (Cho điện thoại 4G/5G)'}
            </button>
          </div>

          {isEditingHost && (
            <div className="host-custom-input-row animate-fade-in-up">
              <div className="flex gap-2">
                <input
                  type="text"
                  className="form-input"
                  style={{ flex: 1 }}
                  placeholder="Dán link Cloudflare Tunnel (ví dụ: https://spin-jewel-garden-adding.trycloudflare.com)"
                  value={customHost}
                  onChange={(e) => handleHostChange(e.target.value)}
                />
                <button
                  type="button"
                  className="btn btn-primary btn-sm"
                  onClick={() => setIsEditingHost(false)}
                >
                  Áp dụng
                </button>
              </div>
              <p className="text-xs" style={{ color: 'var(--color-text-amber)', marginTop: '4px' }}>
                💡 <strong>Mẹo:</strong> Chạy file <code>start_public_tunnel.bat</code>. Đường link đúng sẽ có dạng <code>https://từ-ghép-ngẫu-nhiên.trycloudflare.com</code> (KHÔNG PHẢI là chữ <code>api</code>).
              </p>
            </div>
          )}
        </div>

        {/* Lưới các Bảng Biển Trưng Bày (Museum Standees) */}
        <div className="standee-grid">
          {exhibits.map((exhibit) => {
            const qrInfo = qrImages[exhibit.code]
            const targetUrl = qrInfo?.targetUrl || ''

            return (
              <div key={exhibit.code} className="museum-standee-board">
                {/* Phần Header biển bảo tàng */}
                <div className="standee-museum-brand">
                  <div className="standee-emblem">🏛️</div>
                  <div className="standee-brand-text">
                    <span className="standee-vn-name">BẢO TÀNG CHỨNG TÍCH CHIẾN TRANH</span>
                    <span className="standee-en-name">WAR REMNANTS MUSEUM</span>
                  </div>
                </div>

                {/* Tên hiện vật & Khu vực */}
                <div className="standee-exhibit-header">
                  <div className="standee-code-tag">{exhibit.display_code || exhibit.code}</div>
                  <h2 className="standee-title-vn">{exhibit.title}</h2>
                  <h3 className="standee-title-en">{exhibit.title_en}</h3>
                  <div className="standee-zone-row">
                    <MapPin size={11} />
                    <span>{exhibit.zone}</span>
                    {exhibit.period && <span>· Thời kỳ: {exhibit.period}</span>}
                  </div>
                </div>

                {/* Khung Mã QR to bản trung tâm */}
                <div className="standee-qr-center">
                  <div className="standee-qr-frame">
                    {qrInfo?.dataUrl ? (
                      <img
                        src={qrInfo.dataUrl}
                        alt={`QR Code ${exhibit.title}`}
                        className="standee-qr-img"
                      />
                    ) : (
                      <div className="standee-qr-loading">
                        <span className="spinner" />
                      </div>
                    )}
                  </div>
                </div>

                {/* Hướng dẫn quét bằng Camera điện thoại */}
                <div className="standee-guide-box">
                  <div className="standee-guide-icon">
                    <Smartphone size={20} />
                  </div>
                  <div className="standee-guide-text">
                    <strong className="guide-vn">DÙNG CAMERA ĐIỆN THOẠI HOẶC ZALO ĐỂ QUÉT MÃ</strong>
                    <span className="guide-en">Scan with phone camera to listen to audio guide</span>
                  </div>
                </div>

                {/* Nút thao tác nhanh trên web */}
                <div className="standee-card-footer">
                  <Link
                    to={`/exhibit/${exhibit.code}`}
                    className="btn btn-primary btn-sm"
                    style={{ flex: 1 }}
                  >
                    <span>Mở thử thuyết minh</span>
                    <ExternalLink size={13} />
                  </Link>

                  <button
                    type="button"
                    className="btn btn-ghost btn-sm"
                    onClick={() => handleCopyLink(exhibit.code, targetUrl)}
                    title="Sao chép liên kết mã QR"
                  >
                    {copiedCode === exhibit.code ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </main>
  )
}
