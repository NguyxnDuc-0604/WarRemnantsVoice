import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger("analytics-database")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "analytics.db"))
DATABASE_URL = os.getenv("ANALYTICS_DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

try:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
        pool_pre_ping=True if "sqlite" not in DATABASE_URL else False
    )
    with engine.connect() as conn:
        pass
except Exception as e:
    logger.warning(f"Failed to connect to primary analytics DB ({e}). Falling back to SQLite...")
    DATABASE_URL = f"sqlite:///{DEFAULT_DB_PATH}"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ListeningMetric(Base):
    __tablename__ = "listening_metric"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exhibit_code = Column(String(50), nullable=False)
    language_code = Column(String(10), default="vi")
    listened_duration = Column(Integer, default=0)
    trigger_type = Column(String(50), default="QR_CODE")
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_analytics_db():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning(f"init_analytics_db error: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
