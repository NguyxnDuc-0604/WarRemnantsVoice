import { useEffect, useRef, useState } from 'react'
import { Html5Qrcode, Html5QrcodeSupportedFormats } from 'html5-qrcode'
import { Camera, Image, RefreshCw, AlertCircle, CheckCircle2, SwitchCamera } from 'lucide-react'
import './QRScanner.css'

export default function QRScanner({ onScanSuccess, isActive = true }) {
  const scannerContainerId = 'qr-reader-container'
  const html5QrCodeRef = useRef(null)
  const fileInputRef = useRef(null)

  const [isScanning, setIsScanning] = useState(false)
  const [errorMessage, setErrorMessage] = useState(null)
  const [cameras, setCameras] = useState([])
  const [selectedCameraId, setSelectedCameraId] = useState('')
  const [scannedResult, setScannedResult] = useState(null)

  // Phát âm thanh beep nhẹ khi quét trúng bằng Web Audio API
  const playBeep = () => {
    try {
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)()
      const osc = audioCtx.createOscillator()
      const gain = audioCtx.createGain()
      osc.type = 'sine'
      osc.frequency.setValueAtTime(880, audioCtx.currentTime) // Nốt A5
      gain.gain.setValueAtTime(0.15, audioCtx.currentTime)
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.18)
      osc.connect(gain)
      gain.connect(audioCtx.destination)
      osc.start()
      osc.stop(audioCtx.currentTime + 0.18)
    } catch (e) {
      // AudioContext có thể bị hạn chế nếu chưa tương tác người dùng
    }

    // Rung điện thoại nếu hỗ trợ
    if (navigator.vibrate) {
      try {
        navigator.vibrate(80)
      } catch (e) {}
    }
  }

  // Khởi tạo và lấy danh sách camera
  useEffect(() => {
    let isMounted = true

    Html5Qrcode.getCameras()
      .then((devices) => {
        if (!isMounted) return
        if (devices && devices.length > 0) {
          setCameras(devices)
          // Ưu tiên camera sau (back / environment)
          const backCam = devices.find((d) =>
            d.label.toLowerCase().includes('back') ||
            d.label.toLowerCase().includes('rear') ||
            d.label.toLowerCase().includes('environment')
          )
          setSelectedCameraId(backCam ? backCam.id : devices[0].id)
        } else {
          setErrorMessage('Không tìm thấy camera trên thiết bị.')
        }
      })
      .catch((err) => {
        if (!isMounted) return
        console.warn('Lỗi lấy camera:', err)
        setErrorMessage('Không thể truy cập camera. Vui lòng cấp quyền camera trong cài đặt trình duyệt hoặc sử dụng tính năng tải ảnh.')
      })

    return () => {
      isMounted = false
      stopScanner()
    }
  }, [])

  // Bắt đầu quét camera khi camera ID đã sẵn sàng
  useEffect(() => {
    if (isActive && selectedCameraId && !isScanning && !scannedResult) {
      startScanner(selectedCameraId)
    }
  }, [isActive, selectedCameraId])

  const startScanner = async (cameraId) => {
    try {
      setErrorMessage(null)
      if (html5QrCodeRef.current && html5QrCodeRef.current.isScanning) {
        await html5QrCodeRef.current.stop()
      }

      const qrCode = new Html5Qrcode(scannerContainerId, {
        formatsToSupport: [Html5QrcodeSupportedFormats.QR_CODE],
        verbose: false,
      })
      html5QrCodeRef.current = qrCode

      const config = {
        fps: 12,
        qrbox: { width: 250, height: 250 },
        aspectRatio: 1.0,
      }

      await qrCode.start(
        cameraId,
        config,
        (decodedText) => {
          handleSuccess(decodedText)
        },
        () => {
          // Frame không có QR - bỏ qua
        }
      )

      setIsScanning(true)
    } catch (err) {
      console.error('Không thể khởi động camera:', err)
      setIsScanning(false)
      setErrorMessage('Không thể mở camera. Lưu ý: Trình duyệt điện thoại chỉ cho phép camera qua HTTPS hoặc localhost.')
    }
  }

  const stopScanner = async () => {
    try {
      if (html5QrCodeRef.current && html5QrCodeRef.current.isScanning) {
        await html5QrCodeRef.current.stop()
        await html5QrCodeRef.current.clear()
      }
    } catch (e) {
      console.warn('Lỗi khi tắt camera:', e)
    } finally {
      setIsScanning(false)
    }
  }

  const handleSuccess = (decodedText) => {
    playBeep()
    setScannedResult(decodedText)
    stopScanner()
    if (onScanSuccess) {
      onScanSuccess(decodedText)
    }
  }

  // Quét từ file ảnh upload
  const handleFileUpload = async (event) => {
    const file = event.target.files && event.target.files[0]
    if (!file) return

    setErrorMessage(null)
    try {
      await stopScanner()
      const qrCode = new Html5Qrcode('qr-reader-temp-file', {
        formatsToSupport: [Html5QrcodeSupportedFormats.QR_CODE],
      })
      const decodedText = await qrCode.scanFile(file, true)
      handleSuccess(decodedText)
    } catch (err) {
      console.error('Lỗi quét ảnh QR:', err)
      setErrorMessage('Không tìm thấy mã QR trong ảnh này. Vui lòng chụp rõ nét hơn hoặc thử lại.')
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  // Chuyển đổi camera (trước / sau)
  const handleSwitchCamera = () => {
    if (cameras.length <= 1) return
    const currentIndex = cameras.findIndex((c) => c.id === selectedCameraId)
    const nextIndex = (currentIndex + 1) % cameras.length
    const nextCamera = cameras[nextIndex]
    setSelectedCameraId(nextCamera.id)
    startScanner(nextCamera.id)
  }

  const handleRescan = () => {
    setScannedResult(null)
    setErrorMessage(null)
    if (selectedCameraId) {
      startScanner(selectedCameraId)
    }
  }

  return (
    <div className="qr-scanner-card glass-card">
      <div className="qr-scanner__header">
        <div className="qr-scanner__badge badge badge-amber">
          <Camera size={13} />
          <span>Camera Scanner</span>
        </div>
        <div className="qr-scanner__controls">
          {cameras.length > 1 && (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={handleSwitchCamera}
              title="Đổi camera"
            >
              <SwitchCamera size={16} />
              <span className="hide-on-mobile">Đổi Camera</span>
            </button>
          )}

          <button
            type="button"
            className="btn btn-ghost btn-sm"
            onClick={() => fileInputRef.current?.click()}
            title="Tải ảnh mã QR"
          >
            <Image size={16} />
            <span>Tải ảnh</span>
          </button>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept="image/*"
            style={{ display: 'none' }}
          />
        </div>
      </div>

      {/* Viewfinder scanner box */}
      <div className="qr-scanner__viewport-wrapper">
        <div id={scannerContainerId} className="qr-scanner__video-container" />
        <div id="qr-reader-temp-file" style={{ display: 'none' }} />

        {/* Khung ngắm laser nếu đang quét */}
        {isScanning && !scannedResult && (
          <div className="qr-scanner__overlay">
            <div className="qr-scanner__target-box">
              <span className="corner corner-tl" />
              <span className="corner corner-tr" />
              <span className="corner corner-bl" />
              <span className="corner corner-br" />
              <div className="scanner-laser-line" />
            </div>
            <p className="qr-scanner__guide-text">
              Di chuyển mã QR vào trong khung ngắm
            </p>
          </div>
        )}

        {/* Trạng thái đã quét thành công */}
        {scannedResult && (
          <div className="qr-scanner__result-banner animate-fade-in-up">
            <CheckCircle2 size={24} style={{ color: 'var(--color-success)' }} />
            <div className="qr-scanner__result-info">
              <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                Đã nhận diện mã:
              </span>
              <strong className="text-sm font-semibold gradient-text">
                {scannedResult}
              </strong>
            </div>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={handleRescan}
              style={{ marginLeft: 'auto' }}
            >
              <RefreshCw size={14} />
              Quét lại
            </button>
          </div>
        )}
      </div>

      {/* Thông báo lỗi nếu có */}
      {errorMessage && (
        <div className="qr-scanner__error animate-fade-in-up">
          <AlertCircle size={16} style={{ color: 'var(--color-error)', flexShrink: 0 }} />
          <span className="text-xs">{errorMessage}</span>
        </div>
      )}
    </div>
  )
}
