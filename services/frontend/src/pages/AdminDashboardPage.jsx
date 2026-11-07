import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import QRCode from 'qrcode'
import {
  Users, Headphones, Smartphone, Monitor, Activity, PlusCircle,
  QrCode, Trash2, ExternalLink, RefreshCw, Download, Check, Copy,
  Globe, Clock, MapPin, Eye, CheckCircle2, AlertCircle, ShieldCheck,
  Lock, LogOut, KeyRound, Database, Table, HardDrive, Search, Layers, Edit, Camera, Image as ImageIcon
} from 'lucide-react'
import { fetchAdminStats, fetchExhibits, createExhibit, deleteExhibit, updateExhibit, updateExhibitThumbnail, fetchDatabaseOverview } from '../api/pipelineApi'
import { LANGUAGES } from '../components/LanguageSelector'
import './AdminDashboardPage.css'

// Mật khẩu quản trị bảo tàng mặc định
const ADMIN_PASSWORDS = ['8888', 'admin123', 'baotang2026']

export default function AdminDashboardPage() {
  // Lớp bảo mật: Kiểm tra xem cán bộ đã nhập mật khẩu chưa
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return sessionStorage.getItem('wr_admin_authenticated') === 'true'
  })
  const [inputPin, setInputPin] = useState('')
  const [pinError, setPinError] = useState(false)

  const [activeTab, setActiveTab] = useState('stats') // 'stats', 'exhibits', hoặc 'database'

  // State CSDL (Database Explorer)
  const [dbOverview, setDbOverview] = useState(null)
  const [dbLoading, setDbLoading] = useState(false)
  const [selectedTable, setSelectedTable] = useState('exhibit')
  const [dbViewMode, setDbViewMode] = useState('data') // 'data' hoặc 'schema'
  const [tableSearch, setTableSearch] = useState('')

  // State thống kê Real-time
  const [stats, setStats] = useState(null)
  const [statsLoading, setStatsLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [lastUpdated, setLastUpdated] = useState('')

  // State quản lý hiện vật
  const [exhibits, setExhibits] = useState([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formSuccess, setFormSuccess] = useState(null)
  const [formError, setFormError] = useState(null)

  // Modal xem mã QR hiện vật vừa tạo hoặc đã có
    // Modal chỉnh sửa toàn bộ thông tin hiện vật
  const [editingExhibit, setEditingExhibit] = useState(null)
  const [editFormData, setEditFormData] = useState({
    title: '',
    title_en: '',
    zone: '',
    room_id: '',
    period: '',
    thumbnail_url: '',
    original_text: '',
  })
  const [isUpdatingExhibit, setIsUpdatingExhibit] = useState(false)
  const [editSuccess, setEditSuccess] = useState('')
  const [editError, setEditError] = useState('')

  const [selectedQrExhibit, setSelectedQrExhibit] = useState(null)
  const [qrModalDataUrl, setQrModalDataUrl] = useState('')
  const [copiedLink, setCopiedLink] = useState(false)

  // Form State thêm hiện vật
  const [formData, setFormData] = useState({
    code: '',
    title: '',
    title_en: '',
    zone: 'Khu trưng bày ngoài trời',
    room_id: 'OUTDOOR',
    period: '1965 - 1975',
    thumbnail_url: 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=800&q=80',
    original_text: '',
  })

      // Trạng thái tải ảnh xem trước ('idle' | 'loading' | 'success' | 'error')
  const [createImgStatus, setCreateImgStatus] = useState('idle')
  const [editImgStatus, setEditImgStatus] = useState('idle')

  // Hàm chuẩn hóa và tự động sửa link ảnh (Google Drive, Dropbox, khoảng trắng...)
  const cleanImageUrl = (rawUrl) => {
    if (!rawUrl) return ''
    let url = rawUrl.trim()

    // Chuyển link Google Drive chia sẻ sang link ảnh trực tiếp
    // Dạng 1: https://drive.google.com/file/d/FILE_ID/view...
    const gDriveMatch1 = url.match(/drive\.google\.com\/file\/d\/([a-zA-Z0-9_-]+)/)
    if (gDriveMatch1 && gDriveMatch1[1]) {
      return `https://drive.google.com/thumbnail?id=${gDriveMatch1[1]}&sz=w1000`
    }
    // Dạng 2: https://drive.google.com/open?id=FILE_ID
    const gDriveMatch2 = url.match(/drive\.google\.com\/open\?id=([a-zA-Z0-9_-]+)/)
    if (gDriveMatch2 && gDriveMatch2[1]) {
      return `https://drive.google.com/thumbnail?id=${gDriveMatch2[1]}&sz=w1000`
    }
    // Dạng 3: https://drive.google.com/uc?id=FILE_ID
    const gDriveMatch3 = url.match(/drive\.google\.com\/uc\?.*?id=([a-zA-Z0-9_-]+)/)
    if (gDriveMatch3 && gDriveMatch3[1]) {
      return `https://drive.google.com/thumbnail?id=${gDriveMatch3[1]}&sz=w1000`
    }

    // Chuyển link Dropbox sang link ảnh trực tiếp (raw=1)
    if (url.includes('dropbox.com') && url.includes('dl=0')) {
      return url.replace('dl=0', 'raw=1')
    }

    return url
  }

  // Thay đổi URL ảnh và chuẩn hóa
  const handleThumbUrlChange = (val, target = 'create') => {
    const cleaned = cleanImageUrl(val)
    if (target === 'create') {
      setFormData((prev) => ({ ...prev, thumbnail_url: cleaned }))
      setCreateImgStatus(cleaned ? 'loading' : 'idle')
    } else {
      setEditFormData((prev) => ({ ...prev, thumbnail_url: cleaned }))
      setEditImgStatus(cleaned ? 'loading' : 'idle')
    }
  }

  // Tải file ảnh trực tiếp từ máy tính (chuyển sang Base64 Data URL)
  const handleFileSelect = (e, target = 'create') => {
    const file = e.target.files?.[0]
    if (!file) return

    if (file.size > 8 * 1024 * 1024) {
      alert('Vui lòng chọn ảnh có dung lượng dưới 8MB để đảm bảo tốc độ phản hồi nhanh nhất.')
      return
    }

    const reader = new FileReader()
    reader.onload = (event) => {
      const base64Url = event.target.result
      if (target === 'create') {
        setFormData((prev) => ({ ...prev, thumbnail_url: base64Url }))
        setCreateImgStatus('success')
      } else {
        setEditFormData((prev) => ({ ...prev, thumbnail_url: base64Url }))
        setEditImgStatus('success')
      }
    }
    reader.readAsDataURL(file)
  }

  // Mở modal sửa toàn bộ thông tin hiện vật
  const openEditModal = (exhibit) => {
    setEditingExhibit(exhibit)
    setEditFormData({
      title: exhibit.title || '',
      title_en: exhibit.title_en || '',
      zone: exhibit.zone || '',
      room_id: exhibit.room_id || '',
      period: exhibit.period || '',
      thumbnail_url: exhibit.thumbnail_url || '',
      original_text: exhibit.original_text || '',
    })
    setEditSuccess('')
    setEditError('')
    setEditImgStatus(exhibit.thumbnail_url ? 'success' : 'idle')
  }

  // Lưu toàn bộ thông tin hiện vật vào CSDL
  const handleSaveEditExhibit = async (e) => {
    if (e) e.preventDefault()
    if (!editingExhibit) return
    if (!editFormData.title.trim() || !editFormData.original_text.trim()) {
      setEditError('Tên hiện vật và Nội dung thuyết minh không được để trống!')
      return
    }

    setIsUpdatingExhibit(true)
    setEditError('')
    setEditSuccess('')

    const payload = {
      ...editFormData,
      thumbnail_url: cleanImageUrl(editFormData.thumbnail_url)
    }

    try {
      const res = await updateExhibit(editingExhibit.code, payload)
      setEditSuccess(`Đã cập nhật hiện vật "${payload.title}" thành công!`)

      // Cập nhật ngay trong state danh sách hiện vật
      setExhibits((prev) =>
        prev.map((ex) =>
          ex.code === editingExhibit.code
            ? { ...ex, ...payload }
            : ex
        )
      )

      // Đồng bộ nạp lại database overview và danh sách hiện vật
      loadDbOverview()
      loadExhibitsList()

      setTimeout(() => {
        setEditingExhibit(null)
        setEditSuccess('')
      }, 1200)
    } catch (err) {
      setEditError(err.message || 'Lỗi khi cập nhật thông tin hiện vật.')
    } finally {
      setIsUpdatingExhibit(false)
    }
  }

  // Xử lý đăng nhập bằng mã PIN
  const handleLogin = (e) => {
    if (e) e.preventDefault()
    if (ADMIN_PASSWORDS.includes(inputPin.trim())) {
      sessionStorage.setItem('wr_admin_authenticated', 'true')
      setIsAuthenticated(true)
      setPinError(false)
      setInputPin('')
    } else {
      setPinError(true)
    }
  }

  // Đăng xuất / Khóa màn hình
  const handleLogout = () => {
    sessionStorage.removeItem('wr_admin_authenticated')
    setIsAuthenticated(false)
  }

  // 1. Tải số liệu thống kê thời gian thực
  const loadStats = async () => {
    try {
      const data = await fetchAdminStats()
      setStats(data)
      setLastUpdated(new Date().toLocaleTimeString('vi-VN'))
      setStatsLoading(false)
    } catch (err) {
      console.warn('Lỗi lấy stats admin:', err)
      setStatsLoading(false)
    }
  }

  // 2. Tải danh sách hiện vật
  const loadExhibitsList = async () => {
    try {
      const data = await fetchExhibits()
      setExhibits(data)
    } catch (err) {
      console.warn('Lỗi lấy danh sách hiện vật:', err)
    }
  }

  // 3. Tải danh sách 7 bảng CSDL PRD
  const loadDbOverview = async () => {
    setDbLoading(true)
    try {
      const data = await fetchDatabaseOverview()
      setDbOverview(data)
    } catch (err) {
      console.warn('Lỗi lấy dữ liệu CSDL:', err)
    } finally {
      setDbLoading(false)
    }
  }

  // Polling tự động làm mới số liệu mỗi 3 giây khi đã xác thực (FR-21, UC5)
  useEffect(() => {
    if (!isAuthenticated) return

    loadStats()
    loadExhibitsList()
    loadDbOverview()

    if (!autoRefresh) return
    const interval = setInterval(() => {
      loadStats()
    }, 3000)

    return () => clearInterval(interval)
  }, [isAuthenticated, autoRefresh])

  // Xử lý tạo hiện vật mới
  const handleCreateExhibit = async (e) => {
    e.preventDefault()
    if (!formData.code.trim() || !formData.title.trim() || !formData.original_text.trim()) {
      setFormError('Vui lòng nhập đầy đủ: Mã hiện vật, Tên hiện vật và Nội dung thuyết minh!')
      return
    }

    setIsSubmitting(true)
    setFormError(null)
    setFormSuccess(null)

    try {
      const res = await createExhibit(formData)
      setFormSuccess(`Đã thêm thành công hiện vật: ${res.exhibit.title}!`)
      
      openQrModal(res.exhibit)

      setFormData({
        code: '',
        title: '',
        title_en: '',
        zone: 'Khu trưng bày ngoài trời',
        room_id: 'OUTDOOR',
        period: '',
        thumbnail_url: 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=800&q=80',
        original_text: '',
      })

      loadExhibitsList()
      loadStats()
      loadDbOverview()
    } catch (err) {
      setFormError(err.message || 'Lỗi khi tạo hiện vật.')
    } finally {
      setIsSubmitting(false)
    }
  }

  // Xóa hiện vật
  const handleDeleteExhibit = async (code, title) => {
    if (!window.confirm(`Bạn có chắc chắn muốn xóa hiện vật "${title}" (Mã: ${code}) không?`)) {
      return
    }
    try {
      await deleteExhibit(code)
      loadExhibitsList()
      loadStats()
      loadDbOverview()
    } catch (err) {
      alert(err.message || 'Không thể xóa hiện vật.')
    }
  }

  // Mở modal sinh và hiển thị mã QR
  const openQrModal = async (exhibit) => {
    setSelectedQrExhibit(exhibit)
    try {
      const host = localStorage.getItem('war_remnants_tunnel_host') || window.location.origin
      const targetUrl = `${host.replace(/\/+$/, '')}/exhibit/${exhibit.code}`
      
      const dataUrl = await QRCode.toDataURL(targetUrl, {
        width: 360,
        margin: 1,
        color: { dark: '#0a0c10', light: '#ffffff' },
        errorCorrectionLevel: 'H'
      })
      setQrModalDataUrl(dataUrl)
    } catch (e) {
      console.error(e)
    }
  }

  const handleCopyModalLink = () => {
    if (!selectedQrExhibit) return
    const host = localStorage.getItem('war_remnants_tunnel_host') || window.location.origin
    const url = `${host.replace(/\/+$/, '')}/exhibit/${selectedQrExhibit.code}`
    navigator.clipboard.writeText(url)
    setCopiedLink(true)
    setTimeout(() => setCopiedLink(false), 2000)
  }

  // ════════════════════════════════════════════════════════════════════
  // 🔒 MÀN HÌNH KHÓA XÁC THỰC QUẢN TRỊ (NGĂN KHÁCH THAM QUAN VÀO)
  // ════════════════════════════════════════════════════════════════════
  if (!isAuthenticated) {
    return (
      <main className="admin-lock-screen">
        <div className="admin-lock-card glass-card animate-fade-in-up">
          <div className="lock-icon-wrapper">
            <Lock size={32} style={{ color: 'var(--color-amber-400)' }} />
          </div>

          <div className="lock-header-text">
            <span className="badge badge-amber" style={{ margin: '0 auto 6px' }}>Cổng Quản Trị Nội Bộ</span>
            <h2 className="text-xl font-bold">Xác Thực Cán Bộ Bảo Tàng</h2>
            <p className="text-xs text-muted" style={{ marginTop: '4px' }}>
              Trang này chỉ dành riêng cho cán bộ quản trị. Vui lòng nhập mã PIN bảo mật để tiếp tục.
            </p>
          </div>

          {pinError && (
            <div className="alert-box alert-error animate-fade-in-up">
              <AlertCircle size={15} />
              <span>Mã PIN không chính xác! Vui lòng thử lại.</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="lock-form">
            <div className="form-group">
              <input
                type="password"
                className="form-input text-center font-mono text-lg tracking-widest"
                placeholder="Nhập mã PIN (mặc định: 8888)"
                value={inputPin}
                onChange={(e) => {
                  setInputPin(e.target.value)
                  setPinError(false)
                }}
                autoFocus
                maxLength={20}
              />
            </div>

            <button type="submit" className="btn btn-primary btn-lg" style={{ width: '100%' }}>
              <KeyRound size={16} />
              <span>Mở Khóa Bảng Điều Khiển</span>
            </button>
          </form>

          <div className="lock-footer">
            <Link to="/" className="text-xs text-muted hover-underline">
              ← Quay lại trang chủ bảo tàng
            </Link>
            <p className="text-xs text-muted" style={{ marginTop: '8px' }}>
              Mã PIN mẫu: <code>8888</code> hoặc <code>admin123</code>
            </p>
          </div>
        </div>
      </main>
    )
  }

  // ════════════════════════════════════════════════════════════════════
  // 📊 BẢNG ĐIỀU KHIỂN ADMIN (KHI ĐÃ XÁC THỰC THÀNH CÔNG)
  // ════════════════════════════════════════════════════════════════════
  return (
    <main className="admin-page">
      <div className="container">
        {/* Header Admin */}
        <div className="admin-header">
          <div className="admin-title-row">
            <div>
              <div className="badge badge-amber" style={{ marginBottom: '0.4rem' }}>
                <ShieldCheck size={13} />
                <span>Trung Tâm Quản Trị Hệ Thống (Admin CMS)</span>
              </div>
              <h1 className="text-3xl font-bold">
                Bảo Tàng <span className="gradient-text">Chứng Tích Chiến Tranh</span>
              </h1>
              <p className="text-sm text-secondary" style={{ marginTop: '0.25rem' }}>
                Giám sát người truy cập thời gian thực & Quản lý tạo mã QR hiện vật
              </p>
            </div>

            {/* Cụm nút điều khiển thời gian thực & Đăng xuất */}
            <div className="admin-quick-controls">
              <div className="admin-live-pulse-badge">
                <span className="live-dot" />
                <span className="text-xs font-semibold" style={{ color: '#10b981' }}>
                  Live Stream {autoRefresh ? '(3s/lần)' : '(Tạm dừng)'}
                </span>
              </div>

              <button
                type="button"
                className={`btn btn-sm ${autoRefresh ? 'btn-secondary' : 'btn-ghost'}`}
                onClick={() => setAutoRefresh(!autoRefresh)}
                title="Bật/Tắt tự động cập nhật"
              >
                <Activity size={14} />
                <span>{autoRefresh ? 'Tắt tự động' : 'Bật tự động'}</span>
              </button>

              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={loadStats}
                title="Làm mới ngay"
              >
                <RefreshCw size={14} />
                <span className="hide-on-mobile">Làm mới ({lastUpdated})</span>
              </button>

              <button
                type="button"
                className="btn btn-ghost btn-sm text-danger"
                onClick={handleLogout}
                title="Khóa bảng điều khiển"
              >
                <LogOut size={14} />
                <span className="hide-on-mobile">Đăng xuất</span>
              </button>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="admin-tabs-nav">
            <button
              type="button"
              className={`admin-tab-btn ${activeTab === 'stats' ? 'active' : ''}`}
              onClick={() => setActiveTab('stats')}
            >
              <Users size={16} />
              <span>Thống Kê Người Đang Truy Cập</span>
              {stats?.realtime?.online_visitors > 0 && (
                <span className="tab-counter-badge">{stats.realtime.online_visitors}</span>
              )}
            </button>

            <button
              type="button"
              className={`admin-tab-btn ${activeTab === 'exhibits' ? 'active' : ''}`}
              onClick={() => setActiveTab('exhibits')}
            >
              <PlusCircle size={16} />
              <span>Thêm Hiện Vật & Tạo Mã QR ({exhibits.length})</span>
            </button>

            <button
              type="button"
              className={`admin-tab-btn ${activeTab === 'database' ? 'active' : ''}`}
              onClick={() => {
                setActiveTab('database')
                loadDbOverview()
              }}
            >
              <Database size={16} />
              <span>Cơ Sở Dữ Liệu &amp; Ngôn Ngữ</span>
              <span className="tab-counter-badge" style={{ background: '#3b82f6', color: '#fff' }}>
                {dbOverview?.tables?.length || 8}
              </span>
            </button>

            <Link to="/qr-stands" className="admin-tab-btn" style={{ marginLeft: 'auto' }}>
              <QrCode size={16} />
              <span>Mở Toàn Bộ Biển Mã QR</span>
              <ExternalLink size={12} />
            </Link>
          </div>
        </div>

        {/* ════════════════════════════════════════════════════════════════
            TAB 1: THỐNG KÊ NGƯỜI ĐANG TRUY CẬP THỜI GIAN THỰC (UC5)
           ════════════════════════════════════════════════════════════════ */}
        {activeTab === 'stats' && (
          <div className="admin-stats-tab animate-fade-in-up">
            {/* 4 Thẻ KPI Real-time */}
            <div className="kpi-grid">
              {/* KPI 1: Online Now */}
              <div className="kpi-card glass-card kpi-card--active">
                <div className="kpi-header">
                  <span className="kpi-label">Đang Truy Cập (Online Now)</span>
                  <div className="kpi-pulse-icon">
                    <span className="pulse-ring" />
                    <Users size={20} style={{ color: '#10b981' }} />
                  </div>
                </div>
                <div className="kpi-value-row">
                  <span className="kpi-number gradient-text">
                    {stats?.realtime?.online_visitors ?? 0}
                  </span>
                  <span className="kpi-unit">khách</span>
                </div>
                <p className="kpi-note">
                  Phiên hoạt động tích cực trong 25 giây qua
                </p>
              </div>

              {/* KPI 2: Active Listeners */}
              <div className="kpi-card glass-card">
                <div className="kpi-header">
                  <span className="kpi-label">Đang Nghe Thuyết Minh</span>
                  <Headphones size={20} style={{ color: 'var(--color-amber-400)' }} />
                </div>
                <div className="kpi-value-row">
                  <span className="kpi-number" style={{ color: 'var(--color-amber-400)' }}>
                    {stats?.realtime?.active_listeners ?? 0}
                  </span>
                  <span className="kpi-unit">người</span>
                </div>
                <p className="kpi-note">
                  Đang phát audio giọng đọc AI Neural
                </p>
              </div>

              {/* KPI 3: Mobile vs Desktop */}
              <div className="kpi-card glass-card">
                <div className="kpi-header">
                  <span className="kpi-label">Thiết Bị Di Động (Mobile)</span>
                  <Smartphone size={20} style={{ color: '#38bdf8' }} />
                </div>
                <div className="kpi-value-row">
                  <span className="kpi-number" style={{ color: '#38bdf8' }}>
                    {stats?.breakdown?.by_device?.Mobile ?? 0}
                  </span>
                  <span className="kpi-unit">
                    / {stats?.realtime?.online_visitors ?? 0} thiết bị
                  </span>
                </div>
                <p className="kpi-note">
                  Quét QR bằng Camera Smartphone / Zalo
                </p>
              </div>

              {/* KPI 4: Total Visits Today */}
              <div className="kpi-card glass-card">
                <div className="kpi-header">
                  <span className="kpi-label">Tổng Lượt Kết Nối Hôm Nay</span>
                  <Activity size={20} style={{ color: '#a78bfa' }} />
                </div>
                <div className="kpi-value-row">
                  <span className="kpi-number" style={{ color: '#a78bfa' }}>
                    {stats?.realtime?.total_visits_today ?? 0}
                  </span>
                  <span className="kpi-unit">lượt</span>
                </div>
                <p className="kpi-note">
                  {stats?.realtime?.total_audio_played ?? 0} bài nghe đã hoàn tất
                </p>
              </div>
            </div>

            {/* Hàng 2: Phân bố Ngôn Ngữ & Danh Sách Phiên Đang Kết Nối */}
            <div className="admin-two-col-grid">
              {/* Cột trái: Phân bố ngôn ngữ */}
              <div className="admin-box glass-card">
                <div className="admin-box-header">
                  <div className="flex items-center gap-2">
                    <Globe size={16} style={{ color: 'var(--color-amber-400)' }} />
                    <h3 className="text-base font-bold">Ngôn Ngữ Du Khách Đang Dùng</h3>
                  </div>
                  <span className="text-xs text-muted">Thời gian thực</span>
                </div>

                <div className="lang-breakdown-list">
                  {Object.entries(stats?.breakdown?.by_language || {}).length === 0 ? (
                    <p className="text-xs text-muted" style={{ padding: '1rem', textAlign: 'center' }}>
                      Chưa có phiên du khách nào kết nối. Mở điện thoại quét mã QR để kiểm tra ngay!
                    </p>
                  ) : (
                    Object.entries(stats?.breakdown?.by_language || {}).map(([langCode, count]) => {
                      const langInfo = LANGUAGES.find((l) => l.code === langCode)
                      const total = stats?.realtime?.online_visitors || 1
                      const percent = Math.round((count / total) * 100)

                      return (
                        <div key={langCode} className="lang-breakdown-item">
                          <div className="lang-item-top">
                            <span className="flex items-center gap-2 text-sm font-semibold">
                              <span>{langInfo?.flag || '🌐'}</span>
                              <span>{langInfo?.nativeName || langCode.toUpperCase()}</span>
                            </span>
                            <span className="text-xs font-bold text-amber">
                              {count} khách ({percent}%)
                            </span>
                          </div>
                          <div className="progress-track">
                            <div className="progress-fill" style={{ width: `${percent}%` }} />
                          </div>
                        </div>
                      )
                    })
                  )}
                </div>
              </div>

              {/* Cột phải: Các phiên khách đang trực tiếp online */}
              <div className="admin-box glass-card">
                <div className="admin-box-header">
                  <div className="flex items-center gap-2">
                    <Eye size={16} style={{ color: '#10b981' }} />
                    <h3 className="text-base font-bold">Phiên Du Khách Đang Kết Nối ({stats?.active_sessions_list?.length ?? 0})</h3>
                  </div>
                  <span className="text-xs text-muted">Active Sessions</span>
                </div>

                <div className="active-sessions-table-wrapper">
                  {stats?.active_sessions_list?.length === 0 ? (
                    <div className="empty-sessions">
                      <Users size={32} style={{ opacity: 0.3 }} />
                      <p className="text-xs text-muted" style={{ marginTop: '0.5rem' }}>
                        Hiện không có khách nào online. Khi có người quét mã QR trên điện thoại, phiên truy cập sẽ xuất hiện tại đây ngay lập tức!
                      </p>
                    </div>
                  ) : (
                    <table className="admin-table">
                      <thead>
                        <tr>
                          <th>Session ID</th>
                          <th>Hiện vật</th>
                          <th>Ngôn ngữ</th>
                          <th>Trạng thái</th>
                          <th>Thiết bị</th>
                        </tr>
                      </thead>
                      <tbody>
                        {stats?.active_sessions_list?.map((s, idx) => (
                          <tr key={idx}>
                            <td>
                              <code className="session-tag">{s.session_id}</code>
                            </td>
                            <td>
                              <strong className="text-xs">{s.exhibit}</strong>
                            </td>
                            <td>
                              <span className="text-xs">{s.language?.toUpperCase()}</span>
                            </td>
                            <td>
                              {s.is_listening ? (
                                <span className="badge badge-listening">
                                  <Headphones size={11} /> Đang nghe
                                </span>
                              ) : (
                                <span className="badge badge-viewing">
                                  Đang xem
                                </span>
                              )}
                            </td>
                            <td>
                              <span className="text-xs text-muted">{s.device}</span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </div>
            </div>

            {/* Bảng Nhật Ký Hoạt Động Trực Tiếp (Live Stream Activity Log) */}
            <div className="admin-box glass-card" style={{ marginTop: '1.5rem' }}>
              <div className="admin-box-header">
                <div className="flex items-center gap-2">
                  <Clock size={16} style={{ color: 'var(--color-amber-400)' }} />
                  <h3 className="text-base font-bold">Nhật Ký Truy Cập Thời Gian Thực (Live Activity Log)</h3>
                </div>
                <span className="text-xs text-muted">Tự động cập nhật</span>
              </div>

              <div className="activity-logs-list">
                {stats?.recent_activity_logs?.length === 0 ? (
                  <p className="text-xs text-muted" style={{ padding: '1rem', textAlign: 'center' }}>
                    Chưa có nhật ký hoạt động nào được ghi nhận.
                  </p>
                ) : (
                  stats?.recent_activity_logs?.map((log) => (
                    <div key={log.id} className="activity-log-item">
                      <span className="log-time">{log.time}</span>
                      <span className="log-dot" />
                      <div className="log-content">
                        <strong>Khách [{log.visitor_id}]</strong> đã {log.action.toLowerCase()}{' '}
                        <span className="text-amber">"{log.exhibit_code}"</span> bằng tiếng{' '}
                        <strong>{log.language?.toUpperCase()}</strong> qua thiết bị{' '}
                        <span className="text-muted">{log.device}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════════════════════════════
            TAB 2: THÊM HIỆN VẬT & QUẢN LÝ MÃ QR (UC3, FR-02, FR-04)
           ════════════════════════════════════════════════════════════════ */}
        {activeTab === 'exhibits' && (
          <div className="admin-exhibits-tab animate-fade-in-up">
            <div className="exhibit-management-grid">
              {/* Form thêm hiện vật mới */}
              <div className="exhibit-form-card glass-card">
                <div className="admin-box-header">
                  <div className="flex items-center gap-2">
                    <PlusCircle size={18} style={{ color: 'var(--color-amber-400)' }} />
                    <h3 className="text-base font-bold">Thêm Hiện Vật Mới & Tạo Mã QR</h3>
                  </div>
                </div>

                {formSuccess && (
                  <div className="alert-box alert-success animate-fade-in-up">
                    <CheckCircle2 size={16} />
                    <span>{formSuccess}</span>
                  </div>
                )}

                {formError && (
                  <div className="alert-box alert-error animate-fade-in-up">
                    <AlertCircle size={16} />
                    <span>{formError}</span>
                  </div>
                )}

                <form onSubmit={handleCreateExhibit} className="exhibit-form">
                  <div className="form-group-row">
                    <div className="form-group" style={{ flex: 1 }}>
                      <label className="form-label" htmlFor="ex_code">
                        Mã Định Danh (Code QR) <span className="text-danger">*</span>
                      </label>
                      <input
                        id="ex_code"
                        type="text"
                        className="form-input"
                        placeholder="Ví dụ: C130-HERCULES, EX-06"
                        value={formData.code}
                        onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                        required
                      />
                      <span className="text-xs text-muted">Mã dùng cho link quét mã QR</span>
                    </div>

                    <div className="form-group" style={{ flex: 1 }}>
                      <label className="form-label" htmlFor="ex_period">
                        Thời Kỳ Lịch Sử
                      </label>
                      <input
                        id="ex_period"
                        type="text"
                        className="form-input"
                        placeholder="Ví dụ: 1965 - 1975"
                        value={formData.period}
                        onChange={(e) => setFormData({ ...formData, period: e.target.value })}
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="form-label" htmlFor="ex_title">
                      Tên Hiện Vật Tiếng Việt <span className="text-danger">*</span>
                    </label>
                    <input
                      id="ex_title"
                      type="text"
                      className="form-input"
                      placeholder="Ví dụ: Máy bay vận tải hạng nặng C-130 Hercules"
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label" htmlFor="ex_title_en">
                      Tên Hiện Vật Tiếng Anh (English)
                    </label>
                    <input
                      id="ex_title_en"
                      type="text"
                      className="form-input"
                      placeholder="Ví dụ: C-130 Hercules Heavy Transport Aircraft"
                      value={formData.title_en}
                      onChange={(e) => setFormData({ ...formData, title_en: e.target.value })}
                    />
                  </div>

                  <div className="form-group-row">
                    <div className="form-group" style={{ flex: 1 }}>
                      <label className="form-label" htmlFor="ex_zone">
                        Khu Vực Trưng Bày
                      </label>
                      <input
                        id="ex_zone"
                        type="text"
                        className="form-input"
                        placeholder="Ví dụ: Khu trưng bày ngoài trời"
                        value={formData.zone}
                        onChange={(e) => setFormData({ ...formData, zone: e.target.value })}
                      />
                    </div>

                    <div className="form-group" style={{ flex: 1 }}>
                      <label className="form-label" htmlFor="ex_room">
                        Mã Phòng / Bãi
                      </label>
                      <input
                        id="ex_room"
                        type="text"
                        className="form-input"
                        placeholder="OUTDOOR, ROOM-01..."
                        value={formData.room_id}
                        onChange={(e) => setFormData({ ...formData, room_id: e.target.value })}
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <div className="flex items-center justify-between">
                      <label className="form-label" htmlFor="ex_thumb">
                        Đường Dẫn Ảnh Đại Diện (Image URL)
                      </label>
                      <label className="btn btn-ghost btn-sm" style={{ cursor: 'pointer', fontSize: '0.75rem', padding: '2px 8px' }}>
                        <Camera size={13} />
                        <span>📁 Tải ảnh từ máy tính</span>
                        <input
                          type="file"
                          accept="image/*"
                          style={{ display: 'none' }}
                          onChange={(e) => handleFileSelect(e, 'create')}
                        />
                      </label>
                    </div>
                    <div className="flex gap-2">
                      <input
                        id="ex_thumb"
                        type="text"
                        className="form-input"
                        style={{ flex: 1 }}
                        placeholder="Dán link ảnh (Unsplash, Google Drive, Imgur...) hoặc chọn ảnh từ máy tính"
                        value={formData.thumbnail_url}
                        onChange={(e) => handleThumbUrlChange(e.target.value, 'create')}
                      />
                      {formData.thumbnail_url && (
                        <button
                          type="button"
                          className="btn btn-ghost btn-sm"
                          onClick={() => {
                            setFormData({ ...formData, thumbnail_url: '' })
                            setCreateImgStatus('idle')
                          }}
                          title="Xóa link ảnh"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                    {formData.thumbnail_url && (
                      <div className="admin-thumb-preview-box">
                        <img
                          key={formData.thumbnail_url}
                          src={cleanImageUrl(formData.thumbnail_url)}
                          alt="Xem trước ảnh"
                          className="admin-thumb-preview-img"
                          onLoad={() => setCreateImgStatus('success')}
                          onError={() => setCreateImgStatus('error')}
                        />
                        <div style={{ flex: 1 }}>
                          <span className="text-xs font-semibold block">Xem trước ảnh đại diện</span>
                          {createImgStatus === 'success' && (
                            <span className="text-xs" style={{ color: '#10b981' }}>✓ Ảnh tải thành công</span>
                          )}
                          {createImgStatus === 'error' && (
                            <span className="text-xs" style={{ color: '#ef4444' }}>⚠ Không tải được ảnh từ link này (hãy bấm "Tải ảnh từ máy tính")</span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="form-group">
                    <label className="form-label" htmlFor="ex_text">
                      Nội Dung Thuyết Minh Tiếng Việt Gốc <span className="text-danger">*</span>
                    </label>
                    <textarea
                      id="ex_text"
                      className="form-textarea"
                      rows={5}
                      placeholder="Nhập bài thuyết minh lịch sử chuẩn bằng tiếng Việt. AI sẽ tự động dịch sang 15+ thứ tiếng và sinh giọng đọc khi du khách quét mã QR..."
                      value={formData.original_text}
                      onChange={(e) => setFormData({ ...formData, original_text: e.target.value })}
                      required
                    />
                  </div>

                  <button
                    type="submit"
                    className="btn btn-primary btn-lg"
                    style={{ width: '100%', marginTop: '0.5rem' }}
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <>
                        <span className="spinner" />
                        <span>Đang lưu hiện vật & tạo mã QR...</span>
                      </>
                    ) : (
                      <>
                        <QrCode size={18} />
                        <span>Lưu Hiện Vật & Kích Hoạt Mã QR</span>
                      </>
                    )}
                  </button>
                </form>
              </div>

              {/* Danh sách hiện vật hiện có */}
              <div className="exhibits-list-card glass-card">
                <div className="admin-box-header">
                  <div className="flex items-center gap-2">
                    <QrCode size={18} style={{ color: 'var(--color-amber-400)' }} />
                    <h3 className="text-base font-bold">Danh Mục Mã QR Hiện Vật ({exhibits.length})</h3>
                  </div>
                  <Link to="/qr-stands" className="btn btn-ghost btn-sm">
                    In Toàn Bộ
                  </Link>
                </div>

                <div className="admin-exhibits-items">
                  {exhibits.map((ex) => (
                    <div key={ex.code} className="admin-exhibit-row">
                      <div
                        className="admin-exhibit-thumb-container"
                        onClick={() => openEditModal(ex)}
                        title="Nhấp để chỉnh sửa toàn bộ thông tin hiện vật"
                      >
                        <img
                          src={ex.thumbnail_url}
                          alt={ex.title}
                          className="admin-exhibit-thumb"
                          onError={(e) => {
                            e.target.onerror = null
                            e.target.src = 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=400&q=80'
                          }}
                        />
                        <div className="admin-thumb-hover-overlay">
                          <Edit size={13} />
                          <span>Sửa</span>
                        </div>
                      </div>

                      <div className="admin-exhibit-info">
                        <div className="flex items-center gap-2">
                          <span className="badge badge-amber">{ex.display_code || ex.code}</span>
                          <span className="text-xs text-muted">{ex.zone}</span>
                        </div>
                        <h4 className="text-sm font-bold" style={{ marginTop: '2px' }}>{ex.title}</h4>
                        <p className="text-xs text-muted line-clamp-1">{ex.original_text}</p>
                      </div>

                      <div className="admin-exhibit-actions">
                        <button
                          type="button"
                          className="btn btn-secondary btn-sm"
                          onClick={() => openEditModal(ex)}
                          title="Chỉnh sửa toàn bộ thông tin hiện vật"
                        >
                          <Edit size={14} />
                          <span>Sửa</span>
                        </button>

                        <button
                          type="button"
                          className="btn btn-secondary btn-sm"
                          onClick={() => openQrModal(ex)}
                          title="Xem & Tải mã QR"
                        >
                          <QrCode size={14} />
                          <span>Mã QR</span>
                        </button>

                        <Link
                          to={`/exhibit/${ex.code}`}
                          className="btn btn-ghost btn-sm"
                          title="Mở nghe thử"
                          target="_blank"
                        >
                          <ExternalLink size={14} />
                        </Link>

                        <button
                          type="button"
                          className="btn btn-ghost btn-sm text-danger"
                          onClick={() => handleDeleteExhibit(ex.code, ex.title)}
                          title="Xóa hiện vật"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════════════════════════════
            TAB 3: KHÁM PHÁ CƠ SỞ DỮ LIỆU CHUẨN PRD (7 BẢNG QUAN HỆ)
           ════════════════════════════════════════════════════════════════ */}
        {activeTab === 'database' && (
          <div className="admin-db-tab animate-fade-in-up">
            {/* Banner giới thiệu CSDL */}
            <div className="db-banner glass-card">
              <div className="db-banner-left">
                <div className="db-banner-icon">
                  <Database size={28} color="#3b82f6" />
                </div>
                <div>
                  <div className="badge badge-amber" style={{ marginBottom: '4px' }}>
                    <HardDrive size={12} />
                    <span>Hệ Thống Cơ Sở Dữ Liệu PRD Phần III (Data Dictionary)</span>
                  </div>
                  <h2 className="text-xl font-bold">
                    Khám Phá Trực Quan 7 Bảng CSDL Bảo Tàng
                  </h2>
                  <p className="text-xs text-muted" style={{ marginTop: '2px' }}>
                    Dual-Database Architecture: Hỗ trợ đồng thời <strong>SQLite</strong> (Cục bộ không cần cài đặt) &amp; <strong>PostgreSQL</strong> (Docker Container).
                  </p>
                </div>
              </div>

              <div className="db-banner-right">
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={loadDbOverview}
                  disabled={dbLoading}
                >
                  <RefreshCw size={14} className={dbLoading ? 'spin-animation' : ''} />
                  <span>{dbLoading ? 'Đang đọc CSDL...' : 'Làm mới CSDL'}</span>
                </button>
              </div>
            </div>

            {/* Danh sách 7 Bảng CSDL (Pills Selector) */}
            <div className="db-table-nav">
              {dbOverview?.tables?.map((tbl) => {
                const isSelected = selectedTable === tbl.name
                return (
                  <button
                    key={tbl.name}
                    type="button"
                    className={`db-table-pill ${isSelected ? 'active' : ''}`}
                    onClick={() => {
                      setSelectedTable(tbl.name)
                      setTableSearch('')
                    }}
                  >
                    <Table size={14} />
                    <span className="font-semibold">{tbl.name}</span>
                    <span className={`db-row-counter ${isSelected ? 'active-counter' : ''}`}>
                      {tbl.rowCount} dòng
                    </span>
                  </button>
                )
              })}
            </div>

            {/* Chi tiết Bảng đang được chọn */}
            {(() => {
              const currentTable = dbOverview?.tables?.find((t) => t.name === selectedTable) || dbOverview?.tables?.[0]
              if (!currentTable) {
                return (
                  <div className="glass-card text-center" style={{ padding: '2rem' }}>
                    <span className="spinner" />
                    <p className="text-sm text-muted" style={{ marginTop: '8px' }}>Đang nạp cấu trúc bảng...</p>
                  </div>
                )
              }

              // Lọc dữ liệu theo ô tìm kiếm
              const filteredRows = (currentTable.rows || []).filter((row) => {
                if (!tableSearch.trim()) return true
                return Object.values(row).some((val) =>
                  String(val).toLowerCase().includes(tableSearch.toLowerCase())
                )
              })

              return (
                <div className="db-detail-card glass-card">
                  {/* Header của bảng */}
                  <div className="db-detail-header">
                    <div className="db-detail-info">
                      <div className="flex items-center gap-2">
                        <span className="badge badge-amber">{currentTable.service}</span>
                        <span className="text-xs text-muted">
                          PRD Data Dictionary • <strong>{currentTable.columns.length}</strong> cột • <strong>{currentTable.rowCount}</strong> bản ghi
                        </span>
                      </div>
                      <h3 className="text-lg font-bold" style={{ marginTop: '4px' }}>
                        Bảng <code>{currentTable.name}</code>: {currentTable.displayName}
                      </h3>
                      <p className="text-xs text-secondary" style={{ marginTop: '2px' }}>
                        {currentTable.description}
                      </p>
                    </div>

                    {/* Bộ lọc chế độ xem (Dữ liệu / Cấu trúc) */}
                    <div className="db-view-switch">
                      <button
                        type="button"
                        className={`btn btn-sm ${dbViewMode === 'data' ? 'btn-primary' : 'btn-ghost'}`}
                        onClick={() => setDbViewMode('data')}
                      >
                        <Table size={14} />
                        <span>Xem Dữ Liệu ({currentTable.rowCount})</span>
                      </button>
                      <button
                        type="button"
                        className={`btn btn-sm ${dbViewMode === 'schema' ? 'btn-primary' : 'btn-ghost'}`}
                        onClick={() => setDbViewMode('schema')}
                      >
                        <Layers size={14} />
                        <span>Xem Cấu Trúc Cột ({currentTable.columns.length})</span>
                      </button>
                    </div>
                  </div>

                  {/* 1. CHẾ ĐỘ XEM DỮ LIỆU THỰC TẾ TRONG BẢNG (DATA VIEW) */}
                  {dbViewMode === 'data' && (
                    <div className="db-data-view">
                      <div className="db-search-bar">
                        <div className="search-input-wrapper">
                          <Search size={14} className="search-icon" />
                          <input
                            type="text"
                            className="input search-input"
                            placeholder={`Tìm kiếm trong bảng ${currentTable.name}...`}
                            value={tableSearch}
                            onChange={(e) => setTableSearch(e.target.value)}
                          />
                        </div>
                        <span className="text-xs text-muted">
                          Hiển thị {filteredRows.length} / {currentTable.rowCount} dòng
                        </span>
                      </div>

                      {filteredRows.length > 0 ? (
                        <div className="db-table-scroll-container">
                          <table className="db-data-table">
                            <thead>
                              <tr>
                                <th style={{ width: '40px', textAlign: 'center' }}>#</th>
                                {currentTable.columns.map((col) => (
                                  <th key={col.name}>
                                    <div className="col-th-inner">
                                      <span>{col.name}</span>
                                      {col.primary_key && <span className="pk-badge">PK</span>}
                                    </div>
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {filteredRows.map((row, idx) => (
                                <tr key={idx}>
                                  <td className="row-num text-center">{idx + 1}</td>
                                  {currentTable.columns.map((col) => {
                                    const rawVal = row[col.name]
                                    const displayVal = rawVal === null || rawVal === undefined ? (
                                      <em className="text-muted">null</em>
                                    ) : typeof rawVal === 'boolean' ? (
                                      <span className={rawVal ? 'badge-bool-true' : 'badge-bool-false'}>
                                        {rawVal ? 'true' : 'false'}
                                      </span>
                                    ) : String(rawVal).length > 80 ? (
                                      <span title={String(rawVal)}>
                                        {String(rawVal).slice(0, 80)}...
                                      </span>
                                    ) : (
                                      String(rawVal)
                                    )

                                    return (
                                      <td key={col.name} className="data-cell">
                                        {displayVal}
                                      </td>
                                    )
                                  })}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ) : (
                        <div className="db-empty-state">
                          <AlertCircle size={32} color="#f59e0b" />
                          <h4 className="text-sm font-bold">Chưa có bản ghi nào trong bảng này</h4>
                          <p className="text-xs text-muted" style={{ maxWidth: '450px', marginTop: '4px', textAlign: 'center' }}>
                            {currentTable.name === 'localization' || currentTable.name === 'audio_media'
                              ? 'Dữ liệu sẽ tự động được ghi nhận khi khách tham quan bấm nghe thuyết minh các ngôn ngữ khác nhau trên điện thoại.'
                              : currentTable.name === 'listening_metric'
                              ? 'Dữ liệu sẽ ghi nhận khi khách nghe thuyết minh xong từng đoạn hiện vật (Anonymous Listening Metric).'
                              : 'Hiện tại bảng đang trống. Bạn có thể thêm dữ liệu từ trang quản trị hoặc kiểm tra file SQL khởi tạo.'}
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* 2. CHẾ ĐỘ XEM CẤU TRÚC BẢNG (SCHEMA & DATA DICTIONARY) */}
                  {dbViewMode === 'schema' && (
                    <div className="db-schema-view">
                      <div className="db-table-scroll-container">
                        <table className="db-data-table schema-table">
                          <thead>
                            <tr>
                              <th style={{ width: '40px', textAlign: 'center' }}>STT</th>
                              <th>Tên Cột (Column Name)</th>
                              <th>Kiểu Dữ Liệu (Data Type)</th>
                              <th>Ràng Buộc (Constraints)</th>
                              <th>Vai Trò Theo Chuẩn PRD</th>
                            </tr>
                          </thead>
                          <tbody>
                            {currentTable.columns.map((col, idx) => (
                              <tr key={col.name}>
                                <td className="row-num text-center">{idx + 1}</td>
                                <td>
                                  <strong><code>{col.name}</code></strong>
                                </td>
                                <td>
                                  <span className="badge badge-type">{col.type}</span>
                                </td>
                                <td>
                                  <div className="flex gap-1">
                                    {col.primary_key && <span className="pk-badge">PRIMARY KEY</span>}
                                    {!col.nullable && <span className="badge-notnull">NOT NULL</span>}
                                    {col.nullable && !col.primary_key && <span className="badge-nullable">NULLABLE</span>}
                                  </div>
                                </td>
                                <td className="text-xs text-secondary">
                                  {col.primary_key
                                    ? 'Định danh duy nhất (UUID v4)'
                                    : col.name.includes('_id')
                                    ? 'Khóa ngoại logic (Decoupled Logical Foreign Key)'
                                    : col.name.includes('_json')
                                    ? 'Dữ liệu cấu trúc JSON (Timestamps / Exhibits Order)'
                                    : col.name.includes('version')
                                    ? 'Phiên bản nội dung chống xung đột cache'
                                    : 'Trường thông tin tiêu chuẩn của PRD'}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              )
            })()}
          </div>
        )}

        {/* ════════════════════════════════════════════════════════════════
            MODAL CHỈNH SỬA TOÀN BỘ THÔNG TIN HIỆN VẬT
           ════════════════════════════════════════════════════════════════ */}
        {editingExhibit && (
          <div className="qr-modal-backdrop" onClick={() => setEditingExhibit(null)}>
            <div className="qr-modal-card glass-card animate-fade-in-up" style={{ maxWidth: '640px', maxHeight: '90vh', overflowY: 'auto' }} onClick={(e) => e.stopPropagation()}>
              <div className="qr-modal-header" style={{ position: 'sticky', top: 0, zIndex: 10, background: 'rgba(15, 23, 42, 0.95)', backdropFilter: 'blur(8px)' }}>
                <div>
                  <span className="badge badge-amber">{editingExhibit.display_code || editingExhibit.code}</span>
                  <h3 className="text-base font-bold" style={{ marginTop: '4px' }}>
                    Chỉnh Sửa Hiện Vật: {editingExhibit.title}
                  </h3>
                </div>
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  onClick={() => setEditingExhibit(null)}
                >
                  ✕
                </button>
              </div>

              <form onSubmit={handleSaveEditExhibit} className="qr-modal-body" style={{ gap: '1rem', padding: '1.25rem' }}>
                {editSuccess && (
                  <div className="alert-box alert-success animate-fade-in-up" style={{ margin: 0 }}>
                    <CheckCircle2 size={16} />
                    <span>{editSuccess}</span>
                  </div>
                )}

                {editError && (
                  <div className="alert-box alert-error animate-fade-in-up" style={{ margin: 0 }}>
                    <AlertCircle size={16} />
                    <span>{editError}</span>
                  </div>
                )}

                {/* Hàng 1: Mã hiện vật (Readonly) & Thời kỳ */}
                <div className="form-group-row">
                  <div className="form-group" style={{ flex: 1 }}>
                    <label className="form-label">
                      Mã Hiện Vật (Định danh QR)
                    </label>
                    <input
                      type="text"
                      className="form-input text-muted"
                      value={editingExhibit.code}
                      disabled
                      title="Mã hiện vật cố định để đảm bảo các mã QR và file audio đã sinh không bị mất liên kết"
                    />
                  </div>

                  <div className="form-group" style={{ flex: 1 }}>
                    <label className="form-label" htmlFor="edit_period">
                      Thời Kỳ Lịch Sử
                    </label>
                    <input
                      id="edit_period"
                      type="text"
                      className="form-input"
                      placeholder="Ví dụ: 1965 - 1975"
                      value={editFormData.period}
                      onChange={(e) => setEditFormData({ ...editFormData, period: e.target.value })}
                    />
                  </div>
                </div>

                {/* Hàng 2: Tên hiện vật VN & EN */}
                <div className="form-group">
                  <label className="form-label" htmlFor="edit_title">
                    Tên Hiện Vật Tiếng Việt <span className="text-danger">*</span>
                  </label>
                  <input
                    id="edit_title"
                    type="text"
                    className="form-input"
                    value={editFormData.title}
                    onChange={(e) => setEditFormData({ ...editFormData, title: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="edit_title_en">
                    Tên Hiện Vật Tiếng Anh (English)
                  </label>
                  <input
                    id="edit_title_en"
                    type="text"
                    className="form-input"
                    value={editFormData.title_en}
                    onChange={(e) => setEditFormData({ ...editFormData, title_en: e.target.value })}
                  />
                </div>

                {/* Hàng 3: Khu vực & Mã phòng */}
                <div className="form-group-row">
                  <div className="form-group" style={{ flex: 1 }}>
                    <label className="form-label" htmlFor="edit_zone">
                      Khu Vực Trưng Bày
                    </label>
                    <input
                      id="edit_zone"
                      type="text"
                      className="form-input"
                      value={editFormData.zone}
                      onChange={(e) => setEditFormData({ ...editFormData, zone: e.target.value })}
                    />
                  </div>

                  <div className="form-group" style={{ flex: 1 }}>
                    <label className="form-label" htmlFor="edit_room">
                      Mã Phòng / Bãi
                    </label>
                    <input
                      id="edit_room"
                      type="text"
                      className="form-input"
                      value={editFormData.room_id}
                      onChange={(e) => setEditFormData({ ...editFormData, room_id: e.target.value })}
                    />
                  </div>
                </div>

                {/* Hàng 4: Ảnh đại diện & Live preview */}
                <div className="form-group">
                  <div className="flex items-center justify-between">
                    <label className="form-label" htmlFor="edit_thumb">
                      Đường Dẫn Ảnh Đại Diện (Image URL)
                    </label>
                    <label className="btn btn-ghost btn-sm" style={{ cursor: 'pointer', fontSize: '0.75rem', padding: '2px 8px' }}>
                      <Camera size={13} />
                      <span>📁 Tải ảnh từ máy tính</span>
                      <input
                        type="file"
                        accept="image/*"
                        style={{ display: 'none' }}
                        onChange={(e) => handleFileSelect(e, 'edit')}
                      />
                    </label>
                  </div>

                  <div className="flex gap-2">
                    <input
                      id="edit_thumb"
                      type="text"
                      className="form-input"
                      style={{ flex: 1 }}
                      placeholder="Dán link ảnh (Unsplash, Google Drive, Imgur...) hoặc chọn ảnh từ máy tính"
                      value={editFormData.thumbnail_url}
                      onChange={(e) => handleThumbUrlChange(e.target.value, 'edit')}
                    />
                    {editFormData.thumbnail_url && (
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm"
                        onClick={() => {
                          setEditFormData({ ...editFormData, thumbnail_url: '' })
                          setEditImgStatus('idle')
                        }}
                        title="Xóa link ảnh"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                  <p className="text-xs text-muted" style={{ marginTop: '4px' }}>
                    💡 Hỗ trợ link ảnh trực tiếp (.jpg, .png, .webp), link chia sẻ <strong>Google Drive</strong> (tự động nhận diện), hoặc bấm <strong>"📁 Tải ảnh từ máy tính"</strong>.
                  </p>
                </div>

                {/* Khung xem trước ảnh */}
                <div className="edit-thumb-preview-box">
                  <div className="edit-thumb-preview-header flex items-center justify-between">
                    <span className="text-xs font-semibold">Xem trước ảnh thực tế:</span>
                    {editImgStatus === 'success' && (
                      <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>
                        <CheckCircle2 size={11} /> Ảnh hợp lệ
                      </span>
                    )}
                    {editImgStatus === 'loading' && (
                      <span className="text-xs text-amber font-semibold">Đang tải ảnh...</span>
                    )}
                    {editImgStatus === 'error' && (
                      <span className="badge badge-error" style={{ fontSize: '0.7rem' }}>
                        <AlertCircle size={11} /> Link không tải được ảnh
                      </span>
                    )}
                  </div>

                  {editFormData.thumbnail_url ? (
                    <div className="edit-thumb-preview-media">
                      <img
                        key={editFormData.thumbnail_url}
                        src={cleanImageUrl(editFormData.thumbnail_url)}
                        alt="Xem trước ảnh"
                        className="edit-thumb-preview-img"
                        onLoad={() => setEditImgStatus('success')}
                        onError={() => setEditImgStatus('error')}
                      />
                    </div>
                  ) : (
                    <div className="edit-thumb-preview-empty">
                      <ImageIcon size={32} style={{ opacity: 0.3 }} />
                      <span className="text-xs text-muted">Chưa có ảnh (dán URL hoặc chọn ảnh từ máy tính)</span>
                    </div>
                  )}

                  {editImgStatus === 'error' && (
                    <div className="alert-box alert-error animate-fade-in-up" style={{ marginTop: '8px', padding: '8px 12px' }}>
                      <AlertCircle size={14} />
                      <span className="text-xs">
                        Không thể hiển thị ảnh từ link này. Link có thể là trang web thay vì file ảnh, hoặc máy chủ ảnh chặn truy cập. Bạn có thể bấm nút <strong>"📁 Tải ảnh từ máy tính"</strong> ở trên hoặc chọn ảnh mẫu bên dưới:
                      </span>
                    </div>
                  )}
                </div>

                {/* Gợi ý một số link ảnh mẫu bảo tàng */}
                <div className="sample-thumbnails-picker">
                  <span className="text-xs text-muted">Hoặc chọn ảnh mẫu nhanh:</span>
                  <div className="sample-thumbs-row">
                    {[
                      { name: 'Máy bay tiêm kích', url: 'https://images.unsplash.com/photo-1508614589041-895b88991e3e?auto=format&fit=crop&w=800&q=80' },
                      { name: 'Xe tăng thiết giáp', url: 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=800&q=80' },
                      { name: 'Tài liệu lịch sử', url: 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?auto=format&fit=crop&w=800&q=80' },
                      { name: 'Bảo tàng & Di tích', url: 'https://images.unsplash.com/photo-1566127444979-b3d2b654e3d7?auto=format&fit=crop&w=800&q=80' }
                    ].map((item) => (
                      <button
                        key={item.name}
                        type="button"
                        className="sample-thumb-btn"
                        onClick={() => handleThumbUrlChange(item.url, 'edit')}
                      >
                        {item.name}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Hàng 5: Nội dung thuyết minh gốc tiếng Việt */}
                <div className="form-group">
                  <label className="form-label" htmlFor="edit_text">
                    Nội Dung Thuyết Minh Tiếng Việt Gốc <span className="text-danger">*</span>
                  </label>
                  <textarea
                    id="edit_text"
                    className="form-textarea"
                    rows={5}
                    placeholder="Nội dung thuyết minh chuẩn..."
                    value={editFormData.original_text}
                    onChange={(e) => setEditFormData({ ...editFormData, original_text: e.target.value })}
                    required
                  />
                  <p className="text-xs text-muted" style={{ marginTop: '4px' }}>
                    💡 Khi cập nhật bài thuyết minh, AI sẽ tự động áp dụng nội dung mới này cho du khách quét mã QR.
                  </p>
                </div>

                <div className="qr-modal-footer" style={{ marginTop: '0.5rem', padding: 0 }}>
                  <button
                    type="button"
                    className="btn btn-ghost btn-sm"
                    onClick={() => setEditingExhibit(null)}
                    disabled={isUpdatingExhibit}
                  >
                    Hủy bỏ
                  </button>

                  <button
                    type="submit"
                    className="btn btn-primary btn-sm"
                    disabled={isUpdatingExhibit || !editFormData.title.trim() || !editFormData.original_text.trim()}
                  >
                    {isUpdatingExhibit ? (
                      <>
                        <span className="spinner" />
                        <span>Đang lưu vào CSDL...</span>
                      </>
                    ) : (
                      <>
                        <Check size={14} />
                        <span>Lưu Thay Đổi Vào CSDL</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════════════════════════════
            MODAL HIỂN THỊ MÃ QR HIỆN VẬT
           ════════════════════════════════════════════════════════════════ */}
        {selectedQrExhibit && (
          <div className="qr-modal-backdrop" onClick={() => setSelectedQrExhibit(null)}>
            <div className="qr-modal-card glass-card animate-fade-in-up" onClick={(e) => e.stopPropagation()}>
              <div className="qr-modal-header">
                <div>
                  <span className="badge badge-amber">{selectedQrExhibit.display_code || selectedQrExhibit.code}</span>
                  <h3 className="text-base font-bold" style={{ marginTop: '4px' }}>
                    {selectedQrExhibit.title}
                  </h3>
                </div>
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  onClick={() => setSelectedQrExhibit(null)}
                >
                  ✕
                </button>
              </div>

              <div className="qr-modal-body">
                <div className="qr-modal-image-box">
                  {qrModalDataUrl ? (
                    <img src={qrModalDataUrl} alt="Mã QR" className="qr-modal-img" />
                  ) : (
                    <span className="spinner" />
                  )}
                </div>

                <div className="qr-modal-guide">
                  <p className="text-xs font-semibold text-amber">
                    📱 Hướng Camera điện thoại hoặc Zalo vào để nghe ngay!
                  </p>
                  <p className="text-xs text-muted" style={{ marginTop: '2px' }}>
                    Link đích: <code>/exhibit/{selectedQrExhibit.code}</code>
                  </p>
                </div>
              </div>

              <div className="qr-modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={handleCopyModalLink}
                >
                  {copiedLink ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
                  <span>{copiedLink ? 'Đã chép link' : 'Chép liên kết'}</span>
                </button>

                <a
                  href={qrModalDataUrl}
                  download={`QR_${selectedQrExhibit.code}.png`}
                  className="btn btn-primary btn-sm"
                >
                  <Download size={14} />
                  <span>Tải ảnh PNG</span>
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
