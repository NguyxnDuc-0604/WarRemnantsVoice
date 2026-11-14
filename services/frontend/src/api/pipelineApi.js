const API_BASE = '/api/v1'

/**
 * Lấy danh sách tất cả hiện vật từ backend
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
 * Gửi tín hiệu Heartbeat ping để thống kê người đang online (CCU)
 */
export async function sendHeartbeat(visitorId, exhibitCode = 'HOME', languageCode = 'en', isPlaying = false, deviceType = 'Mobile') {
  try {
    const response = await fetch(`${API_BASE}/metrics/heartbeat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        visitor_id: visitorId,
        exhibit_code: exhibitCode,
        language_code: languageCode,
        is_playing: isPlaying,
        device_type: deviceType,
      })
    })
    return response.json()
  } catch (e) {
    // Heartbeat chạy ngầm, không ngắt luồng UI
    return null
  }
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
 * Lấy toàn bộ số liệu thống kê thời gian thực cho trang Admin Dashboard
 */
export async function fetchAdminStats() {
  const response = await fetch(`${API_BASE}/admin/dashboard-stats`)
  if (!response.ok) {
    throw new Error(`Lỗi tải dữ liệu thống kê Admin: ${response.status}`)
  }
  return response.json()
}

/**
 * Admin: Thêm hiện vật mới và tự động tạo mã QR
 */
export async function createExhibit(data) {
  const response = await fetch(`${API_BASE}/admin/exhibits`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Không thể tạo hiện vật mới.')
  }
  return response.json()
}

/**
 * Admin: Xóa hiện vật
 */
/**
 * Admin: Cáº­p nháº­t URL áº£nh Ä‘áº¡i diá»‡n cho hiá»‡n váº­t
 */
export async function updateExhibitThumbnail(code, thumbnailUrl) {
  const response = await fetch(`${API_BASE}/admin/exhibits/${encodeURIComponent(code)}/thumbnail`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ thumbnail_url: thumbnailUrl })
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'KhÃ´ng thá»ƒ cáº­p nháº­t áº£nh hiá»‡n váº­t.')
  }
  return response.json()
}

/**
 * Admin: Cáº­p nháº­t thÃ´ng tin chi tiáº¿t hiá»‡n váº­t
 */
export async function updateExhibit(code, data) {
  const response = await fetch(`${API_BASE}/admin/exhibits/${encodeURIComponent(code)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'KhÃ´ng thá»ƒ cáº­p nháº­t hiá»‡n váº­t.')
  }
  return response.json()
}

export async function deleteExhibit(code) {
  const response = await fetch(`${API_BASE}/admin/exhibits/${encodeURIComponent(code)}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Không thể xóa hiện vật.')
  }
  return response.json()
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
    throw new Error(
      errorData.detail || `Lỗi server: ${response.status}`
    )
  }

  return response.json()
}

export const fetchExhibitById = fetchExhibitByCode

export async function healthCheck() {
  const response = await fetch('/')
  return response.json()
}

/**
 * Admin: Lấy toàn bộ schema và dữ liệu 7 bảng CSDL theo chuẩn PRD
 */
export async function fetchDatabaseOverview() {
  const response = await fetch(`${API_BASE}/admin/database/overview`)
  if (!response.ok) {
    throw new Error(`Lỗi tải dữ liệu CSDL: ${response.status}`)
  }

  const sample = SAMPLE_EXHIBITS.find(
    (exhibit) => exhibit.id === exhibitId
  )

  if (sample) {
    return sample
  }

  throw new Error(`Không tìm thấy hiện vật ${exhibitId}`)
}

