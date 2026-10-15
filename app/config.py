import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "WarRemnantsVoice AI Pipeline"
    
    # Cấu hình RabbitMQ
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT: int = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_QUEUE: str = "ai_processing_queue"
    
    # Cấu hình MinIO
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET_NAME: str = "museum-audio"
    
    # Cấu hình OpenAI API Key
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your-openai-key-here")

# BẮT BUỘC phải có dòng khởi tạo object 'settings' ở đây:
settings = Settings()