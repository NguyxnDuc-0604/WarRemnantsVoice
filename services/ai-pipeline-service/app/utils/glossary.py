# Từ điển chuẩn hóa thuật ngữ lịch sử Bảo tàng Chứng tích Chiến tranh
HISTORICAL_GLOSSARY = {
    "en": {
        "Ấp Bắc": "Ap Bac",
        "Chiến dịch Hồ Chí Minh": "Ho Chi Minh Campaign",
        "Chứng tích chiến tranh": "War Remnants",
        "Mậu Thân 1968": "Tet Offensive 1968",
        "Bảo tàng Chứng tích Chiến tranh": "War Remnants Museum"
    },
    "fr": {
        "Ấp Bắc": "Ap Bac",
        "Chiến dịch Hồ Chí Minh": "Campagne Ho Chi Minh",
        "Chứng tích chiến tranh": "Vestiges de guerre",
        "Bảo tàng Chứng tích Chiến tranh": "Musée des vestiges de la guerre"
    }
}

def apply_glossary(text: str, target_lang: str) -> str:
    """Thay thế hoặc chuẩn hóa thuật ngữ theo từ điển lịch sử."""
    glossary = HISTORICAL_GLOSSARY.get(target_lang, {})
    for term, replacement in glossary.items():
        text = text.replace(term, replacement)
    return text