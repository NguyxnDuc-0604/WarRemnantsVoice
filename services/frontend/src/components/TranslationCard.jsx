import AudioPlayer from './AudioPlayer'
import { LANGUAGES } from './LanguageSelector'
import { FileAudio, Quote } from 'lucide-react'
import './TranslationCard.css'

/**
 * TranslationCard — hiển thị kết quả dịch + audio player cho 1 ngôn ngữ
 */
export default function TranslationCard({ result, index }) {
  const langInfo = LANGUAGES.find((l) => l.code === result.language)
  const langLabel = langInfo ? `${langInfo.flag} ${langInfo.nativeName}` : result.language

  // Build full URL for audio — src starts with "output/..."
  const audioSrc = result.audio_file_path
    ? `/${result.audio_file_path}?t=${Date.now()}`
    : null

  return (
    <div
      className="translation-card animate-fade-in-up"
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      {/* Header */}
      <div className="translation-card__header">
        <div className="translation-card__lang">
          <span className="translation-card__flag">{langInfo?.flag || '🌐'}</span>
          <div>
            <div className="translation-card__lang-name text-sm font-semibold">
              {langInfo?.label || result.language}
            </div>
            <div className="translation-card__lang-native text-xs" style={{ color: 'var(--color-text-muted)' }}>
              {langInfo?.nativeName}
            </div>
          </div>
        </div>
        <span className="badge badge-green">Hoàn thành</span>
      </div>

      {/* Translated text */}
      <div className="translation-card__text">
        <Quote size={14} className="translation-card__quote-icon" />
        <p className="text-sm" style={{ color: 'var(--color-text-secondary)', lineHeight: 1.7 }}>
          {result.translated_text}
        </p>
      </div>

      {/* Audio Player */}
      {audioSrc ? (
        <div className="translation-card__audio">
          <div className="translation-card__audio-label">
            <FileAudio size={13} />
            <span className="text-xs font-semibold" style={{ color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Audio thuyết minh
            </span>
          </div>
          <AudioPlayer src={audioSrc} language={result.language} langLabel={langLabel} />
        </div>
      ) : (
        <div className="translation-card__no-audio text-xs" style={{ color: 'var(--color-text-muted)' }}>
          Không có file audio
        </div>
      )}
    </div>
  )
}
