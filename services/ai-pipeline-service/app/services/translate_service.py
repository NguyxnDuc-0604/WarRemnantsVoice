import requests
from app.utils.glossary import apply_glossary

def translate_text(text: str, target_lang: str) -> str:
    """
    Dịch văn bản thuyết minh sang ngôn ngữ mục tiêu và áp dụng Glossary lịch sử.
    """
    # Bước 1: Áp dụng từ điển thuật ngữ trước/sau khi dịch
    processed_text = apply_glossary(text, target_lang)

    # Nếu cùng ngôn ngữ gốc thì trả về luôn
    if target_lang == "vi":
        return processed_text

    # Giả lập dịch đơn giản (hoặc thay bằng gọi OpenAI/DeepL API tại đây)
    # Ví dụ tích hợp API dịch:
    # response = requests.post(...)
    
    translated = f"[{target_lang.upper()}] {processed_text}"
    return translated