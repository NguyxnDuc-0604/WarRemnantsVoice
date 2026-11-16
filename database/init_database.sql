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
