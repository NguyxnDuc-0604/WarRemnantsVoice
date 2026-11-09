# ============================================================
# Multi-stage Optimized Dockerfile cho AI Pipeline Service
# Thành viên 2: AI & Pipeline Processing Services
# Giảm thiểu tối đa dung lượng image và tăng tốc độ build
# ============================================================

# --- Stage 1: Build & Dependencies Compiler ---
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Stage 2: Final Minimal Runtime Image ---
FROM python:3.11-slim AS runner

WORKDIR /app

# Cài đặt ffmpeg cho xử lý file âm thanh (nhẹ nhất có thể)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/*

# Sao chép các package Python đã biên dịch từ Stage 1
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy mã nguồn dịch vụ
COPY . .

# Tạo thư mục output cho file audio thuyết minh
RUN mkdir -p /app/output

EXPOSE 8000

# Chạy FastAPI Uvicorn Server
CMD ["uvicorn", "main_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]
