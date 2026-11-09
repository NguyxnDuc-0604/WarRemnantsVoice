-- ============================================================
-- Seed data cho gateway_db
-- Dữ liệu thống kê lượt nghe mẫu
-- ============================================================

INSERT INTO listening_metric (exhibit_id, exhibit_code, language_code, listened_duration, trigger_type, timestamp)
VALUES
('b0000000-0000-0000-0000-000000000001', 'UH1-BELL', 'en', 45, 'QR_CODE', CURRENT_TIMESTAMP - INTERVAL '2 hours'),
('b0000000-0000-0000-0000-000000000001', 'UH1-BELL', 'vi', 60, 'QR_CODE', CURRENT_TIMESTAMP - INTERVAL '1 hour'),
('b0000000-0000-0000-0000-000000000002', 'T54-390',   'en', 55, 'QR_CODE', CURRENT_TIMESTAMP - INTERVAL '30 minutes'),
('b0000000-0000-0000-0000-000000000002', 'T54-390',   'fr', 50, 'QR_CODE', CURRENT_TIMESTAMP - INTERVAL '15 minutes'),
('b0000000-0000-0000-0000-000000000003', 'M107-175',  'ja', 40, 'QR_CODE', CURRENT_TIMESTAMP - INTERVAL '5 minutes');
