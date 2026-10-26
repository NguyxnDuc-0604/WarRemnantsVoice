import edge_tts
import os

# Ánh xạ 15 ngôn ngữ với giọng đọc Neural truyền cảm của Microsoft Edge TTS (FR-12)
VOICE_MAPPING = {
    "vi": "vi-VN-HoaiMyNeural",
    "en": "en-US-AndrewNeural",
    "fr": "fr-FR-HenriNeural",
    "ja": "ja-JP-KeitaNeural",
    "ko": "ko-KR-SunHiNeural",
    "zh": "zh-CN-YunxiNeural",
    "zh-CN": "zh-CN-YunxiNeural",
    "de": "de-DE-ConradNeural",
    "es": "es-ES-AlvaroNeural",
    "it": "it-IT-DiegoNeural",
    "ru": "ru-RU-DmitryNeural",
    "th": "th-TH-NiwatNeural",
    "ar": "ar-SA-HamedNeural",
    "pt": "pt-BR-AntonioNeural",
    "id": "id-ID-ArdiNeural"
}

async def generate_audio(text: str, target_lang: str, output_path: str) -> str:
    """
    Sinh file âm thanh từ văn bản thuyết minh qua Microsoft Edge TTS Neural
    """
    voice = VOICE_MAPPING.get(target_lang, "en-US-AndrewNeural")
    
    # Đảm bảo thư mục đích tồn tại
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return output_path
