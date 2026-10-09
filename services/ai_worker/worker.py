# worker.py
from celery import Celery

# Khởi tạo ứng dụng Celery.
# 'voicemap_ai' là tên của worker.
# broker: Nơi nhận lệnh (ở đây ta dùng Redis chạy ở cổng 6379 trên máy bạn)
app = Celery(
    'voicemap_ai',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

# Cấu hình phụ: Ép worker chỉ nhận định dạng JSON cho an toàn
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Ho_Chi_Minh',
    enable_utc=True,
)