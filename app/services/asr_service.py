import os
from faster_whisper import WhisperModel

# BẮT BUỘC tên class phải viết chính xác là ASRService
class ASRService:
    def __init__(self, model_size: str = "base"):
        # Dùng CPU với định dạng int8 cho nhẹ
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def transcribe_audio(self, audio_path: str) -> dict:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"File audio không tồn tại: {audio_path}")

        segments, info = self.model.transcribe(audio_path, language="vi", beam_size=5)
        
        full_text = []
        timestamps = []

        for segment in segments:
            full_text.append(segment.text)
            timestamps.append({
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip()
            })

        return {
            "language": info.language,
            "full_text": " ".join(full_text).strip(),
            "timestamps": timestamps
        }