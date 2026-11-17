import os
import re
import uuid
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx

from .db.database import engine, Base, SessionLocal, get_db
from .db.models import (
    Exhibit,
    ContentSource,
    Localization,
    AudioMedia,
    TourRoute,
    Glossary,
    SupportedLanguage
)
from .db.seed import seed_database

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [EXHIBIT] %(message)s")
logger = logging.getLogger("exhibit-service")

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8003").rstrip("/")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo bảng CSDL và nạp dữ liệu mẫu theo PRD nếu chưa có
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_database(db)
        finally:
            db.close()
        logger.info("Exhibit Database initialized and verified.")
    except Exception as err:
        logger.error(f"DB-INIT-WARN: {err}")
    yield

app = FastAPI(
    title="WarRemnantsVoice - Exhibit Core Service",
    description="Dịch vụ lõi quản lý thông tin hiện vật, phân khu, tuyến tham quan và dữ liệu thuyết minh theo chuẩn PRD",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class CreateExhibitRequest(BaseModel):
    code: str
    title: str
    title_en: Optional[str] = ""
    zone: Optional[str] = "Khu trưng bày"
    room_id: Optional[str] = "ROOM-01"
    period: Optional[str] = ""
    thumbnail_url: Optional[str] = ""
    original_text: str

class UpdateExhibitThumbnailRequest(BaseModel):
    thumbnail_url: str

class UpdateExhibitRequest(BaseModel):
    title: Optional[str] = None
    title_en: Optional[str] = None
    zone: Optional[str] = None
    room_id: Optional[str] = None
    period: Optional[str] = None
    thumbnail_url: Optional[str] = None
    original_text: Optional[str] = None

def format_exhibit_response(exhibit: Exhibit, db: Session, idx: int = 1) -> dict:
    """Format đối tượng Exhibit ORM thành dictionary đầy đủ cho Frontend"""
    content_src = db.query(ContentSource).filter_by(exhibit_id=exhibit.id).first()
    original_text = content_src.original_text if content_src else ""
    return {
        "id": exhibit.id,
        "code": exhibit.code,
        "display_code": f"EX-{idx:02d}",
        "title": exhibit.title,
        "title_en": exhibit.title_en or exhibit.title,
        "room_id": exhibit.room_id,
        "zone": exhibit.zone,
        "period": exhibit.period or "",
        "latitude": exhibit.latitude,
        "longitude": exhibit.longitude,
        "radius": exhibit.radius,
        "thumbnail_url": exhibit.thumbnail_url,
        "original_text": original_text,
        "content_version": exhibit.content_version,
        "is_published": exhibit.is_published,
        "created_at": exhibit.created_at.isoformat() if exhibit.created_at else None
    }

# Subtitle timestamp generator fallback
def generate_subtitle_timestamps(text: str, total_duration: float = None):
    raw_sentences = re.split(r'(?<=[.!?。！？])\s+', text.strip())
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    if not sentences:
        sentences = [text.strip()]
    total_chars = max(sum(len(s) for s in sentences), 1)
    duration = total_duration if total_duration else max(len(text) * 0.07, 3.5)
    timestamps = []
    current_time = 0.0
    for idx, sentence in enumerate(sentences):
        sentence_duration = max((len(sentence) / total_chars) * duration, 1.2)
        end_time = round(current_time + sentence_duration, 2)
        timestamps.append({
            "id": idx,
            "start": round(current_time, 2),
            "end": end_time,
            "text": sentence
        })
        current_time = end_time
    return timestamps

@app.get("/")
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    count = db.query(Exhibit).count()
    return {
        "service": "Exhibit Core Service",
        "status": "UP",
        "exhibits_count": count
    }

@app.get("/api/v1/exhibits")
def get_all_exhibits(db: Session = Depends(get_db)):
    exhibits = db.query(Exhibit).filter(Exhibit.is_active == True).order_by(Exhibit.created_at.asc()).all()
    results = []
    for idx, ex in enumerate(exhibits, 1):
        formatted = format_exhibit_response(ex, db, idx)
        next_idx = (idx % len(exhibits))
        formatted["next_code"] = exhibits[next_idx].code if len(exhibits) > 1 else None
        results.append(formatted)
    return results

def find_exhibit_by_identifier(db: Session, identifier: str) -> Optional[Exhibit]:
    """Tìm hiện vật an toàn theo code hoặc ID UUID, tránh lỗi Type UUID trên PostgreSQL"""
    if not identifier:
        return None
    raw_str = identifier.strip()
    clean_id = raw_str.upper()

    # 1. Tìm theo mã code chính xác (VD: UH1-BELL)
    exhibit = db.query(Exhibit).filter(Exhibit.code == clean_id).first()
    if exhibit:
        return exhibit

    # 2. Kiểm tra nếu là UUID hợp lệ thì mới truy vấn id
    try:
        val_uuid = uuid.UUID(raw_str)
        exhibit = db.query(Exhibit).filter(Exhibit.id == str(val_uuid)).first()
        if exhibit:
            return exhibit
    except (ValueError, TypeError, AttributeError):
        pass

    # 3. Tìm kiếm tương đối theo mã code
    exhibits = db.query(Exhibit).all()
    clean_stripped = clean_id.replace('-', '').replace('_', '')
    for ex in exhibits:
        if clean_stripped in ex.code.upper().replace('-', '').replace('_', ''):
            return ex

    return None

@app.get("/api/v1/exhibits/{identifier}")
def get_exhibit_by_code_or_id(identifier: str, db: Session = Depends(get_db)):
    exhibit = find_exhibit_by_identifier(db, identifier)
    if not exhibit:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy hiện vật với mã '{identifier}'")

    return format_exhibit_response(exhibit, db)

@app.get("/api/v1/exhibits/{identifier}/audio")
async def get_exhibit_audio(identifier: str, lang: str = Query("en"), db: Session = Depends(get_db)):
    exhibit = find_exhibit_by_identifier(db, identifier)
    if not exhibit:
        raise HTTPException(status_code=404, detail=f"Hiện vật '{identifier}' không tồn tại.")

    content_src = db.query(ContentSource).filter_by(exhibit_id=exhibit.id).first()
    original_text = content_src.original_text if content_src else exhibit.title

    # Kiểm tra trong Localization và AudioMedia đã có sẵn chưa
    # Chuẩn hoá mã ngôn ngữ: hỗ trợ cả zh lẫn zh-CN
    lang_candidates = [lang]
    if lang.lower() in ["zh", "zh-cn"]:
        lang_candidates = ["zh-CN", "zh", "zh-cn"]

    loc = db.query(Localization).filter(
        Localization.exhibit_id == exhibit.id,
        Localization.language_code.in_(lang_candidates),
        Localization.content_version == exhibit.content_version
    ).first()
    
    if loc:
        # Kiểm tra xem bản dịch có bị lỗi trả về tiếng Việt gốc không
        is_bad_vietnamese = (
            lang not in ["vi", "vi-vn", "vi-VN"] and
            loc.translated_text and
            original_text and
            (loc.translated_text.strip() == original_text.strip() or loc.translated_text.strip().startswith(original_text.strip()[:40]))
        )
        if not is_bad_vietnamese:
            audio_rec = db.query(AudioMedia).filter_by(localization_id=loc.id).first()
            if audio_rec:
                return {
                    "exhibit_code": exhibit.code,
                    "language": lang,
                    "translated_title": loc.translated_title,
                    "translated_text": loc.translated_text,
                    "original_text": original_text,
                    "audio_file_path": audio_rec.file_url,
                    "timestamps_json": loc.timestamps_json or [],
                    "duration_seconds": audio_rec.duration_seconds
                }
        else:
            logger.warning(f"Discarding corrupt Vietnamese text in '{loc.language_code}' localization for {exhibit.code}")
            db.delete(loc)
            db.commit()
            loc = None

    # Nếu chưa có, gọi AI Pipeline Service sinh audio & bản dịch qua HTTP inter-service
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            ai_req_payload = {
                "exhibit_code": exhibit.code,
                "title": exhibit.title,
                "original_text": original_text,
                "language": lang
            }
            ai_res = await client.post(f"{AI_SERVICE_URL}/api/v1/internal/generate-audio", json=ai_req_payload)
            if ai_res.status_code == 200:
                data = ai_res.json()
                translated_title = data.get("translated_title", exhibit.title)
                translated_text = data.get("translated_text", original_text)
                audio_url = data.get("audio_url", f"/output/{exhibit.code}/{exhibit.code}_{lang}.mp3")
                timestamps = data.get("timestamps", generate_subtitle_timestamps(translated_text))
                duration = data.get("duration", 30.0)

                # Lưu vào DB để cache lại
                if not loc:
                    loc = Localization(
                        exhibit_id=exhibit.id,
                        language_code=lang,
                        translated_title=translated_title,
                        translated_text=translated_text,
                        timestamps_json=timestamps,
                        content_version=exhibit.content_version,
                        is_reviewed=False
                    )
                    db.add(loc)
                    db.flush()
                
                audio_rec = db.query(AudioMedia).filter_by(localization_id=loc.id).first()
                if not audio_rec:
                    audio_rec = AudioMedia(
                        localization_id=loc.id,
                        file_url=audio_url,
                        storage_path=f"output/{exhibit.code}/{exhibit.code}_{lang}.mp3",
                        duration_seconds=duration,
                        bitrate_kbps=128,
                        status="ready"
                    )
                    db.add(audio_rec)
                db.commit()

                return {
                    "exhibit_code": exhibit.code,
                    "language": lang,
                    "translated_title": translated_title,
                    "translated_text": translated_text,
                    "original_text": original_text,
                    "audio_file_path": audio_url,
                    "timestamps_json": timestamps,
                    "duration_seconds": duration
                }
    except Exception as e:
        logger.warning(f"AI Service call error: {e}. Fallback to mock text.")

    # Fallback an toàn nếu AI Service bận
    mock_timestamps = generate_subtitle_timestamps(original_text)
    return {
        "exhibit_code": exhibit.code,
        "language": lang,
        "translated_title": exhibit.title,
        "translated_text": original_text,
        "original_text": original_text,
        "audio_file_path": f"/output/{exhibit.code}/{exhibit.code}_{lang}.mp3",
        "timestamps_json": mock_timestamps,
        "duration_seconds": mock_timestamps[-1]["end"] if mock_timestamps else 30.0
    }

# ====================================================================
# ADMIN CRUD APIS
# ====================================================================
@app.post("/api/v1/admin/exhibits")
def create_new_exhibit(req: CreateExhibitRequest, db: Session = Depends(get_db)):
    clean_code = req.code.strip().upper().replace(" ", "-")
    existing = db.query(Exhibit).filter(Exhibit.code == clean_code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Mã hiện vật '{clean_code}' đã tồn tại!")

    new_id = str(uuid.uuid4())
    new_exhibit = Exhibit(
        id=new_id,
        code=clean_code,
        title=req.title.strip(),
        title_en=req.title_en.strip() if req.title_en else req.title.strip(),
        room_id=req.room_id.strip() if req.room_id else "ROOM-01",
        zone=req.zone.strip() if req.zone else "Khu trưng bày",
        period=req.period.strip() if req.period else "Hiện vật lịch sử",
        thumbnail_url=req.thumbnail_url.strip() if req.thumbnail_url else "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=800&q=80",
        content_version=1,
        is_published=True,
        is_active=True
    )
    new_source = ContentSource(
        id=str(uuid.uuid4()),
        exhibit_id=new_id,
        original_text=req.original_text.strip(),
        content_version=1
    )
    db.add(new_exhibit)
    db.add(new_source)
    db.commit()
    db.refresh(new_exhibit)

    total_count = db.query(Exhibit).count()
    formatted = format_exhibit_response(new_exhibit, db, total_count)
    return {
        "status": "created",
        "message": f"Đã thêm thành công hiện vật {new_exhibit.title} (Mã: {clean_code})",
        "exhibit": formatted
    }

@app.delete("/api/v1/admin/exhibits/{code}")
def delete_exhibit(code: str, db: Session = Depends(get_db)):
    exhibit = find_exhibit_by_identifier(db, code)
    if not exhibit:
        raise HTTPException(status_code=404, detail="Không tìm thấy hiện vật để xóa")
    
    title = exhibit.title
    db.delete(exhibit)
    db.commit()
    return {"status": "deleted", "message": f"Đã xóa hiện vật {title}"}

@app.patch("/api/v1/admin/exhibits/{code}/thumbnail")
def update_exhibit_thumbnail(code: str, req: UpdateExhibitThumbnailRequest, db: Session = Depends(get_db)):
    exhibit = find_exhibit_by_identifier(db, code)
    if not exhibit:
        raise HTTPException(status_code=404, detail="Không tìm thấy hiện vật")
    
    new_url = req.thumbnail_url.strip()
    if not new_url:
        raise HTTPException(status_code=400, detail="Đường dẫn ảnh không được để trống")
    
    exhibit.thumbnail_url = new_url
    db.commit()
    db.refresh(exhibit)
    return {
        "status": "updated",
        "message": f"Đã cập nhật ảnh đại diện cho hiện vật '{exhibit.title}'",
        "thumbnail_url": exhibit.thumbnail_url
    }

@app.put("/api/v1/admin/exhibits/{code}")
def update_exhibit_full(code: str, req: UpdateExhibitRequest, db: Session = Depends(get_db)):
    exhibit = find_exhibit_by_identifier(db, code)
    if not exhibit:
        raise HTTPException(status_code=404, detail="Không tìm thấy hiện vật")
    
    if req.title is not None:
        exhibit.title = req.title.strip()
    if req.title_en is not None:
        exhibit.title_en = req.title_en.strip()
    if req.zone is not None:
        exhibit.zone = req.zone.strip()
    if req.room_id is not None:
        exhibit.room_id = req.room_id.strip()
    if req.period is not None:
        exhibit.period = req.period.strip()
    if req.thumbnail_url is not None and req.thumbnail_url.strip():
        exhibit.thumbnail_url = req.thumbnail_url.strip()
    
    if req.original_text is not None:
        content_src = db.query(ContentSource).filter_by(exhibit_id=exhibit.id).first()
        if content_src:
            content_src.original_text = req.original_text.strip()
        else:
            new_source = ContentSource(
                id=str(uuid.uuid4()),
                exhibit_id=exhibit.id,
                original_text=req.original_text.strip(),
                content_version=1
            )
            db.add(new_source)

    db.commit()
    db.refresh(exhibit)
    formatted = format_exhibit_response(exhibit, db)
    return {
        "status": "updated",
        "message": f"Đã cập nhật hiện vật '{exhibit.title}' thành công",
        "exhibit": formatted
    }

# ====================================================================
# TOUR ROUTES & GLOSSARY
# ====================================================================
@app.get("/api/v1/routes")
def get_tour_routes(db: Session = Depends(get_db)):
    routes = db.query(TourRoute).filter(TourRoute.is_active == True).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "ordered_exhibits": r.ordered_exhibits_json,
            "estimated_time": r.estimated_time
        }
        for r in routes
    ]

@app.get("/api/v1/glossary")
def get_glossary(db: Session = Depends(get_db)):
    terms = db.query(Glossary).all()
    return [
        {
            "id": g.id,
            "term_vi": g.term_vi,
            "term_en": g.term_en,
            "context_note": g.context_note
        }
        for g in terms
    ]

@app.get("/api/v1/languages")
def get_supported_languages(db: Session = Depends(get_db)):
    langs = db.query(SupportedLanguage).order_by(SupportedLanguage.sort_order.asc()).all()
    return [
        {
            "code": l.code,
            "name_vi": l.name_vi,
            "native_name": l.native_name,
            "flag": l.flag_icon,
            "voice_code": l.voice_code,
            "is_default": l.is_default
        }
        for l in langs
    ]

# ====================================================================
# ADMIN DATABASE EXPLORER
# ====================================================================
@app.get("/api/v1/admin/database/overview")
def get_database_overview(db: Session = Depends(get_db)):
    table_configs = [
        {"name": "supported_language", "displayName": "0. Ngôn ngữ khả dụng (supported_language)", "service": "Exhibit Service", "description": "Danh mục ngôn ngữ hỗ trợ", "model": SupportedLanguage},
        {"name": "exhibit", "displayName": "1. Hiện vật (exhibit)", "service": "Exhibit Core Service", "description": "Quản lý hiện vật trưng bày", "model": Exhibit},
        {"name": "content_source", "displayName": "2. Nội dung gốc (content_source)", "service": "Exhibit Core Service", "description": "Văn bản thuyết minh tiếng Việt chuẩn", "model": ContentSource},
        {"name": "localization", "displayName": "3. Bản dịch & Phụ đề (localization)", "service": "Exhibit Core Service", "description": "Bản dịch đa ngôn ngữ và timestamps phụ đề", "model": Localization},
        {"name": "audio_media", "displayName": "4. Âm thanh AI (audio_media)", "service": "Media & Streaming Service", "description": "Quản lý tệp âm thanh thuyết minh AI", "model": AudioMedia},
        {"name": "tour_route", "displayName": "5. Tuyến tham quan (tour_route)", "service": "Exhibit Core Service", "description": "Lộ trình tham quan theo từng chủ đề", "model": TourRoute},
        {"name": "glossary", "displayName": "6. Từ điển thuật ngữ (glossary)", "service": "Exhibit Core Service", "description": "Chuẩn hóa thuật ngữ lịch sử - quân sự", "model": Glossary},
    ]

    overview = []
    for cfg in table_configs:
        model = cfg["model"]
        columns = [
            {"name": col.name, "type": str(col.type), "primary_key": col.primary_key, "nullable": col.nullable}
            for col in model.__table__.columns
        ]
        query_rows = db.query(model).limit(50).all()
        rows_data = []
        for r in query_rows:
            row_dict = {}
            for col in model.__table__.columns:
                val = getattr(r, col.name)
                if isinstance(val, datetime):
                    val = val.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(val, (dict, list)):
                    val = json.dumps(val, ensure_ascii=False)
                row_dict[col.name] = val
            rows_data.append(row_dict)

        overview.append({
            "name": cfg["name"],
            "displayName": cfg["displayName"],
            "service": cfg["service"],
            "description": cfg["description"],
            "columns": columns,
            "rowCount": db.query(model).count(),
            "rows": rows_data
        })

    return {
        "status": "ok",
        "total_tables": len(overview),
        "database_type": "SQLite / PostgreSQL",
        "tables": overview
    }
