from fastapi import FastAPI, HTTPException, Query, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import os
import re
import json
import time
import uuid
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.database import engine, Base, SessionLocal, get_db
from app.db.models import (
    Exhibit,
    ContentSource,
    Localization,
    AudioMedia,
    TourRoute,
    Glossary,
    ListeningMetric,
    SupportedLanguage
)
from app.db.seed import seed_database
from app.services.translate_service import translate_text
from app.services.tts_service import generate_audio
from app.db.utility import list_table_names, fetch_table_rows

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
    except Exception as err:
        print(f"[DB-INIT-WARN] Loi khoi tao CSDL: {err}")
    yield


# =====================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


# =====================================================
# 2. KHỞI TẠO FASTAPI
# =====================================================

app = FastAPI(
    title="WarRemnantsVoice - AI Pipeline, Exhibit & Admin Service",
    description="Hệ thống thuyết minh tự động đa ngôn ngữ cho Bảo tàng Chứng tích Chiến tranh",
    version="2.4.0",
    lifespan=lifespan
)

# CORS Middleware mở cho mọi Client (Mobile Web, PWA, Remote Tunnel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Thư mục chứa audio file
os.makedirs("./output", exist_ok=True)
app.mount("/output", StaticFiles(directory="./output"), name="output")

TRANSLATION_CACHE: Dict[str, Any] = {}

# ====================================================================
# 🟢 REAL-TIME VISITOR TRACKING & ACTIVE SESSIONS
# ====================================================================
ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}
VISITOR_LOGS: List[Dict[str, Any]] = []
TOTAL_VISITORS_COUNTER = 0

def clean_expired_sessions(timeout_seconds: int = 25):
    """Loại bỏ các session không gửi heartbeat trong 25 giây (đã thoát trang)"""
    now = time.time()
    expired = [sid for sid, data in list(ACTIVE_SESSIONS.items()) if now - data.get("last_ping", 0) > timeout_seconds]
    for sid in expired:
        del ACTIVE_SESSIONS[sid]

def generate_subtitle_timestamps(text: str, total_duration: float = None):
    raw_sentences = re.split(r'(?<=[.!?。！？])\s+', text.strip())
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    if not sentences:
        sentences = [text.strip()]
    
    total_chars = sum(len(s) for s in sentences)
    if total_chars == 0:
        total_chars = 1

    duration = total_duration if total_duration else max(len(text) * 0.07, 3.5)
    
    timestamps = []
    current_time = 0.0
    for idx, sentence in enumerate(sentences):
        sentence_duration = (len(sentence) / total_chars) * duration
        sentence_duration = max(sentence_duration, 1.2)
        end_time = round(current_time + sentence_duration, 2)
        
        timestamps.append({
            "id": idx,
            "start": round(current_time, 2),
            "end": end_time,
            "text": sentence
        })
        current_time = end_time

    return timestamps

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

# Request Models
class TranslationRequest(BaseModel):

    task_id: str
    exhibit_id: str
    original_text: str
    target_languages: List[str] = ["en"]

class MetricReportRequest(BaseModel):
    exhibit_code: str
    language_code: str
    listened_duration: int
    trigger_type: str = "QR_CODE"

class HeartbeatRequest(BaseModel):
    visitor_id: str
    exhibit_code: Optional[str] = "HOME"
    language_code: Optional[str] = "en"
    is_playing: bool = False
    device_type: Optional[str] = "Mobile"

class CreateExhibitRequest(BaseModel):
    code: str
    title: str
    title_en: Optional[str] = ""
    zone: Optional[str] = "Khu trÆ°ng bÃ y"
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


# =====================================================
# 6. HÀM GHI LOG VÀO DATABASE
# =====================================================

def write_log(db, task_id, message, level="INFO"):

    log = PipelineLog(
        task_id=task_id,
        log_level=level,
        message=message
    )

    db.add(log)
    db.commit()


# =====================================================
# 7. HÀM TẠO PROCESSING STEP
# =====================================================

def create_processing_step(db, task_id, step_name):

    step = ProcessingStep(
        task_id=task_id,
        step_name=step_name,
        status="processing",
        started_at=datetime.now()
    )

    db.add(step)
    db.commit()
    db.refresh(step)

    return step


# =====================================================
# 8. HEALTH CHECK
# =====================================================

@app.get("/")
def health_check(db: Session = Depends(get_db)):
    clean_expired_sessions()
    exhibits_count = db.query(Exhibit).filter(Exhibit.is_active == True).count()
    return {
        "status": "ok",
        "service": "WarRemnantsVoice Exhibit & AI Service",
        "version": "2.4.0",
        "database": "CONNECTED",
        "active_visitors_online": len(ACTIVE_SESSIONS),
        "exhibits_count": exhibits_count
    }

# ====================================================================
# 👥 VISITOR HEARTBEAT
# ====================================================================
@app.post("/api/v1/metrics/heartbeat")
def receive_heartbeat(payload: HeartbeatRequest, request: Request):
    global TOTAL_VISITORS_COUNTER
    now = time.time()
    vid = payload.visitor_id
    
    is_new = vid not in ACTIVE_SESSIONS
    if is_new:
        TOTAL_VISITORS_COUNTER += 1
        client_host = request.client.host if request.client else "unknown"
        VISITOR_LOGS.insert(0, {
            "id": f"log-{int(now * 1000)}",
            "visitor_id": vid[:8],
            "exhibit_code": payload.exhibit_code,
            "language": payload.language_code,
            "device": payload.device_type,
            "action": "Kết nối tham quan",
            "time": datetime.now().strftime("%H:%M:%S"),
            "ip": client_host
        })
        if len(VISITOR_LOGS) > 50:
            VISITOR_LOGS.pop()

    ACTIVE_SESSIONS[vid] = {
        "visitor_id": vid,
        "exhibit_code": payload.exhibit_code,
        "language_code": payload.language_code,
        "is_playing": payload.is_playing,
        "device_type": payload.device_type,
        "last_ping": now,
        "connected_at": ACTIVE_SESSIONS.get(vid, {}).get("connected_at", datetime.now().strftime("%H:%M:%S"))
    }
    
    clean_expired_sessions()
    return {
        "status": "ok",
        "active_online": len(ACTIVE_SESSIONS)
    }

# ====================================================================
# 📊 ADMIN OBSERVABILITY & DASHBOARD STATS (UC5, FR-21, FR-22)
# ====================================================================
@app.get("/api/v1/admin/dashboard-stats")
def get_admin_dashboard_stats(db: Session = Depends(get_db)):
    clean_expired_sessions()
    
    online_count = len(ACTIVE_SESSIONS)
    listening_count = sum(1 for s in ACTIVE_SESSIONS.values() if s.get("is_playing"))
    total_audio_played = db.query(ListeningMetric).count()
    
    # Thống kê ngôn ngữ
    lang_counts: Dict[str, int] = {}
    for s in ACTIVE_SESSIONS.values():
        lang = s.get("language_code", "en")
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
    # Thống kê thiết bị
    device_counts = {"Mobile": 0, "Desktop": 0}
    for s in ACTIVE_SESSIONS.values():
        dev = s.get("device_type", "Mobile")
        if dev in device_counts:
            device_counts[dev] += 1
        else:
            device_counts["Mobile"] += 1

    # Thống kê hiện vật đang xem
    exhibit_now: Dict[str, int] = {}
    for s in ACTIVE_SESSIONS.values():
        ex = s.get("exhibit_code", "HOME")
        exhibit_now[ex] = exhibit_now.get(ex, 0) + 1

    return {
        "realtime": {
            "online_visitors": online_count,
            "active_listeners": listening_count,
            "total_visits_today": max(TOTAL_VISITORS_COUNTER, online_count),
            "total_audio_played": total_audio_played,
            "server_time": datetime.now().strftime("%H:%M:%S - %d/%m/%Y"),
            "system_health": "ONLINE"
        },
        "breakdown": {
            "by_language": lang_counts,
            "by_device": device_counts,
            "by_exhibit": exhibit_now
        },
        "recent_activity_logs": VISITOR_LOGS[:20],
        "active_sessions_list": [
            {
                "session_id": sid[:8],
                "exhibit": s.get("exhibit_code"),
                "language": s.get("language_code"),
                "is_listening": s.get("is_playing"),
                "device": s.get("device_type"),
                "connected_at": s.get("connected_at")
            }
            for sid, s in list(ACTIVE_SESSIONS.items())[:30]
        ]
    }

# ====================================================================
# ➕ ADMIN EXHIBIT MANAGEMENT (UC3, FR-02, FR-04)
# ====================================================================
@app.post("/api/v1/admin/exhibits")
def create_new_exhibit(req: CreateExhibitRequest, db: Session = Depends(get_db)):
    """
    Thêm hiện vật mới và lưu trữ bền vững vào CSDL
    """
    clean_code = req.code.strip().upper().replace(" ", "-")
    
    # Kiểm tra trùng mã
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
    clean_code = code.strip().upper()
    exhibit = db.query(Exhibit).filter(
        (Exhibit.code == clean_code) | (Exhibit.id == code.strip())
    ).first()
    
    if not exhibit:
        raise HTTPException(status_code=404, detail="Không tìm thấy hiện vật để xóa")
    
    title = exhibit.title
    db.delete(exhibit)
    db.commit()
    return {"status": "deleted", "message": f"Đã xóa hiện vật {title}"}

# ====================================================================

@app.patch("/api/v1/admin/exhibits/{code}/thumbnail")
def update_exhibit_thumbnail(code: str, req: UpdateExhibitThumbnailRequest, db: Session = Depends(get_db)):
    """Cáº­p nháº­t nhanh URL áº£nh Ä‘áº¡i diá»‡n cho hiá»‡n váº­t"""
    clean_code = code.strip().upper()
    exhibit = db.query(Exhibit).filter(
        (Exhibit.code == clean_code) | (Exhibit.id == code.strip())
    ).first()
    
    if not exhibit:
        raise HTTPException(status_code=404, detail="KhÃ´ng tÃ¬m tháº¥y hiá»‡n váº­t")
    
    new_url = req.thumbnail_url.strip()
    if not new_url:
        raise HTTPException(status_code=400, detail="ÄÆ°á»ng dáº«n áº£nh khÃ´ng Ä‘Æ°á»£c Ä‘á»ƒ trá»‘ng")
    
    exhibit.thumbnail_url = new_url
    db.commit()
    db.refresh(exhibit)
    return {
        "status": "updated",
        "message": f"ÄÃ£ cáº­p nháº­t áº£nh Ä‘áº¡i diá»‡n cho hiá»‡n váº­t '{exhibit.title}'",
        "thumbnail_url": exhibit.thumbnail_url
    }

@app.put("/api/v1/admin/exhibits/{code}")
def update_exhibit_full(code: str, req: UpdateExhibitRequest, db: Session = Depends(get_db)):
    """Cáº­p nháº­t thÃ´ng tin chi tiáº¿t hiá»‡n váº­t vÃ  vÄƒn báº£n gá»‘c"""
    clean_code = code.strip().upper()
    exhibit = db.query(Exhibit).filter(
        (Exhibit.code == clean_code) | (Exhibit.id == code.strip())
    ).first()
    
    if not exhibit:
        raise HTTPException(status_code=404, detail="KhÃ´ng tÃ¬m tháº¥y hiá»‡n váº­t")
    
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
        "message": f"ÄÃ£ cáº­p nháº­t hiá»‡n váº­t '{exhibit.title}' thÃ nh cÃ´ng",
        "exhibit": formatted
    }
# 🏛️ PUBLIC EXHIBIT APIS
# ====================================================================
@app.get("/api/v1/exhibits")
def get_all_exhibits(db: Session = Depends(get_db)):
    exhibits = db.query(Exhibit).filter(Exhibit.is_active == True).order_by(Exhibit.created_at.asc()).all()
    results = []
    for idx, ex in enumerate(exhibits, 1):
        formatted = format_exhibit_response(ex, db, idx)
        # Gợi ý hiện vật tiếp theo theo vòng lặp
        next_idx = (idx % len(exhibits))
        formatted["next_code"] = exhibits[next_idx].code if len(exhibits) > 1 else None
        results.append(formatted)
    return results

@app.get("/api/v1/exhibits/{identifier}")
def get_exhibit_by_code_or_id(identifier: str, db: Session = Depends(get_db)):
    clean_id = identifier.strip().upper()
    exhibit = db.query(Exhibit).filter(
        (Exhibit.code == clean_id) | (Exhibit.id == identifier.strip())
    ).first()
    
    if not exhibit:
        exhibits = db.query(Exhibit).all()
        for ex in exhibits:
            if clean_id.replace('-', '') in ex.code.upper().replace('-', ''):
                exhibit = ex
                break

    if not exhibit:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy hiện vật với mã '{identifier}'")

    return format_exhibit_response(exhibit, db)

@app.get("/api/v1/exhibits/{identifier}/audio")
async def get_exhibit_audio(identifier: str, lang: str = Query("en"), db: Session = Depends(get_db)):
    clean_id = identifier.strip().upper()
    exhibit = db.query(Exhibit).filter(
        (Exhibit.code == clean_id) | (Exhibit.id == identifier.strip())
    ).first()
    
    if not exhibit:
        exhibits = db.query(Exhibit).all()
        for ex in exhibits:
            if clean_id.replace('-', '') in ex.code.upper().replace('-', ''):
                exhibit = ex
                break

    if not exhibit:
        raise HTTPException(status_code=404, detail=f"Hiện vật '{identifier}' không tồn tại.")

    # Lấy văn bản gốc
    content_src = db.query(ContentSource).filter_by(exhibit_id=exhibit.id).first()
    original_text = content_src.original_text if content_src else exhibit.title

    cache_key = f"{exhibit.code}_{lang}_v{exhibit.content_version}"
    if cache_key in TRANSLATION_CACHE:
        return TRANSLATION_CACHE[cache_key]

    # Kiểm tra trong Localization và AudioMedia CSDL
    loc = db.query(Localization).filter_by(
        exhibit_id=exhibit.id,
        language_code=lang,
        content_version=exhibit.content_version
    ).first()
    
    if loc:
        audio_rec = db.query(AudioMedia).filter_by(localization_id=loc.id).first()
        if audio_rec and os.path.exists(audio_rec.storage_path):
            result_payload = {
                "exhibit_code": exhibit.code,
                "language": lang,
                "translated_title": loc.translated_title,
                "translated_text": loc.translated_text,
                "original_text": original_text,
                "audio_file_path": audio_rec.file_url,
                "timestamps_json": loc.timestamps_json or [],
                "duration_seconds": audio_rec.duration_seconds
            }
            TRANSLATION_CACHE[cache_key] = result_payload
            return result_payload

    try:
        # Dịch thuật
        if lang == "vi":
            translated_text = original_text
            translated_title = exhibit.title
        else:
            translated_text = translate_text(original_text, lang)
            translated_title = exhibit.title_en if (lang == "en" and exhibit.title_en) else translate_text(exhibit.title, lang)

        output_dir = os.path.join(".", "output", exhibit.code)
        os.makedirs(output_dir, exist_ok=True)
        
        audio_filename = f"{exhibit.code}_{lang}.mp3"
        full_disk_path = os.path.join(output_dir, audio_filename)
        
        await generate_audio(translated_text, lang, full_disk_path)
        
        timestamps = generate_subtitle_timestamps(translated_text)
        duration_sec = timestamps[-1]["end"] if timestamps else 30.0
        web_audio_url = f"/output/{exhibit.code}/{audio_filename}"
        
        # Lưu vào bảng Localization và AudioMedia trong CSDL
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
        else:
            loc.translated_title = translated_title
            loc.translated_text = translated_text
            loc.timestamps_json = timestamps

        audio_rec = db.query(AudioMedia).filter_by(localization_id=loc.id).first()
        if not audio_rec:
            audio_rec = AudioMedia(
                localization_id=loc.id,
                file_url=web_audio_url,
                storage_path=full_disk_path,
                duration_seconds=duration_sec,
                bitrate_kbps=128,
                status="ready"
            )
            db.add(audio_rec)
        else:
            audio_rec.file_url = web_audio_url
            audio_rec.storage_path = full_disk_path
            audio_rec.duration_seconds = duration_sec

        db.commit()

        result_payload = {
            "exhibit_code": exhibit.code,
            "language": lang,
            "translated_title": translated_title,
            "translated_text": translated_text,
            "original_text": original_text,
            "audio_file_path": web_audio_url,
            "timestamps_json": timestamps,
            "duration_seconds": duration_sec
        }
        
        TRANSLATION_CACHE[cache_key] = result_payload
        return result_payload

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý audio/dịch thuật: {str(e)}")

@app.post("/api/v1/process-audio")
async def process_translation_and_tts(payload: TranslationRequest, db: Session = Depends(get_db)):
    try:

        # -------------------------------------------------
        # KIỂM TRA DỮ LIỆU ĐẦU VÀO
        # -------------------------------------------------

        if not payload.target_languages:
            raise HTTPException(
                status_code=400,
                detail="Danh sách ngôn ngữ không được để trống"
            )

        if not payload.original_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Nội dung hiện vật không được để trống"
            )

        # -------------------------------------------------
        # KIỂM TRA TASK ID
        # -------------------------------------------------

        existing_task = db.query(PipelineTask).filter(
            PipelineTask.task_id == payload.task_id
        ).first()

        if existing_task:

            raise HTTPException(
                status_code=409,
                detail="Task ID đã tồn tại"
            )

        # -------------------------------------------------
        # BƯỚC 1: TẠO TÁC VỤ AI
        # -------------------------------------------------

        task = PipelineTask(
            task_id=payload.task_id,
            exhibit_id=payload.exhibit_id,
            original_text=payload.original_text,
            status="processing"
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        write_log(
            db,
            payload.task_id,
            "Bắt đầu xử lý tác vụ AI"
        )

        results = []

        # Tạo thư mục lưu audio theo hiện vật
        output_dir = os.path.join(
            OUTPUT_DIR,
            payload.exhibit_id
        )

        os.makedirs(output_dir, exist_ok=True)

        # -------------------------------------------------
        # BƯỚC 2: DỊCH THUẬT VÀ TẠO AUDIO
        # -------------------------------------------------

        for lang in payload.target_languages:
            translated_text = translate_text(payload.original_text, lang)
            audio_filename = f"{payload.exhibit_id}_{lang}.mp3"
            full_disk_path = os.path.join(output_dir, audio_filename)
            
            await generate_audio(translated_text, lang, full_disk_path)
            
            web_audio_url = f"/output/{payload.exhibit_id}/{audio_filename}"
            timestamps = generate_subtitle_timestamps(translated_text)
            
            results.append({
                "language": lang,
                "translated_text": translated_text,
                "audio_file_path": web_audio_url,
                "timestamps_json": timestamps
            })

        return {
            "task_id": payload.task_id,
            "exhibit_id": payload.exhibit_id,
            "status": "COMPLETED",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý AI: {str(e)}")

@app.post("/api/v1/metrics/listen")
def record_listening_metric(metric: MetricReportRequest, db: Session = Depends(get_db)):
    ex = db.query(Exhibit).filter(Exhibit.code == metric.exhibit_code.strip().upper()).first()
    exhibit_id = ex.id if ex else None

    new_metric = ListeningMetric(
        exhibit_id=exhibit_id,
        exhibit_code=metric.exhibit_code,
        language_code=metric.language_code,
        listened_duration=metric.listened_duration,
        trigger_type=metric.trigger_type,
        timestamp=datetime.utcnow()
    )
    db.add(new_metric)
    db.commit()
    
    total_records = db.query(ListeningMetric).count()
    
    VISITOR_LOGS.insert(0, {
        "id": f"log-play-{int(time.time() * 1000)}",
        "visitor_id": "Visitor",
        "exhibit_code": metric.exhibit_code,
        "language": metric.language_code,
        "device": "Mobile",
        "action": f"Nghe bài ({metric.listened_duration}s)",
        "time": datetime.now().strftime("%H:%M:%S"),
        "ip": "Client"
    })
    return {"status": "recorded", "total_records": total_records}

# ====================================================================
# 🗺️ PRD TOUR ROUTES & GLOSSARY APIS
# ====================================================================
@app.get("/api/v1/routes")
def get_tour_routes(db: Session = Depends(get_db)):
    """Lấy danh sách các tuyến tham quan theo chuyên đề (PRD UC2)"""
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
    """Lấy từ điển thuật ngữ lịch sử - quân sự chuẩn hóa (PRD FR-11)"""
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

# ====================================================================
# 🌐 PUBLIC SUPPORTED LANGUAGES API (DANH MỤC 15 NGÔN NGỮ KHẢ DỤNG)
# ====================================================================
@app.get("/api/v1/languages")
def get_supported_languages(db: Session = Depends(get_db)):
    """Lấy danh sách 15 ngôn ngữ khả dụng trong hệ thống từ database (PRD FR-11, BR-01)"""
    langs = db.query(SupportedLanguage).filter(SupportedLanguage.is_active == True).order_by(SupportedLanguage.sort_order.asc()).all()
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
# 🗄️ ADMIN DATABASE EXPLORER API (SHOW TOÀN BỘ CÁC BẢNG PRD TRÊN UI)
# ====================================================================
@app.get("/api/v1/admin/database/overview")
def get_database_overview(db: Session = Depends(get_db)):
    """API cung cấp toàn bộ schema và dữ liệu các bảng CSDL theo chuẩn PRD cho Admin UI"""
    table_configs = [
        {
            "name": "supported_language",
            "displayName": "0. Ngôn ngữ khả dụng (supported_language)",
            "service": "Localization Service",
            "description": "Danh mục 15 ngôn ngữ khả dụng trong hệ thống kèm cờ quốc gia và model giọng đọc TTS",
            "model": SupportedLanguage
        },
        {
            "name": "exhibit",
            "displayName": "1. Hiện vật (exhibit)",
            "service": "Exhibit Core Service",
            "description": "Quản lý định danh hiện vật trưng bày, phân khu, toạ độ & phiên bản",
            "model": Exhibit
        },
        {
            "name": "content_source",
            "displayName": "2. Nội dung gốc (content_source)",
            "service": "Content Management Service",
            "description": "Văn bản thuyết minh tiếng Việt chuẩn được bảo tàng kiểm duyệt",
            "model": ContentSource
        },
        {
            "name": "localization",
            "displayName": "3. Bản dịch & Phụ đề (localization)",
            "service": "Localization Service",
            "description": "Bản dịch đa ngôn ngữ và phụ đề timestamps JSON đồng bộ giọng đọc",
            "model": Localization
        },
        {
            "name": "audio_media",
            "displayName": "4. Âm thanh AI (audio_media)",
            "service": "Streaming & Media Service",
            "description": "Quản lý tệp âm thanh thuyết minh AI, thời lượng và đường dẫn lưu trữ",
            "model": AudioMedia
        },
        {
            "name": "tour_route",
            "displayName": "5. Tuyến tham quan (tour_route)",
            "service": "Exhibit Core Service",
            "description": "Lộ trình tham quan theo từng chủ đề lịch sử và thời gian dự kiến",
            "model": TourRoute
        },
        {
            "name": "glossary",
            "displayName": "6. Từ điển thuật ngữ (glossary)",
            "service": "Localization Service",
            "description": "Chuẩn hóa thuật ngữ lịch sử - quân sự nhạy cảm theo PRD FR-11",
            "model": Glossary
        },
        {
            "name": "listening_metric",
            "displayName": "7. Thống kê nghe (listening_metric)",
            "service": "Analytics Service",
            "description": "Ghi nhận số liệu lượt nghe ẩn danh, thời lượng và trigger quét mã QR",
            "model": ListeningMetric
        }
    ]

    overview = []
    for cfg in table_configs:
        model = cfg["model"]
        columns = [
            {
                "name": col.name,
                "type": str(col.type),
                "primary_key": col.primary_key,
                "nullable": col.nullable
            }
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
        "database_type": "SQLite / PostgreSQL (Dual DB Support)",
        "tables": overview
    }



# ====================================================================
# DATABASE EXPLORER - Dynamic table list & rows
# ====================================================================
@app.get("/api/v1/admin/db/tables")
def admin_list_tables(db: Session = Depends(get_db)):
    """Return a JSON array of all user-defined tables."""
    try:
        return {"tables": list_table_names(db)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list tables: {exc}")

@app.get("/api/v1/admin/db/tables/{table_name}")
def admin_get_table(table_name: str, limit: int = 100, db: Session = Depends(get_db)):
    """Return up to limit rows from table_name as JSON."""
    try:
        rows = fetch_table_rows(db, table_name, limit)
        return {"table": table_name, "rows": rows}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to read table {table_name}: {exc}")

# ====================================================================
# ADMIN TUNNEL URL - chi admin moi duoc lay link Cloudflare Tunnel
# ====================================================================
import secrets as _secrets
from fastapi.security import HTTPBasic as _HTTPBasic, HTTPBasicCredentials as _HTTPBasicCredentials

_security_basic = _HTTPBasic(auto_error=False)
_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin-secret")

def _require_admin(creds: _HTTPBasicCredentials = Depends(_security_basic)):
    if not creds:
        raise HTTPException(status_code=401, detail="Unauthorized",
                            headers={"WWW-Authenticate": "Basic"})
    ok_user = _secrets.compare_digest(creds.username, "admin")
    ok_pass = _secrets.compare_digest(creds.password, _ADMIN_PASSWORD)
    if not (ok_user and ok_pass):
        raise HTTPException(status_code=401, detail="Unauthorized",
                            headers={"WWW-Authenticate": "Basic"})

@app.get("/api/v1/admin/tunnel-url")
def get_tunnel_url(_: None = Depends(_require_admin)):
    """Tra ve Cloudflare Tunnel URL chi danh cho admin xac thuc."""
    tunnel_url = os.getenv("CLOUDFLARE_TUNNEL_URL", "")
    if not tunnel_url:
        raise HTTPException(status_code=500,
                            detail="CLOUDFLARE_TUNNEL_URL chua duoc cau hinh tren server")
    return {"tunnel_url": tunnel_url}
