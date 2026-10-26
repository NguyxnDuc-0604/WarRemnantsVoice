import { Link } from 'react-router-dom'
import { Headphones, Globe, Mic, Zap, ChevronRight, Shield, Volume2, QrCode, Smartphone } from 'lucide-react'
import './HomePage.css'

const FEATURES = [
  {
    icon: <QrCode size={22} />,
    title: 'Quét Mã QR Hiện Vật',
    desc: 'Quét mã QR tại bảo tàng bằng camera điện thoại để nghe ngay bài thuyết minh tương ứng.',
  },
  {
    icon: <Globe size={22} />,
    title: '13+ Ngôn Ngữ',
    desc: 'Dịch thuật tự động sang Anh, Pháp, Nhật, Hàn, Trung, Đức, Tây Ban Nha và nhiều ngôn ngữ khác.',
  },
  {
    icon: <Volume2 size={22} />,
    title: 'Giọng Đọc Neural AI',
    desc: 'Microsoft Edge TTS Neural — giọng đọc tự nhiên như người thật, chuẩn ngữ điệu từng quốc gia.',
  },
  {
    icon: <Smartphone size={22} />,
    title: 'Đa Thiết Bị Không Cần Cài Đặt',
    desc: 'Truy cập trực tiếp từ trình duyệt smartphone qua mạng nội bộ hoặc đường dẫn internet an toàn.',
  },
  {
    icon: <Shield size={22} />,
    title: 'Từ Điển Lịch Sử (Glossary)',
    desc: 'Bảo toàn và chuẩn hoá các thuật ngữ lịch sử (Chiến dịch Hồ Chí Minh, Chuồng Cọp, Ấp Bắc...).',
  },
  {
    icon: <Zap size={22} />,
    title: 'Xử Lý Nhanh Chóng',
    desc: 'Pipeline AI thời gian thực: nhận diện mã QR → dịch thuật ngữ cảnh → phát audio chỉ trong vài giây.',
  },
]

const SAMPLE_EXHIBITS = [
  {
    id: 'EX-01',
    name: 'Máy bay UH-1 "Huey"',
    zone: 'Khu trưng bày ngoài trời',
    text: 'Trực thăng UH-1 Iroquois được sử dụng rộng rãi trong Chiến tranh Việt Nam bởi quân đội Hoa Kỳ từ năm 1962 đến 1975.',
    langs: ['🇬🇧', '🇫🇷', '🇯🇵', '🇨🇳'],
  },
  {
    id: 'EX-02',
    name: 'Xe tăng M48 Patton',
    zone: 'Sân trưng bày vũ khí',
    text: 'Xe tăng M48 Patton là loại xe tăng chiến đấu chủ lực được Mỹ sử dụng trong giai đoạn 1967–1972.',
    langs: ['🇬🇧', '🇰🇷', '🇩🇪', '🇧🇷'],
  },
  {
    id: 'EX-03',
    name: 'Chiến dịch Hồ Chí Minh',
    zone: 'Phòng lịch sử tổng thể',
    text: 'Chiến dịch Hồ Chí Minh diễn ra từ ngày 26 tháng 4 đến 30 tháng 4 năm 1975, kết thúc cuộc kháng chiến.',
    langs: ['🇬🇧', '🇫🇷', '🇷🇺', '🇸🇦'],
  },
]

export default function HomePage() {
  return (
    <main className="home">
      {/* ── Hero Section ─────────────────────────── */}
      <section className="hero">
        <div className="hero__bg-grid" aria-hidden />
        <div className="hero__glow hero__glow--1" aria-hidden />
        <div className="hero__glow hero__glow--2" aria-hidden />

        <div className="container hero__content">
          <div className="hero__badge badge badge-amber animate-fade-in-up">
            <Mic size={11} />
            AI-Powered Museum Audio Guide · QR Scanner
          </div>

          <h1 className="hero__title animate-fade-in-up animate-fade-in-up-delay-1">
            Thuyết Minh Bảo Tàng
            <br />
            <span className="gradient-text">Quét Mã QR & Đa Ngôn Ngữ</span>
          </h1>

          <p className="hero__desc animate-fade-in-up animate-fade-in-up-delay-2">
            Hệ thống AI tự động dịch nội dung thuyết minh hiện vật sang <strong>13+ ngôn ngữ</strong> và
            tổng hợp giọng đọc tự nhiên. Dễ dàng truy cập từ điện thoại di động mọi lúc mọi nơi.
          </p>

          <div className="hero__actions animate-fade-in-up animate-fade-in-up-delay-3">
            <Link to="/qr-scan" className="btn btn-primary btn-lg">
              <QrCode size={18} />
              Quét Mã QR Hiện Vật
              <ChevronRight size={16} />
            </Link>

            <Link to="/translate" className="btn btn-secondary btn-lg">
              <Headphones size={18} />
              Tự Nhập Thuyết Minh
            </Link>

            <Link to="/qr-codes" className="btn btn-ghost btn-lg">
              Xem Mã QR Mẫu
            </Link>
          </div>

          {/* Stats */}
          <div className="hero__stats animate-fade-in-up" style={{ animationDelay: '0.4s', opacity: 0 }}>
            <div className="hero__stat">
              <span className="hero__stat-value gradient-text">13+</span>
              <span className="hero__stat-label">Ngôn ngữ</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-value gradient-text">QR Scan</span>
              <span className="hero__stat-label">Camera tức thì</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-value gradient-text">Neural</span>
              <span className="hero__stat-label">Giọng đọc AI</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-value gradient-text">Mobile</span>
              <span className="hero__stat-label">Đa thiết bị</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ────────────────────────────── */}
      <section className="section">
        <div className="container">
          <div className="section-header">
            <h2 className="text-3xl font-bold">Tính Năng Nổi Bật</h2>
            <p className="text-sm" style={{ color: 'var(--color-text-secondary)', marginTop: '0.5rem' }}>
              Giải pháp Audio Guide hiện đại cho Bảo tàng Chứng tích Chiến tranh
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

      {/* ── Sample Exhibits ──────────────────────── */}
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="section-header">
            <h2 className="text-3xl font-bold">Hiện Vật Mẫu Nổi Bật</h2>
            <p className="text-sm" style={{ color: 'var(--color-text-secondary)', marginTop: '0.5rem' }}>
              Bấm vào hiện vật để mở màn hình quét hoặc nghe thuyết minh ngay
            </p>
          </div>
          <div className="exhibits-grid">
            {SAMPLE_EXHIBITS.map((exhibit) => (
              <div key={exhibit.id} className="exhibit-card glass-card">
                <div className="exhibit-card__header">
                  <span className="badge badge-amber">{exhibit.id}</span>
                  <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>{exhibit.zone}</span>
                </div>
                <h3 className="exhibit-card__name text-base font-semibold" style={{ margin: '0.75rem 0 0.5rem' }}>
                  {exhibit.name}
                </h3>
                <p className="text-sm" style={{ color: 'var(--color-text-secondary)', lineHeight: 1.6, marginBottom: '1rem' }}>
                  {exhibit.text}
                </p>
                <div className="exhibit-card__langs">
                  {exhibit.langs.map((flag, j) => (
                    <span key={j} className="exhibit-card__lang-flag">{flag}</span>
                  ))}
                  <Link
                    to={`/qr-scan?id=${encodeURIComponent(exhibit.id)}`}
                    className="btn btn-sm btn-primary"
                    style={{ marginLeft: 'auto' }}
                  >
                    Nghe Thuyết Minh →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ────────────────────────────────── */}
      <section className="cta-section">
        <div className="container cta-section__inner">
          <QrCode size={40} style={{ color: 'var(--color-amber-400)', marginBottom: '1rem' }} />
          <h2 className="text-2xl font-bold" style={{ marginBottom: '0.5rem' }}>
            Sẵn sàng khám phá bảo tàng?
          </h2>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)', marginBottom: '1.5rem' }}>
            Bật camera điện thoại, quét mã QR trên hiện vật và chọn ngôn ngữ bạn muốn lắng nghe.
          </p>
          <div className="flex gap-3 flex-wrap justify-center">
            <Link to="/qr-scan" className="btn btn-primary btn-lg">
              <QrCode size={18} />
              Mở Trình Quét QR
            </Link>
            <Link to="/qr-codes" className="btn btn-secondary btn-lg">
              Xem Thư Viện Mã QR
            </Link>
          </div>
        </div>
      </section>
    </main>
  )
}
