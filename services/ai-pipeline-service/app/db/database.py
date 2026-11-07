import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Xác định đường dẫn tuyệt đối đến thư mục gốc của dự án
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
DEFAULT_DB_FILE = os.path.join(PROJECT_ROOT, "war_remnants_museum.db").replace("\\", "/")

# Lấy DATABASE_URL từ biến môi trường (Docker PostgreSQL hoặc Local SQLite fallback)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DEFAULT_DB_FILE}" # Cố định tuyệt đối vào war_remnants_museum.db ở thư mục gốc
)

# Cấu hình engine phù hợp cho SQLite và PostgreSQL
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency cung cấp DB session cho FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
