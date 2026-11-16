import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import QRCode from 'qrcode'
import {
  QrCode, Download, ExternalLink, Printer, Headphones,
  MapPin, Calendar, Check, Copy
} from 'lucide-react'
import { fetchExhibits } from '../api/pipelineApi'
import './QRExhibitsPage.css'

export default function QRExhibitsPage() {
  const [exhibits, setExhibits] = useState([])
  const [qrImages, setQrImages] = useState({})
  const [copiedId, setCopiedId] = useState(null)

  useEffect(() => {
    fetchExhibits()
      .then((data) => {
        setExhibits(data)
        // Tạo ảnh QR cho từng hiện vật
        data.forEach((ex) => {
          generateQrDataUrl(ex.id)
        })
      })
      .catch((err) => console.warn('Lỗi lấy danh sách:', err))
  }, [])

  const generateQrDataUrl = async (exhibitId) => {
    try {
      // Nội dung mã QR: có thể là URL hoàn chỉnh hoặc exhibitId
      // Ưu tiên URL trỏ tới trang scan kèm ID hiện vật
      const currentOrigin = window.location.origin
      const qrTargetContent = `${currentOrigin}/qr-scan?id=${encodeURIComponent(exhibitId)}`

      const dataUrl = await QRCode.toDataURL(qrTargetContent, {
        width: 320,
        margin: 2,
        color: {
          dark: '#0f172a',
          light: '#ffffff',
        },
      })

      setQrImages((prev) => ({ ...prev, [exhibitId]: dataUrl }))
    } catch (err) {
      console.error('Lỗi sinh mã QR:', err)
    }
  }

  const handleDownloadQr = (exhibitId, exhibitName) => {
    const dataUrl = qrImages[exhibitId]
    if (!dataUrl) return
    const a = document.createElement('a')
    a.href = dataUrl
    a.download = `QRCode_${exhibitId}_${exhibitName.replace(/\s+/g, '_')}.png`
    a.click()
  }

  const handleCopyCode = (id) => {
    navigator.clipboard.writeText(id)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handlePrint = () => {
    window.print()
  }

  return (
    <main className="qr-exhibits-page">
      <div className="container">
        {/* Header */}
        <div className="qr-exhibits__header">
          <div>
            <div className="badge badge-amber" style={{ marginBottom: '0.5rem' }}>
              <QrCode size={12} />
              <span>Bảo Tàng Chứng Tích Chiến Tranh</span>
            </div>
            <h1 className="text-3xl font-bold">
              Thư Viện <span className="gradient-text">Mã QR Hiện Vật</span>
            </h1>
            <p className="text-sm" style={{ color: 'var(--color-text-secondary)', marginTop: '0.25rem' }}>
              Dùng camera điện thoại quét các mã QR dưới đây trên màn hình để nghe thuyết minh tự động
            </p>
          </div>

          <div className="qr-exhibits__actions">
            <Link to="/qr-scan" className="btn btn-primary btn-sm">
              <Headphones size={16} />
              <span>Mở Máy Quét QR</span>
            </Link>
            <button type="button" className="btn btn-secondary btn-sm" onClick={handlePrint}>
              <Printer size={16} />
              <span className="hide-on-mobile">In Bảng Mã QR</span>
            </button>
          </div>
        </div>

        {/* Lưới các thẻ hiện vật kèm mã QR */}
        <div className="qr-cards-grid">
          {exhibits.map((exhibit) => {
            const qrUrl = qrImages[exhibit.id]
            const scanLink = `/qr-scan?id=${encodeURIComponent(exhibit.id)}`

            return (
              <div key={exhibit.id} className="qr-exhibit-card glass-card">
                {/* Phần mã QR chuẩn */}
                <div className="qr-box-wrapper">
                  {qrUrl ? (
                    <img
                      src={qrUrl}
                      alt={`Mã QR ${exhibit.name}`}
                      className="qr-image"
                    />
                  ) : (
                    <div className="qr-image-placeholder">
                      <span className="spinner" />
                    </div>
                  )}
                  <div className="qr-box-badge">
                    <span className="badge badge-amber">{exhibit.id}</span>
                  </div>
                </div>

                {/* Thông tin hiện vật */}
                <div className="qr-exhibit-content">
                  <div className="qr-exhibit-top">
                    <div className="flex items-center gap-2">
                      <MapPin size={12} style={{ color: 'var(--color-amber-400)' }} />
                      <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                        {exhibit.zone}
                      </span>
                    </div>
                    {exhibit.period && (
                      <div className="flex items-center gap-1">
                        <Calendar size={11} style={{ color: 'var(--color-text-muted)' }} />
                        <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                          {exhibit.period}
                        </span>
                      </div>
                    )}
                  </div>

                  <h3 className="qr-exhibit-title text-base font-bold">
                    {exhibit.name}
                  </h3>

                  <p className="qr-exhibit-desc text-xs">
                    {exhibit.original_text}
                  </p>

                  {/* Nút hành động */}
                  <div className="qr-exhibit-buttons">
                    <Link to={scanLink} className="btn btn-primary btn-sm" style={{ flex: 1 }}>
                      <Headphones size={14} />
                      <span>Thuyết minh</span>
                    </Link>

                    <button
                      type="button"
                      className="btn btn-ghost btn-sm"
                      onClick={() => handleCopyCode(exhibit.id)}
                      title="Sao chép mã ID"
                    >
                      {copiedId === exhibit.id ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
                    </button>

                    <button
                      type="button"
                      className="btn btn-ghost btn-sm"
                      onClick={() => handleDownloadQr(exhibit.id, exhibit.name)}
                      title="Tải ảnh mã QR"
                    >
                      <Download size={14} />
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </main>
  )
}
