-- ============================================================================
-- SEED DATA - DỮ LIỆU MẪU CHUẨN LỊCH SỬ BẢO TÀNG CHỨNG TÍCH CHIẾN TRANH
-- Hệ thống Thuyết minh Tự động Đa ngôn ngữ (WarRemnantsVoice)
-- Tọa độ Bảo tàng: 28 Võ Văn Tần, Phường Võ Thị Sáu, Quận 3, TP.HCM (~10.7797, 106.6923)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. SEED AUTH SERVICE (Vai trò & Tài khoản Quản trị)
-- ----------------------------------------------------------------------------
INSERT INTO auth_service.system_role (id, code, name, description)
VALUES 
    ('a0000000-0000-0000-0000-000000000001', 'ADMIN', 'Quản trị viên Hệ thống', 'Toàn quyền cấu hình hệ thống, người dùng và kiểm duyệt'),
    ('a0000000-0000-0000-0000-000000000002', 'CURATOR', 'Cán bộ Bảo tàng / Biên tập viên', 'Quản lý hiện vật, kiểm duyệt phụ đề và audio đa ngôn ngữ'),
    ('a0000000-0000-0000-0000-000000000003', 'DEVOPS', 'Kỹ sư Vận hành', 'Theo dõi sức khỏe hạ tầng Microservices, RabbitMQ và Streaming')
ON CONFLICT (code) DO NOTHING;

INSERT INTO auth_service.system_permission (id, code, name, category)
VALUES
    ('b0000000-0000-0000-0000-000000000001', 'exhibit:read', 'Xem danh mục hiện vật', 'EXHIBIT'),
    ('b0000000-0000-0000-0000-000000000002', 'exhibit:write', 'Thêm sửa hiện vật', 'EXHIBIT'),
    ('b0000000-0000-0000-0000-000000000003', 'translation:review', 'Kiểm duyệt bản dịch', 'LOCALIZATION'),
    ('b0000000-0000-0000-0000-000000000004', 'glossary:manage', 'Quản lý từ điển lịch sử', 'LOCALIZATION'),
    ('b0000000-0000-0000-0000-000000000005', 'system:monitor', 'Giám sát hạ tầng & thống kê', 'SYSTEM')
ON CONFLICT (code) DO NOTHING;

-- Tài khoản quản trị mặc định (Mật khẩu mẫu: Bảo mật Argon2id / băm Bcrypt)
INSERT INTO auth_service.system_user (id, username, email, password_hash, full_name, role_id, is_active)
VALUES
    ('c0000000-0000-0000-0000-000000000001', 'admin_baotang', 'admin@baotangchungkien.vn', '$2a$12$e80yq9gq0ZkR.qH8zF3kEuOdf1Lpms58iRk5UjSj8lqK.VreG7Uea', 'Nguyễn Quốc Huy (Admin)', 'a0000000-0000-0000-0000-000000000001', TRUE),
    ('c0000000-0000-0000-0000-000000000002', 'curator_lan', 'curator@baotangchungkien.vn', '$2a$12$e80yq9gq0ZkR.qH8zF3kEuOdf1Lpms58iRk5UjSj8lqK.VreG7Uea', 'Trần Thị Mai Lan (Curator)', 'a0000000-0000-0000-0000-000000000002', TRUE),
    ('c0000000-0000-0000-0000-000000000003', 'devops_lead', 'devops@baotangchungkien.vn', '$2a$12$e80yq9gq0ZkR.qH8zF3kEuOdf1Lpms58iRk5UjSj8lqK.VreG7Uea', 'Lê Hoàng Nam (DevOps)', 'a0000000-0000-0000-0000-000000000003', TRUE)
ON CONFLICT (username) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. SEED LOCALIZATION GLOSSARY (Từ điển chuẩn hóa thuật ngữ lịch sử - quân sự)
-- ----------------------------------------------------------------------------
INSERT INTO localization_service.glossary (id, term_vi, term_en, context_note, is_restricted)
VALUES
    ('d0000000-0000-0000-0000-000000000001', 'Chiến dịch Hồ Chí Minh', 'Ho Chi Minh Campaign', 'Chiến dịch lịch sử giải phóng miền Nam thống nhất đất nước tháng 4/1975, tuyệt đối không dịch nghĩa đen', TRUE),
    ('d0000000-0000-0000-0000-000000000002', 'Chiến dịch Điện Biên Phủ trên không', 'Airborne Dien Bien Phu Operation (Linebacker II)', 'Chiến dịch phòng không 12 ngày đêm Hà Nội năm 1972', TRUE),
    ('d0000000-0000-0000-0000-000000000003', 'Chất độc Da cam/Dioxin', 'Agent Orange / Dioxin', 'Chất độc hóa học do quân đội Mỹ rải xuống chiến trường Việt Nam', TRUE),
    ('d0000000-0000-0000-0000-000000000004', 'Pháo 175mm Vua chiến trường', 'M107 175mm "King of the Battlefield" Self-Propelled Gun', 'Pháo tầm xa của quân đội Mỹ trang bị trong chiến tranh Việt Nam', TRUE),
    ('d0000000-0000-0000-0000-000000000005', 'Ấp Bắc', 'Ap Bac Battle', 'Chiến thắng vang dội tại Tiền Giang năm 1963', TRUE),
    ('d0000000-0000-0000-0000-000000000006', 'Chuồng cọp Côn Đảo', 'Con Dao Tiger Cages', 'Khu biệt giam tra tấn tù nhân chính trị tại nhà tù Côn Đảo', TRUE),
    ('d0000000-0000-0000-0000-000000000007', 'Xe tăng T-54 số hiệu 390', 'T-54 Tank No. 390', 'Chiếc xe tăng húc đổ cổng chính Dinh Độc Lập trưa ngày 30/04/1975', TRUE),
    ('d0000000-0000-0000-0000-000000000008', 'Máy chém thời Ngô Đình Diệm', 'Guillotine under the Ngo Dinh Diem Regime', 'Dụng cụ hành quyết tàn bạo thi hành theo Luật 10/59', TRUE)
ON CONFLICT (term_vi) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. SEED EXHIBIT SERVICE (Hiện vật trưng bày cốt lõi & Nội dung nguồn)
-- ----------------------------------------------------------------------------
-- 3.1. Hiện vật 1: Xe tăng T-54 số hiệu 390 (Sân ngoài trời)
INSERT INTO exhibit_service.exhibit (
    id, code, title, room_id, latitude, longitude, radius, thumbnail_url, content_version, is_published, is_active
) VALUES (
    'e0000000-0000-0000-0000-000000000001',
    'T54-390',
    'Xe tăng T-54B số hiệu 390',
    'OUTDOOR',
    10.779740,
    106.692350,
    15,
    'https://storage.baotang.vn/thumbnails/tank-t54-390.webp',
    1,
    TRUE,
    TRUE
) ON CONFLICT (code) DO NOTHING;

INSERT INTO exhibit_service.content_source (
    id, exhibit_id, original_text, original_audio_url, content_version
) VALUES (
    'f0000000-0000-0000-0000-000000000001',
    'e0000000-0000-0000-0000-000000000001',
    'Xe tăng T-54 số hiệu 390 thuộc Đại đội 4, Tiểu đoàn 1, Lữ đoàn Tăng thiết giáp 203. Trưa ngày 30 tháng 4 năm 1975, chính chiếc xe tăng lịch sử này do Trung úy Vũ Đăng Toàn chỉ huy đã húc đổ cổng chính Dinh Độc Lập, đánh dấu thời khắc toàn thắng của Chiến dịch Hồ Chí Minh lịch sử, non sông thu về một mối.',
    'https://storage.baotang.vn/audio-raw/t54-390-vi.wav',
    1
) ON CONFLICT DO NOTHING;

-- 3.2. Hiện vật 2: Trực thăng UH-1 Iroquois "Huey" (Sân ngoài trời)
INSERT INTO exhibit_service.exhibit (
    id, code, title, room_id, latitude, longitude, radius, thumbnail_url, content_version, is_published, is_active
) VALUES (
    'e0000000-0000-0000-0000-000000000002',
    'UH1-BELL',
    'Trực thăng đa năng UH-1 Iroquois (Huey)',
    'OUTDOOR',
    10.779600,
    106.692200,
    15,
    'https://storage.baotang.vn/thumbnails/heli-uh1-bell.webp',
    1,
    TRUE,
    TRUE
) ON CONFLICT (code) DO NOTHING;

INSERT INTO exhibit_service.content_source (
    id, exhibit_id, original_text, original_audio_url, content_version
) VALUES (
    'f0000000-0000-0000-0000-000000000002',
    'e0000000-0000-0000-0000-000000000002',
    'Trực thăng UH-1 là biểu tượng tác chiến cơ động trên không của quân đội Mỹ trong chiến tranh Việt Nam. Máy bay được sử dụng phổ biến trong các chiến thuật trực thăng vận, đổ bộ quân viễn chinh và bắn phá hỗ trợ hỏa lực yểm trợ mặt đất.',
    'https://storage.baotang.vn/audio-raw/uh1-bell-vi.wav',
    1
) ON CONFLICT DO NOTHING;

-- 3.3. Hiện vật 3: Máy bay vận tải C-130 Hercules (Sân ngoài trời)
INSERT INTO exhibit_service.exhibit (
    id, code, title, room_id, latitude, longitude, radius, thumbnail_url, content_version, is_published, is_active
) VALUES (
    'e0000000-0000-0000-0000-000000000003',
    'C130-HERCULES',
    'Máy bay vận tải quân sự hạng nặng C-130 Hercules',
    'OUTDOOR',
    10.779850,
    106.692480,
    20,
    'https://storage.baotang.vn/thumbnails/c130-hercules.webp',
    1,
    TRUE,
    TRUE
) ON CONFLICT (code) DO NOTHING;

INSERT INTO exhibit_service.content_source (
    id, exhibit_id, original_text, original_audio_url, content_version
) VALUES (
    'f0000000-0000-0000-0000-000000000003',
    'e0000000-0000-0000-0000-000000000003',
    'Máy bay vận tải C-130 Hercules là loại máy bay 4 động cơ cánh quạt phản lực cỡ lớn, được quân đội Mỹ và quân lực Việt Nam Cộng hòa sử dụng để tiếp tế vũ khí hạng nặng, chuyển quân và ném các loại bom siêu lớn phá rừng.',
    'https://storage.baotang.vn/audio-raw/c130-hercules-vi.wav',
    1
) ON CONFLICT DO NOTHING;

-- 3.4. Hiện vật 4: Pháo tự hành 175mm M107 "Vua chiến trường" (Sân ngoài trời)
INSERT INTO exhibit_service.exhibit (
    id, code, title, room_id, latitude, longitude, radius, thumbnail_url, content_version, is_published, is_active
) VALUES (
    'e0000000-0000-0000-0000-000000000004',
    'M107-175MM',
    'Pháo tự hành 175mm M107 "Vua chiến trường"',
    'OUTDOOR',
    10.779450,
    106.692300,
    15,
    'https://storage.baotang.vn/thumbnails/m107-gun.webp',
    1,
    TRUE,
    TRUE
) ON CONFLICT (code) DO NOTHING;

INSERT INTO exhibit_service.content_source (
    id, exhibit_id, original_text, original_audio_url, content_version
) VALUES (
    'f0000000-0000-0000-0000-000000000004',
    'e0000000-0000-0000-0000-000000000004',
    'Pháo 175mm Vua chiến trường M107 có tầm bắn xa kỷ lục thời bấy giờ lên tới 32 km. Pháo được Mỹ triển khai tại các căn cứ hỏa lực dọc theo Vĩ tuyến 17 và đường mòn Hồ Chí Minh nhằm ngăn chặn dòng chi viện của quân dân miền Bắc.',
    'https://storage.baotang.vn/audio-raw/m107-vi.wav',
    1
) ON CONFLICT DO NOTHING;

-- 3.5. Hiện vật 5: Máy chém thời Ngô Đình Diệm (Trong nhà - Kích hoạt bằng mã QR)
INSERT INTO exhibit_service.exhibit (
    id, code, title, room_id, latitude, longitude, radius, thumbnail_url, content_version, is_published, is_active
) VALUES (
    'e0000000-0000-0000-0000-000000000005',
    'GUILLOTINE-1960',
    'Máy chém thi hành Luật 10/59 thời Ngô Đình Diệm',
    'ROOM-CHUNG-TICH',
    NULL,
    NULL,
    15,
    'https://storage.baotang.vn/thumbnails/guillotine.webp',
    1,
    TRUE,
    TRUE
) ON CONFLICT (code) DO NOTHING;

INSERT INTO exhibit_service.content_source (
    id, exhibit_id, original_text, original_audio_url, content_version
) VALUES (
    'f0000000-0000-0000-0000-000000000005',
    'e0000000-0000-0000-0000-000000000005',
    'Máy chém thời Ngô Đình Diệm do thực dân Pháp mang sang Việt Nam từ đầu thế kỷ 20, sau đó được chính quyền Ngô Đình Diệm đưa đi lưu động khắp các tỉnh miền Nam để xử tử những chiến sĩ yêu nước và đồng bào yêu hòa bình theo Đạo luật 10/59 tàn bạo.',
    'https://storage.baotang.vn/audio-raw/guillotine-vi.wav',
    1
) ON CONFLICT DO NOTHING;

-- 3.6. Hiện vật 6: Chứng tích Hậu quả Chất độc Da cam/Dioxin (Trong nhà - QR)
INSERT INTO exhibit_service.exhibit (
    id, code, title, room_id, latitude, longitude, radius, thumbnail_url, content_version, is_published, is_active
) VALUES (
    'e0000000-0000-0000-0000-000000000006',
    'DIOXIN-VICTIMS',
    'Bộ tư liệu Hậu quả chất độc Da cam/Dioxin',
    'ROOM-DIOXIN',
    NULL,
    NULL,
    15,
    'https://storage.baotang.vn/thumbnails/dioxin-room.webp',
    1,
    TRUE,
    TRUE
) ON CONFLICT (code) DO NOTHING;

INSERT INTO exhibit_service.content_source (
    id, exhibit_id, original_text, original_audio_url, content_version
) VALUES (
    'f0000000-0000-0000-0000-000000000006',
    'e0000000-0000-0000-0000-000000000006',
    'Từ năm 1961 đến 1971, quân đội Mỹ đã rải gần 80 triệu lít chất diệt cỏ, phần lớn là Chất độc Da cam/Dioxin xuống miền Nam Việt Nam. Di chứng của chất độc đã để lại nỗi đau thảm khốc cho hàng triệu nạn nhân qua nhiều thế hệ.',
    'https://storage.baotang.vn/audio-raw/dioxin-vi.wav',
    1
) ON CONFLICT DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. SEED TOUR ROUTE (02 Lộ trình tham quan chuyên đề mặc định - FR-18)
-- ----------------------------------------------------------------------------
INSERT INTO exhibit_service.tour_route (
    id, title, description, ordered_exhibits_json, estimated_time, is_active
) VALUES 
    (
        '00000000-0000-0000-0000-000000000001',
        'Khí tài Quân sự Ngoài trời (Outdoor Military Collection)',
        'Lộ trình khám phá các khí tài quân sự hạng nặng tại sân bảo tàng: Xe tăng T-54 số hiệu 390, Trực thăng UH-1 Huey, Máy bay C-130 Hercules và Pháo 175mm.',
        '["e0000000-0000-0000-0000-000000000001", "e0000000-0000-0000-0000-000000000002", "e0000000-0000-0000-0000-000000000003", "e0000000-0000-0000-0000-000000000004"]'::jsonb,
        45,
        TRUE
    ),
    (
        '00000000-0000-0000-0000-000000000002',
        'Chứng tích Tội ác Chiến tranh & Hậu quả Da cam',
        'Lộ trình chuyên đề lịch sử sâu sắc: Trực diện trước các chứng tích chiến tranh, Đạo luật 10/59 với Máy chém và Nỗi đau di chứng da cam.',
        '["e0000000-0000-0000-0000-000000000005", "e0000000-0000-0000-0000-000000000006"]'::jsonb,
        60,
        TRUE
    )
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. SEED LOCALIZATION (Bản dịch & Mốc thời gian phụ đề mẫu)
-- ----------------------------------------------------------------------------
-- Bản dịch Tiếng Anh cho Xe tăng T-54 (đã tuân thủ Glossary "T-54 Tank No. 390", "Ho Chi Minh Campaign")
INSERT INTO localization_service.localization (
    id, exhibit_id, language_code, translated_title, translated_text, timestamps_json, content_version, is_reviewed
) VALUES (
    '10000000-0000-0000-0000-000000000001',
    'e0000000-0000-0000-0000-000000000001',
    'en',
    'T-54 Tank No. 390',
    'T-54 Tank No. 390 belonged to Company 4, Battalion 1, Tank Brigade 203. At noon on April 30, 1975, commanded by Lieutenant Vu Dang Toan, this historic tank crashed through the main gates of the Independence Palace, marking the complete victory of the historic Ho Chi Minh Campaign and reunifying Vietnam.',
    '[
        {"start_ms": 0, "end_ms": 4200, "text": "T-54 Tank No. 390 belonged to Company 4, Battalion 1, Tank Brigade 203."},
        {"start_ms": 4200, "end_ms": 11500, "text": "At noon on April 30, 1975, commanded by Lieutenant Vu Dang Toan, this historic tank crashed through the main gates of the Independence Palace,"},
        {"start_ms": 11500, "end_ms": 17800, "text": "marking the complete victory of the historic Ho Chi Minh Campaign and reunifying Vietnam."}
    ]'::jsonb,
    1,
    TRUE
) ON CONFLICT (exhibit_id, language_code, content_version) DO NOTHING;

-- Bản dịch Tiếng Pháp cho Xe tăng T-54
INSERT INTO localization_service.localization (
    id, exhibit_id, language_code, translated_title, translated_text, timestamps_json, content_version, is_reviewed
) VALUES (
    '10000000-0000-0000-0000-000000000002',
    'e0000000-0000-0000-0000-000000000001',
    'fr',
    'Char de combat T-54 numéro 390',
    'Le char T-54 numéro 390 appartenait à la 4e compagnie, 1er bataillon, 203e brigade blindée. À midi le 30 avril 1975, sous le commandement du lieutenant Vu Dang Toan, ce char historique a défoncé les grilles principales du Palais de l''Indépendance, marquant la victoire finale de la campagne historique Ho Chi Minh.',
    '[
        {"start_ms": 0, "end_ms": 4500, "text": "Le char T-54 numéro 390 appartenait à la 4e compagnie, 1er bataillon, 203e brigade blindée."},
        {"start_ms": 4500, "end_ms": 12000, "text": "À midi le 30 avril 1975, sous le commandement du lieutenant Vu Dang Toan, ce char historique a défoncé les grilles principales du Palais de l''Indépendance,"},
        {"start_ms": 12000, "end_ms": 18200, "text": "marquant la victoire finale de la campagne historique Ho Chi Minh."}
    ]'::jsonb,
    1,
    TRUE
) ON CONFLICT (exhibit_id, language_code, content_version) DO NOTHING;

-- Bản dịch Tiếng Anh cho Chất độc Da cam/Dioxin
INSERT INTO localization_service.localization (
    id, exhibit_id, language_code, translated_title, translated_text, timestamps_json, content_version, is_reviewed
) VALUES (
    '10000000-0000-0000-0000-000000000003',
    'e0000000-0000-0000-0000-000000000006',
    'en',
    'Documentary Evidence of Agent Orange / Dioxin Consequences',
    'Between 1961 and 1971, the US military sprayed nearly 80 million liters of toxic defoliants, mostly Agent Orange / Dioxin, across southern Vietnam. The devastating chemical legacy continues to affect millions of victims across multiple generations.',
    '[
        {"start_ms": 0, "end_ms": 6500, "text": "Between 1961 and 1971, the US military sprayed nearly 80 million liters of toxic defoliants,"},
        {"start_ms": 6500, "end_ms": 11200, "text": "mostly Agent Orange / Dioxin, across southern Vietnam."},
        {"start_ms": 11200, "end_ms": 17500, "text": "The devastating chemical legacy continues to affect millions of victims across multiple generations."}
    ]'::jsonb,
    1,
    TRUE
) ON CONFLICT (exhibit_id, language_code, content_version) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. SEED AUDIO MEDIA (Siêu dữ liệu file âm thanh trên MinIO Object Storage)
-- ----------------------------------------------------------------------------
INSERT INTO media_service.audio_media (
    id, localization_id, file_url, storage_path, duration_seconds, bitrate_kbps, voice_code, status
) VALUES 
    (
        '20000000-0000-0000-0000-000000000001',
        '10000000-0000-0000-0000-000000000001',
        'https://minio.baotang.vn/audio-media/exhibits/t54-390/en_v1.mp3',
        'audio-media/exhibits/t54-390/en_v1.mp3',
        17.80,
        128,
        'en-US-GuyNeural',
        'ready'
    ),
    (
        '20000000-0000-0000-0000-000000000002',
        '10000000-0000-0000-0000-000000000002',
        'https://minio.baotang.vn/audio-media/exhibits/t54-390/fr_v1.mp3',
        'audio-media/exhibits/t54-390/fr_v1.mp3',
        18.20,
        128,
        'fr-FR-HenriNeural',
        'ready'
    ),
    (
        '20000000-0000-0000-0000-000000000003',
        '10000000-0000-0000-0000-000000000003',
        'https://minio.baotang.vn/audio-media/exhibits/dioxin-victims/en_v1.mp3',
        'audio-media/exhibits/dioxin-victims/en_v1.mp3',
        17.50,
        128,
        'en-US-JennyNeural',
        'ready'
    )
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 7. SEED LISTENING METRIC (Mẫu sự kiện lượt nghe ẩn danh cho Dashboard)
-- ----------------------------------------------------------------------------
INSERT INTO metric_service.listening_metric (exhibit_id, language_code, listened_duration, trigger_type, timestamp)
VALUES
    ('e0000000-0000-0000-0000-000000000001', 'en', 18, 'GPS_GEOFENCE', CURRENT_TIMESTAMP - INTERVAL '2 hours'),
    ('e0000000-0000-0000-0000-000000000001', 'fr', 18, 'GPS_GEOFENCE', CURRENT_TIMESTAMP - INTERVAL '90 minutes'),
    ('e0000000-0000-0000-0000-000000000001', 'vi', 20, 'QR_CODE', CURRENT_TIMESTAMP - INTERVAL '1 hour'),
    ('e0000000-0000-0000-0000-000000000001', 'en', 15, 'GPS_GEOFENCE', CURRENT_TIMESTAMP - INTERVAL '45 minutes'),
    ('e0000000-0000-0000-0000-000000000002', 'en', 14, 'GPS_GEOFENCE', CURRENT_TIMESTAMP - INTERVAL '30 minutes'),
    ('e0000000-0000-0000-0000-000000000003', 'zh', 16, 'GPS_GEOFENCE', CURRENT_TIMESTAMP - INTERVAL '25 minutes'),
    ('e0000000-0000-0000-0000-000000000005', 'en', 25, 'QR_CODE', CURRENT_TIMESTAMP - INTERVAL '20 minutes'),
    ('e0000000-0000-0000-0000-000000000006', 'en', 17, 'QR_CODE', CURRENT_TIMESTAMP - INTERVAL '10 minutes'),
    ('e0000000-0000-0000-0000-000000000006', 'ja', 17, 'QR_CODE', CURRENT_TIMESTAMP - INTERVAL '5 minutes');
