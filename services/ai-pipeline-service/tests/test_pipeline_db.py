"""
test_pipeline_db.py — Unit Tests cho Pipeline Database & Decoupled Logical Foreign Keys
Thành viên 2: AI & Pipeline Processing Services
"""

import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base
from app.database.models import (
    SupportedLanguage,
    Glossary,
    Localization,
    AudioMedia,
    PipelineJob
)
from app.database.seed import seed_pipeline_database

# Tạo database SQLite in-memory biệt lập hoàn toàn cho unit test
TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_db():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_pipeline_seed_data(test_db):
    """Kiểm tra auto-seed 15 ngôn ngữ và 10 thuật ngữ glossary vào pipeline_db"""
    seed_pipeline_database(test_db)
    
    lang_count = test_db.query(SupportedLanguage).count()
    assert lang_count == 15
    
    vi_lang = test_db.query(SupportedLanguage).filter_by(code="vi").first()
    assert vi_lang is not None
    assert vi_lang.name_vi == "Tiếng Việt"
    assert vi_lang.is_default is True

    glossary_count = test_db.query(Glossary).count()
    assert glossary_count == 10
    
    term = test_db.query(Glossary).filter_by(term_vi="Ấp Bắc").first()
    assert term is not None
    assert term.term_en == "Ap Bac"

def test_decoupled_localization_and_audio(test_db):
    """
    Kiểm tra tạo Localization và AudioMedia với Logical FK exhibit_id
    Không bị phụ thuộc vào bảng exhibit của exhibit_db (Microservices Decoupling)
    """
    # Không cần tạo Exhibit, Localization vẫn hoạt động độc lập với logical exhibit_id
    fake_exhibit_id = str(uuid.uuid4())
    fake_code = "UH1-BELL"

    loc = Localization(
        id=str(uuid.uuid4()),
        exhibit_id=fake_exhibit_id,
        exhibit_code=fake_code,
        language_code="en",
        translated_title="UH-1 Iroquois Helicopter",
        translated_text="The UH-1 Iroquois is an iconic military helicopter.",
        timestamps_json=[{"id": 0, "start": 0.0, "end": 3.5, "text": "The UH-1 Iroquois is an iconic military helicopter."}],
        content_version=1,
        is_reviewed=True
    )
    test_db.add(loc)
    test_db.commit()

    # Thêm audio media liên kết với localization
    audio = AudioMedia(
        id=str(uuid.uuid4()),
        localization_id=loc.id,
        file_url=f"/output/{fake_code}/{fake_code}_en.mp3",
        storage_path=f"./output/{fake_code}/{fake_code}_en.mp3",
        duration_seconds=3.5,
        bitrate_kbps=128,
        voice_code="en-US-AndrewNeural",
        status="ready"
    )
    test_db.add(audio)
    test_db.commit()

    saved_loc = test_db.query(Localization).filter_by(exhibit_code=fake_code).first()
    assert saved_loc is not None
    assert len(saved_loc.audio_files) == 1
    assert saved_loc.audio_files[0].voice_code == "en-US-AndrewNeural"

def test_pipeline_job_lifecycle(test_db):
    """Kiểm tra vòng đời của PipelineJob (pending -> processing -> completed)"""
    job = PipelineJob(
        id=str(uuid.uuid4()),
        task_id="celery-task-12345",
        exhibit_id=str(uuid.uuid4()),
        exhibit_code="T54-390",
        target_languages=["en", "fr", "ja"],
        status="pending",
        priority=1
    )
    test_db.add(job)
    test_db.commit()

    # Kiểm tra truy vấn
    query_job = test_db.query(PipelineJob).filter_by(task_id="celery-task-12345").first()
    assert query_job is not None
    assert query_job.status == "pending"

    # Chuyển trạng thái
    query_job.status = "completed"
    test_db.commit()

    updated_job = test_db.query(PipelineJob).filter_by(task_id="celery-task-12345").first()
    assert updated_job.status == "completed"
