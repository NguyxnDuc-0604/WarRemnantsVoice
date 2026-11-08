
import os
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.database.connection import engine, SessionLocal, Base

from app.database.models import (
    PipelineTask,
    ProcessingStep,
    Translation,
    GeneratedAudio,
    PipelineLog
)

from app.services.translate_service import translate_text
from app.services.tts_service import generate_audio


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
    title="WarRemnantsVoice - AI Pipeline Service",
    description="API dịch thuật đa ngôn ngữ và sinh âm thanh thuyết minh tự động",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount(
    "/output",
    StaticFiles(directory=OUTPUT_DIR),
    name="output"
)


# =====================================================
# 3. KẾT NỐI DATABASE
# =====================================================

@app.on_event("startup")
def startup_event():

    try:
        Base.metadata.create_all(bind=engine)

        print("===================================")
        print("AI PIPELINE DATABASE CONNECTED!")
        print("Database: ai_pipeline_db")
        print("===================================")

    except Exception as e:
        print(f"DATABASE CONNECTION ERROR: {e}")
        raise


# =====================================================
# 4. DANH SÁCH HIỆN VẬT MẪU
# =====================================================

EXHIBITS_DATABASE = [

    {
        "id": "EX-01",
        "name": "Máy bay trực thăng UH-1 'Huey'",
        "zone": "Khu trưng bày ngoài trời",
        "image_url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=600&q=80",
        "original_text": "Trực thăng UH-1 Iroquois (biệt danh Huey) được quân đội Hoa Kỳ sử dụng rộng rãi trong Chiến tranh Việt Nam từ năm 1962 đến 1975 với các nhiệm vụ đổ quân, cứu thương và yểm trợ hoả lực không quân.",
        "period": "1962 - 1975"
    },

    {
        "id": "EX-02",
        "name": "Xe tăng M48 Patton",
        "zone": "Sân trưng bày cơ giới",
        "image_url": "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=600&q=80",
        "original_text": "Xe tăng hạng trung M48 Patton là dòng tăng chiến đấu chủ lực được Mỹ viện trợ và triển khai tại chiến trường miền Nam Việt Nam, trang bị pháo nòng 90mm.",
        "period": "1967 - 1972"
    },

    {
        "id": "EX-03",
        "name": "Chiến dịch Hồ Chí Minh",
        "zone": "Phòng trưng bày lịch sử tổng hợp",
        "image_url": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=600&q=80",
        "original_text": "Chiến dịch Hồ Chí Minh lịch sử diễn ra từ ngày 26 đến ngày 30 tháng 4 năm 1975, đỉnh cao của cuộc Tổng tiến công và nổi dậy mùa Xuân 1975, giải phóng hoàn toàn miền Nam, thống nhất đất nước.",
        "period": "4/1975"
    },

    {
        "id": "EX-04",
        "name": "Chuồng cọp Côn Đảo (Mô hình phục dựng)",
        "zone": "Khu chứng tích nhà tù",
        "image_url": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=600&q=80",
        "original_text": "Mô hình phục dựng Chuồng cọp nhà tù Côn Đảo tái hiện chế độ giam giữ khắc nghiệt đối với các chiến sĩ cách mạng, thể hiện tinh thần kiên cường, bất khuất của những người tù yêu nước.",
        "period": "1940 - 1975"
    },

    {
        "id": "EX-05",
        "name": "Pháo tự hành M107 175mm ('Vua chiến trường')",
        "zone": "Khu trưng bày ngoài trời",
        "image_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=80",
        "original_text": "Pháo tự hành M107 cỡ nòng 175mm từng được mệnh danh là 'Vua chiến trường' của quân đội Mỹ với tầm bắn tối đa lên tới hơn 32 km.",
        "period": "1968 - 1975"
    }

]


# =====================================================
# 5. SCHEMA REQUEST / RESPONSE
# =====================================================

class TranslationRequest(BaseModel):

    task_id: str
    exhibit_id: str
    original_text: str

    target_languages: List[str] = Field(
        default_factory=lambda: ["en", "fr"]
    )


class TranslationResult(BaseModel):

    language: str
    translated_text: str
    audio_file_path: str


class TranslationResponse(BaseModel):

    task_id: str
    exhibit_id: str
    status: str
    results: List[TranslationResult]


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
def health_check():

    return {
        "status": "ok",
        "service": "WarRemnantsVoice AI Pipeline Service",
        "version": "2.0.0",
        "database": "PostgreSQL",
        "database_name": "ai_pipeline_db",
        "exhibits_count": len(EXHIBITS_DATABASE)
    }


# =====================================================
# 9. LẤY DANH SÁCH HIỆN VẬT
# =====================================================

@app.get("/api/v1/exhibits")
def get_exhibits():

    return EXHIBITS_DATABASE


# =====================================================
# 10. LẤY CHI TIẾT HIỆN VẬT THEO ID
# =====================================================

@app.get("/api/v1/exhibits/{exhibit_id}")
def get_exhibit_by_id(exhibit_id: str):

    normalized_id = exhibit_id.strip().upper()

    for exhibit in EXHIBITS_DATABASE:

        if exhibit["id"].upper() == normalized_id:
            return exhibit

    raise HTTPException(
        status_code=404,
        detail=f"Không tìm thấy hiện vật có mã '{exhibit_id}'"
    )


# =====================================================
# 11. API DỊCH THUẬT VÀ TẠO AUDIO
# =====================================================

@app.post(
    "/api/v1/process-audio",
    response_model=TranslationResponse
)
async def process_translation_and_tts(payload: TranslationRequest):

    db = SessionLocal()

    task = None

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

            # =============================================
            # 2.1. DỊCH THUẬT
            # =============================================

            translation_step = create_processing_step(
                db,
                payload.task_id,
                f"TRANSLATION_{lang}"
            )

            try:

                translated_text = translate_text(
                    payload.original_text,
                    lang
                )

                translation = Translation(
                    task_id=payload.task_id,
                    language=lang,
                    translated_text=translated_text
                )

                db.add(translation)

                translation_step.status = "completed"
                translation_step.completed_at = datetime.now()

                db.commit()

                write_log(
                    db,
                    payload.task_id,
                    f"Dịch thuật thành công: {lang}"
                )

            except Exception as e:

                translation_step.status = "failed"
                translation_step.error_message = str(e)
                translation_step.completed_at = datetime.now()

                db.commit()

                raise

            # =============================================
            # 2.2. TẠO AUDIO
            # =============================================

            tts_step = create_processing_step(
                db,
                payload.task_id,
                f"TTS_{lang}"
            )

            try:

                audio_filename = (
                    f"{payload.exhibit_id}_{lang}.mp3"
                )

                full_disk_path = os.path.join(
                    output_dir,
                    audio_filename
                )

                await generate_audio(
                    translated_text,
                    lang,
                    full_disk_path
                )

                # Đường dẫn audio cho trình duyệt
                web_audio_url = (
                    f"/output/{payload.exhibit_id}/"
                    f"{audio_filename}"
                )

                audio = GeneratedAudio(
                    task_id=payload.task_id,
                    language=lang,
                    audio_file_path=web_audio_url
                )

                db.add(audio)

                tts_step.status = "completed"
                tts_step.completed_at = datetime.now()

                db.commit()

                write_log(
                    db,
                    payload.task_id,
                    f"Tạo audio thành công: {lang}"
                )

                results.append(
                    TranslationResult(
                        language=lang,
                        translated_text=translated_text,
                        audio_file_path=web_audio_url
                    )
                )

            except Exception as e:

                tts_step.status = "failed"
                tts_step.error_message = str(e)
                tts_step.completed_at = datetime.now()

                db.commit()

                raise

        # -------------------------------------------------
        # BƯỚC 3: HOÀN THÀNH TÁC VỤ
        # -------------------------------------------------

        task.status = "completed"
        task.updated_at = datetime.now()

        db.commit()

        write_log(
            db,
            payload.task_id,
            "Hoàn thành toàn bộ pipeline AI"
        )

        return TranslationResponse(
            task_id=payload.task_id,
            exhibit_id=payload.exhibit_id,
            status="COMPLETED",
            results=results
        )

    # -----------------------------------------------------
    # XỬ LÝ LỖI
    # -----------------------------------------------------

    except HTTPException:

        raise

    except Exception as e:

        db.rollback()

        if task is not None:

            task = db.query(PipelineTask).filter(
                PipelineTask.task_id == payload.task_id
            ).first()

            if task:

                task.status = "failed"
                task.updated_at = datetime.now()

                db.commit()

                write_log(
                    db,
                    payload.task_id,
                    f"Lỗi xử lý AI: {str(e)}",
                    "ERROR"
                )

        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xử lý AI: {str(e)}"
        )

    finally:

        db.close()


# =====================================================
# 12. CHẠY KIỂM TRA DATABASE
# =====================================================

@app.get("/api/v1/database/status")
def database_status():

    db = SessionLocal()

    try:

        from sqlalchemy import text

        db.execute(text("SELECT 1"))

        return {
            "status": "connected",
            "database": "ai_pipeline_db",
            "message": "PostgreSQL hoạt động bình thường"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )

    finally:

        db.close()
