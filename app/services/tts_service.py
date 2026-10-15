import edge_tts

# Bản đồ ánh xạ mã ngôn ngữ sang giọng đọc Neural của Microsoft Edge
VOICE_MAP = {
    "vi": "vi-VN-HoaiMyNeural",      # Tiếng Việt
    "en": "en-US-AndrewNeural",      # Tiếng Anh
    "fr": "fr-FR-HenriNeural",       # Tiếng Pháp
    "zh": "zh-CN-YunxiNeural",       # Tiếng Trung
    "ja": "ja-JP-KeitaNeural",       # Tiếng Nhật
    "ko": "ko-KR-InJoonNeural",      # Tiếng Hàn
    "de": "de-DE-KillianNeural",     # Tiếng Đức
    "es": "es-ES-AlvaroNeural"       # Tiếng Tây Ban Nha
}

# BẮT BUỘC tên class phải là TTSService
class TTSService:
    async def generate_speech(self, text: str, lang_code: str, output_file_path: str) -> str:
        """
        Sinh file âm thanh audio MP3 từ văn bản và lưu vào output_file_path
        """
        voice = VOICE_MAP.get(lang_code, "en-US-AndrewNeural")
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file_path)
        return output_file_path