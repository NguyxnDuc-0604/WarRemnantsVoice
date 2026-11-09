"""
test_tts.py — Unit Tests cho TTS Service và Subtitle Timestamps
Thành viên 2: AI & Pipeline Processing Services
"""

import pytest
from app.services.tts_service import VOICE_MAPPING
from main_fastapi import generate_subtitle_timestamps

def test_voice_mapping_exists():
    """Đảm bảo các ngôn ngữ chính đều có cấu hình giọng đọc Edge TTS Neural"""
    required_langs = ["vi", "en", "fr", "ja", "ko", "zh", "de", "es", "ru", "th"]
    for lang in required_langs:
        assert lang in VOICE_MAPPING
        assert "Neural" in VOICE_MAPPING[lang]

def test_subtitle_timestamps_generation():
    """Kiểm tra thuật toán sinh timestamps phụ đề đồng bộ"""
    text = "Đây là câu thứ nhất. Đây là câu thứ hai! Còn đây là câu thứ ba?"
    timestamps = generate_subtitle_timestamps(text, total_duration=9.0)

    assert len(timestamps) == 3
    assert timestamps[0]["id"] == 0
    assert timestamps[0]["start"] == 0.0
    assert timestamps[0]["end"] > 0.0
    assert timestamps[-1]["end"] >= timestamps[1]["end"]

def test_subtitle_timestamps_single_sentence():
    """Kiểm tra sinh phụ đề cho văn bản ngắn 1 câu"""
    text = "Hiện vật lịch sử tiêu biểu của bảo tàng."
    timestamps = generate_subtitle_timestamps(text)
    assert len(timestamps) == 1
    assert timestamps[0]["text"] == text
