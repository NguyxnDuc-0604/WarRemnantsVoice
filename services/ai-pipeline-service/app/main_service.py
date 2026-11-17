import os
import re
import logging
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.translate_service import translate_text
from app.services.tts_service import generate_audio, VOICE_MAPPING

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [AI-PIPELINE] %(message)s")
logger = logging.getLogger("ai-pipeline-service")

app = FastAPI(
    title="WarRemnantsVoice - AI Pipeline Service",
    description="Dịch vụ AI dịch thuật đa ngôn ngữ và chuyển văn bản thành giọng đọc truyền cảm (Neural TTS)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thư mục lưu audio (đồng bộ với Streaming Service)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
DEFAULT_MEDIA_DIR = os.path.join(PROJECT_ROOT, "output")
MEDIA_DIR = os.getenv("MEDIA_DIR", DEFAULT_MEDIA_DIR)
os.makedirs(MEDIA_DIR, exist_ok=True)

class TranslationRequest(BaseModel):
    task_id: str
    exhibit_id: str
    original_text: str
    target_languages: List[str] = ["en"]

class InternalGenerateAudioRequest(BaseModel):
    exhibit_code: str
    title: str
    original_text: str
    language: str

def generate_subtitle_timestamps(text: str, total_duration: float = None):
    """Chia văn bản thành từng câu kèm timestamps giả lập đồng bộ với nhịp nói"""
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
def health_check():
    return {
        "service": "AI Pipeline Service",
        "status": "UP",
        "supported_voices": list(VOICE_MAPPING.keys()),
        "output_dir": MEDIA_DIR
    }

@app.post("/api/v1/process-audio")
async def process_translation_and_tts(payload: TranslationRequest):
    """API xử lý batch dịch thuật và tạo tệp audio cho nhiều ngôn ngữ"""
    if not payload.target_languages:
        raise HTTPException(status_code=400, detail="Danh sách ngôn ngữ không được để trống")
    if not payload.original_text.strip():
        raise HTTPException(status_code=400, detail="Nội dung không được để trống")

    results = []
    output_dir = os.path.join(MEDIA_DIR, payload.exhibit_id)
    os.makedirs(output_dir, exist_ok=True)

    for lang in payload.target_languages:
        try:
            if lang == "vi":
                translated_text = payload.original_text
            else:
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
        except Exception as e:
            logger.error(f"Error processing lang {lang}: {e}")
            results.append({
                "language": lang,
                "error": str(e)
            })

    return {
        "task_id": payload.task_id,
        "exhibit_id": payload.exhibit_id,
        "status": "COMPLETED",
        "results": results
    }

@app.post("/api/v1/internal/generate-audio")
async def internal_generate_audio(req: InternalGenerateAudioRequest):
    """API nội bộ cho Exhibit Service gọi để dịch và sinh âm thanh theo yêu cầu tức thì (On-Demand)"""
    try:
        lang = req.language
        if lang == "vi":
            translated_title = req.title
            translated_text = req.original_text
        else:
            translated_title = translate_text(req.title, lang)
            translated_text = translate_text(req.original_text, lang)

        output_dir = os.path.join(MEDIA_DIR, req.exhibit_code)
        os.makedirs(output_dir, exist_ok=True)
        
        audio_filename = f"{req.exhibit_code}_{lang}.mp3"
        full_disk_path = os.path.join(output_dir, audio_filename)
        
        await generate_audio(translated_text, lang, full_disk_path)
        
        timestamps = generate_subtitle_timestamps(translated_text)
        duration = timestamps[-1]["end"] if timestamps else 30.0
        web_audio_url = f"/output/{req.exhibit_code}/{audio_filename}"

        return {
            "status": "success",
            "translated_title": translated_title,
            "translated_text": translated_text,
            "audio_url": web_audio_url,
            "timestamps": timestamps,
            "duration": duration
        }
    except Exception as e:
        logger.error(f"Internal generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
