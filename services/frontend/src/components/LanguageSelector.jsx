import './LanguageSelector.css'

export const LANGUAGES = [
  { code: 'en',    label: 'English',    flag: '🇬🇧', nativeName: 'English' },
  { code: 'fr',    label: 'Français',   flag: '🇫🇷', nativeName: 'Français' },
  { code: 'ja',    label: 'Japanese',   flag: '🇯🇵', nativeName: '日本語' },
  { code: 'ko',    label: 'Korean',     flag: '🇰🇷', nativeName: '한국어' },
  { code: 'zh-CN', label: 'Chinese',    flag: '🇨🇳', nativeName: '中文' },
  { code: 'de',    label: 'Deutsch',    flag: '🇩🇪', nativeName: 'Deutsch' },
  { code: 'es',    label: 'Spanish',    flag: '🇪🇸', nativeName: 'Español' },
  { code: 'it',    label: 'Italian',    flag: '🇮🇹', nativeName: 'Italiano' },
  { code: 'ru',    label: 'Russian',    flag: '🇷🇺', nativeName: 'Русский' },
  { code: 'th',    label: 'Thai',       flag: '🇹🇭', nativeName: 'ภาษาไทย' },
  { code: 'ar',    label: 'Arabic',     flag: '🇸🇦', nativeName: 'العربية' },
  { code: 'pt',    label: 'Portuguese', flag: '🇧🇷', nativeName: 'Português' },
  { code: 'vi',    label: 'Vietnamese', flag: '🇻🇳', nativeName: 'Tiếng Việt' },
]

/**
 * LanguageSelector — chọn ngôn ngữ đích để dịch & TTS
 */
export default function LanguageSelector({ selected, onChange }) {
  return (
    <div className="lang-selector">
      <div className="lang-selector__grid">
        {LANGUAGES.map((lang) => (
          <button
            key={lang.code}
            className={`lang-selector__item ${selected === lang.code ? 'lang-selector__item--active' : ''}`}
            onClick={() => onChange(lang.code)}
            title={lang.label}
            type="button"
          >
            <span className="lang-selector__flag">{lang.flag}</span>
            <span className="lang-selector__name">{lang.nativeName}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
