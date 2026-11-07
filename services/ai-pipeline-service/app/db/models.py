import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    DateTime,
    JSON,
    ForeignKey,
    BigInteger
)
from sqlalchemy.orm import relationship
from app.db.database import Base

class Exhibit(Base):
    __tablename__ = "exhibit"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    title_en = Column(String(255), nullable=True)
    room_id = Column(String(50), nullable=False)
    zone = Column(String(100), default="Khu trưng bày")
    period = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    radius = Column(Integer, default=15)
    thumbnail_url = Column(Text, nullable=True)
    content_version = Column(Integer, nullable=False, default=1)
    is_published = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    content_sources = relationship("ContentSource", back_populates="exhibit", cascade="all, delete-orphan")


class ContentSource(Base):
    __tablename__ = "content_source"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exhibit_id = Column(String(36), ForeignKey("exhibit.id", ondelete="CASCADE"), nullable=False)
    original_text = Column(Text, nullable=True)
    original_audio_url = Column(String(500), nullable=True)
    content_version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    exhibit = relationship("Exhibit", back_populates="content_sources")


class Localization(Base):
    __tablename__ = "localization"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exhibit_id = Column(String(36), nullable=False, index=True) # Decoupled logical FK
    language_code = Column(String(10), nullable=False, index=True)
    translated_title = Column(String(255), nullable=False)
    translated_text = Column(Text, nullable=False)
    timestamps_json = Column(JSON, nullable=True)
    content_version = Column(Integer, nullable=False, default=1)
    is_reviewed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class AudioMedia(Base):
    __tablename__ = "audio_media"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    localization_id = Column(String(36), nullable=False, index=True) # Decoupled logical FK
    file_url = Column(String(500), nullable=False)
    storage_path = Column(String(255), nullable=False)
    duration_seconds = Column(Float, nullable=False, default=0.0)
    bitrate_kbps = Column(Integer, default=128)
    voice_code = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default="ready")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TourRoute(Base):
    __tablename__ = "tour_route"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    ordered_exhibits_json = Column(JSON, nullable=False)
    estimated_time = Column(Integer, nullable=False, default=45) # in minutes
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Glossary(Base):
    __tablename__ = "glossary"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    term_vi = Column(String(150), unique=True, nullable=False)
    term_en = Column(String(150), nullable=False)
    context_note = Column(String(255), nullable=True)
    is_restricted = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ListeningMetric(Base):
    __tablename__ = "listening_metric"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    exhibit_id = Column(String(36), nullable=True)
    exhibit_code = Column(String(50), nullable=True)
    language_code = Column(String(10), nullable=False)
    listened_duration = Column(Integer, nullable=False)
    trigger_type = Column(String(20), nullable=False, default="QR_CODE")
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class SupportedLanguage(Base):
    __tablename__ = "supported_language"

    code = Column(String(10), primary_key=True)
    name_vi = Column(String(100), nullable=False)
    native_name = Column(String(100), nullable=False)
    flag_icon = Column(String(10), nullable=True)
    voice_code = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    is_default = Column(Boolean, nullable=False, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

