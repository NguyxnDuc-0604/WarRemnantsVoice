import asyncio
import edge_tts
import whisper
from deep_translator import MyMemoryTranslator
from worker import app

# --- BƯỚC MỚI: TẢI MODEL WHISPER VÀO RAM ---
print("Đang tải mô hình Whisper vào bộ nhớ...")
whisper_model = whisper.load_model("base")
print("Tải Whisper thành công!")

async def generate_audio(text, voice, output_filename):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_filename)

@app.task(bind=True, name="process_poi_pipeline")
def process_poi_pipeline(self, poi_id, original_text=None, original_audio_path=None, target_lang_code='en'):
    """
    Quy trình xử lý nội dung POI phiên bản Nâng Cấp:
    1. ASR: Nhận file âm thanh gốc -> Bóc tách thành văn bản.
    2. Dịch sang ngôn ngữ đích.
    3. TTS: Chuyển văn bản dịch thành file Audio.
    """
    print(f"\n[x] Bắt đầu xử lý POI {poi_id} cho ngôn ngữ đích: {target_lang_code}")
    
    try:
        current_text = original_text
        source_lang_for_translation = 'vi-VN' # Mặc định nếu nhập text là tiếng Việt

        # BƯỚC 1: ASR - BÓC BĂNG (SPEECH-TO-TEXT)
        if original_audio_path:
            print(f"[-] Đang bóc băng file âm thanh: {original_audio_path}")
            # Để Whisper tự động nhận diện ngôn ngữ
            result = whisper_model.transcribe(original_audio_path)
            current_text = result["text"].strip()
            
            detected_lang = result.get("language", "vi")
            print(f"[-] Whisper nhận diện ngôn ngữ gốc là: {detected_lang}")
            print(f"[-] Kết quả bóc băng (ASR): '{current_text}'")
            
            lang_map = {'vi': 'vi-VN', 'en': 'en-US', 'fr': 'fr-FR', 'ja': 'ja-JP'}
            source_lang_for_translation = lang_map.get(detected_lang, 'vi-VN')

        if not current_text:
             return {"status": "error", "error": "Không có văn bản hoặc file âm thanh đầu vào."}

        # BƯỚC 2: DỊCH THUẬT (TRANSLATION)
        target_lang_map = {'vi': 'vi-VN', 'en': 'en-US', 'fr': 'fr-FR', 'ja': 'ja-JP'}
        target_translator_lang = target_lang_map.get(target_lang_code, 'en-US')

        print(f"[-] Đang dịch thuật từ {source_lang_for_translation} sang {target_translator_lang}...")
        translator = MyMemoryTranslator(source=source_lang_for_translation, target=target_translator_lang)
        translated_text = translator.translate(current_text)
        print(f"[-] Kết quả dịch: '{translated_text}'")

        # BƯỚC 3: TEXT-TO-SPEECH (TTS)
        voice_mapping = {
            'en': 'en-US-ChristopherNeural',
            'fr': 'fr-FR-HenriNeural',
            'ja': 'ja-JP-KeitaNeural',
            'vi': 'vi-VN-HoaiMyNeural'
        }
        
        voice = voice_mapping.get(target_lang_code, 'en-US-ChristopherNeural')
        output_file = f"audio_poi_{poi_id}_{target_lang_code}.mp3"
        
        asyncio.run(generate_audio(translated_text, voice, output_file))
        print(f"[-] Đã tạo xong file audio TTS: {output_file}")

        return {
            "status": "success",
            "poi_id": poi_id,
            "language": target_lang_code,
            "original_text_used": current_text,
            "translated_text": translated_text,
            "audio_file": output_file
        }

    except Exception as e:
        print(f"[!] Lỗi khi xử lý POI {poi_id}: {str(e)}")
        return {"status": "error", "error": str(e)}