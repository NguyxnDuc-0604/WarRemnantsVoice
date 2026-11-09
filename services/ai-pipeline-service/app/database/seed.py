"""
seed.py — Khởi tạo dữ liệu mẫu cho pipeline_db

Chỉ seed các bảng thuộc quyền sở hữu của AI Pipeline Service:
  - SupportedLanguage (15 ngôn ngữ)
  - Glossary (10 thuật ngữ lịch sử)

Lưu ý: KHÔNG seed Exhibit, ContentSource, TourRoute — đó là việc của exhibit-service.
"""

from sqlalchemy.orm import Session
from app.database.models import SupportedLanguage, Glossary


def seed_pipeline_database(db: Session) -> None:
    """
    Tự động nạp dữ liệu mẫu vào pipeline_db khi khởi động service
    nếu database còn trống.
    """
    # ============================================================
    # 1. Seed 15 ngôn ngữ khả dụng (Supported Languages)
    # ============================================================
    if db.query(SupportedLanguage).count() == 0:
        print("[pipeline_db] Đang khởi tạo 15 ngôn ngữ khả dụng...")
        languages = [
            SupportedLanguage(code="vi", name_vi="Tiếng Việt",        native_name="Tiếng Việt",      flag_icon="🇻🇳", voice_code="vi-VN-HoaiMyNeural",    is_default=True,  sort_order=1),
            SupportedLanguage(code="en", name_vi="Tiếng Anh",         native_name="English",          flag_icon="🇬🇧", voice_code="en-US-AndrewNeural",    is_default=True,  sort_order=2),
            SupportedLanguage(code="fr", name_vi="Tiếng Pháp",        native_name="Français",         flag_icon="🇫🇷", voice_code="fr-FR-HenriNeural",     is_default=False, sort_order=3),
            SupportedLanguage(code="zh", name_vi="Tiếng Trung",       native_name="中文",              flag_icon="🇨🇳", voice_code="zh-CN-YunxiNeural",     is_default=False, sort_order=4),
            SupportedLanguage(code="ja", name_vi="Tiếng Nhật",        native_name="日本語",            flag_icon="🇯🇵", voice_code="ja-JP-KeitaNeural",     is_default=False, sort_order=5),
            SupportedLanguage(code="ko", name_vi="Tiếng Hàn",         native_name="한국어",            flag_icon="🇰🇷", voice_code="ko-KR-SunHiNeural",     is_default=False, sort_order=6),
            SupportedLanguage(code="es", name_vi="Tiếng Tây Ban Nha", native_name="Español",          flag_icon="🇪🇸", voice_code="es-ES-AlvaroNeural",    is_default=False, sort_order=7),
            SupportedLanguage(code="de", name_vi="Tiếng Đức",         native_name="Deutsch",          flag_icon="🇩🇪", voice_code="de-DE-ConradNeural",    is_default=False, sort_order=8),
            SupportedLanguage(code="ru", name_vi="Tiếng Nga",         native_name="Русский",          flag_icon="🇷🇺", voice_code="ru-RU-DmitryNeural",    is_default=False, sort_order=9),
            SupportedLanguage(code="it", name_vi="Tiếng Ý",           native_name="Italiano",         flag_icon="🇮🇹", voice_code="it-IT-DiegoNeural",     is_default=False, sort_order=10),
            SupportedLanguage(code="th", name_vi="Tiếng Thái",        native_name="ภาษาไทย",          flag_icon="🇹🇭", voice_code="th-TH-NiwatNeural",     is_default=False, sort_order=11),
            SupportedLanguage(code="id", name_vi="Tiếng Indonesia",   native_name="Bahasa Indonesia", flag_icon="🇮🇩", voice_code="id-ID-ArdiNeural",      is_default=False, sort_order=12),
            SupportedLanguage(code="km", name_vi="Tiếng Khmer",       native_name="ភាសាខ្មែរ",        flag_icon="🇰🇭", voice_code="km-KH-PisethNeural",    is_default=False, sort_order=13),
            SupportedLanguage(code="lo", name_vi="Tiếng Lào",         native_name="ພາສາລາວ",          flag_icon="🇱🇦", voice_code="lo-LA-KeomanyNeural",   is_default=False, sort_order=14),
            SupportedLanguage(code="ar", name_vi="Tiếng Ả Rập",       native_name="العربية",          flag_icon="🇸🇦", voice_code="ar-SA-HamedNeural",     is_default=False, sort_order=15),
        ]
        db.add_all(languages)
        db.commit()
        print(f"[pipeline_db] ✅ Đã seed {len(languages)} ngôn ngữ.")

    # ============================================================
    # 2. Seed Glossary — Từ điển thuật ngữ lịch sử
    # ============================================================
    if db.query(Glossary).count() == 0:
        print("[pipeline_db] Đang khởi tạo từ điển thuật ngữ lịch sử...")
        glossary_items = [
            Glossary(term_vi="Ấp Bắc",                        term_en="Ap Bac",                      context_note="Địa danh chiến dịch năm 1963",                           is_restricted=True),
            Glossary(term_vi="Chiến dịch Hồ Chí Minh",        term_en="Ho Chi Minh Campaign",         context_note="Chiến dịch mùa Xuân 1975 giải phóng miền Nam",           is_restricted=True),
            Glossary(term_vi="Chứng tích chiến tranh",         term_en="War Remnants",                 context_note="Tên chính thức của bảo tàng",                            is_restricted=True),
            Glossary(term_vi="Mậu Thân 1968",                  term_en="Tet Offensive 1968",           context_note="Cuộc Tổng tiến công và nổi dậy Xuân Mậu Thân",           is_restricted=True),
            Glossary(term_vi="Bảo tàng Chứng tích Chiến tranh",term_en="War Remnants Museum",          context_note="Tên tổ chức chính thức",                                 is_restricted=True),
            Glossary(term_vi="Chuồng cọp",                     term_en="Tiger Cages",                  context_note="Hệ thống giam giữ đặc biệt tại nhà tù Côn Đảo",          is_restricted=True),
            Glossary(term_vi="Vua chiến trường",               term_en="King of Battlefield",          context_note="Biệt danh pháo tự hành M107 175mm",                     is_restricted=False),
            Glossary(term_vi="Chiến dịch Điện Biên Phủ",      term_en="Dien Bien Phu Campaign",       context_note="Chiến dịch 1954 kết thúc chiến tranh Pháp - Việt",       is_restricted=True),
            Glossary(term_vi="Giải phóng miền Nam",            term_en="Liberation of South Vietnam",  context_note="Sự kiện 30/4/1975",                                      is_restricted=True),
            Glossary(term_vi="Dinh Độc Lập",                   term_en="Independence Palace",          context_note="Địa danh lịch sử, nay là Hội trường Thống Nhất",         is_restricted=True),
        ]
        db.add_all(glossary_items)
        db.commit()
        print(f"[pipeline_db] ✅ Đã seed {len(glossary_items)} thuật ngữ Glossary.")
