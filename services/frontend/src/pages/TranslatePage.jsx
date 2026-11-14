import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Headphones, Loader2, AlertCircle, RotateCcw, Sparkles, ChevronDown, ChevronUp
} from 'lucide-react'
import LanguageSelector, { LANGUAGES } from '../components/LanguageSelector'
import TranslationCard from '../components/TranslationCard'
import { processAudio } from '../api/pipelineApi'
import './TranslatePage.css'

const EXAMPLE_TEXTS = [
  'Trực thăng UH-1 Iroquois được sử dụng rộng rãi trong Chiến tranh Việt Nam bởi quân đội Hoa Kỳ từ năm 1962 đến 1975. Đây là một trong những biểu tượng gắn liền với cuộc chiến trong ký ức của nhiều thế hệ.',
  'Bảo tàng Chứng tích Chiến tranh tại Thành phố Hồ Chí Minh lưu giữ hơn 20.000 tài liệu, hiện vật và hình ảnh về cuộc kháng chiến của nhân dân Việt Nam.',
  'Chiến dịch Hồ Chí Minh diễn ra từ ngày 26 tháng 4 đến 30 tháng 4 năm 1975, là đỉnh cao của cuộc Tổng tấn công Mùa Xuân 1975, kết thúc chiến tranh và thống nhất đất nước.',
]

export default function TranslatePage() {
  const [searchParams] = useSearchParams()

  const [text, setText] = useState(() => searchParams.get('text') || EXAMPLE_TEXTS[0])
  const [selectedLang, setSelectedLang] = useState('en')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState([])
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])
  const [showHistory, setShowHistory] = useState(false)

  // Nếu có ?text= param từ trang chủ → auto-fill
  useEffect(() => {
    const paramText = searchParams.get('text')
    if (paramText) setText(paramText)
  }, [searchParams])

  const handleTranslate = async () => {
    if (!text.trim()) {
      setError('Vui lòng nhập nội dung cần dịch!')
      return
    }

    setIsLoading(true)
    setError(null)
    setResults([])

    try {
      const data = await processAudio(text, [selectedLang])

      if (data.results && data.results.length > 0) {
        setResults(data.results)
        // Lưu vào lịch sử
        const langInfo = LANGUAGES.find((l) => l.code === selectedLang)
        setHistory((prev) => [
          {
            id: data.task_id,
            text: text.slice(0, 60) + (text.length > 60 ? '...' : ''),
            lang: `${langInfo?.flag} ${langInfo?.nativeName}`,
            timestamp: new Date().toLocaleTimeString('vi-VN'),
            results: data.results,
          },
          ...prev.slice(0, 9), // Giữ tối đa 10 mục
        ])
      } else {
        setError('API trả về kết quả rỗng. Kiểm tra lại backend.')
      }
    } catch (err) {
      setError(err.message || 'Lỗi không xác định. Đảm bảo backend đang chạy tại localhost:8000.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleTranslate()
    }
  }

  const handleExampleClick = (example) => {
    setText(example)
    setResults([])
    setError(null)
  }

  const handleReset = () => {
    setText('')
    setResults([])
    setError(null)
  }

  return (
    <main className="translate-page">
      <div className="container">
        <div className="translate-page__header">
          <h1 className="text-3xl font-bold">
            <span className="gradient-text">Thuyết Minh</span> Đa Ngôn Ngữ
          </h1>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)', marginTop: '0.25rem' }}>
            Dịch thuật AI + Sinh giọng đọc Neural — hỗ trợ 13 ngôn ngữ
          </p>
        </div>

        <div className="translate-page__layout">
          {/* ── LEFT: Input panel ── */}
          <div className="translate-panel glass-card">
            {/* Text input */}
            <div className="translate-panel__section">
              <div className="translate-panel__label-row">
                <label className="form-label" htmlFor="sourceText">
                  Nội dung tiếng Việt
                </label>
                <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                  {text.length} / 4900 ký tự
                </span>
              </div>
              <textarea
                id="sourceText"
                className="form-textarea"
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Nhập nội dung thuyết minh tiếng Việt..."
                maxLength={4900}
                rows={6}
              />
              <p className="text-xs" style={{ color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
                Gợi ý: nhấn <kbd className="kbd">Ctrl+Enter</kbd> để dịch nhanh
              </p>
            </div>

            {/* Examples */}
            <div className="translate-panel__section">
              <label className="form-label">Ví dụ nhanh</label>
              <div className="examples-list">
                {EXAMPLE_TEXTS.map((ex, i) => (
                  <button
                    key={i}
                    className="example-btn"
                    onClick={() => handleExampleClick(ex)}
                    type="button"
                  >
                    <Sparkles size={12} style={{ flexShrink: 0 }} />
                    <span>{ex.slice(0, 55)}...</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Language selector */}
            <div className="translate-panel__section">
              <label className="form-label">Chọn ngôn ngữ đích</label>
              <LanguageSelector selected={selectedLang} onChange={setSelectedLang} />
            </div>

            {/* Action buttons */}
            <div className="translate-panel__actions">
              <button
                id="btn-translate"
                className="btn btn-primary btn-lg"
                onClick={handleTranslate}
                disabled={isLoading || !text.trim()}
                style={{ flex: 1 }}
              >
                {isLoading ? (
                  <>
                    <span className="spinner" />
                    AI đang xử lý...
                  </>
                ) : (
                  <>
                    <Headphones size={18} />
                    Dịch & Tạo Giọng Đọc
                  </>
                )}
              </button>
              <button
                className="btn btn-ghost"
                onClick={handleReset}
                disabled={isLoading}
                title="Xóa trắng"
              >
                <RotateCcw size={16} />
              </button>
            </div>
          </div>

          {/* ── RIGHT: Results panel ── */}
          <div className="results-panel">
            {/* Error */}
            {error && (
              <div className="error-box glass-card animate-fade-in-up">
                <AlertCircle size={18} style={{ color: 'var(--color-error)', flexShrink: 0 }} />
                <div>
                  <div className="text-sm font-semibold" style={{ color: 'var(--color-error)' }}>
                    Lỗi xử lý
                  </div>
                  <div className="text-xs" style={{ color: 'var(--color-text-secondary)', marginTop: '0.25rem' }}>
                    {error}
                  </div>
                </div>
              </div>
            )}

            {/* Loading skeleton */}
            {isLoading && (
              <div className="loading-card glass-card animate-fade-in-up">
                <div className="loading-card__inner">
                  <div className="loading-spinner-large">
                    <Headphones size={24} style={{ color: 'var(--color-amber-500)' }} />
                  </div>
                  <div>
                    <div className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
                      AI Pipeline đang xử lý...
                    </div>
                    <div className="text-xs" style={{ color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
                      Dịch thuật → Áp dụng Glossary → Tổng hợp giọng đọc
                    </div>
                  </div>
                </div>
                <div className="loading-steps">
                  {['Google Translate', 'Glossary Lịch Sử', 'Edge TTS Neural'].map((step, i) => (
                    <div key={i} className="loading-step">
                      <span className="spinner" style={{ width: '12px', height: '12px' }} />
                      <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>{step}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Results */}
            {results.length > 0 && (
              <div className="results-list">
                {results.map((result, i) => (
                  <TranslationCard key={result.language + i} result={result} index={i} />
                ))}
              </div>
            )}

            {/* Empty state */}
            {!isLoading && !error && results.length === 0 && (
              <div className="empty-state glass-card">
                <Headphones size={40} style={{ color: 'var(--color-text-muted)' }} />
                <p className="text-sm" style={{ color: 'var(--color-text-muted)', textAlign: 'center' }}>
                  Nhập nội dung tiếng Việt, chọn ngôn ngữ và nhấn{' '}
                  <strong style={{ color: 'var(--color-text-secondary)' }}>Dịch & Tạo Giọng Đọc</strong>
                </p>
              </div>
            )}

            {/* History */}
            {history.length > 0 && (
              <div className="history-section">
                <button
                  className="history-toggle btn btn-ghost btn-sm"
                  onClick={() => setShowHistory((v) => !v)}
                  type="button"
                >
                  {showHistory ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  Lịch sử ({history.length})
                </button>
                {showHistory && (
                  <div className="history-list">
                    {history.map((item) => (
                      <button
                        key={item.id}
                        className="history-item"
                        onClick={() => setResults(item.results)}
                        type="button"
                      >
                        <div className="text-xs font-semibold" style={{ color: 'var(--color-text-amber)' }}>
                          {item.lang}
                        </div>
                        <div className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                          {item.text}
                        </div>
                        <div className="text-xs" style={{ color: 'var(--color-text-muted)', marginTop: '2px' }}>
                          {item.timestamp}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}
