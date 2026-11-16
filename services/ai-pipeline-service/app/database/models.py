
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    func
)

from app.database.connection import Base


# 1. Quản lý tác vụ AI
class PipelineTask(Base):
    __tablename__ = "pipeline_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(100), unique=True, nullable=False)
    exhibit_id = Column(String(100), nullable=False)
    original_text = Column(Text)
    status = Column(String(30), default="pending")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )


# 2. Theo dõi các bước xử lý
class ProcessingStep(Base):
    __tablename__ = "processing_steps"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(
        String(100),
        ForeignKey("pipeline_tasks.task_id")
    )
    step_name = Column(String(50), nullable=False)
    status = Column(String(30), default="pending")
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)


# 3. Lưu bản dịch
class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(
        String(100),
        ForeignKey("pipeline_tasks.task_id")
    )
    language = Column(String(10), nullable=False)
    translated_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


# 4. Quản lý file âm thanh
class GeneratedAudio(Base):
    __tablename__ = "generated_audio"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(
        String(100),
        ForeignKey("pipeline_tasks.task_id")
    )
    language = Column(String(10), nullable=False)
    audio_file_path = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


# 5. Nhật ký xử lý
class PipelineLog(Base):
    __tablename__ = "pipeline_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(
        String(100),
        ForeignKey("pipeline_tasks.task_id")
    )
    log_level = Column(String(20), default="INFO")
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
