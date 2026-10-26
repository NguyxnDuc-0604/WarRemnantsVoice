from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import asyncio

from app.services.translate_service import translate_text
from app.services.tts_service import generate_audio

app = FastAPI(
    title="WarRemnantsVoice - AI Pipeline Service",
    description="API dịch thuật đa ngôn ngữ và sinh âm thanh thuyết minh tự động",
    version="2.0.0"
)

# Cấu hình CORS để mọi thiết bị (Mobile, PC, Ngrok, Cloudflare Tunnel) đều gọi được API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đảm bảo thư mục output tồn tại và mount static files
os.makedirs("./output", exist_ok=True)
app.mount("/output", StaticFiles(directory="./output"), name="output")

# Danh mục hiện vật bảo tàng mẫu (để quét mã QR hoặc chọn nhanh)
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

# Schema dữ liệu đầu vào
class TranslationRequest(BaseModel):
    task_id: str
    exhibit_id: str
    original_text: str
    target_languages: List[str] = ["en", "fr"]

# Schema dữ liệu đầu ra
class TranslationResult(BaseModel):
    language: str
    translated_text: str
    audio_file_path: str

class TranslationResponse(BaseModel):
    task_id: str
    exhibit_id: str
    status: str
    results: List[TranslationResult]

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "WarRemnantsVoice AI Pipeline Service",
        "version": "2.0.0",
        "exhibits_count": len(EXHIBITS_DATABASE)
    }

@app.get("/api/v1/exhibits")
def get_exhibits():
    """Lấy danh sách tất cả hiện vật mẫu phục vụ quét mã QR hoặc chọn nhanh"""
    return EXHIBITS_DATABASE

@app.get("/api/v1/exhibits/{exhibit_id}")
def get_exhibit_by_id(exhibit_id: str):
    """Lấy thông tin chi tiết một hiện vật theo mã QR ID"""
    normalized_id = exhibit_id.strip().upper()
    for exhibit in EXHIBITS_DATABASE:
        if exhibit["id"].upper() == normalized_id:
            return exhibit
    raise HTTPException(status_code=404, detail=f"Không tìm thấy hiện vật có mã '{exhibit_id}'")

@app.post("/api/v1/process-audio", response_model=TranslationResponse)
async def process_translation_and_tts(payload: TranslationRequest):
    """
    Endpoint xử lý Dịch thuật & Sinh Audio đa ngôn ngữ
    """
    try:
        results = []
        output_dir = os.path.join(".", "output", payload.exhibit_id)
        os.makedirs(output_dir, exist_ok=True)

        for lang in payload.target_languages:
            # 1. Dịch thuật & áp dụng Glossary
            translated_text = translate_text(payload.original_text, lang)
            
            # 2. Sinh giọng đọc Audio
            audio_filename = f"{payload.exhibit_id}_{lang}.mp3"
            full_disk_path = os.path.join(output_dir, audio_filename)
            
            await generate_audio(translated_text, lang, full_disk_path)
            
            # URL web chuẩn để trình duyệt truy cập file qua static mount /output
            web_audio_url = f"/output/{payload.exhibit_id}/{audio_filename}"
            
            results.append(
                TranslationResult(
                    language=lang,
                    translated_text=translated_text,
                    audio_file_path=web_audio_url
                )
            )

        return TranslationResponse(
            task_id=payload.task_id,
            exhibit_id=payload.exhibit_id,
            status="COMPLETED",
            results=results
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý AI: {str(e)}")
