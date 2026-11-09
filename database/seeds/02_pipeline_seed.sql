-- ============================================================
-- Seed data cho pipeline_db
-- Thành viên 2: AI & Pipeline Processing Services
-- ============================================================

-- ============================================================
-- SEED: 15 ngôn ngữ khả dụng
-- ============================================================
INSERT INTO supported_language (code, name_vi, native_name, flag_icon, voice_code, is_active, is_default, sort_order) VALUES
('vi', 'Tiếng Việt',       'Tiếng Việt',      '🇻🇳', 'vi-VN-HoaiMyNeural',    TRUE, TRUE,  1),
('en', 'Tiếng Anh',        'English',          '🇬🇧', 'en-US-AndrewNeural',    TRUE, TRUE,  2),
('fr', 'Tiếng Pháp',       'Français',         '🇫🇷', 'fr-FR-HenriNeural',     TRUE, FALSE, 3),
('zh', 'Tiếng Trung',      '中文',              '🇨🇳', 'zh-CN-YunxiNeural',     TRUE, FALSE, 4),
('ja', 'Tiếng Nhật',       '日本語',            '🇯🇵', 'ja-JP-KeitaNeural',     TRUE, FALSE, 5),
('ko', 'Tiếng Hàn',        '한국어',            '🇰🇷', 'ko-KR-SunHiNeural',     TRUE, FALSE, 6),
('es', 'Tiếng Tây Ban Nha','Español',          '🇪🇸', 'es-ES-AlvaroNeural',    TRUE, FALSE, 7),
('de', 'Tiếng Đức',        'Deutsch',          '🇩🇪', 'de-DE-ConradNeural',    TRUE, FALSE, 8),
('ru', 'Tiếng Nga',        'Русский',          '🇷🇺', 'ru-RU-DmitryNeural',    TRUE, FALSE, 9),
('it', 'Tiếng Ý',          'Italiano',         '🇮🇹', 'it-IT-DiegoNeural',     TRUE, FALSE, 10),
('th', 'Tiếng Thái',       'ภาษาไทย',          '🇹🇭', 'th-TH-NiwatNeural',     TRUE, FALSE, 11),
('id', 'Tiếng Indonesia',  'Bahasa Indonesia', '🇮🇩', 'id-ID-ArdiNeural',      TRUE, FALSE, 12),
('km', 'Tiếng Khmer',      'ភាសាខ្មែរ',        '🇰🇭', 'km-KH-PisethNeural',    TRUE, FALSE, 13),
('lo', 'Tiếng Lào',        'ພາສາລາວ',          '🇱🇦', 'lo-LA-KeomanyNeural',   TRUE, FALSE, 14),
('ar', 'Tiếng Ả Rập',      'العربية',          '🇸🇦', 'ar-SA-HamedNeural',     TRUE, FALSE, 15)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- SEED: Từ điển thuật ngữ lịch sử - quân sự chuẩn hóa
-- ============================================================
INSERT INTO glossary (term_vi, term_en, context_note, is_restricted) VALUES
('Ấp Bắc',                       'Ap Bac',                   'Địa danh chiến dịch năm 1963',                           TRUE),
('Chiến dịch Hồ Chí Minh',       'Ho Chi Minh Campaign',     'Chiến dịch mùa Xuân 1975 giải phóng miền Nam',           TRUE),
('Chứng tích chiến tranh',        'War Remnants',             'Tên chính thức của bảo tàng',                            TRUE),
('Mậu Thân 1968',                 'Tet Offensive 1968',       'Cuộc Tổng tiến công và nổi dậy Xuân Mậu Thân',           TRUE),
('Bảo tàng Chứng tích Chiến tranh','War Remnants Museum',     'Tên tổ chức chính thức',                                 TRUE),
('Chuồng cọp',                    'Tiger Cages',              'Hệ thống giam giữ đặc biệt tại nhà tù Côn Đảo',          TRUE),
('Vua chiến trường',              'King of Battlefield',      'Biệt danh pháo tự hành M107 175mm',                     FALSE),
('Chiến dịch Điện Biên Phủ',     'Dien Bien Phu Campaign',   'Chiến dịch 1954 kết thúc chiến tranh Pháp - Việt',       TRUE),
('Giải phóng miền Nam',           'Liberation of South Vietnam', 'Sự kiện 30/4/1975',                                  TRUE),
('Dinh Độc Lập',                  'Independence Palace',      'Địa danh lịch sử Sài Gòn, nay là Hội trường Thống Nhất', TRUE)
ON CONFLICT (term_vi) DO NOTHING;
