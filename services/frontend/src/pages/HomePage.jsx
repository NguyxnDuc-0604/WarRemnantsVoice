import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Headphones, Globe, Mic, Zap, ChevronRight, Shield, Volume2, QrCode, Smartphone, Sparkles, AlertCircle, RefreshCw } from 'lucide-react'
import { fetchExhibits } from '../api/pipelineApi'
import './HomePage.css'

const FEATURES = [
  {
    icon: <QrCode size={22} />,
    title: 'Quét Mã QR Bằng Camera Điện Thoại',
    desc: 'Không cần cài đặt ứng dụng hay đăng nhập. Khách chỉ cần mở Camera thường hoặc Zalo trên điện thoại quét mã QR để nghe thuyết minh tức thì (≤1.5s).',
  },
  {
    icon: <Globe size={22} />,
    title: '15+ Ngôn Ngữ Tự Động',
    desc: 'Dịch thuật tự động sang Anh, Pháp, Nhật, Hàn, Trung, Đức, Tây Ban Nha, Nga... và ghi nhớ ngôn ngữ suốt buổi tham quan.',
  },
  {
    icon: <Volume2 size={22} />,
    title: 'Giọng Đọc Neural AI & Phụ Đề Đồng Bộ',
    desc: 'Microsoft Edge TTS Neural với giọng đọc truyền cảm, trang nghiêm. Phụ đề tự động cuộn chữ và sáng theo từng câu đang đọc (FR-16).',
  },
  {
    icon: <Smartphone size={22} />,
    title: 'Đa Thiết Bị Truy Cập Đồng Thời',
    desc: 'Hàng chục, hàng trăm khách tham quan dùng 4G/5G hoặc mạng khác nhau có thể cùng quét mã QR và nghe độc lập không bị nghẽn.',
  },
  {
    icon: <Shield size={22} />,
    title: 'Từ Điển Thuật Ngữ Lịch Sử (Glossary)',
    desc: 'Kiểm soát nghiêm ngặt các thuật ngữ quân sự, chiến dịch (Ấp Bắc, Chiến dịch Hồ Chí Minh, Chuồng Cọp...) đạt độ chính xác ≥95%.',
  },
  {
    icon: <Zap size={22} />,
    title: 'Phát Âm Thanh Phân Đoạn (Streaming)',
    desc: 'Tối ưu hoá luồng phát âm thanh HTTP Range Requests giúp âm thanh vang lên trong ≤2 giây kể cả khi sóng di động 3G/4G yếu.',
  },
]

const FALLBACK_EXHIBITS = [
  {
    id: 'EX-01',
    code: 'UH1-BELL',
    title: 'Máy bay UH-1 "Huey"',
    zone: 'Khu trưng bày ngoài trời',
    original_text: 'Trực thăng UH-1 Iroquois được quân đội Hoa Kỳ sử dụng rộng rãi trong Chiến tranh Việt Nam từ năm 1962 đến 1975.',
    thumbnail_url: 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 'EX-02',
    code: 'T54-390',
    title: 'Xe tăng T-54B số hiệu 390',
    zone: 'Sân trưng bày cơ giới ngoài trời',
    original_text: 'Xe tăng húc đổ cổng chính Dinh Độc Lập lúc 10h45 ngày 30/4/1975, mốc son thống nhất đất nước.',
    thumbnail_url: 'https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 'EX-03',
    code: 'CONDAO-CAGE',
    title: 'Mô hình Chuồng cọp Côn Đảo',
    zone: 'Khu chứng tích tội ác chiến tranh',
    original_text: 'Tái hiện chế độ giam giữ khắc nghiệt đối với các chiến sĩ cách mạng, biểu tượng của ý chí bất khuất.',
    thumbnail_url: 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=800&q=80'
  },
]

const DEFAULT_LANG_FLAGS = ['🇻🇳', '🇬🇧', '🇫🇷', '🇯🇵', '🇨🇳', '🇰🇷']

export default function HomePage() {
  const [exhibits, setExhibits] = useState([])
  const [loading, setLoading] = useState(true)
  const [isBackendConnected, setIsBackendConnected] = useState(false)

  const loadExhibits = () => {
    setLoading(true)
    fetchExhibits()
      .then((data) => {
        if (data && data.length > 0) {
          setExhibits(data)
          setIsBackendConnected(true)
        } else {
          setExhibits(FALLBACK_EXHIBITS)
          setIsBackendConnected(false)
        }
      })
      .catch((err) => {
        console.warn('Backend chưa bật hoặc đang kết nối lại:', err)
        setExhibits(FALLBACK_EXHIBITS)
        setIsBackendConnected(false)
      })
      .finally(() => {
        setLoading(false)
      })
  }

  useEffect(() => {
    loadExhibits()
  }, [])

  return (
    <main className="home">
      {/* ── Hero Section ─────────────────────────── */}
      <section className="hero">
        <div className="hero__bg-grid" aria-hidden />
        <div className="hero__glow hero__glow--1" aria-hidden />
        <div className="hero__glow hero__glow--2" aria-hidden />

        <div className="container hero__content">
          <div className="hero__badge badge badge-amber animate-fade-in-up">
            <Sparkles size={11} />
            Hệ thống Thuyết minh Tự động Đa ngôn ngữ (WarRemnantsVoice)
          </div>

          <h1 className="hero__title animate-fade-in-up animate-fade-in-up-delay-1">
            Bảo Tàng Chứng Tích Chiến Tranh
            <br />
            <span className="gradient-text">Quét Mã QR Nghe Thuyết Minh</span>
          </h1>

          <p className="hero__desc animate-fade-in-up animate-fade-in-up-delay-2">
            Khách tham quan chỉ cần dùng <strong>Camera điện thoại</strong> hoặc <strong>Zalo</strong> quét mã QR tại hiện vật để nghe bài thuyết minh và xem phụ đề đồng bộ bằng <strong>15+ ngôn ngữ</strong>.
            Không cần tải app · Không cần đăng ký tài khoản.
          </p>

          <div className="hero__actions animate-fade-in-up animate-fade-in-up-delay-3">
            <Link to="/qr-stands" className="btn btn-primary btn-lg">
              <QrCode size={18} />
              Xem Biển Mã QR Hiện Vật
              <ChevronRight size={16} />
            </Link>

            <Link to="/exhibit/UH1-BELL" className="btn btn-secondary btn-lg">
              <Headphones size={18} />
              Trải Nghiệm Thuyết Minh Mẫu (EX-01)
            </Link>
          </div>

          {/* Stats Bar */}
          <div className="hero__stats animate-fade-in-up" style={{ animationDelay: '0.4s', opacity: 0 }}>
            <div className="hero__stat">
              <span className="hero__stat-value gradient-text">Camera QR</span>
              <span className="hero__stat-label">Không cần tải app</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-value gradient-text">15+</span>
              <span className="hero__stat-label">Ngôn ngữ quốc tế</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-value gradient-text">≤1.5s</span>
              <span className="hero__stat-label">Thời gian mở trang</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-value gradient-text">Neural</span>
              <span className="hero__stat-label">Giọng đọc AI & Phụ đề</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ────────────────────────────── */}
      <section className="section">
        <div className="container">
          <div className="section-header">
            <h2 className="text-3xl font-bold">Quy Trình Nghiệp Vụ Theo Chuẩn PRD</h2>
            <p className="text-sm" style={{ color: 'var(--color-text-secondary)', marginTop: '0.5rem' }}>
              Thiết kế chuyên biệt cho du khách quốc tế và công tác quản lý của Bảo tàng Chứng tích Chiến tranh
            </p>
          </div>
          <div className="features-grid">
            {FEATURES.map((feat, i) => (
              <div
                key={i}
                className="feature-card glass-card animate-fade-in-up"
                style={{ animationDelay: `${i * 0.08}s`, opacity: 0 }}
              >
                <div className="feature-card__icon">{feat.icon}</div>
                <h3 className="feature-card__title text-base font-semibold">{feat.title}</h3>
                <p className="feature-card__desc text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                  {feat.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Real Exhibits from Database ──────────────────────── */}
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h2 className="text-3xl font-bold">
                Danh Mục Hiện Vật Trưng Bày ({exhibits.length} Hiện Vật)
              </h2>
              <p className="text-sm" style={{ color: 'var(--color-text-secondary)', marginTop: '0.5rem' }}>
                Dữ liệu được quản lý động từ Microservice CSDL Bảo tàng. Bấm vào để nghe thuyết minh trực tiếp.
              </p>
            </div>
            {!isBackendConnected && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '0.4rem 0.8rem', borderRadius: '8px', color: '#f87171', fontSize: '0.8rem' }}>
                <AlertCircle size={14} />
                <span>Backend chưa bật. Đang hiển thị bản lưu đệm.</span>
                <button onClick={loadExhibits} style={{ background: 'transparent', border: 'none', color: '#f87171', cursor: 'pointer', display: 'flex', alignItems: 'center', marginLeft: '0.5rem' }}>
                  <RefreshCw size={12} style={{ marginRight: '3px' }} /> Thử lại
                </button>
              </div>
            )}
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--color-text-muted)' }}>
              <RefreshCw className="animate-spin" size={24} style={{ margin: '0 auto 1rem' }} />
              <p>Đang tải danh sách hiện vật từ Microservices...</p>
            </div>
          ) : (
            <div className="exhibits-grid">
              {exhibits.map((exhibit, idx) => (
                <div key={exhibit.code || idx} className="exhibit-card glass-card" style={{ display: 'flex', flexDirection: 'column' }}>
                  {exhibit.thumbnail_url && (
                    <div style={{ height: '160px', overflow: 'hidden', borderRadius: '8px', marginBottom: '0.75rem', position: 'relative' }}>
                      <img
                        src={exhibit.thumbnail_url}
                        alt={exhibit.title}
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        onError={(e) => { e.target.style.display = 'none' }}
                      />
                      <span className="badge badge-amber" style={{ position: 'absolute', top: '8px', left: '8px', backdropFilter: 'blur(4px)' }}>
                        {exhibit.display_code || `EX-${idx + 1 < 10 ? '0' : ''}${idx + 1}`}
                      </span>
                    </div>
                  )}

                  <div className="exhibit-card__header">
                    {!exhibit.thumbnail_url && (
                      <span className="badge badge-amber">{exhibit.display_code || `EX-${idx + 1}`}</span>
                    )}
                    <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>{exhibit.zone || 'Khu trưng bày'}</span>
                  </div>

                  <h3 className="exhibit-card__name text-base font-semibold" style={{ margin: '0.75rem 0 0.5rem' }}>
                    {exhibit.title || exhibit.name}
                  </h3>

                  <p className="text-sm" style={{ color: 'var(--color-text-secondary)', lineHeight: 1.6, marginBottom: '1rem', flex: 1, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {exhibit.original_text || exhibit.text}
                  </p>

                  <div className="exhibit-card__langs" style={{ marginTop: 'auto' }}>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      {DEFAULT_LANG_FLAGS.map((flag, j) => (
                        <span key={j} className="exhibit-card__lang-flag" style={{ fontSize: '0.9rem' }}>{flag}</span>
                      ))}
                    </div>
                    <Link
                      to={`/exhibit/${exhibit.code}`}
                      className="btn btn-sm btn-primary"
                      style={{ marginLeft: 'auto' }}
                    >
                      Nghe Thuyết Minh →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* ── CTA ────────────────────────────────── */}
      <section className="cta-section">
        <div className="container cta-section__inner">
          <QrCode size={42} style={{ color: 'var(--color-amber-400)', marginBottom: '1rem' }} />
          <h2 className="text-2xl font-bold" style={{ marginBottom: '0.5rem' }}>
            Kiểm Thử Trực Tiếp Trên Điện Thoại
          </h2>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)', marginBottom: '1.5rem', maxWidth: '520px' }}>
            Mở <strong>Biển Mã QR Hiện Vật</strong> trên màn hình máy tính, sau đó cầm bất kỳ điện thoại nào (dùng 4G/5G hoặc WiFi) bật Camera hoặc Zalo lên quét là nghe được ngay!
          </p>
          <div className="flex gap-3 flex-wrap justify-center">
            <Link to="/qr-stands" className="btn btn-primary btn-lg">
              <QrCode size={18} />
              Mở Danh Sách Biển Mã QR
            </Link>
            <Link to="/admin" className="btn btn-secondary btn-lg">
              Trang Quản Trị Admin
            </Link>
          </div>
        </div>
      </section>
    </main>
  )
}
