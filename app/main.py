from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
import shutil
import os

from app.services.asr_service import ASRService
from app.services.translation_service import TranslationService
from app.services.tts_service import TTSService

app = FastAPI(title="WarRemnantsVoice AI Pipeline API", version="1.0.0")

asr_service = ASRService()
translation_service = TranslationService()
tts_service = TTSService()

class TranslationRequest(BaseModel):
    text: str
    target_lang: str

class TTSRequest(BaseModel):
    text: str
    lang_code: str

@app.get("/")
def health_check():
    return {"status": "ok", "service": "AI Pipeline Services"}

# Endpoint 1: Bóc băng Audio tiếng Việt
@app.post("/api/v1/ai/asr")
async def transcribe_audio(file: UploadFile = File(...)):
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = asr_service.transcribe_audio(temp_path)
    os.remove(temp_path)
    return result

# Endpoint 2: Dịch văn bản + Áp dụng từ điển lịch sử
@app.post("/api/v1/ai/translate")
async def translate_text(req: TranslationRequest):
    translated = await translation_service.translate_text(req.text, req.target_lang)
    return {"original_text": req.text, "target_lang": req.target_lang, "translated_text": translated}

# Endpoint 3: Sinh giọng đọc Audio MP3
@app.post("/api/v1/ai/tts")
async def text_to_speech(req: TTSRequest):
    output_path = f"/tmp/tts_output_{req.lang_code}.mp3"
    await tts_service.generate_speech(req.text, req.lang_code, output_path)
    return {"status": "success", "file_path": output_path}
from fastapi import FastAPI

# BẮT BUỘC phải đặt tên biến là 'app' (chữ thường)
app = FastAPI(title="WarRemnantsVoice AI Pipeline API")

@app.get("/")
def health_check():
    return {"status": "ok", "service": "AI Pipeline Services"}
from fastapi import FastAPI
from pydantic import BaseModel
from app.services.translation_service import TranslationService
from app.services.tts_service import TTSService

# Khởi tạo FastAPI
app = FastAPI(title="WarRemnantsVoice AI Pipeline API", version="1.0.0")

# Khởi tạo các Service
translation_service = TranslationService()
tts_service = TTSService()

# Định nghĩa cấu trúc dữ liệu nhận vào (Request Schema)
class TranslationRequest(BaseModel):
    text: str
    target_lang: str

class TTSRequest(BaseModel):
    text: str
    lang_code: str

# 1. API Health Check
@app.get("/", summary="Health Check")
def health_check():
    return {"status": "ok", "service": "AI Pipeline Services"}

# 2. API Dịch thuật
@app.post("/api/v1/ai/translate", summary="Dịch thuật văn bản thuyết minh")
async def translate_text(req: TranslationRequest):
    translated = await translation_service.translate_text(req.text, req.target_lang)
    return {
        "original_text": req.text,
        "target_lang": req.target_lang,
        "translated_text": translated
    }

# 3. API Sinh giọng nói Audio MP3
@app.post("/api/v1/ai/tts", summary="Sinh file Audio MP3 từ văn bản")
async def text_to_speech(req: TTSRequest):
    output_path = f"/tmp_tts_{req.lang_code}.mp3"
    await tts_service.generate_speech(req.text, req.lang_code, output_path)
    return {
        "status": "success",
        "message": "Đã tạo file audio thành công",
        "file_path": output_path
    }
    from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles  # <--- Thêm import này
from pydantic import BaseModel
from app.services.translation_service import TranslationService
from app.services.tts_service import TTSService
import os

app = FastAPI(title="WarRemnantsVoice AI Pipeline API", version="1.0.0")

# Thêm dòng này để biến thư mục chứa file MP3 thành link web tĩnh
os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

translation_service = TranslationService()
tts_service = TTSService()

class TTSRequest(BaseModel):
    text: str
    lang_code: str

@app.post("/api/v1/ai/tts", summary="Sinh file Audio MP3 từ văn bản")
async def text_to_speech(req: TTSRequest):
    filename = f"audio_{req.lang_code}.mp3"
    output_path = f"static/audio/{filename}"
    
    await tts_service.generate_speech(req.text, req.lang_code, output_path)
    
    # Trả về URL đường dẫn web trực tiếp để nghe
    file_url = f"http://127.0.0.1:8000/static/audio/{filename}"
    return {
        "status": "success",
        "audio_url": file_url
    }