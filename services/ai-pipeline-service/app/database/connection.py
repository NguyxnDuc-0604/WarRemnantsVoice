"""
connection.py — Kết nối tới pipeline_db (Database riêng của AI Pipeline Service)

Kiến trúc Database-per-Service:
  - Service này SỞ HỮU: pipeline_db
  - Các bảng thuộc quyền: supported_language, glossary,
                           localization, audio_media, pipeline_job
  - KHÔNG truy cập trực tiếp: exhibit_db, gateway_db
  - Giao tiếp với service khác qua: HTTP API (không dùng JOIN cross-DB)

Môi trường:
  - Local (không Docker): SQLite — pipeline_db.sqlite3
  - Docker / Production:  PostgreSQL — DATABASE_URL từ biến môi trường
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ================================================================
# Xác định đường dẫn gốc dự án để đặt file SQLite
# ================================================================
_SERVICE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_PROJECT_ROOT = os.path.abspath(os.path.join(_SERVICE_DIR, "..", ".."))

# File SQLite riêng cho pipeline service (KHÔNG dùng chung war_remnants_museum.db)
_DEFAULT_SQLITE = os.path.join(_PROJECT_ROOT, "pipeline_db.sqlite3").replace("\\", "/")

# Lấy DATABASE_URL từ biến môi trường
# Trong docker-compose: DATABASE_URL=postgresql://pipeline_user:pipeline_pass@pipeline_db:5432/pipeline_db
DATABASE_URL: str = os.getenv("PIPELINE_DATABASE_URL", f"sqlite:///{_DEFAULT_SQLITE}")

# ================================================================
# Tạo Engine phù hợp cho từng loại database
# ================================================================
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Bắt buộc với SQLite + FastAPI async
        echo=False
    )
else:
    # PostgreSQL — dùng khi chạy Docker
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,   # Tự động reconnect nếu mất kết nối
        pool_size=10,
        max_overflow=20,
        echo=False
    )

# ================================================================
# Session & Base
# ================================================================
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    FastAPI Dependency — cung cấp DB session cho mỗi request.
    Tự động đóng session sau khi request hoàn thành.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
