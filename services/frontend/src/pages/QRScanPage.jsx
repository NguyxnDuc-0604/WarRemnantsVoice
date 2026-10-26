import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import {
  QrCode, Headphones, Sparkles, MapPin, Calendar, ExternalLink,
  ChevronRight, RefreshCw, Volume2, Globe2, BookOpen
} from 'lucide-react'
import QRScanner from '../components/QRScanner'
import LanguageSelector, { LANGUAGES } from '../components/LanguageSelector'
import AudioPlayer from '../components/AudioPlayer'
import { fetchExhibits, fetchExhibitById, processAudio } from '../api/pipelineApi'
import './QRScanPage.css'

export default function QRScanPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  const [selectedLang, setSelectedLang] = useState('en')
  const [currentExhibit, setCurrentExhibit] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [processStep, setProcessStep] = useState('')
  const [translationResult, setTranslationResult] = useState(null)
  const [error, setError] = useState(null)
  const [availableExhibits, setAvailableExhibits] = useState([])

  // Lấy danh sách hiện vật mẫu
  useEffect(() => {
    fetchExhibits()
      .then((data) => setAvailableExhibits(data))
      .catch((err) => console.warn('Không tải được danh sách hiện vật:', err))
  }, [])

  // Nếu URL có ?id=EX-01 thì tự động nạp hiện vật đó
  useEffect(() => {
    const exhibitParam = searchParams.get('id') || searchParams.get('exhibit')
    if (exhibitParam) {
      handleExhibitSelected(exhibitParam)
    }
  }, [searchParams])

  // Xử lý khi quét trúng mã QR
  const handleScanSuccess = async (rawQrText) => {
    setError(null)
    const text = rawQrText.trim()

    // 1. Kiểm tra nếu là URL có param ?id= hoặc ?exhibit=
    let exhibitId = null
    try {
      if (text.startsWith('http://') || text.startsWith('https://')) {
        const url = new URL(text)
        exhibitId = url.searchParams.get('id') || url.searchParams.get('exhibit')
      }
    } catch (e) {}

    // 2. Nếu là format ID trực tiếp như EX-01, EX-02...
    if (!exhibitId && /^EX-\d+/i.test(text)) {
      exhibitId = text.toUpperCase()
    }

    if (exhibitId) {
      await handleExhibitSelected(exhibitId)
    } else {
      // Mã QR chứa đoạn văn bản tự do
      await handleCustomTextScan(text)
    }
  }

  // Nạp thông tin hiện vật từ ID và tự động dịch
  const handleExhibitSelected = async (id) => {
    setError(null)
    setIsProcessing(true)
    setTranslationResult(null)
    setProcessStep('Đang tìm thông tin hiện vật...')

    try {
      const exhibit = await fetchExhibitById(id)
      setCurrentExhibit(exhibit)

      // Cập nhật URL mà không reload trang
      setSearchParams({ id: exhibit.id }, { replace: true })

      // Tự động dịch và sinh giọng thuyết minh
      setProcessStep(`Dịch sang ${LANGUAGES.find((l) => l.code === selectedLang)?.nativeName || selectedLang}...`)
      const pipelineData = await processAudio(exhibit.original_text, [selectedLang], exhibit.id)

      if (pipelineData.results && pipelineData.results.length > 0) {
        setTranslationResult(pipelineData.results[0])
      }
    } catch (err) {
      console.error(err)
      setError(err.message || 'Không thể xử lý hiện vật này.')
    } finally {
      setIsProcessing(false)
      setProcessStep('')
    }
  }

  // Quét trúng đoạn văn bản tự do
  const handleCustomTextScan = async (text) => {
    setError(null)
    setIsProcessing(true)
    setTranslationResult(null)
    setCurrentExhibit({
      id: 'CUSTOM-QR',
      name: 'Nội dung quét từ mã QR',
      zone: 'Hiện vật quét tự do',
      original_text: text,
      image_url: null,
    })

    try {
      setProcessStep('Đang xử lý dịch thuật & sinh giọng đọc AI...')
      const pipelineData = await processAudio(text, [selectedLang], 'QR-CUSTOM')
      if (pipelineData.results && pipelineData.results.length > 0) {
        setTranslationResult(pipelineData.results[0])
      }
    } catch (err) {
      setError(err.message || 'Lỗi xử lý văn bản từ mã QR.')
    } finally {
      setIsProcessing(false)
      setProcessStep('')
    }
  }

  // Đổi ngôn ngữ đích -> tự động dịch lại nếu đang xem hiện vật
  const handleLanguageChange = async (newLang) => {
    setSelectedLang(newLang)
    if (currentExhibit) {
      setIsProcessing(true)
      setError(null)
      setProcessStep(`Đang dịch sang ${LANGUAGES.find((l) => l.code === newLang)?.nativeName || newLang}...`)
      try {
        const pipelineData = await processAudio(currentExhibit.original_text, [newLang], currentExhibit.id)
        if (pipelineData.results && pipelineData.results.length > 0) {
          setTranslationResult(pipelineData.results[0])
        }
      } catch (err) {
        setError(err.message || 'Lỗi khi dịch ngôn ngữ mới.')
      } finally {
        setIsProcessing(false)
        setProcessStep('')
      }
    }
  }

  return (
    <main className="qr-scan-page">
      <div className="container">
        {/* Header giới thiệu */}
        <div className="qr-page__header">
          <div className="qr-page__title-row">
            <div>
              <div className="badge badge-amber" style={{ marginBottom: '0.5rem' }}>
                <QrCode size={12} />
                <span>Audio Guide Tự Động</span>
              </div>
              <h1 className="text-3xl font-bold">
                Quét Mã QR <span className="gradient-text">Hiện Vật</span>
              </h1>
              <p className="text-sm" style={{ color: 'var(--color-text-secondary)', marginTop: '0.25rem' }}>
                Hướng camera điện thoại vào bảng mã QR tại hiện vật để nghe thuyết minh tức thì
              </p>
            </div>

            <Link to="/qr-codes" className="btn btn-secondary btn-sm qr-codes-link-btn">
              <BookOpen size={16} />
              <span>Xem Thư Viện Mã QR Mẫu</span>
              <ExternalLink size={12} />
            </Link>
          </div>
        </div>

        {/* Bố cục chính 2 cột (hoặc 1 cột trên mobile) */}
        <div className="qr-page__grid">
          {/* ── CỘT TRÁI: Scanner & Chọn Ngôn Ngữ ── */}
          <div className="qr-page__left-col">
            {/* Bộ quét Camera QR */}
            <QRScanner onScanSuccess={handleScanSuccess} isActive={true} />

            {/* Chọn ngôn ngữ thuyết minh */}
            <div className="qr-lang-picker glass-card">
              <div className="qr-lang-picker__header">
                <div className="flex items-center gap-2">
                  <Globe2 size={16} style={{ color: 'var(--color-amber-400)' }} />
                  <span className="text-sm font-semibold">Ngôn ngữ thuyết minh</span>
                </div>
                <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                  {LANGUAGES.find((l) => l.code === selectedLang)?.nativeName}
                </span>
              </div>
              <LanguageSelector selected={selectedLang} onChange={handleLanguageChange} />
            </div>

            {/* Danh sách hiện vật mẫu bấm để quét mô phỏng nhanh */}
            <div className="quick-exhibits glass-card">
              <div className="quick-exhibits__header">
                <Sparkles size={16} style={{ color: 'var(--color-amber-400)' }} />
                <span className="text-sm font-semibold">Hiện vật mẫu (Bấm để thử nghiệm ngay)</span>
              </div>
              <p className="text-xs" style={{ color: 'var(--color-text-muted)', marginBottom: '0.75rem' }}>
                Không cần in giấy, bấm vào hiện vật bất kỳ bên dưới để trải nghiệm ngay:
              </p>
              <div className="quick-exhibits__list">
                {availableExhibits.map((ex) => (
                  <button
                    key={ex.id}
                    type="button"
                    className={`quick-exhibit-btn ${currentExhibit?.id === ex.id ? 'active' : ''}`}
                    onClick={() => handleExhibitSelected(ex.id)}
                    disabled={isProcessing}
                  >
                    <span className="badge badge-amber">{ex.id}</span>
                    <span className="quick-exhibit-name">{ex.name}</span>
                    <ChevronRight size={14} style={{ marginLeft: 'auto', opacity: 0.5 }} />
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* ── CỘT PHẢI: Kết quả thuyết minh & Audio Player ── */}
          <div className="qr-page__right-col">
            {/* Đang xử lý */}
            {isProcessing && (
              <div className="qr-processing-card glass-card animate-fade-in-up">
                <div className="loading-spinner-large">
                  <Headphones size={24} style={{ color: 'var(--color-amber-400)' }} />
                </div>
                <div className="qr-processing__info">
                  <div className="text-sm font-semibold gradient-text">
                    {processStep || 'AI đang xử lý thuyết minh...'}
                  </div>
                  <div className="text-xs" style={{ color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
                    Google Translator · Historical Glossary · Microsoft Edge TTS Neural
                  </div>
                </div>
              </div>
            )}

            {/* Lỗi */}
            {error && (
              <div className="error-box glass-card animate-fade-in-up">
                <span className="text-sm font-semibold" style={{ color: 'var(--color-error)' }}>
                  Lỗi: {error}
                </span>
              </div>
            )}

            {/* Thẻ Chi tiết Hiện vật & Thuyết minh */}
            {currentExhibit && (
              <div className="exhibit-detail-card glass-card animate-fade-in-up">
                {/* Ảnh hiện vật nếu có */}
                {currentExhibit.image_url && (
                  <div className="exhibit-detail__cover">
                    <img
                      src={currentExhibit.image_url}
                      alt={currentExhibit.name}
                      className="exhibit-detail__img"
                      loading="lazy"
                    />
                    <div className="exhibit-detail__cover-overlay">
                      <span className="badge badge-amber">{currentExhibit.id}</span>
                      {currentExhibit.period && (
                        <span className="badge" style={{ background: 'rgba(0,0,0,0.6)', color: '#fff' }}>
                          <Calendar size={11} /> {currentExhibit.period}
                        </span>
                      )}
                    </div>
                  </div>
                )}

                <div className="exhibit-detail__body">
                  <div className="exhibit-detail__meta">
                    <h2 className="text-xl font-bold">{currentExhibit.name}</h2>
                    {currentExhibit.zone && (
                      <div className="exhibit-detail__zone">
                        <MapPin size={13} style={{ color: 'var(--color-amber-400)' }} />
                        <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                          {currentExhibit.zone}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Trình phát Audio Thuyết Minh */}
                  {translationResult && (
                    <div className="exhibit-detail__audio-section">
                      <div className="audio-section__header">
                        <Volume2 size={16} style={{ color: 'var(--color-amber-400)' }} />
                        <span className="text-xs font-semibold uppercase tracking-wider">
                          Audio Thuyết Minh ({LANGUAGES.find((l) => l.code === selectedLang)?.nativeName})
                        </span>
                      </div>
                      <AudioPlayer
                        audioUrl={translationResult.audio_file_path}
                        title={`${currentExhibit.name} (${selectedLang.toUpperCase()})`}
                      />
                    </div>
                  )}

                  {/* Nội dung thuyết minh dịch thuật */}
                  {translationResult && (
                    <div className="exhibit-detail__trans-box">
                      <div className="text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--color-text-amber)', marginBottom: '0.25rem' }}>
                        Nội dung thuyết minh dịch:
                      </div>
                      <p className="exhibit-detail__trans-text">
                        {translationResult.translated_text}
                      </p>
                    </div>
                  )}

                  {/* Bản gốc tiếng Việt */}
                  <div className="exhibit-detail__original-box">
                    <div className="text-xs font-semibold" style={{ color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>
                      Bản gốc tiếng Việt:
                    </div>
                    <p className="text-xs" style={{ color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                      {currentExhibit.original_text}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Trạng thái chưa quét */}
            {!currentExhibit && !isProcessing && (
              <div className="qr-page__empty-card glass-card">
                <QrCode size={48} style={{ color: 'var(--color-text-muted)', opacity: 0.6 }} />
                <h3 className="text-base font-semibold" style={{ color: 'var(--color-text-primary)' }}>
                  Chưa quét hiện vật nào
                </h3>
                <p className="text-xs" style={{ color: 'var(--color-text-muted)', textAlign: 'center', maxWidth: '320px' }}>
                  Quét mã QR tại bảo tàng bằng camera điện thoại hoặc chọn một hiện vật mẫu ở bên trái để nghe thuyết minh.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}
