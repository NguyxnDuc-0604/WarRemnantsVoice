import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .db import init_analytics_db, get_db, ListeningMetric

app = FastAPI(
    title="WarRemnantsVoice - Analytics & Real-Time Monitoring Service",
    description="Dịch vụ phân tích số liệu, giám sát du khách thời gian thực và ghi nhận lượt nghe theo chuẩn PRD",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_analytics_db()

# State quản lý session du khách thời gian thực
ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}
VISITOR_LOGS: List[Dict[str, Any]] = []
TOTAL_VISITORS_COUNTER = 0

def clean_expired_sessions(timeout_seconds: int = 25):
    """Loại bỏ các session không gửi heartbeat trong 25 giây (đã thoát trang)"""
    now = time.time()
    expired = [sid for sid, data in list(ACTIVE_SESSIONS.items()) if now - data.get("last_ping", 0) > timeout_seconds]
    for sid in expired:
        del ACTIVE_SESSIONS[sid]

class HeartbeatRequest(BaseModel):
    visitor_id: str
    exhibit_code: Optional[str] = "HOME"
    language_code: Optional[str] = "en"
    is_playing: Optional[bool] = False
    device_type: Optional[str] = "Mobile"

class MetricReportRequest(BaseModel):
    exhibit_code: str
    language_code: str
    listened_duration: int
    trigger_type: Optional[str] = "QR_CODE"

@app.get("/")
@app.get("/health")
def health_check():
    clean_expired_sessions()
    return {
        "service": "Analytics & Monitoring Service",
        "status": "UP",
        "active_visitors_online": len(ACTIVE_SESSIONS),
        "total_visitors_today": TOTAL_VISITORS_COUNTER
    }

@app.post("/api/v1/metrics/heartbeat")
def receive_heartbeat(payload: HeartbeatRequest, request: Request):
    global TOTAL_VISITORS_COUNTER
    now = time.time()
    vid = payload.visitor_id
    
    is_new = vid not in ACTIVE_SESSIONS
    if is_new:
        TOTAL_VISITORS_COUNTER += 1
        client_host = request.client.host if request.client else "unknown"
        VISITOR_LOGS.insert(0, {
            "id": f"log-{int(now * 1000)}",
            "visitor_id": vid[:8],
            "exhibit_code": payload.exhibit_code,
            "language": payload.language_code,
            "device": payload.device_type,
            "action": "Kết nối tham quan",
            "time": datetime.now().strftime("%H:%M:%S"),
            "ip": client_host
        })
        if len(VISITOR_LOGS) > 50:
            VISITOR_LOGS.pop()

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

@app.get("/api/v1/admin/dashboard-stats")
def get_admin_dashboard_stats(db: Session = Depends(get_db)):
    clean_expired_sessions()
    
    online_count = len(ACTIVE_SESSIONS)
    listening_count = sum(1 for s in ACTIVE_SESSIONS.values() if s.get("is_playing"))
    total_audio_played = db.query(ListeningMetric).count()
    
    # Thống kê ngôn ngữ
    lang_counts: Dict[str, int] = {}
    for s in ACTIVE_SESSIONS.values():
        lang = s.get("language_code", "en")
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
    # Thống kê thiết bị
    device_counts = {"Mobile": 0, "Desktop": 0}
    for s in ACTIVE_SESSIONS.values():
        dev = s.get("device_type", "Mobile")
        if dev in device_counts:
            device_counts[dev] += 1
        else:
            device_counts["Mobile"] += 1

    # Thống kê hiện vật đang xem
    exhibit_now: Dict[str, int] = {}
    for s in ACTIVE_SESSIONS.values():
        ex = s.get("exhibit_code", "HOME")
        exhibit_now[ex] = exhibit_now.get(ex, 0) + 1

    return {
        "realtime": {
            "online_visitors": online_count,
            "active_listeners": listening_count,
            "total_visits_today": max(TOTAL_VISITORS_COUNTER, online_count),
            "total_audio_played": total_audio_played,
            "server_time": datetime.now().strftime("%H:%M:%S - %d/%m/%Y"),
            "system_health": "ONLINE"
        },
        "breakdown": {
            "by_language": lang_counts,
            "by_device": device_counts,
            "by_exhibit": exhibit_now
        },
        "recent_activity_logs": VISITOR_LOGS[:20],
        "active_sessions_list": [
            {
                "session_id": sid[:8],
                "exhibit": s.get("exhibit_code"),
                "language": s.get("language_code"),
                "is_listening": s.get("is_playing"),
                "device": s.get("device_type"),
                "connected_at": s.get("connected_at")
            }
            for sid, s in list(ACTIVE_SESSIONS.items())[:30]
        ]
    }

@app.post("/api/v1/metrics/listen")
def record_listening_metric(metric: MetricReportRequest, db: Session = Depends(get_db)):
    new_metric = ListeningMetric(
        exhibit_code=metric.exhibit_code,
        language_code=metric.language_code,
        listened_duration=metric.listened_duration,
        trigger_type=metric.trigger_type,
        timestamp=datetime.utcnow()
    )
    db.add(new_metric)
    db.commit()
    
    total_records = db.query(ListeningMetric).count()
    
    VISITOR_LOGS.insert(0, {
        "id": f"log-play-{int(time.time() * 1000)}",
        "visitor_id": "Visitor",
        "exhibit_code": metric.exhibit_code,
        "language": metric.language_code,
        "device": "Mobile",
        "action": f"Nghe bài ({metric.listened_duration}s)",
        "time": datetime.now().strftime("%H:%M:%S"),
        "ip": "Client"
    })
    return {"status": "recorded", "total_records": total_records}
