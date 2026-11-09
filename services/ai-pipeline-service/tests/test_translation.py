"""
test_translation.py — Unit Tests cho Translation & Glossary Service
Thành viên 2: AI & Pipeline Processing Services
"""

import pytest
from app.utils.glossary import apply_glossary, HISTORICAL_GLOSSARY
from app.services.translate_service import translate_text, LANG_CODE_MAPPING

def test_glossary_replacement_en():
    """Kiểm tra thay thế đúng thuật ngữ lịch sử tiếng Anh"""
    sample_text = "Trận đánh tại Ấp Bắc và Chiến dịch Hồ Chí Minh là dấu mốc quan trọng."
    result = apply_glossary(sample_text, "en")
    assert "Ap Bac" in result
    assert "Ho Chi Minh Campaign" in result

def test_glossary_replacement_fr():
    """Kiểm tra thay thế thuật ngữ tiếng Pháp"""
    sample_text = "Bảo tàng Chứng tích Chiến tranh lưu giữ nhiều hiện vật."
    result = apply_glossary(sample_text, "fr")
    assert "Musée des vestiges de la guerre" in result

def test_translation_same_language():
    """Dịch từ tiếng Việt sang tiếng Việt phải giữ nguyên bản gốc"""
    vi_text = "Xe tăng T-54B số hiệu 390 húc đổ cổng Dinh Độc Lập."
    result = translate_text(vi_text, "vi")
    assert result == vi_text

def test_translation_empty_string():
    """Xử lý an toàn khi đầu vào rỗng"""
    assert translate_text("", "en") == ""
    assert translate_text("   ", "fr") == ""

def test_lang_code_mapping():
    """Kiểm tra mapping mã ngôn ngữ chuẩn Google"""
    assert LANG_CODE_MAPPING.get("zh") == "zh-CN"
    assert LANG_CODE_MAPPING.get("zh-cn") == "zh-CN"
