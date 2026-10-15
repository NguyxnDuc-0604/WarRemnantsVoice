import edge_tts
import os

# Ánh xạ ngôn ngữ với giọng đọc truyền cảm của Microsoft Edge TTS
VOICE_MAPPING = {
    "vi": "vi-VN-HoaiMyNeural",
    "en": "en-US-AndrewNeural",
    "fr": "fr-FR-HenriNeural",
    "ja": "ja-JP-KeitaNeural",
    "zh": "zh-CN-YunxiNeural"
}

async def generate_audio(text: str, target_lang: str, output_path: str) -> str:
    """
    Sinh file âm thanh từ văn bản thuyết minh.
    """
    voice = VOICE_MAPPING.get(target_lang, "en-US-AndrewNeural")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return output_path