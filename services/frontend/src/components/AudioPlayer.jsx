import { useState, useRef, useEffect } from 'react'
import { Play, Pause, Volume2, Download, RotateCcw } from 'lucide-react'
import './AudioPlayer.css'

/**
 * AudioPlayer — trình phát audio với UI tùy chỉnh đẹp
 */
export default function AudioPlayer({ src, language, langLabel }) {
  const audioRef = useRef(null)
  const progressRef = useRef(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [duration, setDuration] = useState(0)
  const [currentTime, setCurrentTime] = useState(0)
  const [volume, setVolume] = useState(1)

  // Reset khi src thay đổi
  useEffect(() => {
    setIsPlaying(false)
    setProgress(0)
    setCurrentTime(0)
  }, [src])

  const togglePlay = async () => {
    const audio = audioRef.current
    if (!audio) return
    if (isPlaying) {
      audio.pause()
    } else {
      await audio.play()
    }
  }

  const handleTimeUpdate = () => {
    const audio = audioRef.current
    if (!audio) return
    const pct = (audio.currentTime / audio.duration) * 100
    setProgress(isNaN(pct) ? 0 : pct)
    setCurrentTime(audio.currentTime)
  }

  const handleLoadedMetadata = () => {
    setDuration(audioRef.current?.duration || 0)
  }

  const handleProgressClick = (e) => {
    const rect = progressRef.current.getBoundingClientRect()
    const pct = (e.clientX - rect.left) / rect.width
    const audio = audioRef.current
    if (!audio) return
    audio.currentTime = pct * audio.duration
  }

  const handleEnded = () => setIsPlaying(false)

  const formatTime = (s) => {
    if (isNaN(s)) return '0:00'
    const m = Math.floor(s / 60)
    const sec = Math.floor(s % 60)
    return `${m}:${sec.toString().padStart(2, '0')}`
  }

  const handleReplay = () => {
    const audio = audioRef.current
    if (!audio) return
    audio.currentTime = 0
    audio.play()
  }

  return (
    <div className="audio-player">
      <audio
        ref={audioRef}
        src={src}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={handleEnded}
        preload="metadata"
      />

      {/* Language badge */}
      <div className="audio-player__header">
        <span className="badge badge-amber">{langLabel || language}</span>
        <span className="audio-player__time text-xs">
          {formatTime(currentTime)} / {formatTime(duration)}
        </span>
      </div>

      {/* Progress bar */}
      <div
        className="audio-player__progress"
        ref={progressRef}
        onClick={handleProgressClick}
      >
        <div
          className="audio-player__progress-fill"
          style={{ width: `${progress}%` }}
        />
        <div
          className="audio-player__progress-thumb"
          style={{ left: `${progress}%` }}
        />
      </div>

      {/* Controls */}
      <div className="audio-player__controls">
        <button
          className="audio-player__replay-btn"
          onClick={handleReplay}
          title="Phát lại từ đầu"
        >
          <RotateCcw size={14} />
        </button>

        <button
          className={`audio-player__play-btn ${isPlaying ? 'audio-player__play-btn--playing' : ''}`}
          onClick={togglePlay}
        >
          {isPlaying ? <Pause size={18} /> : <Play size={18} />}
        </button>

        <div className="audio-player__volume">
          <Volume2 size={14} style={{ color: 'var(--color-text-muted)', flexShrink: 0 }} />
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={volume}
            onChange={(e) => {
              const v = parseFloat(e.target.value)
              setVolume(v)
              if (audioRef.current) audioRef.current.volume = v
            }}
            className="audio-player__volume-slider"
          />
        </div>

        <a
          href={src}
          download
          className="audio-player__download-btn"
          title="Tải xuống"
        >
          <Download size={14} />
        </a>
      </div>
    </div>
  )
}
