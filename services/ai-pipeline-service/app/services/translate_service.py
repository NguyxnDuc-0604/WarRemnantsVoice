import urllib.parse
import requests
from app.utils.glossary import apply_glossary

try:
    from deep_translator import GoogleTranslator
    HAS_DEEP_TRANSLATOR = True
except ImportError:
    HAS_DEEP_TRANSLATOR = False

# Ánh xạ mã ngôn ngữ chuẩn Google Translate
LANG_CODE_MAPPING = {
    "zh": "zh-CN",
    "zh-cn": "zh-CN",
    "zh-CN": "zh-CN",
}

def translate_via_google_api(text: str, target_lang: str) -> str:
    """Fallback dịch trực tiếp qua Google Translate Web API miễn phí (không cần API key)"""
    lang = LANG_CODE_MAPPING.get(target_lang.lower(), target_lang)
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=vi&tl={lang}&dt=t&q={urllib.parse.quote(text)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data and isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
            translated_sentences = [part[0] for part in data[0] if part and len(part) > 0 and part[0]]
            return "".join(translated_sentences)
    raise Exception(f"Google Web API returned status {response.status_code}")

def translate_text(text: str, target_lang: str) -> str:
    """
    Dịch văn bản tiếng Việt sang ngôn ngữ đích chuẩn xác và áp dụng Glossary lịch sử
    """
    if not text or not text.strip():
        return ""

    clean_target = target_lang.lower().strip()
    if clean_target == "vi":
        return text.strip()

    # Chuẩn hoá mã ngôn ngữ
    lang_for_google = LANG_CODE_MAPPING.get(clean_target, clean_target)

    translated = None

    # Phương án 1: Dùng deep_translator
    if HAS_DEEP_TRANSLATOR:
        try:
            translator = GoogleTranslator(source="vi", target=lang_for_google)
            # Nếu văn bản dài hơn 4500 ký tự thì chia đoạn
            if len(text) > 4000:
                chunks = [text[i:i+3500] for i in range(0, len(text), 3500)]
                translated = " ".join([translator.translate(chunk) for chunk in chunks])
            else:
                translated = translator.translate(text)
        except Exception as e:
            print(f"[WARN] deep_translator error: {e}, falling back to web API...")

    # Phương án 2: Fallback qua Web API
    if not translated:
        try:
            translated = translate_via_google_api(text, lang_for_google)
        except Exception as e:
            print(f"[ERROR] Both translation methods failed: {e}")
            # Nếu mất mạng hoàn toàn thì giữ nguyên text
            translated = text

    # Áp dụng từ điển thuật ngữ lịch sử (Glossary) sau khi dịch (FR-10, BR-02)
    final_text = apply_glossary(translated, clean_target)
    return final_text
