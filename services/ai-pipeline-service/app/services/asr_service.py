"""
asr_service.py — ASR (Speech-to-Text) & NLP Text Normalization Service
Thành viên 2: AI & Pipeline Processing Services

Nhiệm vụ:
  1. ASR: Bóc tách giọng nói từ tệp âm thanh (WAV/MP3/M4A) thành văn bản tiếng Việt/đa ngôn ngữ.
  2. NLP: Chuẩn hóa câu từ, làm sạch văn bản thô, ngắt câu và căn chỉnh dấu câu.
"""

import os
import re
from typing import Dict, Any, Optional

# Cố gắng load whisper nếu môi trường hỗ trợ
_WHISPER_MODEL = None
_WHISPER_LOADED = False

def get_whisper_model(model_name: str = "base"):
    """
    Lazy load Whisper model vào RAM khi có yêu cầu bóc tách âm thanh
    """
    global _WHISPER_MODEL, _WHISPER_LOADED
    if not _WHISPER_LOADED:
        try:
            import whisper
            print(f"[ASR] Đang tải mô hình Whisper ({model_name})...")
            _WHISPER_MODEL = whisper.load_model(model_name)
            _WHISPER_LOADED = True
            print("[ASR] Tải mô hình Whisper thành công!")
        except Exception as e:
            print(f"[ASR-WARN] Không thể tải thư viện whisper ({e}). Sẽ sử dụng bộ bóc tách dự phòng.")
            _WHISPER_MODEL = None
            _WHISPER_LOADED = True
    return _WHISPER_MODEL


def normalize_text_nlp(raw_text: str) -> str:
    """
    NLP Service: Chuẩn hóa câu từ và ngữ pháp cơ bản:
      - Xóa khoảng trắng thừa, ký tự điều khiển lạ
      - Viết hoa đầu câu
      - Chuẩn hóa dấu câu (. , ! ?)
    """
    if not raw_text:
        return ""

    # Loại bỏ khoảng trắng thừa và tab
    text = re.sub(r'\s+', ' ', raw_text.strip())

    # Đảm bảo dấu câu đứng sát từ phía trước và có dấu cách phía sau
    text = re.sub(r'\s*([,.:;?!])\s*', r'\1 ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Viết hoa chữ cái đầu tiên của câu
    sentences = re.split(r'([.!?]\s*)', text)
    normalized_parts = []
    for part in sentences:
        if part and not re.match(r'^[.!?]\s*$', part):
            part = part[0].upper() + part[1:] if len(part) > 1 else part.upper()
        normalized_parts.append(part)

    return "".join(normalized_parts).strip()


def transcribe_audio_file(audio_path: str, language: Optional[str] = "vi") -> Dict[str, Any]:
    """
    Bóc tách âm thanh thành văn bản qua Whisper ASR kèm xử lý NLP.
    Nếu Whisper chưa được cài đặt (trên môi trường nhẹ), fallback sang thông báo tương thích.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Tệp âm thanh không tồn tại tại: {audio_path}")

    model = get_whisper_model()
    if model is not None:
        try:
            result = model.transcribe(audio_path, language=language)
            raw_text = result.get("text", "").strip()
            detected_lang = result.get("language", language or "vi")
            cleaned_text = normalize_text_nlp(raw_text)
            return {
                "status": "success",
                "detected_language": detected_lang,
                "raw_text": raw_text,
                "normalized_text": cleaned_text,
                "segments": result.get("segments", [])
            }
        except Exception as err:
            return {
                "status": "error",
                "error": f"Lỗi trong quá trình bóc tách ASR: {str(err)}"
            }
    else:
        # Fallback chế độ demo / mô phỏng chuẩn
        return {
            "status": "mock_completed",
            "detected_language": language or "vi",
            "raw_text": "Trực thăng UH-1 Iroquois là biểu tượng không quân trong Chiến tranh Việt Nam.",
            "normalized_text": "Trực thăng UH-1 Iroquois là biểu tượng không quân trong Chiến tranh Việt Nam.",
            "note": "ASR chạy ở chế độ mô phỏng nhẹ (cần cài đặt openai-whisper và ffmpeg để chạy full model GPU/CPU)."
        }
