import pika
import json
import asyncio
import os
from app.config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASS, QUEUE_IN, QUEUE_OUT
from app.services.translate_service import translate_text
from app.services.tts_service import generate_audio

def process_message(ch, method, properties, body):
    data = json.loads(body)
    print(f" [x] Nhận Job mới: {data.get('task_id')}")

    task_id = data.get("task_id")
    exhibit_id = data.get("exhibit_id")
    original_text = data.get("original_text", "")
    target_languages = data.get("target_languages", ["en"])

    results = []
    output_dir = f"./output/{exhibit_id}"
    os.makedirs(output_dir, exist_ok=True)

    for lang in target_languages:
        # 1. Dịch thuật & chuẩn hóa từ điển
        translated_text = translate_text(original_text, lang)
        
        # 2. Sinh giọng đọc Audio
        audio_filename = f"{exhibit_id}_{lang}.mp3"
        audio_path = os.path.join(output_dir, audio_filename)
        
        asyncio.run(generate_audio(translated_text, lang, audio_path))
        
        results.append({
            "language": lang,
            "translated_text": translated_text,
            "audio_file_path": audio_path
        })

    # 3. Phản hồi kết quả về Queue đầu ra
    response_payload = {
        "task_id": task_id,
        "exhibit_id": exhibit_id,
        "status": "COMPLETED",
        "results": results
    }

    ch.basic_publish(
        exchange='',
        routing_key=QUEUE_OUT,
        body=json.dumps(response_payload)
    )
    print(f" [✓] Hoàn thành Task: {task_id}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT, '/', credentials)
    
    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue=QUEUE_IN, durable=True)
        channel.queue_declare(queue=QUEUE_OUT, durable=True)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=QUEUE_IN, on_message_callback=process_message)

        print(" [*] AI Pipeline Worker đang chạy và chờ tin nhắn từ RabbitMQ...")
        channel.start_consuming()
    except Exception as e:
        print(f" Lỗi kết nối RabbitMQ: {e}")

if __name__ == "__main__":
    main()
    import asyncio
import os
from app.services.translate_service import translate_text
from app.services.tts_service import generate_audio

async def run_test():
    print("=== BẮT ĐẦU TEST AI PIPELINE WORKER ===")
    
    # 1. Dữ liệu giả lập
    exhibit_id = "ex-001"
    original_text = "Trận Ấp Bắc diễn ra vào ngày 2 tháng 1 năm 1963 tại Bảo tàng Chứng tích Chiến tranh."
    target_languages = ["en", "fr"]
    
    output_dir = f"./output/{exhibit_id}"
    os.makedirs(output_dir, exist_ok=True)

    print(f"Văn bản gốc: {original_text}\n")

    for lang in target_languages:
        # 2. Test dịch + từ điển Glossary
        translated_text = translate_text(original_text, lang)
        print(f"[{lang.upper()}] Bản dịch: {translated_text}")

        # 3. Test sinh file âm thanh .mp3
        audio_filename = f"{exhibit_id}_{lang}.mp3"
        audio_path = os.path.join(output_dir, audio_filename)
        
        print(f"[{lang.upper()}] Đang tạo file audio...")
        await generate_audio(translated_text, lang, audio_path)
        print(f" => Thành công! File lưu tại: {audio_path}\n")

    print("=== TẤT CẢ TÍNH NĂNG AI ĐÃ CHẠY HOÀN HẢO! ===")

if __name__ == "__main__":
    asyncio.run(run_test())