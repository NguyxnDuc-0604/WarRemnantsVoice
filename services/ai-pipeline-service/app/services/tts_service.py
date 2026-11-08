
import edge_tts
import os
import asyncio
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ánh xạ ngôn ngữ với giọng đọc Microsoft Edge TTS
VOICE_MAPPING = {
    "vi": "vi-VN-HoaiMyNeural",
    "en": "en-US-AndrewNeural",
    "fr": "fr-FR-HenriNeural",
    "ja": "ja-JP-KeitaNeural",
    "zh": "zh-CN-YunxiNeural"
}


async def generate_audio(
    text: str,
    target_lang: str,
    output_path: str
) -> str:
    """
    Sinh file âm thanh từ văn bản thuyết minh.

    Args:
        text: Nội dung cần đọc.
        target_lang: Mã ngôn ngữ (vi, en, fr, ja, zh).
        output_path: Đường dẫn lưu file MP3.

    Returns:
        Đường dẫn file âm thanh.
    """

    if not text or not text.strip():
        raise ValueError("Nội dung văn bản không được để trống")

    target_lang = target_lang.strip().lower()

    voice = VOICE_MAPPING.get(
        target_lang,
        "en-US-AndrewNeural"
    )

    # Tạo thư mục nếu chưa tồn tại
    output_dir = os.path.dirname(output_path)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Thử tạo audio tối đa 3 lần
    max_retries = 3

    for attempt in range(1, max_retries + 1):

        try:
            logger.info(
                f"Generating audio: language={target_lang}, "
                f"voice={voice}, attempt={attempt}"
            )

            # Tạo đối tượng Edge TTS mới mỗi lần thử
            communicate = edge_tts.Communicate(
                text,
                voice
            )

            # Giới hạn thời gian xử lý 120 giây
            await asyncio.wait_for(
                communicate.save(output_path),
                timeout=120
            )

            # Kiểm tra file sau khi tạo
            if not os.path.exists(output_path):
                raise RuntimeError("Không tìm thấy file MP3 sau khi tạo")

            if os.path.getsize(output_path) == 0:
                raise RuntimeError("File MP3 được tạo nhưng bị rỗng")

            logger.info(
                f"Audio generated successfully: {output_path}"
            )

            return output_path

        except Exception as e:

            logger.error(
                f"Audio generation failed "
                f"(attempt {attempt}/{max_retries}): {e}"
            )

            # Xóa file lỗi nếu có
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError:
                    pass

            if attempt == max_retries:
                raise RuntimeError(
                    f"Không thể tạo audio sau "
                    f"{max_retries} lần thử: {str(e)}"
                ) from e

            # Chờ trước khi thử lại
            await asyncio.sleep(attempt * 3)

    raise RuntimeError("Không thể tạo file âm thanh")
