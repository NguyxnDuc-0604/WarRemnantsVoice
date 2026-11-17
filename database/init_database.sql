-- ====================================================================
-- HỆ THỐNG THUYẾT MINH TỰ ĐỘNG ĐA NGÔN NGỮ CHO BẢO TÀNG CHỨNG TÍCH CHIẾN TRANH
-- Dự án: WarRemnantsVoice (Đồ án Công Nghệ Phần Mềm - Nhóm 3)
-- CƠ SỞ DỮ LIỆU CHUẨN THEO PRD PHẦN III (DATA DICTIONARY - 7 BẢNG)
-- ====================================================================

-- Kích hoạt extension sinh UUID ngẫu nhiên (nếu dùng PostgreSQL)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ====================================================================
-- 0. BẢNG SUPPORTED_LANGUAGE (Danh mục 15 ngôn ngữ khả dụng) - Localization Service
-- ====================================================================
CREATE TABLE IF NOT EXISTS supported_language (
    code VARCHAR(10) PRIMARY KEY,
    name_vi VARCHAR(100) NOT NULL,
    native_name VARCHAR(100) NOT NULL,
    flag_icon VARCHAR(10),
    voice_code VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Nạp sẵn 15 ngôn ngữ chuẩn theo PRD
INSERT INTO supported_language (code, name_vi, native_name, flag_icon, voice_code, is_active, is_default, sort_order) VALUES
('vi', 'Tiếng Việt', 'Tiếng Việt', '🇻🇳', 'vi-VN-HoaiMyNeural', TRUE, TRUE, 1),
('en', 'Tiếng Anh', 'English', '🇬🇧', 'en-US-JennyNeural', TRUE, TRUE, 2),
('fr', 'Tiếng Pháp', 'Français', '🇫🇷', 'fr-FR-DeniseNeural', TRUE, FALSE, 3),
('zh', 'Tiếng Trung', '中文', '🇨🇳', 'zh-CN-XiaoxiaoNeural', TRUE, FALSE, 4),
('ja', 'Tiếng Nhật', '日本語', '🇯🇵', 'ja-JP-NanamiNeural', TRUE, FALSE, 5),
('ko', 'Tiếng Hàn', '한국어', '🇰🇷', 'ko-KR-SunHiNeural', TRUE, FALSE, 6),
('es', 'Tiếng Tây Ban Nha', 'Español', '🇪🇸', 'es-ES-ElviraNeural', TRUE, FALSE, 7),
('de', 'Tiếng Đức', 'Deutsch', '🇩🇪', 'de-DE-KatjaNeural', TRUE, FALSE, 8),
('ru', 'Tiếng Nga', 'Русский', '🇷🇺', 'ru-RU-SvetlanaNeural', TRUE, FALSE, 9),
('it', 'Tiếng Ý', 'Italiano', '🇮🇹', 'it-IT-ElsaNeural', TRUE, FALSE, 10),
('th', 'Tiếng Thái', 'ภาษาไทย', '🇹🇭', 'th-TH-PremwadeeNeural', TRUE, FALSE, 11),
('id', 'Tiếng Indonesia', 'Bahasa Indonesia', '🇮🇩', 'id-ID-GadisNeural', TRUE, FALSE, 12),
('km', 'Tiếng Khmer', 'ភាសាខ្មែរ', '🇰🇭', 'km-KH-PisethNeural', TRUE, FALSE, 13),
('lo', 'Tiếng Lào', 'ພາສາລາວ', '🇱🇦', 'lo-LA-KeomanyNeural', TRUE, FALSE, 14),
('ar', 'Tiếng Ả Rập', 'العربية', '🇸🇦', 'ar-SA-ZariyahNeural', TRUE, FALSE, 15)
ON CONFLICT (code) DO NOTHING;

-- ====================================================================
-- 1. BẢNG EXHIBIT (Hiện vật trưng bày) - Quản lý bởi Exhibit Core Service
-- ====================================================================
CREATE TABLE IF NOT EXISTS exhibit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    title_en VARCHAR(255),
    room_id VARCHAR(50) NOT NULL,
    zone VARCHAR(100) DEFAULT 'Khu trưng bày',
    period VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    radius INT DEFAULT 15,
    thumbnail_url VARCHAR(500),
    content_version INT NOT NULL DEFAULT 1,
    is_published BOOLEAN NOT NULL DEFAULT TRUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- 2. BẢNG CONTENT_SOURCE (Nội dung nguồn tiếng Việt)
-- ====================================================================
CREATE TABLE IF NOT EXISTS content_source (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exhibit_id UUID NOT NULL REFERENCES exhibit(id) ON DELETE CASCADE,
    original_text TEXT,
    original_audio_url VARCHAR(500),
    content_version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- 3. BẢNG LOCALIZATION (Bản dịch & Phụ đề đa ngôn ngữ) - Localization Service
-- ====================================================================
CREATE TABLE IF NOT EXISTS localization (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exhibit_id UUID NOT NULL, -- Decoupled Logical Foreign Key (PRD III.2)
    language_code VARCHAR(10) NOT NULL,
    translated_title VARCHAR(255) NOT NULL,
    translated_text TEXT NOT NULL,
    timestamps_json JSONB,
    content_version INT NOT NULL DEFAULT 1,
    is_reviewed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_exhibit_lang_version UNIQUE (exhibit_id, language_code, content_version)
);

-- ====================================================================
-- 4. BẢNG AUDIO_MEDIA (Tệp âm thanh thuyết minh) - Streaming & Media Service
-- ====================================================================
CREATE TABLE IF NOT EXISTS audio_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    localization_id UUID NOT NULL, -- Decoupled Logical Foreign Key
    file_url VARCHAR(500) NOT NULL,
    storage_path VARCHAR(255) NOT NULL,
    duration_seconds DECIMAL(8, 2) NOT NULL DEFAULT 0,
    bitrate_kbps INT DEFAULT 128,
    voice_code VARCHAR(50),
    status VARCHAR(20) NOT NULL DEFAULT 'ready',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- 5. BẢNG TOUR_ROUTE (Lộ trình chuyên đề tham quan) - Exhibit Core Service
-- ====================================================================
CREATE TABLE IF NOT EXISTS tour_route (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    ordered_exhibits_json JSONB NOT NULL,
    estimated_time INT NOT NULL DEFAULT 45, -- Tính bằng phút
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- 6. BẢNG GLOSSARY (Từ điển chuẩn hóa thuật ngữ lịch sử - quân sự)
-- ====================================================================
CREATE TABLE IF NOT EXISTS glossary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    term_vi VARCHAR(150) UNIQUE NOT NULL,
    term_en VARCHAR(150) NOT NULL,
    context_note VARCHAR(255),
    is_restricted BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- 7. BẢNG LISTENING_METRIC (Số liệu thống kê lượt nghe ẩn danh) - Analytics
-- ====================================================================
CREATE TABLE IF NOT EXISTS listening_metric (
    id BIGSERIAL PRIMARY KEY,
    exhibit_id UUID NOT NULL, -- Decoupled Logical Foreign Key
    exhibit_code VARCHAR(50),
    language_code VARCHAR(10) NOT NULL,
    listened_duration INT NOT NULL,
    trigger_type VARCHAR(20) NOT NULL DEFAULT 'QR_CODE', -- 'QR_CODE' hoặc 'GPS_GEOFENCE'
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tạo Index tối ưu hóa truy vấn nhanh (NFR-01: Truy xuất ≤ 1.5s)
CREATE INDEX IF NOT EXISTS idx_exhibit_code ON exhibit(code);
CREATE INDEX IF NOT EXISTS idx_exhibit_active ON exhibit(is_active, is_published);
CREATE INDEX IF NOT EXISTS idx_localization_lookup ON localization(exhibit_id, language_code);
CREATE INDEX IF NOT EXISTS idx_metric_timestamp ON listening_metric(timestamp);

-- ====================================================================
-- DỮ LIỆU KHỞI TẠO MẪU (SEED DATA CHUẨN BẢO TÀNG CHỨNG TÍCH CHIẾN TRANH)
-- ====================================================================

-- 1. Nạp Từ điển Glossary lịch sử (PRD FR-11, BR-02)
INSERT INTO glossary (term_vi, term_en, context_note) VALUES
('Ấp Bắc', 'Ap Bac', 'Địa danh chiến dịch năm 1963'),
('Chiến dịch Hồ Chí Minh', 'Ho Chi Minh Campaign', 'Chiến dịch mùa Xuân 1975 giải phóng miền Nam'),
('Chứng tích chiến tranh', 'War Remnants', 'Tên chính thức của bảo tàng'),
('Mậu Thân 1968', 'Tet Offensive 1968', 'Cuộc Tổng tiến công và nổi dậy Xuân Mậu Thân'),
('Bảo tàng Chứng tích Chiến tranh', 'War Remnants Museum', 'Tên tổ chức'),
('Chuồng cọp', 'Tiger Cages', 'Hệ thống giam giữ đặc biệt tại nhà tù Côn Đảo'),
('Vua chiến trường', 'King of Battlefield', 'Biệt danh pháo tự hành M107 175mm')
ON CONFLICT (term_vi) DO NOTHING;

-- 2. Nạp Lộ trình chuyên đề mẫu (Tour Route - UC2)
INSERT INTO tour_route (id, title, description, ordered_exhibits_json, estimated_time) VALUES
(
    'a0000000-0000-0000-0000-000000000001',
    'Tuyến 1: Hiện vật ngoài trời & Phương tiện chiến tranh',
    'Khám phá các loại máy bay, trực thăng và xe tăng chủ lực trong Chiến tranh Việt Nam được trưng bày tại sân ngoài trời.',
    '["UH1-BELL", "T54-390", "M107-175"]'::jsonb,
    30
),
(
    'a0000000-0000-0000-0000-000000000002',
    'Tuyến 2: Chứng tích tội ác & Ký ức lịch sử',
    'Tìm hiểu các chứng tích nhà tù, hậu quả chiến tranh và thắng lợi của Chiến dịch Hồ Chí Minh lịch sử.',
    '["CONDAO-CAGE", "HOCHIMINH-CAMPAIGN"]'::jsonb,
    45
)
ON CONFLICT DO NOTHING;

-- 3. Nạp 5 Hiện vật tiêu biểu
-- Hiện vật 1: UH-1 Iroquois
INSERT INTO exhibit (id, code, title, title_en, room_id, zone, latitude, longitude, radius, thumbnail_url, content_version, is_published, is_active)
VALUES (
    'b0000000-0000-0000-0000-000000000001',
    'UH1-BELL',
    'Máy bay trực thăng UH-1 Iroquois ''Huey''',
    'UH-1 Iroquois ''Huey'' Helicopter',
    'OUTDOOR',
    'Khu trưng bày ngoài trời',
    10.77940000,
    106.69220000,
    15,
    'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=800&q=80',
    1,
    TRUE,
    TRUE
) ON CONFLICT (code) DO NOTHING;

INSERT INTO content_source (exhibit_id, original_text, content_version)
VALUES (
    'b0000000-0000-0000-0000-000000000001',
    'Trực thăng UH-1 Iroquois, thường được gọi là ''Huey'', là biểu tượng không quân của quân đội Mỹ trong Chiến tranh Việt Nam. Được sử dụng từ năm 1962 đến 1975 với các nhiệm vụ đổ quân chiến thuật, cứu thương và yểm trợ hoả lực. Chiếc máy bay trưng bày tại đây là một trong những chứng tích ghi lại các cuộc càn quét khốc liệt trên chiến trường miền Nam.',
    1
) ON CONFLICT DO NOTHING;

-- Hiện vật 2: Xe tăng T-54B 390
INSERT INTO exhibit (id, code, title, title_en, room_id, zone, latitude, longitude, radius, thumbnail_url, content_version, is_published, is_active)
VALUES (
    'b0000000-0000-0000-0000-000000000002',
    'T54-390',
    'Xe tăng T-54B số hiệu 390',
    'T-54B Tank No. 390',
    'OUTDOOR',
    'Sân trưng bày cơ giới ngoài trời',
    10.77960000,
    106.69250000,
    15,
    'https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=800&q=80',
    1,
    TRUE,
    TRUE
) ON CONFLICT (code) DO NOTHING;

INSERT INTO content_source (exhibit_id, original_text, content_version)
VALUES (
    'b0000000-0000-0000-0000-000000000002',
    'Xe tăng T-54B số hiệu 390 thuộc Đại đội 4, Tiểu đoàn 1, Lữ đoàn Tăng - Thiết giáp 203. Vào lúc 10 giờ 45 phút ngày 30 tháng 4 năm 1975, chiếc xe tăng này đã húc đổ cổng chính Dinh Độc Lập, đánh dấu thời khắc giải phóng hoàn toàn miền Nam, thống nhất non sông.',
    1
) ON CONFLICT DO NOTHING;

-- Hiện vật 3: Pháo M107 175mm
INSERT INTO exhibit (id, code, title, title_en, room_id, zone, latitude, longitude, radius, thumbnail_url, content_version, is_published, is_active)
VALUES (
    'b0000000-0000-0000-0000-000000000003',
    'M107-175',
    'Pháo tự hành M107 175mm ''Vua chiến trường''',
    'M107 175mm Self-Propelled Gun',
    'OUTDOOR',
    'Khu trưng bày pháo binh ngoài trời',
    10.77920000,
    106.69280000,
    15,
    'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80',
    1,
    TRUE,
    TRUE
) ON CONFLICT (code) DO NOTHING;

INSERT INTO content_source (exhibit_id, original_text, content_version)
VALUES (
    'b0000000-0000-0000-0000-000000000003',
    'Pháo tự hành hạng nặng M107 cỡ nòng 175mm từng được mệnh danh là ''Vua chiến trường'' của quân đội Mỹ với tầm bắn tối đa lên tới hơn 32 km. Khẩu pháo này từng tham gia nhiều chiến dịch ác liệt tại Quảng Trị, Đường 9 Nam Lào và Đông Nam Bộ.',
    1
) ON CONFLICT DO NOTHING;

-- Hiện vật 4: Chuồng cọp Côn Đảo
INSERT INTO exhibit (id, code, title, title_en, room_id, zone, latitude, longitude, radius, thumbnail_url, content_version, is_published, is_active)
VALUES (
    'b0000000-0000-0000-0000-000000000004',
    'CONDAO-CAGE',
    'Mô hình phục dựng Chuồng cọp Côn Đảo',
    'Con Dao Tiger Cages Replica',
    'ROOM-02',
    'Khu chứng tích tội ác chiến tranh',
    NULL,
    NULL,
    10,
    'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=800&q=80',
    1,
    TRUE,
    TRUE
) ON CONFLICT (code) DO NOTHING;

INSERT INTO content_source (exhibit_id, original_text, content_version)
VALUES (
    'b0000000-0000-0000-0000-000000000004',
    'Chuồng cọp Côn Đảo là hệ thống giam giữ bí mật đặc biệt khắc nghiệt do chính quyền thực dân và tay sai xây dựng nhằm đày ải, tra tấn tinh thần và thể xác các chiến sĩ yêu nước. Không gian ngột ngạt, xiềng xích và vôi bột rải từ trên cao thể hiện tội ác tột cùng nhưng cũng là biểu tượng sáng ngời của ý chí bất khuất.',
    1
) ON CONFLICT DO NOTHING;

-- Hiện vật 5: Sa bàn Chiến dịch Hồ Chí Minh
INSERT INTO exhibit (id, code, title, title_en, room_id, zone, latitude, longitude, radius, thumbnail_url, content_version, is_published, is_active)
VALUES (
    'b0000000-0000-0000-0000-000000000005',
    'HOCHIMINH-CAMPAIGN',
    'Sa bàn Chiến dịch Hồ Chí Minh lịch sử',
    'Historical Ho Chi Minh Campaign Diorama',
    'ROOM-03',
    'Phòng trưng bày lịch sử tổng hợp',
    NULL,
    NULL,
    10,
    'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80',
    1,
    TRUE,
    TRUE
) ON CONFLICT (code) DO NOTHING;

INSERT INTO content_source (exhibit_id, original_text, content_version)
VALUES (
    'b0000000-0000-0000-0000-000000000005',
    'Chiến dịch Hồ Chí Minh diễn ra từ ngày 26 đến 30 tháng 4 năm 1975 là chiến dịch quyết chiến chiến lược lớn nhất trong lịch sử dân tộc. Bằng 5 cánh quân tiến công thần tốc, quân và dân ta đã đập tan bộ máy chiến tranh đầu não, giải phóng Sài Gòn và non sông thu về một mối.',
    1
) ON CONFLICT DO NOTHING;

-- Hiện vật 6: Máy bay cường kích A-37 Dragonfly
INSERT INTO exhibit (id, code, title, title_en, room_id, zone, latitude, longitude, radius, thumbnail_url, content_version, is_published, is_active)
VALUES (
    'b0000000-0000-0000-0000-000000000006',
    'A37-DRAGONFLY',
    'Máy bay cường kích A-37 Dragonfly',
    'Cessna A-37 Dragonfly Attack Aircraft',
    'OUTDOOR',
    'Khu trưng bày không quân ngoài trời',
    10.77950000,
    106.69230000,
    15,
    'https://images.unsplash.com/photo-1519074069444-1ba4ea16e6f1?auto=format&fit=crop&w=800&q=80',
    1,
    TRUE,
    TRUE
) ON CONFLICT (code) DO NOTHING;

INSERT INTO content_source (exhibit_id, original_text, content_version)
VALUES (
    'b0000000-0000-0000-0000-000000000006',
    'Máy bay cường kích hạng nhẹ A-37 Dragonfly được chế tạo cho các chiến dịch yểm trợ mặt đất tầm gần. Đặc biệt, chiều ngày 28/4/1975, Phi đội Quyết Thắng của Không quân Nhân dân Việt Nam gồm 5 chiếc A-37 thu được của địch đã cất cánh từ sân bay Thành Sơn (Phan Rang) bất ngờ tập kích sân bay Tân Sơn Nhất, phá huỷ nhiều máy bay địch và đẩy nhanh sự sụp đổ của chính quyền Sài Gòn.',
    1
) ON CONFLICT DO NOTHING;

-- Hiện vật 7: Máy chém thời kỳ chiến tranh
INSERT INTO exhibit (id, code, title, title_en, room_id, zone, latitude, longitude, radius, thumbnail_url, content_version, is_published, is_active)
VALUES (
    'b0000000-0000-0000-0000-000000000007',
    'GUILLOTINE-CONDAO',
    'Máy chém thời kỳ chiến tranh',
    'Historical Guillotine of the War Era',
    'ROOM-01',
    'Khu chứng tích nhà tù thực dân',
    NULL,
    NULL,
    10,
    'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=800&q=80',
    1,
    TRUE,
    TRUE
) ON CONFLICT (code) DO NOTHING;

INSERT INTO content_source (exhibit_id, original_text, content_version)
VALUES (
    'b0000000-0000-0000-0000-000000000007',
    'Máy chém do chính quyền thực dân Pháp đưa sang Việt Nam vào đầu thế kỷ XX và được chính quyền Ngô Đình Diệm tiếp tục sử dụng theo Luật 10/59 để đàn áp khốc liệt phong trào cách mạng miền Nam. Chiếc máy chém cao hơn 4 mét với lưỡi dao thép nặng gần 50 kg là minh chứng thép cho sự tàn bạo của chế độ cai trị lúc bấy giờ.',
    1
) ON CONFLICT DO NOTHING;

-- Hiện vật 8: Bom phát quang BLU-82
INSERT INTO exhibit (id, code, title, title_en, room_id, zone, latitude, longitude, radius, thumbnail_url, content_version, is_published, is_active)
VALUES (
    'b0000000-0000-0000-0000-000000000008',
    'BLU82-BOMB',
    'Vỏ bom phát quang khổng lồ BLU-82 Daisy Cutter',
    'BLU-82 Daisy Cutter High-Explosive Bomb Casing',
    'OUTDOOR',
    'Sân trưng bày bom đạn ngoài trời',
    10.77910000,
    106.69270000,
    15,
    'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80',
    1,
    TRUE,
    TRUE
) ON CONFLICT (code) DO NOTHING;

INSERT INTO content_source (exhibit_id, original_text, content_version)
VALUES (
    'b0000000-0000-0000-0000-000000000008',
    'Bom BLU-82, có biệt danh là Daisy Cutter hay bom phát quang, có trọng lượng lên tới 6.800 kg (15.000 pound). Quả bom được thả từ máy bay vận tải C-130 nhằm tạo ra sức ép huỷ diệt trên diện rộng và dọn sạch các bãi đáp trực thăng giữa rừng rậm nhiệt đới trong chiến tranh Việt Nam.',
    1
) ON CONFLICT DO NOTHING;

-- ====================================================================
-- 4. TOÀN BỘ 13 NGÔN NGỮ VÀ FILE AUDIO CHO UH1-BELL
-- ====================================================================

INSERT INTO localization (id, exhibit_id, language_code, translated_title, translated_text, timestamps_json, content_version, is_reviewed)
VALUES (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'en', 'UH-1 Iroquois ''Huey'' Helicopter', 'The UH-1 Iroquois helicopter, commonly known as the ''Huey'', is an aviation icon of the U.S. military during the Vietnam War. Used from 1962 to 1975 for tactical troop transport, medical evacuation, and close air support. The aircraft displayed here is one of the historic remnants documenting fierce sweeps across the southern battlefields.', '[{"id": 0, "start": 0.0, "end": 6.05, "text": "The UH-1 Iroquois helicopter, commonly known as the ''Huey'', is an aviation icon of the U.S."}, {"id": 1, "start": 6.05, "end": 8.18, "text": "military during the Vietnam War."}, {"id": 2, "start": 8.18, "end": 14.49, "text": "Used from 1962 to 1975 for tactical troop transport, medical evacuation, and close air support."}, {"id": 3, "start": 14.49, "end": 22.4, "text": "The aircraft displayed here is one of the historic remnants documenting fierce sweeps across the southern battlefields."}]'::jsonb, 1, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO audio_media (id, localization_id, file_url, storage_path, duration_seconds, bitrate_kbps, voice_code, status)
SELECT gen_random_uuid(), l.id, '/output/UH1-BELL/UH1-BELL_en.mp3', './output/UH1-BELL/UH1-BELL_en.mp3', 22.4, 128, 'en-Neural', 'ready'
FROM localization l
WHERE l.exhibit_id = 'b0000000-0000-0000-0000-000000000001' AND l.language_code = 'en'
AND NOT EXISTS (SELECT 1 FROM audio_media am WHERE am.localization_id = l.id);

INSERT INTO localization (id, exhibit_id, language_code, translated_title, translated_text, timestamps_json, content_version, is_reviewed)
VALUES (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'fr', 'Hélicoptère UH-1 Iroquois ''Huey''', 'L''hélicoptère UH-1 Iroquois, communément appelé ''Huey'', est une icône de l''aviation militaire américaine pendant la guerre du Vietnam. Utilisé de 1962 à 1975 pour le transport tactique de troupes, les évacuations sanitaires et l''appui aérien. L''appareil exposé ici témoigne des violentes opérations militaires menées dans le Sud.', '[{"id": 0, "start": 0.0, "end": 8.36, "text": "L''hélicoptère UH-1 Iroquois, communément appelé ''Huey'', est une icône de l''aviation militaire américaine pendant la guerre du Vietnam."}, {"id": 1, "start": 8.36, "end": 15.04, "text": "Utilisé de 1962 à 1975 pour le transport tactique de troupes, les évacuations sanitaires et l''appui aérien."}, {"id": 2, "start": 15.04, "end": 20.41, "text": "L''appareil exposé ici témoigne des violentes opérations militaires menées dans le Sud."}]'::jsonb, 1, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO audio_media (id, localization_id, file_url, storage_path, duration_seconds, bitrate_kbps, voice_code, status)
SELECT gen_random_uuid(), l.id, '/output/UH1-BELL/UH1-BELL_fr.mp3', './output/UH1-BELL/UH1-BELL_fr.mp3', 20.4, 128, 'fr-Neural', 'ready'
FROM localization l
WHERE l.exhibit_id = 'b0000000-0000-0000-0000-000000000001' AND l.language_code = 'fr'
AND NOT EXISTS (SELECT 1 FROM audio_media am WHERE am.localization_id = l.id);

INSERT INTO localization (id, exhibit_id, language_code, translated_title, translated_text, timestamps_json, content_version, is_reviewed)
VALUES (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'ja', 'UH-1 イロコイ ''ヒューイ'' ヘリコプター', 'UH-1イロコイヘリコプター（通称「ヒューイ」）は、ベトナム戦争における米軍航空戦力の象徴です。1962年から1975年まで戦術的な兵員輸送、救護、火力支援に投入されました。ここに展示されている機体は、南部戦線における激戦の歴史を物語る貴重な証拠です。', '[{"id": 0, "start": 0.0, "end": 24.6, "text": "UH-1イロコイヘリコプター（通称「ヒューイ」）は、ベトナム戦争における米軍航空戦力の象徴です。1962年から1975年まで戦術的な兵員輸送、救護、火力支援に投入されました。ここに展示されている機体は、南部戦線における激戦の歴史を物語る貴重な証拠です。"}]'::jsonb, 1, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO audio_media (id, localization_id, file_url, storage_path, duration_seconds, bitrate_kbps, voice_code, status)
SELECT gen_random_uuid(), l.id, '/output/UH1-BELL/UH1-BELL_ja.mp3', './output/UH1-BELL/UH1-BELL_ja.mp3', 24.6, 128, 'ja-Neural', 'ready'
FROM localization l
WHERE l.exhibit_id = 'b0000000-0000-0000-0000-000000000001' AND l.language_code = 'ja'
AND NOT EXISTS (SELECT 1 FROM audio_media am WHERE am.localization_id = l.id);

INSERT INTO localization (id, exhibit_id, language_code, translated_title, translated_text, timestamps_json, content_version, is_reviewed)
VALUES (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'ko', 'UH-1 이로쿼이 ''휴이'' 헬리콥터', 'UH-1 이로쿼이(Iroquois) 헬리콥터는 일명 ''휴이(Huey)''로 널리 알려진 베트남 전쟁 당시 미군의 상징적인 항공기입니다. 1962년부터 1975년까지 전술 병력 수송, 의무 후송, 화력 지원 임무에 투입되었습니다. 이곳에 전시된 기체는 치열했던 남부 전장의 역사를 증언하는 중요한 유물입니다.', '[{"id": 0, "start": 0.0, "end": 10.97, "text": "UH-1 이로쿼이(Iroquois) 헬리콥터는 일명 ''휴이(Huey)''로 널리 알려진 베트남 전쟁 당시 미군의 상징적인 항공기입니다."}, {"id": 1, "start": 10.97, "end": 18.53, "text": "1962년부터 1975년까지 전술 병력 수송, 의무 후송, 화력 지원 임무에 투입되었습니다."}, {"id": 2, "start": 18.53, "end": 24.9, "text": "이곳에 전시된 기체는 치열했던 남부 전장의 역사를 증언하는 중요한 유물입니다."}]'::jsonb, 1, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO audio_media (id, localization_id, file_url, storage_path, duration_seconds, bitrate_kbps, voice_code, status)
SELECT gen_random_uuid(), l.id, '/output/UH1-BELL/UH1-BELL_ko.mp3', './output/UH1-BELL/UH1-BELL_ko.mp3', 24.9, 128, 'ko-Neural', 'ready'
FROM localization l
WHERE l.exhibit_id = 'b0000000-0000-0000-0000-000000000001' AND l.language_code = 'ko'
AND NOT EXISTS (SELECT 1 FROM audio_media am WHERE am.localization_id = l.id);

INSERT INTO localization (id, exhibit_id, language_code, translated_title, translated_text, timestamps_json, content_version, is_reviewed)
VALUES (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'es', 'Helicóptero UH-1 Iroquois ''Huey''', 'El helicóptero UH-1 Iroquois, comúnmente apodado ''Huey'', es un emblema de la aviación del ejército estadounidense durante la Guerra de Vietnam. Utilizado entre 1962 y 1975 para el transporte táctico de tropas, evacuación médica y apoyo aéreo. El ejemplar exhibido es testimonio de los duros combates en el sur.', '[{"id": 0, "start": 0.0, "end": 11.05, "text": "El helicóptero UH-1 Iroquois, comúnmente apodado ''Huey'', es un emblema de la aviación del ejército estadounidense durante la Guerra de Vietnam."}, {"id": 1, "start": 11.05, "end": 18.62, "text": "Utilizado entre 1962 y 1975 para el transporte táctico de tropas, evacuación médica y apoyo aéreo."}, {"id": 2, "start": 18.62, "end": 23.8, "text": "El ejemplar exhibido es testimonio de los duros combates en el sur."}]'::jsonb, 1, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO audio_media (id, localization_id, file_url, storage_path, duration_seconds, bitrate_kbps, voice_code, status)
SELECT gen_random_uuid(), l.id, '/output/UH1-BELL/UH1-BELL_es.mp3', './output/UH1-BELL/UH1-BELL_es.mp3', 23.8, 128, 'es-Neural', 'ready'
FROM localization l
WHERE l.exhibit_id = 'b0000000-0000-0000-0000-000000000001' AND l.language_code = 'es'
AND NOT EXISTS (SELECT 1 FROM audio_media am WHERE am.localization_id = l.id);

INSERT INTO localization (id, exhibit_id, language_code, translated_title, translated_text, timestamps_json, content_version, is_reviewed)
VALUES (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'de', 'UH-1 Iroquois ''Huey'' Hubschrauber', 'Der Hubschrauber UH-1 Iroquois, allgemein als ''Huey'' bekannt, ist das bekannteste Luftfahrzeugsymbol der US-Streitkräfte im Vietnamkrieg. Eingesetzt von 1962 bis 1975 für taktische Truppentransporte, Verwundetentransporte und Luftnahunterstützung. Die hier ausgestellte Maschine ist ein historisches Zeugnis jener Kämpfe.', '[{"id": 0, "start": 0.0, "end": 10.39, "text": "Der Hubschrauber UH-1 Iroquois, allgemein als ''Huey'' bekannt, ist das bekannteste Luftfahrzeugsymbol der US-Streitkräfte im Vietnamkrieg."}, {"id": 1, "start": 10.39, "end": 18.66, "text": "Eingesetzt von 1962 bis 1975 für taktische Truppentransporte, Verwundetentransporte und Luftnahunterstützung."}, {"id": 2, "start": 18.66, "end": 24.2, "text": "Die hier ausgestellte Maschine ist ein historisches Zeugnis jener Kämpfe."}]'::jsonb, 1, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO audio_media (id, localization_id, file_url, storage_path, duration_seconds, bitrate_kbps, voice_code, status)
SELECT gen_random_uuid(), l.id, '/output/UH1-BELL/UH1-BELL_de.mp3', './output/UH1-BELL/UH1-BELL_de.mp3', 24.2, 128, 'de-Neural', 'ready'
FROM localization l
WHERE l.exhibit_id = 'b0000000-0000-0000-0000-000000000001' AND l.language_code = 'de'
AND NOT EXISTS (SELECT 1 FROM audio_media am WHERE am.localization_id = l.id);

INSERT INTO localization (id, exhibit_id, language_code, translated_title, translated_text, timestamps_json, content_version, is_reviewed)
VALUES (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'ru', 'Вертолёт UH-1 Iroquois ''Хьюи''', 'Вертолёт UH-1 Iroquois, широко известный как ''Хьюи'' (Huey), стал символом военной авиации США во время войны во Вьетнаме. Использовался с 1962 по 1975 год для тактической переброски десанта, медицинской эвакуации и огневой поддержки. Представленный здесь борт — одно из свидетельств ожесточённых боёв на юге страны.', '[{"id": 0, "start": 0.0, "end": 9.59, "text": "Вертолёт UH-1 Iroquois, широко известный как ''Хьюи'' (Huey), стал символом военной авиации США во время войны во Вьетнаме."}, {"id": 1, "start": 9.59, "end": 18.38, "text": "Использовался с 1962 по 1975 год для тактической переброски десанта, медицинской эвакуации и огневой поддержки."}, {"id": 2, "start": 18.38, "end": 24.8, "text": "Представленный здесь борт — одно из свидетельств ожесточённых боёв на юге страны."}]'::jsonb, 1, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO audio_media (id, localization_id, file_url, storage_path, duration_seconds, bitrate_kbps, voice_code, status)
SELECT gen_random_uuid(), l.id, '/output/UH1-BELL/UH1-BELL_ru.mp3', './output/UH1-BELL/UH1-BELL_ru.mp3', 24.8, 128, 'ru-Neural', 'ready'
FROM localization l
WHERE l.exhibit_id = 'b0000000-0000-0000-0000-000000000001' AND l.language_code = 'ru'
AND NOT EXISTS (SELECT 1 FROM audio_media am WHERE am.localization_id = l.id);

INSERT INTO localization (id, exhibit_id, language_code, translated_title, translated_text, timestamps_json, content_version, is_reviewed)
VALUES (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'zh-CN', 'UH-1“易洛魁”休伊直升机', 'UH-1“易洛魁”直升机，通常被称为“休伊”（Huey），是越南战争期间美军空中力量的标志。它在1962年至1975年间服役，主要执行战术运兵、战场医疗救援和空中火力支援任务。此处展出的这架直升机是记录南部战场激烈扫荡的历史见证。', '[{"id": 0, "start": 0.0, "end": 19.2, "text": "UH-1“易洛魁”直升机，通常被称为“休伊”（Huey），是越南战争期间美军空中力量的标志。它在1962年至1975年间服役，主要执行战术运兵、战场医疗救援和空中火力支援任务。此处展出的这架直升机是记录南部战场激烈扫荡的历史见证。"}]'::jsonb, 1, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO audio_media (id, localization_id, file_url, storage_path, duration_seconds, bitrate_kbps, voice_code, status)
SELECT gen_random_uuid(), l.id, '/output/UH1-BELL/UH1-BELL_zh-CN.mp3', './output/UH1-BELL/UH1-BELL_zh-CN.mp3', 19.2, 128, 'zh-CN-Neural', 'ready'
FROM localization l
WHERE l.exhibit_id = 'b0000000-0000-0000-0000-000000000001' AND l.language_code = 'zh-CN'
AND NOT EXISTS (SELECT 1 FROM audio_media am WHERE am.localization_id = l.id);

INSERT INTO localization (id, exhibit_id, language_code, translated_title, translated_text, timestamps_json, content_version, is_reviewed)
VALUES (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'it', 'Elicottero UH-1 Iroquois ''Huey''', 'L''elicottero UH-1 Iroquois, comunemente noto come ''Huey'', è un''icona dell''aviazione militare statunitense durante la guerra del Vietnam. Utilizzato dal 1962 al 1975 per il trasporto táctico di truppe, evacuazione medica e supporto aereo ravvicinato. L''esemplare esposto qui è una testimonianza storica delle feroci operazioni militari condotte nel Sud.', '[{"id": 0, "start": 0.0, "end": 10.45, "text": "L''elicottero UH-1 Iroquois, comunemente noto come ''Huey'', è un''icona dell''aviazione militare statunitense durante la guerra del Vietnam."}, {"id": 1, "start": 10.45, "end": 19.06, "text": "Utilizzato dal 1962 al 1975 per il trasporto táctico di truppe, evacuazione medica e supporto aereo ravvicinato."}, {"id": 2, "start": 19.06, "end": 26.9, "text": "L''esemplare esposto qui è una testimonianza storica delle feroci operazioni militari condotte nel Sud."}]'::jsonb, 1, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO audio_media (id, localization_id, file_url, storage_path, duration_seconds, bitrate_kbps, voice_code, status)
SELECT gen_random_uuid(), l.id, '/output/UH1-BELL/UH1-BELL_it.mp3', './output/UH1-BELL/UH1-BELL_it.mp3', 26.9, 128, 'it-Neural', 'ready'
FROM localization l
WHERE l.exhibit_id = 'b0000000-0000-0000-0000-000000000001' AND l.language_code = 'it'
AND NOT EXISTS (SELECT 1 FROM audio_media am WHERE am.localization_id = l.id);

INSERT INTO localization (id, exhibit_id, language_code, translated_title, translated_text, timestamps_json, content_version, is_reviewed)
VALUES (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'vi', 'Máy bay trực thăng UH-1 Iroquois ''Huey''', 'Trực thăng UH-1 Iroquois, thường được gọi là ''Huey'', là biểu tượng không quân của quân đội Mỹ trong Chiến tranh Việt Nam. Được sử dụng từ năm 1962 đến 1975 với các nhiệm vụ đổ quân chiến thuật, cứu thương và yểm trợ hoả lực. Chiếc máy bay trưng bày tại đây là một trong những chứng tích ghi lại các cuộc càn quét khốc liệt trên chiến trường miền Nam.', '[{"id": 0, "start": 0.0, "end": 7.37, "text": "Trực thăng UH-1 Iroquois, thường được gọi là ''Huey'', là biểu tượng không quân của quân đội Mỹ trong Chiến tranh Việt Nam."}, {"id": 1, "start": 7.37, "end": 13.58, "text": "Được sử dụng từ năm 1962 đến 1975 với các nhiệm vụ đổ quân chiến thuật, cứu thương và yểm trợ hoả lực."}, {"id": 2, "start": 13.58, "end": 21.19, "text": "Chiếc máy bay trưng bày tại đây là một trong những chứng tích ghi lại các cuộc càn quét khốc liệt trên chiến trường miền Nam."}]'::jsonb, 1, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO audio_media (id, localization_id, file_url, storage_path, duration_seconds, bitrate_kbps, voice_code, status)
SELECT gen_random_uuid(), l.id, '/output/UH1-BELL/UH1-BELL_vi.mp3', './output/UH1-BELL/UH1-BELL_vi.mp3', 21.2, 128, 'vi-Neural', 'ready'
FROM localization l
WHERE l.exhibit_id = 'b0000000-0000-0000-0000-000000000001' AND l.language_code = 'vi'
AND NOT EXISTS (SELECT 1 FROM audio_media am WHERE am.localization_id = l.id);

INSERT INTO localization (id, exhibit_id, language_code, translated_title, translated_text, timestamps_json, content_version, is_reviewed)
VALUES (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'th', 'เฮลิคอปเตอร์ UH-1 Iroquois ''Huey''', 'เฮลิคอปเตอร์ UH-1 อิโรควอยส์ หรือที่รู้จักกันทั่วไปในชื่อ ''ฮิวอี้'' (Huey) เป็นสัญลักษณ์ของกองทัพอากาศสหรัฐฯ ในช่วงสงครามเวียดนาม ประจำการตั้งแต่ปี 1962 ถึง 1975 ในภารกิจส่งกำลังพลทางยุทธวิธี ลำเลียงผู้บาดเจ็บ และสนับสนุนการยิงทางอากาศ เครื่องบินที่จัดแสดงที่นี่เป็นหนึ่งในหลักฐานทางประวัติศาสตร์ของสมรภูมิอันดุเดือดในภาคใต้', '[{"id": 0, "start": 0.0, "end": 24.0, "text": "เฮลิคอปเตอร์ UH-1 อิโรควอยส์ หรือที่รู้จักกันทั่วไปในชื่อ ''ฮิวอี้'' (Huey) เป็นสัญลักษณ์ของกองทัพอากาศสหรัฐฯ ในช่วงสงครามเวียดนาม ประจำการตั้งแต่ปี 1962 ถึง 1975 ในภารกิจส่งกำลังพลทางยุทธวิธี ลำเลียงผู้บาดเจ็บ และสนับสนุนการยิงทางอากาศ เครื่องบินที่จัดแสดงที่นี่เป็นหนึ่งในหลักฐานทางประวัติศาสตร์ของสมรภูมิอันดุเดือดในภาคใต้"}]'::jsonb, 1, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO audio_media (id, localization_id, file_url, storage_path, duration_seconds, bitrate_kbps, voice_code, status)
SELECT gen_random_uuid(), l.id, '/output/UH1-BELL/UH1-BELL_th.mp3', './output/UH1-BELL/UH1-BELL_th.mp3', 24.0, 128, 'th-Neural', 'ready'
FROM localization l
WHERE l.exhibit_id = 'b0000000-0000-0000-0000-000000000001' AND l.language_code = 'th'
AND NOT EXISTS (SELECT 1 FROM audio_media am WHERE am.localization_id = l.id);

INSERT INTO localization (id, exhibit_id, language_code, translated_title, translated_text, timestamps_json, content_version, is_reviewed)
VALUES (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'ar', 'مروحية UH-1 إيروكواس ''هوي''', 'تعتبر المروحية UH-1 إيروكواس، المعروفة باسم ''هوي'' (Huey)، أيقونة الطيران العسكري الأمريكي خلال حرب فيتنام. تم استخدامها من عام 1962 إلى عام 1975 لمهام النقل التكتيكي للقوات والإخلاء الطبي والدعم الجوي القريب. تعد الطائرة المعروضة هنا إحدى الشواهد التاريخية التي توثق العمليات العسكرية الضارية في جنوب فيتنام.', '[{"id": 0, "start": 0.0, "end": 7.38, "text": "تعتبر المروحية UH-1 إيروكواس، المعروفة باسم ''هوي'' (Huey)، أيقونة الطيران العسكري الأمريكي خلال حرب فيتنام."}, {"id": 1, "start": 7.38, "end": 14.41, "text": "تم استخدامها من عام 1962 إلى عام 1975 لمهام النقل التكتيكي للقوات والإخلاء الطبي والدعم الجوي القريب."}, {"id": 2, "start": 14.41, "end": 21.3, "text": "تعد الطائرة المعروضة هنا إحدى الشواهد التاريخية التي توثق العمليات العسكرية الضارية في جنوب فيتنام."}]'::jsonb, 1, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO audio_media (id, localization_id, file_url, storage_path, duration_seconds, bitrate_kbps, voice_code, status)
SELECT gen_random_uuid(), l.id, '/output/UH1-BELL/UH1-BELL_ar.mp3', './output/UH1-BELL/UH1-BELL_ar.mp3', 21.3, 128, 'ar-Neural', 'ready'
FROM localization l
WHERE l.exhibit_id = 'b0000000-0000-0000-0000-000000000001' AND l.language_code = 'ar'
AND NOT EXISTS (SELECT 1 FROM audio_media am WHERE am.localization_id = l.id);

INSERT INTO localization (id, exhibit_id, language_code, translated_title, translated_text, timestamps_json, content_version, is_reviewed)
VALUES (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'pt', 'Helicóptero UH-1 Iroquois ''Huey''', 'O helicóptero UH-1 Iroquois, comumente conhecido como ''Huey'', é um ícone da aviação militar dos EUA durante a Guerra do Vietnã. Utilizado de 1962 a 1975 para transporte tático de tropas, evacuação médica e apoio aéreo aproximado. A aeronave aqui exposta é um dos testemunhos históricos das intensas operações militares no sul do país.', '[{"id": 0, "start": 0.0, "end": 9.75, "text": "O helicóptero UH-1 Iroquois, comumente conhecido como ''Huey'', é um ícone da aviação militar dos EUA durante a Guerra do Vietnã."}, {"id": 1, "start": 9.75, "end": 17.51, "text": "Utilizado de 1962 a 1975 para transporte tático de tropas, evacuação médica e apoio aéreo aproximado."}, {"id": 2, "start": 17.51, "end": 25.5, "text": "A aeronave aqui exposta é um dos testemunhos históricos das intensas operações militares no sul do país."}]'::jsonb, 1, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO audio_media (id, localization_id, file_url, storage_path, duration_seconds, bitrate_kbps, voice_code, status)
SELECT gen_random_uuid(), l.id, '/output/UH1-BELL/UH1-BELL_pt.mp3', './output/UH1-BELL/UH1-BELL_pt.mp3', 25.5, 128, 'pt-Neural', 'ready'
FROM localization l
WHERE l.exhibit_id = 'b0000000-0000-0000-0000-000000000001' AND l.language_code = 'pt'
AND NOT EXISTS (SELECT 1 FROM audio_media am WHERE am.localization_id = l.id);