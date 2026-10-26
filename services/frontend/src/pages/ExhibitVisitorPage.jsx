import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  Play, Pause, RotateCcw, RotateCw, Volume2, Globe, MapPin,
  Calendar, ChevronRight, Sparkles, BookOpen, Check, Share2, AlertCircle
} from 'lucide-react'
import { fetchExhibitByCode, fetchExhibitAudio, reportListeningMetric } from '../api/pipelineApi'
import { LANGUAGES } from '../components/LanguageSelector'
import './ExhibitVisitorPage.css'

export default function ExhibitVisitorPage() {
  const { code } = useParams()
  const navigate = useNavigate()

  // Lấy ngôn ngữ lưu trước đó từ localStorage (BR-07, FR-07)
  const [selectedLang, setSelectedLang] = useState(() => {
    return localStorage.getItem('war_remnants_lang') || 'en'
  })

  const [exhibit, setExhibit] = useState(null)
  const [audioData, setAudioData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [audioLoading, setAudioLoading] = useState(false)
  const [error, setError] = useState(null)
  const [audioError, setAudioError] = useState(null)

  // Audio player state
  const audioRef = useRef(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [playbackRate, setPlaybackRate] = useState(1.0)
  const [showOriginal, setShowOriginal] = useState(false)
  const [currentSentenceId, setCurrentSentenceId] = useState(0)

  // Subtitle auto-scroll ref
  const subtitleContainerRef = useRef(null)
  const sentenceRefs = useRef({})

  // 1. Tải thông tin hiện vật khi `code` thay đổi (≤ 1.5s - NFR-01)
  useEffect(() => {
    let isMounted = true
    setLoading(true)
    setError(null)
    setIsPlaying(false)

    fetchExhibitByCode(code)
      .then((data) => {
        if (!isMounted) return
        setExhibit(data)
        setLoading(false)
      })
      .catch((err) => {
        if (!isMounted) return
        console.error('Lỗi nạp hiện vật:', err)
        setError(err.message || 'Không tìm thấy hiện vật này.')
        setLoading(false)
      })

    return () => { isMounted = false }
  }, [code])

  // 2. Tải bản dịch và file âm thanh khi hiện vật hoặc ngôn ngữ thay đổi
  useEffect(() => {
    if (!exhibit) return
    let isMounted = true
    setAudioLoading(true)
    setAudioError(null)
    setIsPlaying(false)
    setCurrentTime(0)

    // Lưu ngôn ngữ vào localStorage để các lần quét sau tự động nhớ (FR-07)
    localStorage.setItem('war_remnants_lang', selectedLang)

    fetchExhibitAudio(exhibit.code, selectedLang)
      .then((data) => {
        if (!isMounted) return
        setAudioData(data)
        setAudioLoading(false)
        if (audioRef.current) {
          audioRef.current.load()
        }
      })
      .catch((err) => {
        if (!isMounted) return
        console.error('Lỗi tải audio:', err)
        setAudioLoading(false)
        setAudioError('Không thể tải giọng đọc AI. Hãy đảm bảo Backend (start_backend.bat) đang chạy.')
      })

    return () => { isMounted = false }
  }, [exhibit, selectedLang])

  // 3. Quản lý phát âm thanh & cập nhật vị trí phụ đề thời gian thực (FR-16)
  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const handleTimeUpdate = () => {
      const time = audio.currentTime
      setCurrentTime(time)

      // Tìm câu tương ứng với currentTime
      if (audioData?.timestamps_json) {
        const found = audioData.timestamps_json.find(
          (item) => time >= item.start && time < item.end
        )
        if (found && found.id !== currentSentenceId) {
          setCurrentSentenceId(found.id)

          // Cuộn phụ đề mượt mà vào giữa khung nhìn (FR-16)
          const targetEl = sentenceRefs.current[found.id]
          if (targetEl && subtitleContainerRef.current) {
            targetEl.scrollIntoView({
              behavior: 'smooth',
              block: 'center',
            })
          }
        }
      }
    }

    const handleLoadedMetadata = () => {
      setDuration(audio.duration || 0)
    }

    const handleEnded = () => {
      setIsPlaying(false)
      // Báo cáo số liệu nghe ẩn danh khi hoàn thành (FR-20, BR-15)
      if (exhibit) {
        reportListeningMetric(exhibit.code, selectedLang, audio.duration || 0, 'QR_CODE')
      }
    }

    audio.addEventListener('timeupdate', handleTimeUpdate)
    audio.addEventListener('loadedmetadata', handleLoadedMetadata)
    audio.addEventListener('ended', handleEnded)

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate)
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata)
      audio.removeEventListener('ended', handleEnded)
    }
  }, [audioData, currentSentenceId, exhibit, selectedLang])

  // Đổi tốc độ đọc (FR-17)
  const changePlaybackRate = (rate) => {
    setPlaybackRate(rate)
    if (audioRef.current) {
      audioRef.current.playbackRate = rate
    }
  }

  // Bật/tắt phát
  const togglePlay = () => {
    const audio = audioRef.current
    if (!audio) return

    if (isPlaying) {
      audio.pause()
      setIsPlaying(false)
    } else {
      if (!audio.src && audioData?.audio_file_path) {
        audio.src = audioData.audio_file_path
        audio.load()
      }
      audio.play().then(() => {
        setIsPlaying(true)
      }).catch((e) => {
        console.warn('Lỗi autoplay:', e)
        setAudioError('Không thể phát âm thanh: Vui lòng kiểm tra xem Backend (start_backend.bat) đã chạy chưa.')
      })
    }
  }

  // Tua tới / lui 10 giây (FR-17)
  const seekRelative = (seconds) => {
    const audio = audioRef.current
    if (!audio) return
    const newTime = Math.min(Math.max(audio.currentTime + seconds, 0), duration)
    audio.currentTime = newTime
    setCurrentTime(newTime)
  }

  // Chạm vào một câu trong phụ đề để tua thẳng đến câu đó
  const jumpToSentence = (startTime) => {
    const audio = audioRef.current
    if (!audio) return
    audio.currentTime = startTime
    setCurrentTime(startTime)
    if (!isPlaying) {
      audio.play().then(() => setIsPlaying(true)).catch(() => {})
    }
  }

  // Định dạng thời gian (mm:ss)
  const formatTime = (secs) => {
    if (!secs || isNaN(secs)) return '0:00'
    const m = Math.floor(secs / 60)
    const s = Math.floor(secs % 60)
    return `${m}:${s < 10 ? '0' : ''}${s}`
  }

  if (loading) {
    return (
      <div className="visitor-loading-screen">
        <div className="loading-spinner-large">
          <Volume2 size={32} style={{ color: 'var(--color-amber-400)' }} />
        </div>
        <div className="visitor-loading-text">
          <h2 className="text-lg font-bold gradient-text">Đang kết nối hiện vật...</h2>
          <p className="text-xs text-muted">Bảo tàng Chứng tích Chiến tranh TP.HCM</p>
        </div>
      </div>
    )
  }

  if (error || !exhibit) {
    return (
      <div className="container" style={{ padding: '3rem 1rem', textAlign: 'center' }}>
        <div className="glass-card" style={{ padding: '2rem', maxWidth: '480px', margin: '0 auto' }}>
          <h2 className="text-xl font-bold" style={{ color: 'var(--color-error)', marginBottom: '0.5rem' }}>
            Không tìm thấy hiện vật
          </h2>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)', marginBottom: '1.5rem' }}>
            Mã hiện vật <strong>{code}</strong> có thể chưa được kích hoạt hoặc mã QR không hợp lệ.
          </p>
          <Link to="/qr-stands" className="btn btn-primary btn-md">
            Xem danh mục bảng mã QR hiện vật
          </Link>
        </div>
      </div>
    )
  }

  return (
    <main className="visitor-page">
      <div className="visitor-container">
        {/* Header thông tin bảo tàng */}
        <div className="visitor-top-bar">
          <div className="visitor-brand">
            <span className="badge badge-amber">{exhibit.display_code || exhibit.code}</span>
            <span className="visitor-museum-title">Bảo tàng Chứng tích Chiến tranh</span>
          </div>
          <div className="visitor-zone-tag">
            <MapPin size={12} />
            <span>{exhibit.zone}</span>
          </div>
        </div>

        {/* Cảnh báo lỗi âm thanh nếu backend chưa bật */}
        {audioError && (
          <div className="error-box glass-card animate-fade-in-up" style={{ padding: '10px 14px' }}>
            <AlertCircle size={18} style={{ color: 'var(--color-error)', flexShrink: 0 }} />
            <span className="text-xs" style={{ color: '#fca5a5' }}>{audioError}</span>
          </div>
        )}

        {/* Ảnh bìa hiện vật */}
        <div className="visitor-hero-image-wrapper">
          <img
            src={exhibit.thumbnail_url}
            alt={exhibit.title}
            className="visitor-hero-image"
          />
          <div className="visitor-hero-gradient" />
          <div className="visitor-hero-info">
            {exhibit.period && (
              <span className="visitor-period-badge">
                <Calendar size={12} /> Thời kỳ: {exhibit.period}
              </span>
            )}
            <h1 className="visitor-exhibit-title">
              {selectedLang === 'vi' ? exhibit.title : (audioData?.translated_title || exhibit.title_en || exhibit.title)}
            </h1>
          </div>
        </div>

        {/* Bộ chọn ngôn ngữ nhanh 15+ thứ tiếng (FR-07) */}
        <div className="visitor-lang-bar">
          <div className="visitor-lang-label">
            <Globe size={14} style={{ color: 'var(--color-amber-400)' }} />
            <span>Ngôn ngữ thuyết minh:</span>
          </div>
          <div className="visitor-lang-pills">
            {LANGUAGES.map((lang) => (
              <button
                key={lang.code}
                type="button"
                className={`visitor-lang-pill ${selectedLang === lang.code ? 'active' : ''}`}
                onClick={() => setSelectedLang(lang.code)}
              >
                <span className="visitor-lang-flag">{lang.flag}</span>
                <span className="visitor-lang-name">{lang.nativeName}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Nút to bản: "Chạm để bắt đầu nghe thuyết minh" (BR-10) */}
        {!isPlaying && currentTime === 0 && (
          <div className="visitor-big-play-cta animate-fade-in-up">
            <button
              type="button"
              className="btn btn-primary btn-lg visitor-big-play-btn"
              onClick={togglePlay}
              disabled={audioLoading}
            >
              {audioLoading ? (
                <>
                  <span className="spinner" />
                  <span>Đang tổng hợp giọng đọc AI...</span>
                </>
              ) : (
                <>
                  <Play size={22} fill="currentColor" />
                  <span>Chạm để bắt đầu nghe thuyết minh</span>
                </>
              )}
            </button>
            <p className="text-xs text-muted" style={{ textAlign: 'center', marginTop: '6px' }}>
              Giọng đọc Neural AI chuẩn ngữ điệu · Phụ đề chạy đồng bộ
            </p>
          </div>
        )}

        {/* Trình phát âm thanh phân đoạn & Điều khiển (FR-15, FR-17) */}
        <div className="visitor-player-card glass-card">
          <audio
            ref={audioRef}
            src={audioData?.audio_file_path}
            preload="auto"
          />

          {/* Thanh tua thời gian */}
          <div className="visitor-progress-row">
            <span className="visitor-time">{formatTime(currentTime)}</span>
            <input
              type="range"
              min={0}
              max={duration || 100}
              value={currentTime}
              onChange={(e) => {
                const val = parseFloat(e.target.value)
                if (audioRef.current) audioRef.current.currentTime = val
                setCurrentTime(val)
              }}
              className="visitor-progress-bar"
            />
            <span className="visitor-time">{formatTime(duration)}</span>
          </div>

          {/* Cụm nút điều khiển chính: -10s, Play/Pause, +10s, Tốc độ */}
          <div className="visitor-controls-row">
            {/* Tốc độ đọc (0.8x, 1.0x, 1.2x) */}
            <div className="visitor-rate-group">
              {[0.8, 1.0, 1.2].map((rate) => (
                <button
                  key={rate}
                  type="button"
                  className={`visitor-rate-btn ${playbackRate === rate ? 'active' : ''}`}
                  onClick={() => changePlaybackRate(rate)}
                >
                  {rate}x
                </button>
              ))}
            </div>

            {/* Cụm phát nhạc */}
            <div className="visitor-main-btns">
              <button
                type="button"
                className="visitor-seek-btn"
                onClick={() => seekRelative(-10)}
                title="Tua lùi 10 giây"
              >
                <RotateCcw size={18} />
                <span className="seek-text">10</span>
              </button>

              <button
                type="button"
                className="visitor-play-circle-btn"
                onClick={togglePlay}
                disabled={audioLoading}
              >
                {audioLoading ? (
                  <span className="spinner" />
                ) : isPlaying ? (
                  <Pause size={24} fill="currentColor" />
                ) : (
                  <Play size={24} fill="currentColor" style={{ marginLeft: '3px' }} />
                )}
              </button>

              <button
                type="button"
                className="visitor-seek-btn"
                onClick={() => seekRelative(10)}
                title="Tua tới 10 giây"
              >
                <RotateCw size={18} />
                <span className="seek-text">10</span>
              </button>
            </div>

            {/* Nút chuyển đổi đối chiếu Tiếng Việt / Bản dịch */}
            <button
              type="button"
              className={`visitor-toggle-orig-btn ${showOriginal ? 'active' : ''}`}
              onClick={() => setShowOriginal(!showOriginal)}
              title="Xem bản gốc tiếng Việt"
            >
              <BookOpen size={16} />
              <span className="hide-on-mobile">{showOriginal ? 'Bản dịch' : 'Bản gốc'}</span>
            </button>
          </div>
        </div>

        {/* Khung Phụ Đề Cuộn Đồng Bộ Theo Giọng Đọc (FR-16) */}
        <div className="visitor-subtitles-section glass-card">
          <div className="visitor-subtitles-header">
            <div className="flex items-center gap-2">
              <Sparkles size={16} style={{ color: 'var(--color-amber-400)' }} />
              <span className="text-sm font-semibold">
                {showOriginal ? 'Nội dung tiếng Việt gốc' : 'Phụ đề thuyết minh (Chạm câu để tua)'}
              </span>
            </div>
            <span className="text-xs text-muted">
              {showOriginal ? 'Tiếng Việt' : LANGUAGES.find(l => l.code === selectedLang)?.nativeName}
            </span>
          </div>

          <div className="visitor-subtitles-body" ref={subtitleContainerRef}>
            {showOriginal ? (
              <p className="visitor-original-paragraph">
                {exhibit.original_text}
              </p>
            ) : audioData?.timestamps_json && audioData.timestamps_json.length > 0 ? (
              <div className="visitor-sentences-list">
                {audioData.timestamps_json.map((sentence) => {
                  const isActive = currentSentenceId === sentence.id && isPlaying
                  return (
                    <p
                      key={sentence.id}
                      ref={(el) => (sentenceRefs.current[sentence.id] = el)}
                      className={`visitor-sentence ${isActive ? 'visitor-sentence--active' : ''}`}
                      onClick={() => jumpToSentence(sentence.start)}
                    >
                      {sentence.text}
                    </p>
                  )
                })}
              </div>
            ) : (
              <p className="visitor-plain-text">
                {audioData?.translated_text || exhibit.original_text}
              </p>
            )}
          </div>
        </div>

        {/* Gợi ý hiện vật kế tiếp trong lộ trình (UC2) */}
        {exhibit.next_code && (
          <div className="visitor-next-exhibit-card glass-card animate-fade-in-up">
            <div className="visitor-next-info">
              <span className="text-xs text-muted uppercase tracking-wider">Điểm tham quan kế tiếp</span>
              <h4 className="text-sm font-bold gradient-text">Tiếp tục lộ trình bảo tàng</h4>
            </div>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => navigate(`/exhibit/${exhibit.next_code}`)}
            >
              <span>Xem hiện vật tiếp</span>
              <ChevronRight size={16} />
            </button>
          </div>
        )}

        {/* Footer bảo tàng */}
        <div className="visitor-footer">
          <p className="text-xs text-muted">
            Hệ thống Audio Guide Tự Động · WarRemnantsVoice MVP v1.0
          </p>
          <p className="text-xs text-muted" style={{ marginTop: '2px' }}>
            Không yêu cầu tải ứng dụng · Không thu thập dữ liệu cá nhân
          </p>
        </div>
      </div>
    </main>
  )
}
