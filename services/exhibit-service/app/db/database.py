import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger("exhibit-database")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "exhibits.db"))
DATABASE_URL = os.getenv("EXHIBIT_DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# Chuẩn hóa postgresql:// sang postgresql+psycopg2:// nếu dùng PostgreSQL
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

try:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
        pool_pre_ping=True if "sqlite" not in DATABASE_URL else False,
        echo=False
    )
    # Test connection
    with engine.connect() as conn:
        pass
    logger.info(f"Connected to database successfully: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
except Exception as e:
    logger.warning(f"Failed to connect to primary DB ({e}). Falling back to SQLite exhibits.db...")
    DATABASE_URL = f"sqlite:///{DEFAULT_DB_PATH}"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
