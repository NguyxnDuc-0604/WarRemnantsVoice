-- ============================================================================
-- AUTH SERVICE SCHEMA (auth_db / auth_service)
-- Hệ thống Thuyết minh Tự động Đa ngôn ngữ (WarRemnantsVoice)
-- Phân hệ: Identity & Access Management (Auth Service)
-- ============================================================================

-- Bật extension sinh UUID nếu chưa có
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Tạo schema nếu sử dụng mô hình Logical Schemas
CREATE SCHEMA IF NOT EXISTS auth_service;

SET search_path TO auth_service, public;

-- ----------------------------------------------------------------------------
-- 1. BẢNG PHÂN QUYỀN VÀ TÀI KHOẢN HỆ THỐNG
-- ----------------------------------------------------------------------------

-- Bảng vai trò hệ thống
CREATE TABLE IF NOT EXISTS auth_service.system_role (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,      -- ADMIN, CURATOR, DEVOPS
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Bảng quyền hạn chi tiết
CREATE TABLE IF NOT EXISTS auth_service.system_permission (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(100) UNIQUE NOT NULL,     -- exhibit:write, translation:review, glossary:manage, system:monitor
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Bảng liên kết Vai trò - Quyền hạn (Role-Permission Mapping)
CREATE TABLE IF NOT EXISTS auth_service.role_permission (
    role_id UUID NOT NULL REFERENCES auth_service.system_role(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES auth_service.system_permission(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id)
);

-- Bảng tài khoản cán bộ quản trị bảo tàng
CREATE TABLE IF NOT EXISTS auth_service.system_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,   -- Mã hóa bằng Argon2id hoặc Bcrypt
    full_name VARCHAR(100) NOT NULL,
    role_id UUID NOT NULL REFERENCES auth_service.system_role(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Bảng nhật ký kiểm toán hành vi (Audit Log)
CREATE TABLE IF NOT EXISTS auth_service.audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth_service.system_user(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,          -- LOGIN, CREATE_EXHIBIT, UPDATE_TRANSLATION, REVIEW_AUDIO
    target_resource VARCHAR(100),          -- exhibit:T54-390, glossary:AgentOrange
    ip_address VARCHAR(45),
    user_agent TEXT,
    details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- INDEXES & PERFORMANCE OPTIMIZATION
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_user_username ON auth_service.system_user(username);
CREATE INDEX IF NOT EXISTS idx_user_email ON auth_service.system_user(email);
CREATE INDEX IF NOT EXISTS idx_user_role ON auth_service.system_user(role_id);
CREATE INDEX IF NOT EXISTS idx_audit_user_action ON auth_service.audit_log(user_id, action);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON auth_service.audit_log(created_at DESC);

-- Trigger tự động cập nhật updated_at
CREATE OR REPLACE FUNCTION auth_service.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_system_user_updated_at ON auth_service.system_user;
CREATE TRIGGER trg_system_user_updated_at
BEFORE UPDATE ON auth_service.system_user
FOR EACH ROW EXECUTE FUNCTION auth_service.update_updated_at_column();
