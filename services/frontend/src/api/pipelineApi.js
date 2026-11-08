
const API_BASE = '/api/v1'

// 4 hiện vật mẫu để thử chức năng QR
const SAMPLE_EXHIBITS = [
  {
    id: 'EX-001',
    name: 'Trực thăng UH-1',
    zone: 'Khu trưng bày ngoài trời',
    period: 'Chiến tranh Việt Nam',
    original_text:
      'Đây là mẫu nội dung thuyết minh về trực thăng UH-1. Hiện vật được giới thiệu trong bối cảnh lịch sử chiến tranh Việt Nam. Khi sử dụng chính thức, cần bổ sung thông tin lịch sử đã được kiểm chứng.',
  },
  {
    id: 'EX-002',
    name: 'Xe tăng M48 Patton',
    zone: 'Khu trưng bày ngoài trời',
    period: 'Chiến tranh Việt Nam',
    original_text:
      'Đây là mẫu nội dung thuyết minh về xe tăng M48 Patton. Nội dung giới thiệu đặc điểm phương tiện và bối cảnh lịch sử. Cần bổ sung thông tin cụ thể theo hồ sơ hiện vật của bảo tàng.',
  },
  {
    id: 'EX-003',
    name: 'Pháo quân sự',
    zone: 'Khu trưng bày ngoài trời',
    period: 'Trưng bày lịch sử',
    original_text:
      'Đây là mẫu nội dung giới thiệu một hiện vật pháo quân sự. Phần thuyết minh sẽ cung cấp thông tin về đặc điểm và vai trò lịch sử của hiện vật sau khi được xác minh.',
  },
  {
    id: 'EX-004',
    name: 'Máy bay trưng bày',
    zone: 'Khu trưng bày ngoài trời',
    period: 'Trưng bày lịch sử',
    original_text:
      'Đây là mẫu nội dung thuyết minh về máy bay trưng bày. Khách tham quan có thể tìm hiểu thông tin về phương tiện và bối cảnh lịch sử liên quan.',
  },
]

// Dịch văn bản và tạo audio qua AI Pipeline
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

// Lấy hiện vật từ backend; nếu chưa có dữ liệu thì dùng mẫu
export async function fetchExhibits() {
  try {
    const response = await fetch(`${API_BASE}/exhibits`)

    if (response.ok) {
      const data = await response.json()

      if (Array.isArray(data) && data.length > 0) {
        return data
      }
    }
  } catch (error) {
    console.warn('Không kết nối được API hiện vật, dùng dữ liệu mẫu.')
  }

  return SAMPLE_EXHIBITS
}

// Lấy chi tiết hiện vật theo ID
export async function fetchExhibitById(exhibitId) {
  try {
    const response = await fetch(
      `${API_BASE}/exhibits/${encodeURIComponent(exhibitId)}`
    )

    if (response.ok) {
      return await response.json()
    }
  } catch (error) {
    console.warn('Không kết nối được API, thử tìm hiện vật mẫu.')
  }

  const sample = SAMPLE_EXHIBITS.find(
    (exhibit) => exhibit.id === exhibitId
  )

  if (sample) {
    return sample
  }

  throw new Error(`Không tìm thấy hiện vật ${exhibitId}`)
}

// Kiểm tra backend
export async function healthCheck() {
  const response = await fetch('/')
  return response.json()
}
