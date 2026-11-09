"""
test_asr_nlp.py — Unit Tests cho ASR (Speech-to-Text) và NLP Service
Thành viên 2: AI & Pipeline Processing Services
"""

import pytest
from app.services.asr_service import normalize_text_nlp, transcribe_audio_file

def test_nlp_normalize_spaces():
    """Kiểm tra làm sạch khoảng trắng thừa và ký tự tab"""
    raw = "   Hiện   vật    lịch   sử    Việt   Nam.   "
    cleaned = normalize_text_nlp(raw)
    assert cleaned == "Hiện vật lịch sử Việt Nam."

def test_nlp_normalize_punctuation():
    """Kiểm tra căn chỉnh dấu câu chuẩn (sát từ trước, cách từ sau)"""
    raw = "trực thăng UH-1,xe tăng T-54B!pháo M107."
    cleaned = normalize_text_nlp(raw)
    assert "UH-1, xe tăng" in cleaned
    assert "T-54B! Pháo" in cleaned

def test_nlp_normalize_capitalization():
    """Kiểm tra tự động viết hoa chữ cái đầu câu"""
    raw = "chiến dịch hồ chí minh. non sông thống nhất."
    cleaned = normalize_text_nlp(raw)
    assert cleaned.startswith("Chiến")
    assert "Non sông" in cleaned

def test_asr_file_not_found():
    """Kiểm tra bắt lỗi chuẩn xác khi file audio không tồn tại"""
    with pytest.raises(FileNotFoundError):
        transcribe_audio_file("non_existent_audio_file_12345.mp3")
