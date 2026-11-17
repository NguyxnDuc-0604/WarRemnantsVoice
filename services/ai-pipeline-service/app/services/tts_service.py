import edge_tts
import os
import asyncio
import logging
import urllib.request
import urllib.parse
import shutil

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    "ar": "ar-EG-SalmaNeural",
    "pt": "pt-BR-AntonioNeural",
    "id": "id-ID-ArdiNeural"
}

def generate_google_tts_sync(text: str, target_lang: str, output_path: str) -> str:
    """
    Fallback TTS sử dụng Google Translate TTS khi Edge TTS gặp lỗi hoặc kiểm duyệt từ ngữ
    """
    lang = target_lang.split("-")[0] if target_lang != "zh-CN" else "zh-CN"
    words = text.split()
    chunks = []
    curr = []
    curr_len = 0
    for w in words:
        if curr_len + len(w) + 1 > 90:
            chunks.append(" ".join(curr))
            curr = [w]
            curr_len = len(w)
        else:
            curr.append(w)
            curr_len += len(w) + 1
    if curr:
        chunks.append(" ".join(curr))

    combined = bytearray()
    for chunk in chunks:
        url = "https://translate.google.com/translate_tts?ie=UTF-8&tl=" + lang + "&client=tw-ob&q=" + urllib.parse.quote(chunk)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            combined.extend(resp.read())

    tmp_path = output_path + ".tmp"
    with open(tmp_path, "wb") as f:
        f.write(combined)

    if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
        shutil.move(tmp_path, output_path)
        return output_path
    else:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise RuntimeError(f"Google TTS sinh tệp rỗng cho ngôn ngữ {target_lang}")

async def generate_audio(
    text: str,
    target_lang: str,
    output_path: str
) -> str:
    """
    Sinh file âm thanh từ văn bản thuyết minh qua Microsoft Edge TTS Neural (với Google TTS fallback)
    """
    voice = VOICE_MAPPING.get(target_lang, "en-US-AndrewNeural")
    
    # Đảm bảo thư mục đích tồn tại
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    tmp_path = output_path + ".tmp"
    try:
        communicate = edge_tts.Communicate(text, voice)
        await asyncio.wait_for(communicate.save(tmp_path), timeout=15.0)
        if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
            shutil.move(tmp_path, output_path)
            return output_path
        else:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise RuntimeError(f"Edge TTS sinh tệp rỗng cho ngôn ngữ {target_lang}")
    except Exception as e:
        logger.warning(f"Edge TTS thất bại ({e}), đang chuyển sang Google TTS fallback cho {target_lang}...")
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, generate_google_tts_sync, text, target_lang, output_path)
