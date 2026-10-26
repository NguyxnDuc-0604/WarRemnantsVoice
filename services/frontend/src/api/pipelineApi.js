const API_BASE = '/api/v1'

/**
 * Lấy danh sách tất cả hiện vật mẫu từ backend
 */
export async function fetchExhibits() {
  const response = await fetch(`${API_BASE}/exhibits`)
  if (!response.ok) {
    throw new Error(`Không thể lấy danh sách hiện vật: ${response.status}`)
  }
  return response.json()
}

/**
 * Lấy chi tiết một hiện vật theo mã code (UH1-BELL, T54-390, EX-01...)
 */
export async function fetchExhibitByCode(identifier) {
  const response = await fetch(`${API_BASE}/exhibits/${encodeURIComponent(identifier)}`)
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `Không tìm thấy hiện vật '${identifier}'`)
  }
  return response.json()
}

/**
 * Lấy bản dịch, file audio MP3 và mốc thời gian phụ đề JSON cho một hiện vật
 * @param {string} identifier - Mã hiện vật (UH1-BELL, EX-01...)
 * @param {string} lang - Mã ngôn ngữ (en, fr, ja, ko...)
 */
export async function fetchExhibitAudio(identifier, lang = 'en') {
  const response = await fetch(`${API_BASE}/exhibits/${encodeURIComponent(identifier)}/audio?lang=${encodeURIComponent(lang)}`)
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `Lỗi tải âm thanh thuyết minh (${response.status})`)
  }
  return response.json()
}

/**
 * Báo cáo thống kê lượt nghe ẩn danh (FR-20, BR-15)
 */
export async function reportListeningMetric(exhibitCode, langCode, duration, triggerType = 'QR_CODE') {
  try {
    await fetch(`${API_BASE}/metrics/listen`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        exhibit_code: exhibitCode,
        language_code: langCode,
        listened_duration: Math.round(duration),
        trigger_type: triggerType
      })
    })
  } catch (e) {
    console.warn('Không thể ghi nhận metric:', e)
  }
}

/**
 * Gọi AI Pipeline tự do: Dịch văn bản + Sinh audio
 */
export async function processAudio(text, languages, exhibitId = null) {
  const timestamp = Date.now()
  const payload = {
    task_id: `task-${timestamp}`,
    exhibit_id: exhibitId || `exhibit-${timestamp}`,
    original_text: text,
    target_languages: languages,
  }

  const response = await fetch(`${API_BASE}/process-audio`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `Lỗi server: ${response.status}`)
  }

  return response.json()
}

/**
 * Alias cho fetchExhibitByCode
 */
export const fetchExhibitById = fetchExhibitByCode

/**
 * Kiểm tra backend có hoạt động không
 */
export async function healthCheck() {
  const response = await fetch('/')
  return response.json()
}
