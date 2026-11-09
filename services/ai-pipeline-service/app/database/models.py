"""
models.py — SQLAlchemy ORM Models cho pipeline_db

Thành viên 2 sở hữu 5 bảng:
  1. SupportedLanguage  — Danh mục ngôn ngữ & cấu hình giọng TTS
  2. Glossary           — Từ điển chuẩn hóa thuật ngữ lịch sử
  3. Localization       — Bản dịch đa ngôn ngữ + timestamps phụ đề
  4. AudioMedia         — File âm thanh TTS đã sinh
  5. PipelineJob        — Trạng thái xử lý job (Celery Task Worker)

Nguyên tắc Decoupled FK:
  - exhibit_id, exhibit_code trong Localization & PipelineJob là Logical FK
    (chỉ là String, KHÔNG có FOREIGN KEY constraint sang exhibit_db)
  - Giao tiếp với exhibit-service qua HTTP API
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean,
    Text, DateTime, JSON, BigInteger, Numeric, ForeignKey
)
from sqlalchemy.orm import relationship
from app.database.connection import Base


# ================================================================
# BẢNG 1: SUPPORTED_LANGUAGE
# Config 15 ngôn ngữ — dùng bởi TTS Service & Translation Service
# ================================================================
class SupportedLanguage(Base):
    __tablename__ = "supported_language"

    code        = Column(String(10), primary_key=True)
    name_vi     = Column(String(100), nullable=False)
    native_name = Column(String(100), nullable=False)
    flag_icon   = Column(String(10), nullable=True)
    voice_code  = Column(String(50), nullable=True)   # Edge TTS neural voice
    is_active   = Column(Boolean, nullable=False, default=True)
    is_default  = Column(Boolean, nullable=False, default=False)
    sort_order  = Column(Integer, default=0)
    created_at  = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "code":        self.code,
            "name_vi":     self.name_vi,
            "native_name": self.native_name,
            "flag":        self.flag_icon,
            "voice_code":  self.voice_code,
            "is_default":  self.is_default,
        }


# ================================================================
# BẢNG 2: GLOSSARY
# Từ điển lịch sử - quân sự chuẩn hóa, áp dụng sau bước dịch
# ================================================================
class Glossary(Base):
    __tablename__ = "glossary"

    id           = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    term_vi      = Column(String(150), unique=True, nullable=False)
    term_en      = Column(String(150), nullable=False)
    context_note = Column(String(255), nullable=True)
    is_restricted = Column(Boolean, nullable=False, default=True)
    created_at   = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id":           self.id,
            "term_vi":      self.term_vi,
            "term_en":      self.term_en,
            "context_note": self.context_note,
        }


# ================================================================
# BẢNG 3: LOCALIZATION
# Output của Translation Service — bản dịch + phụ đề timestamps
# exhibit_id: Logical FK (string), không ràng buộc cross-DB
# ================================================================
class Localization(Base):
    __tablename__ = "localization"

    id               = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exhibit_id       = Column(String(36), nullable=False, index=True)   # Logical FK → exhibit_db
    exhibit_code     = Column(String(50), nullable=False, index=True)   # Denormalized
    language_code    = Column(String(10), nullable=False, index=True)
    translated_title = Column(String(255), nullable=False)
    translated_text  = Column(Text, nullable=False)
    timestamps_json  = Column(JSON, nullable=True)   # [{id, start, end, text}]
    content_version  = Column(Integer, nullable=False, default=1)
    is_reviewed      = Column(Boolean, nullable=False, default=False)
    created_at       = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship với AudioMedia (cùng pipeline_db — dùng FK thật)
    audio_files = relationship("AudioMedia", back_populates="localization", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id":               self.id,
            "exhibit_id":       self.exhibit_id,
            "exhibit_code":     self.exhibit_code,
            "language_code":    self.language_code,
            "translated_title": self.translated_title,
            "translated_text":  self.translated_text,
            "timestamps_json":  self.timestamps_json or [],
            "content_version":  self.content_version,
            "is_reviewed":      self.is_reviewed,
        }


# ================================================================
# BẢNG 4: AUDIO_MEDIA
# Output của TTS Service — file âm thanh Edge TTS Neural
# localization_id: FK thật trong cùng pipeline_db
# ================================================================
class AudioMedia(Base):
    __tablename__ = "audio_media"

    id               = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    localization_id  = Column(String(36), ForeignKey("localization.id", ondelete="CASCADE"), nullable=False, index=True)   # FK -> localization.id (cùng DB)
    file_url         = Column(String(500), nullable=False)   # URL web: /output/CODE/CODE_en.mp3
    storage_path     = Column(String(255), nullable=False)   # Đường dẫn disk tuyệt đối
    duration_seconds = Column(Float, nullable=False, default=0.0)
    bitrate_kbps     = Column(Integer, default=128)
    voice_code       = Column(String(50), nullable=True)     # Voice model đã dùng sinh file
    status           = Column(String(20), nullable=False, default="ready")
    # status: 'pending' | 'processing' | 'ready' | 'error'
    created_at       = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship ngược về Localization
    localization = relationship("Localization", back_populates="audio_files")

    def to_dict(self):
        return {
            "id":               self.id,
            "localization_id":  self.localization_id,
            "file_url":         self.file_url,
            "duration_seconds": self.duration_seconds,
            "voice_code":       self.voice_code,
            "status":           self.status,
        }


# ================================================================
# BẢNG 5: PIPELINE_JOB  (MỚI)
# Theo dõi trạng thái xử lý pipeline cho Celery Task Worker
# Mỗi job = 1 lần yêu cầu sinh audio cho 1 hiện vật N ngôn ngữ
# ================================================================
class PipelineJob(Base):
    __tablename__ = "pipeline_job"

    id               = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id          = Column(String(100), unique=True, nullable=False)  # Celery task UUID
    exhibit_id       = Column(String(36), nullable=False, index=True)    # Logical FK → exhibit_db
    exhibit_code     = Column(String(50), nullable=False, index=True)
    target_languages = Column(JSON, nullable=False, default=list)         # ["en", "fr", "ja", ...]
    status           = Column(String(20), nullable=False, default="pending", index=True)
    # status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
    priority         = Column(Integer, nullable=False, default=5)         # 1 (cao) → 10 (thấp)
    error_message    = Column(Text, nullable=True)
    retry_count      = Column(Integer, nullable=False, default=0)
    max_retries      = Column(Integer, nullable=False, default=3)
    started_at       = Column(DateTime, nullable=True)
    completed_at     = Column(DateTime, nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self):
        return {
            "id":               self.id,
            "task_id":          self.task_id,
            "exhibit_code":     self.exhibit_code,
            "target_languages": self.target_languages,
            "status":           self.status,
            "priority":         self.priority,
            "retry_count":      self.retry_count,
            "error_message":    self.error_message,
            "created_at":       self.created_at.isoformat() if self.created_at else None,
            "started_at":       self.started_at.isoformat() if self.started_at else None,
            "completed_at":     self.completed_at.isoformat() if self.completed_at else None,
        }
