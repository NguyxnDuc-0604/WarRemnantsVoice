from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List
import os
import asyncio

from app.services.translate_service import translate_text
from app.services.tts_service import generate_audio

app = FastAPI(
    title="WarRemnantsVoice - AI Pipeline Service",
    description="API dịch thuật đa ngôn ngữ và sinh âm thanh thuyết minh tự động",
    version="1.0.0"
)

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
    return {"status": "ok", "service": "AI Pipeline Service"}

@app.post("/api/v1/process-audio", response_model=TranslationResponse)
async def process_translation_and_tts(payload: TranslationRequest):
    """
    Endpoint xử lý Dịch thuật & Sinh Audio đa ngôn ngữ
    """
    try:
        results = []
        output_dir = f"./output/{payload.exhibit_id}"
        os.makedirs(output_dir, exist_ok=True)

        for lang in payload.target_languages:
            # 1. Dịch thuật & áp dụng Glossary
            translated_text = translate_text(payload.original_text, lang)
            
            # 2. Sinh giọng đọc Audio
            audio_filename = f"{payload.exhibit_id}_{lang}.mp3"
            audio_path = os.path.join(output_dir, audio_filename)
            
            await generate_audio(translated_text, lang, audio_path)
            
            results.append(
                TranslationResult(
                    language=lang,
                    translated_text=translated_text,
                    audio_file_path=audio_path
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