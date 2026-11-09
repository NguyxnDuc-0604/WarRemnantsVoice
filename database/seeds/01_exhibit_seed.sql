-- ============================================================
-- Seed data cho exhibit_db
-- Dữ liệu 5 hiện vật tiêu biểu & 2 tuyến tham quan mẫu
-- ============================================================

-- 1. Nạp 5 Hiện vật tiêu biểu
INSERT INTO exhibit (id, code, title, title_en, room_id, zone, period, latitude, longitude, radius, thumbnail_url, content_version, is_published, is_active)
VALUES 
(
    'b0000000-0000-0000-0000-000000000001',
    'UH1-BELL',
    'Máy bay trực thăng UH-1 Iroquois ''Huey''',
    'UH-1 Iroquois ''Huey'' Helicopter',
    'OUTDOOR',
    'Khu trưng bày ngoài trời',
    '1962 - 1975',
    10.77940000,
    106.69220000,
    15,
    'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=800&q=80',
    1,
    TRUE,
    TRUE
),
(
    'b0000000-0000-0000-0000-000000000002',
    'T54-390',
    'Xe tăng T-54B số hiệu 390',
    'T-54B Tank No. 390',
    'OUTDOOR',
    'Sân trưng bày cơ giới ngoài trời',
    'Kháng chiến chống Mỹ',
    10.77960000,
    106.69250000,
    15,
    'https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=800&q=80',
    1,
    TRUE,
    TRUE
),
(
    'b0000000-0000-0000-0000-000000000003',
    'M107-175',
    'Pháo tự hành M107 175mm ''Vua chiến trường''',
    'M107 175mm Self-Propelled Gun',
    'OUTDOOR',
    'Khu trưng bày pháo binh ngoài trời',
    '1968 - 1975',
    10.77920000,
    106.69280000,
    15,
    'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80',
    1,
    TRUE,
    TRUE
),
(
    'b0000000-0000-0000-0000-000000000004',
    'CONDAO-CAGE',
    'Mô hình phục dựng Chuồng cọp Côn Đảo',
    'Con Dao Tiger Cages Replica',
    'ROOM-02',
    'Khu chứng tích tội ác chiến tranh',
    'Thời kỳ thuộc địa & kháng chiến',
    NULL,
    NULL,
    10,
    'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=800&q=80',
    1,
    TRUE,
    TRUE
),
(
    'b0000000-0000-0000-0000-000000000005',
    'HOCHIMINH-CAMPAIGN',
    'Sa bàn Chiến dịch Hồ Chí Minh lịch sử',
    'Historical Ho Chi Minh Campaign Diorama',
    'ROOM-03',
    'Phòng trưng bày lịch sử tổng hợp',
    'Tháng 4/1975',
    NULL,
    NULL,
    10,
    'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80',
    1,
    TRUE,
    TRUE
)
ON CONFLICT (code) DO NOTHING;

-- 2. Nạp Nội dung nguồn tiếng Việt (Content Source)
INSERT INTO content_source (exhibit_id, original_text, content_version)
VALUES 
(
    'b0000000-0000-0000-0000-000000000001',
    'Trực thăng UH-1 Iroquois, thường được gọi là ''Huey'', là biểu tượng không quân của quân đội Mỹ trong Chiến tranh Việt Nam. Được sử dụng từ năm 1962 đến 1975 với các nhiệm vụ đổ quân chiến thuật, cứu thương và yểm trợ hoả lực. Chiếc máy bay trưng bày tại đây là một trong những chứng tích ghi lại các cuộc càn quét khốc liệt trên chiến trường miền Nam.',
    1
),
(
    'b0000000-0000-0000-0000-000000000002',
    'Xe tăng T-54B số hiệu 390 thuộc Đại đội 4, Tiểu đoàn 1, Lữ đoàn Tăng - Thiết giáp 203. Vào lúc 10 giờ 45 phút ngày 30 tháng 4 năm 1975, chiếc xe tăng này đã húc đổ cổng chính Dinh Độc Lập, đánh dấu thời khắc giải phóng hoàn toàn miền Nam, thống nhất non sông.',
    1
),
(
    'b0000000-0000-0000-0000-000000000003',
    'Pháo tự hành hạng nặng M107 cỡ nòng 175mm từng được mệnh danh là ''Vua chiến trường'' của quân đội Mỹ với tầm bắn tối đa lên tới hơn 32 km. Khẩu pháo này từng tham gia nhiều chiến dịch ác liệt tại Quảng Trị, Đường 9 Nam Lào và Đông Nam Bộ.',
    1
),
(
    'b0000000-0000-0000-0000-000000000004',
    'Chuồng cọp Côn Đảo là hệ thống giam giữ bí mật đặc biệt khắc nghiệt do chính quyền thực dân và tay sai xây dựng nhằm đày ải, tra tấn tinh thần và thể xác các chiến sĩ yêu nước. Không gian ngột ngạt, xiềng xích và vôi bột rải từ trên cao thể hiện tội ác tột cùng nhưng cũng là biểu tượng sáng ngời của ý chí bất khuất.',
    1
),
(
    'b0000000-0000-0000-0000-000000000005',
    'Chiến dịch Hồ Chí Minh diễn ra từ ngày 26 đến 30 tháng 4 năm 1975 là chiến dịch quyết chiến chiến lược lớn nhất trong lịch sử dân tộc. Bằng 5 cánh quân tiến công thần tốc, quân và dân ta đã đập tan bộ máy chiến tranh đầu não, giải phóng Sài Gòn và non sông thu về một mối.',
    1
)
ON CONFLICT DO NOTHING;

-- 3. Nạp Lộ trình tham quan mẫu (Tour Route)
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
