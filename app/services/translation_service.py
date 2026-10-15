import json
import os
from openai import AsyncOpenAI
from app.config import settings

# BẮT BUỘC tên class phải viết chính xác là TranslationService
class TranslationService:
    def __init__(self):
        # Khởi tạo client OpenAI (Sẽ dùng API Key trong config)
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def translate_text(self, text: str, target_lang: str) -> str:
        """
        Dịch đoạn thuyết minh sang ngôn ngữ mục tiêu
        """
        system_prompt = f"""
        Bạn là chuyên gia dịch thuật lịch sử cho Bảo tàng Chứng tích Chiến tranh.
        Dịch đoạn thuyết minh sau sang ngôn ngữ có mã '{target_lang}'.
        Yêu cầu: Trang nghiêm, khách quan, giữ đúng thuật ngữ lịch sử.
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Nếu chưa cấu hình OpenAI Key thì trả về kết quả Mockup để test API
            print(f"[Translation Warning] {e}")
            return f"[{target_lang.upper()}] {text}"