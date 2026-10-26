from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import re
import time
import asyncio
from datetime import datetime

from app.services.translate_service import translate_text
from app.services.tts_service import generate_audio

app = FastAPI(
    title="WarRemnantsVoice - AI Pipeline & Exhibit Service",
    description="Hệ thống thuyết minh tự động đa ngôn ngữ cho Bảo tàng Chứng tích Chiến tranh",
    version="2.2.0"
)

# CORS Middleware mở cho mọi Client (Mobile Web, PWA, Remote Tunnel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thư mục chứa audio file
os.makedirs("./output", exist_ok=True)
app.mount("/output", StaticFiles(directory="./output"), name="output")

# Cơ sở dữ liệu danh mục hiện vật mẫu chuẩn theo PRD
EXHIBITS_DATABASE = [
    {
        "id": "ex-01-uuid",
        "code": "UH1-BELL",
        "display_code": "EX-01",
        "title": "Máy bay trực thăng UH-1 Iroquois 'Huey'",
        "title_en": "UH-1 Iroquois 'Huey' Helicopter",
        "room_id": "OUTDOOR",
        "zone": "Khu trưng bày ngoài trời",
        "latitude": 10.7794,
        "longitude": 106.6922,
        "radius": 15,
        "thumbnail_url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=800&q=80",
        "period": "1962 - 1975",
        "original_text": "Trực thăng UH-1 Iroquois, thường được gọi là 'Huey', là biểu tượng không quân của quân đội Mỹ trong Chiến tranh Việt Nam. Được sử dụng từ năm 1962 đến 1975 với các nhiệm vụ đổ quân chiến thuật, cứu thương và yểm trợ hoả lực. Chiếc máy bay trưng bày tại đây là một trong những chứng tích ghi lại các cuộc càn quét khốc liệt trên chiến trường miền Nam.",
        "content_version": 1,
        "is_published": True,
        "next_code": "T54-390"
    },
    {
        "id": "ex-02-uuid",
        "code": "T54-390",
        "display_code": "EX-02",
        "title": "Xe tăng T-54B số hiệu 390",
        "title_en": "T-54B Tank No. 390",
        "room_id": "OUTDOOR",
        "zone": "Sân trưng bày cơ giới ngoài trời",
        "latitude": 10.7796,
        "longitude": 106.6925,
        "radius": 15,
        "thumbnail_url": "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=800&q=80",
        "period": "1975",
        "original_text": "Xe tăng T-54B số hiệu 390 thuộc Đại đội 4, Tiểu đoàn 1, Lữ đoàn Tăng - Thiết giáp 203. Vào lúc 10 giờ 45 phút ngày 30 tháng 4 năm 1975, chiếc xe tăng này đã húc đổ cổng chính Dinh Độc Lập, đánh dấu thời khắc giải phóng hoàn toàn miền Nam, thống nhất non sông.",
        "content_version": 1,
        "is_published": True,
        "next_code": "M107-175"
    },
    {
        "id": "ex-03-uuid",
        "code": "M107-175",
        "display_code": "EX-03",
        "title": "Pháo tự hành M107 175mm 'Vua chiến trường'",
        "title_en": "M107 175mm Self-Propelled Gun",
        "room_id": "OUTDOOR",
        "zone": "Khu trưng bày pháo binh ngoài trời",
        "latitude": 10.7792,
        "longitude": 106.6928,
        "radius": 15,
        "thumbnail_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80",
        "period": "1968 - 1975",
        "original_text": "Pháo tự hành hạng nặng M107 cỡ nòng 175mm từng được mệnh danh là 'Vua chiến trường' của quân đội Mỹ với tầm bắn tối đa lên tới hơn 32 km. Khẩu pháo này từng tham gia nhiều chiến dịch ác liệt tại Quảng Trị, Đường 9 Nam Lào và Đông Nam Bộ.",
        "content_version": 1,
        "is_published": True,
        "next_code": "CONDAO-CAGE"
    },
    {
        "id": "ex-04-uuid",
        "code": "CONDAO-CAGE",
        "display_code": "EX-04",
        "title": "Mô hình phục dựng Chuồng cọp Côn Đảo",
        "title_en": "Con Dao Tiger Cages Replica",
        "room_id": "ROOM-02",
        "zone": "Khu chứng tích tội ác chiến tranh",
        "latitude": None,
        "longitude": None,
        "radius": 10,
        "thumbnail_url": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=800&q=80",
        "period": "1940 - 1975",
        "original_text": "Chuồng cọp Côn Đảo là hệ thống giam giữ bí mật đặc biệt khắc nghiệt do chính quyền thực dân và tay sai xây dựng nhằm đày ải, tra tấn tinh thần và thể xác các chiến sĩ yêu nước. Không gian ngột ngạt, xiềng xích và vôi bột rải từ trên cao thể hiện tội ác tột cùng nhưng cũng là biểu tượng sáng ngời của ý chí bất khuất.",
        "content_version": 1,
        "is_published": True,
        "next_code": "HOCHIMINH-CAMPAIGN"
    },
    {
        "id": "ex-05-uuid",
        "code": "HOCHIMINH-CAMPAIGN",
        "display_code": "EX-05",
        "title": "Sa bàn Chiến dịch Hồ Chí Minh lịch sử",
        "title_en": "Historical Ho Chi Minh Campaign Diorama",
        "room_id": "ROOM-03",
        "zone": "Phòng trưng bày lịch sử tổng hợp",
        "latitude": None,
        "longitude": None,
        "radius": 10,
        "thumbnail_url": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80",
        "period": "Tháng 4/1975",
        "original_text": "Chiến dịch Hồ Chí Minh diễn ra từ ngày 26 đến 30 tháng 4 năm 1975 là chiến dịch quyết chiến chiến lược lớn nhất trong lịch sử dân tộc. Bằng 5 cánh quân tiến công thần tốc, quân và dân ta đã đập tan bộ máy chiến tranh đầu não, giải phóng Sài Gòn và non sông thu về một mối.",
        "content_version": 1,
        "is_published": True,
        "next_code": "UH1-BELL"
    }
]

# Lưu trữ cache các bản dịch & audio đã sinh (BR-05)
TRANSLATION_CACHE: Dict[str, Any] = {}

# Lưu trữ số liệu thống kê lượt nghe ẩn danh (FR-20, BR-15)
LISTENING_METRICS: List[Dict[str, Any]] = []

# ====================================================================
# 🟢 REAL-TIME VISITOR TRACKING & OBSERVABILITY (PRD UC5, FR-21, FR-22)
# ====================================================================
# Lưu trữ các phiên người dùng đang hoạt động trong thời gian thực
ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}

# Nhật ký sự kiện truy cập thời gian thực (Live Stream)
VISITOR_LOGS: List[Dict[str, Any]] = []

TOTAL_VISITORS_COUNTER = 0

def clean_expired_sessions(timeout_seconds: int = 25):
    """Xóa các session không gửi heartbeat trong 25 giây (coi như đã rời khỏi trang)"""
    now = time.time()
    expired = [sid for sid, data in ACTIVE_SESSIONS.items() if now - data.get("last_ping", 0) > timeout_seconds]
    for sid in expired:
        del ACTIVE_SESSIONS[sid]

# Hàm chia câu và ước tính mốc thời gian phụ đề JSON (FR-16)
def generate_subtitle_timestamps(text: str, total_duration: float = None):
    raw_sentences = re.split(r'(?<=[.!?。！？])\s+', text.strip())
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    if not sentences:
        sentences = [text.strip()]
    
    total_chars = sum(len(s) for s in sentences)
    if total_chars == 0:
        total_chars = 1

    duration = total_duration if total_duration else max(len(text) * 0.07, 3.5)
    
    timestamps = []
    current_time = 0.0
    for idx, sentence in enumerate(sentences):
        sentence_duration = (len(sentence) / total_chars) * duration
        sentence_duration = max(sentence_duration, 1.2)
        end_time = round(current_time + sentence_duration, 2)
        
        timestamps.append({
            "id": idx,
            "start": round(current_time, 2),
            "end": end_time,
            "text": sentence
        })
        current_time = end_time

    return timestamps

# Models
class TranslationRequest(BaseModel):
    task_id: str
    exhibit_id: str
    original_text: str
    target_languages: List[str] = ["en"]

class MetricReportRequest(BaseModel):
    exhibit_code: str
    language_code: str
    listened_duration: int
    trigger_type: str = "QR_CODE"

class HeartbeatRequest(BaseModel):
    visitor_id: str
    exhibit_code: Optional[str] = "HOME"
    language_code: Optional[str] = "en"
    is_playing: bool = False
    device_type: Optional[str] = "Mobile" # "Mobile" hoặc "Desktop"

@app.get("/")
def health_check():
    clean_expired_sessions()
    return {
        "status": "ok",
        "service": "WarRemnantsVoice Exhibit & AI Service",
        "version": "2.2.0",
        "active_visitors_online": len(ACTIVE_SESSIONS),
        "exhibits_count": len(EXHIBITS_DATABASE)
    }

# ====================================================================
# 👥 VISITOR HEARTBEAT & REAL-TIME TRACKING
# ====================================================================
@app.post("/api/v1/metrics/heartbeat")
def receive_heartbeat(payload: HeartbeatRequest, request: Request):
    """
    Tiếp nhận ping từ thiết bị du khách mỗi 5-10 giây để đếm người đang online thời gian thực
    """
    global TOTAL_VISITORS_COUNTER
    now = time.time()
    vid = payload.visitor_id
    
    is_new = vid not in ACTIVE_SESSIONS
    if is_new:
        TOTAL_VISITORS_COUNTER += 1
        
        # Ghi nhận vào nhật ký truy cập trực tiếp
        client_host = request.client.host if request.client else "unknown"
        VISITOR_LOGS.insert(0, {
            "id": f"log-{int(now * 1000)}",
            "visitor_id": vid[:8] + "...",
            "exhibit_code": payload.exhibit_code,
            "language": payload.language_code,
            "device": payload.device_type,
            "action": "Vào xem hiện vật",
            "time": datetime.now().strftime("%H:%M:%S"),
            "ip": client_host
        })
        # Giữ tối đa 50 log gần nhất
        if len(VISITOR_LOGS) > 50:
            VISITOR_LOGS.pop()

    # Cập nhật thông tin session
    ACTIVE_SESSIONS[vid] = {
        "visitor_id": vid,
        "exhibit_code": payload.exhibit_code,
        "language_code": payload.language_code,
        "is_playing": payload.is_playing,
        "device_type": payload.device_type,
        "last_ping": now,
        "connected_at": ACTIVE_SESSIONS.get(vid, {}).get("connected_at", datetime.now().strftime("%H:%M:%S"))
    }
    
    clean_expired_sessions()
    return {
        "status": "ok",
        "active_online": len(ACTIVE_SESSIONS)
    }

# ====================================================================
# 📊 ADMIN OBSERVABILITY & ANALYTICS DASHBOARD (UC5, FR-21, FR-22)
# ====================================================================
@app.get("/api/v1/admin/dashboard-stats")
def get_admin_dashboard_stats():
    """
    Endpoint cung cấp toàn bộ chỉ số giám sát thời gian thực cho Admin:
    - Số người đang online (CCU)
    - Số người đang nghe thuyết minh
    - Thống kê theo ngôn ngữ, thiết bị, hiện vật
    - Nhật ký du khách
    """
    clean_expired_sessions()
    
    online_count = len(ACTIVE_SESSIONS)
    listening_count = sum(1 for s in ACTIVE_SESSIONS.values() if s.get("is_playing"))
    
    # Phân bố theo ngôn ngữ
    lang_counts: Dict[str, int] = {}
    for s in ACTIVE_SESSIONS.values():
        lang = s.get("language_code", "unknown")
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
    # Phân bố theo thiết bị
    device_counts = {"Mobile": 0, "Desktop": 0}
    for s in ACTIVE_SESSIONS.values():
        dev = s.get("device_type", "Mobile")
        device_counts[dev] = device_counts.get(dev, 0) + 1

    # Phân bố theo hiện vật đang xem
    exhibit_now: Dict[str, int] = {}
    for s in ACTIVE_SESSIONS.values():
        ex = s.get("exhibit_code", "HOME")
        exhibit_now[ex] = exhibit_now.get(ex, 0) + 1

    # Thống kê tổng lượt nghe từ LISTENING_METRICS
    total_audio_plays = len(LISTENING_METRICS)
    
    return {
        "realtime": {
            "online_visitors": online_count,
            "active_listeners": listening_count,
            "total_visits_today": max(TOTAL_VISITORS_COUNTER, online_count),
            "total_audio_played": total_audio_plays,
            "server_time": datetime.now().strftime("%H:%M:%S - %d/%m/%Y"),
            "system_health": "HEALTHY",
            "uptime_status": "ONLINE"
        },
        "breakdown": {
            "by_language": lang_counts,
            "by_device": device_counts,
            "by_exhibit": exhibit_now
        },
        "recent_activity_logs": VISITOR_LOGS[:20],
        "active_sessions_list": [
            {
                "session_id": sid[:8] + "...",
                "exhibit": s.get("exhibit_code"),
                "language": s.get("language_code"),
                "is_listening": s.get("is_playing"),
                "device": s.get("device_type"),
                "connected_at": s.get("connected_at")
            }
            for sid, s in list(ACTIVE_SESSIONS.items())[:25]
        ]
    }

# ====================================================================
# 🏛️ EXHIBIT APIS
# ====================================================================
@app.get("/api/v1/exhibits")
def get_all_exhibits():
    """Lấy danh sách tất cả hiện vật phục vụ khách tham quan & tạo bảng QR"""
    return EXHIBITS_DATABASE

@app.get("/api/v1/exhibits/{identifier}")
def get_exhibit_by_code_or_id(identifier: str):
    clean_id = identifier.strip().upper()
    for exhibit in EXHIBITS_DATABASE:
        if (exhibit["code"].upper() == clean_id or 
            exhibit["display_code"].upper() == clean_id or 
            exhibit["id"].upper() == clean_id):
            return exhibit
            
    for exhibit in EXHIBITS_DATABASE:
        if clean_id.replace('-', '') in exhibit["code"].upper().replace('-', ''):
            return exhibit

    raise HTTPException(status_code=404, detail=f"Không tìm thấy hiện vật với mã '{identifier}'")

@app.get("/api/v1/exhibits/{identifier}/audio")
async def get_exhibit_audio(identifier: str, lang: str = Query("en")):
    clean_id = identifier.strip().upper()
    target_exhibit = None
    for ex in EXHIBITS_DATABASE:
        if (ex["code"].upper() == clean_id or 
            ex["display_code"].upper() == clean_id or 
            ex["id"].upper() == clean_id):
            target_exhibit = ex
            break

    if not target_exhibit:
        raise HTTPException(status_code=404, detail=f"Hiện vật '{identifier}' không tồn tại.")

    cache_key = f"{target_exhibit['code']}_{lang}_v{target_exhibit['content_version']}"
    
    if cache_key in TRANSLATION_CACHE:
        return TRANSLATION_CACHE[cache_key]

    try:
        translated_text = translate_text(target_exhibit["original_text"], lang)
        
        output_dir = os.path.join(".", "output", target_exhibit["code"])
        os.makedirs(output_dir, exist_ok=True)
        
        audio_filename = f"{target_exhibit['code']}_{lang}.mp3"
        full_disk_path = os.path.join(output_dir, audio_filename)
        
        await generate_audio(translated_text, lang, full_disk_path)
        
        timestamps = generate_subtitle_timestamps(translated_text)
        web_audio_url = f"/output/{target_exhibit['code']}/{audio_filename}"
        
        result_payload = {
            "exhibit_code": target_exhibit["code"],
            "language": lang,
            "translated_title": target_exhibit.get("title_en") if lang == "en" else target_exhibit["title"],
            "translated_text": translated_text,
            "original_text": target_exhibit["original_text"],
            "audio_file_path": web_audio_url,
            "timestamps_json": timestamps,
            "duration_seconds": timestamps[-1]["end"] if timestamps else 30
        }
        
        TRANSLATION_CACHE[cache_key] = result_payload
        return result_payload

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý audio/dịch thuật: {str(e)}")

@app.post("/api/v1/process-audio")
async def process_translation_and_tts(payload: TranslationRequest):
    try:
        results = []
        output_dir = os.path.join(".", "output", payload.exhibit_id)
        os.makedirs(output_dir, exist_ok=True)

        for lang in payload.target_languages:
            translated_text = translate_text(payload.original_text, lang)
            audio_filename = f"{payload.exhibit_id}_{lang}.mp3"
            full_disk_path = os.path.join(output_dir, audio_filename)
            
            await generate_audio(translated_text, lang, full_disk_path)
            
            web_audio_url = f"/output/{payload.exhibit_id}/{audio_filename}"
            timestamps = generate_subtitle_timestamps(translated_text)
            
            results.append({
                "language": lang,
                "translated_text": translated_text,
                "audio_file_path": web_audio_url,
                "timestamps_json": timestamps
            })

        return {
            "task_id": payload.task_id,
            "exhibit_id": payload.exhibit_id,
            "status": "COMPLETED",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý AI: {str(e)}")

@app.post("/api/v1/metrics/listen")
def record_listening_metric(metric: MetricReportRequest):
    record = {
        "exhibit_code": metric.exhibit_code,
        "language_code": metric.language_code,
        "listened_duration": metric.listened_duration,
        "trigger_type": metric.trigger_type,
        "timestamp": datetime.now().isoformat()
    }
    LISTENING_METRICS.append(record)
    
    # Ghi nhận vào log hiển thị
    VISITOR_LOGS.insert(0, {
        "id": f"log-play-{int(time.time() * 1000)}",
        "visitor_id": "Visitor",
        "exhibit_code": metric.exhibit_code,
        "language": metric.language_code,
        "device": "Mobile",
        "action": f"Nghe xong bài ({metric.listened_duration}s)",
        "time": datetime.now().strftime("%H:%M:%S"),
        "ip": "Client"
    })
    return {"status": "recorded", "total_records": len(LISTENING_METRICS)}
