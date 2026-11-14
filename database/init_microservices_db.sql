-- ============================================================================
-- KHỞI TẠO CÁC CƠ SỞ DỮ LIỆU ĐỘC LẬP THEO MICROSERVICES (DATABASE-PER-SERVICE)
-- Sử dụng khi triển khai các container hoặc database instance riêng biệt
-- ============================================================================

-- 1. Database cho Identity & Access Management Service
CREATE DATABASE auth_db
    WITH OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- 2. Database cho Exhibit Core Service
CREATE DATABASE exhibit_db
    WITH OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- 3. Database cho Localization & Glossary Service
CREATE DATABASE localization_db
    WITH OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- 4. Database cho Streaming & Media Distribution Service
CREATE DATABASE media_db
    WITH OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- 5. Database cho Analytics & Metric Service
CREATE DATABASE metric_db
    WITH OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;
