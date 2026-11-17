import os
import re
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
import mimetypes

app = FastAPI(
    title="WarRemnantsVoice - Media & Streaming Service",
    description="Dịch vụ phân phối & Streaming âm thanh đa ngôn ngữ tối ưu cho thiết bị di động (hỗ trợ HTTP 206 Range)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thư mục lưu trữ file audio output
# Hỗ trợ cấu hình đường dẫn qua biến môi trường MEDIA_DIR
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
DEFAULT_MEDIA_DIR = os.path.join(PROJECT_ROOT, "output")
MEDIA_DIR = os.getenv("MEDIA_DIR", DEFAULT_MEDIA_DIR)

os.makedirs(MEDIA_DIR, exist_ok=True)

@app.get("/")
@app.get("/health")
def health_check():
    return {
        "service": "Media & Streaming Service",
        "status": "UP",
        "media_dir": MEDIA_DIR,
        "files_count": len(os.listdir(MEDIA_DIR)) if os.path.exists(MEDIA_DIR) else 0
    }

def send_partial_file(path: str, range_header: str):
    """Xử lý HTTP 206 Partial Content cho streaming âm thanh mượt mà trên iPhone/Android"""
    file_size = os.path.getsize(path)
    
    # Range format: bytes=start-end
    range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
    if not range_match:
        return FileResponse(path, media_type="audio/mpeg")
        
    start = int(range_match.group(1))
    end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
    
    if start >= file_size or end >= file_size or start > end:
        return Response(status_code=416, headers={"Content-Range": f"bytes */{file_size}"})
        
    chunk_size = (end - start) + 1
    
    def file_iterator():
        with open(path, "rb") as f:
            f.seek(start)
            remaining = chunk_size
            while remaining > 0:
                read_size = min(remaining, 64 * 1024)
                data = f.read(read_size)
                if not data:
                    break
                remaining -= len(data)
                yield data

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(chunk_size),
        "Content-Type": "audio/mpeg",
    }
    return StreamingResponse(file_iterator(), status_code=206, headers=headers)

@app.get("/output/{file_path:path}")
async def stream_audio(request: Request, file_path: str):
    """Endpoint stream âm thanh, hỗ trợ tìm kiếm file trong thư mục output chung hoặc subfolder"""
    full_path = os.path.normpath(os.path.join(MEDIA_DIR, file_path))
    
    # Kiểm tra an toàn đường dẫn (tránh path traversal)
    if not full_path.startswith(os.path.normpath(MEDIA_DIR)):
        raise HTTPException(status_code=403, detail="Truy cập tệp không hợp lệ")
        
    # Nếu không tìm thấy trong MEDIA_DIR, kiểm tra xem có ở ai-pipeline-service/output không
    if not os.path.isfile(full_path):
        alt_path = os.path.join(PROJECT_ROOT, "services", "ai-pipeline-service", "output", file_path)
        if os.path.isfile(alt_path):
            full_path = alt_path
            
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail=f"Không tìm thấy tệp âm thanh: {file_path}")

    range_header = request.headers.get("range")
    if range_header:
        return send_partial_file(full_path, range_header)

    mime_type, _ = mimetypes.guess_type(full_path)
    return FileResponse(
        full_path,
        media_type=mime_type or "audio/mpeg",
        headers={"Accept-Ranges": "bytes"}
    )
