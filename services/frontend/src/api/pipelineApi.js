const API_BASE = '/api/v1'

/**
 * Gọi AI Pipeline: Dịch văn bản + Sinh audio
 * @param {string} text - Văn bản tiếng Việt gốc
 * @param {string[]} languages - Danh sách mã ngôn ngữ đích (vd: ['en', 'fr'])
 * @param {string} exhibitId - ID hiện vật (dùng để đặt tên file audio)
 * @returns {Promise<object>} - Kết quả dịch và đường dẫn audio
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
 * Lấy chi tiết một hiện vật theo ID (EX-01, EX-02...)
 */
export async function fetchExhibitById(exhibitId) {
  const response = await fetch(`${API_BASE}/exhibits/${encodeURIComponent(exhibitId)}`)
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `Không tìm thấy hiện vật ${exhibitId}`)
  }
  return response.json()
}

/**
 * Kiểm tra backend có hoạt động không
 */
export async function healthCheck() {
  const response = await fetch('/')
  return response.json()
}
