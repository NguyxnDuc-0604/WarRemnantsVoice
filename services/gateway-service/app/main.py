import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [GATEWAY] %(message)s")
logger = logging.getLogger("api-gateway")

# Cấu hình địa chỉ của các downstream services
EXHIBIT_SERVICE_URL = os.getenv("EXHIBIT_SERVICE_URL", "http://localhost:8001").rstrip("/")
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8002").rstrip("/")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8003").rstrip("/")
STREAMING_SERVICE_URL = os.getenv("STREAMING_SERVICE_URL", "http://localhost:8004").rstrip("/")

client: httpx.AsyncClient = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    client = httpx.AsyncClient(timeout=60.0)
    logger.info("API Gateway persistent HTTP client initialized.")
    yield
    await client.aclose()
    logger.info("API Gateway HTTP client closed.")

app = FastAPI(
    title="WarRemnantsVoice - API Gateway",
    description="Cổng giao tiếp tập trung (API Gateway) cho hệ thống Microservices Bảo tàng Chứng tích Chiến tranh",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def route_target(path: str) -> str:
    """Xác định service đích dựa theo đường dẫn URL"""
    if path.startswith("/output"):
        return STREAMING_SERVICE_URL
    
    if path.startswith("/api/v1/metrics") or path.startswith("/api/v1/admin/dashboard-stats"):
        return ANALYTICS_SERVICE_URL
    
    if path.startswith("/api/v1/process-audio") or path.startswith("/api/v1/languages") or path.startswith("/api/v1/tasks"):
        return AI_SERVICE_URL
        
    return EXHIBIT_SERVICE_URL

@app.get("/")
async def gateway_root():
    return {
        "service": "WarRemnantsVoice API Gateway",
        "status": "UP",
        "version": "1.0.0",
        "routes": {
            "exhibit_service": EXHIBIT_SERVICE_URL,
            "analytics_service": ANALYTICS_SERVICE_URL,
            "ai_pipeline_service": AI_SERVICE_URL,
            "streaming_service": STREAMING_SERVICE_URL,
        }
    }

@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    """Kiểm tra sức khỏe của API Gateway và toàn bộ các downstream microservices"""
    services_status = {}
    targets = {
        "exhibit_service": f"{EXHIBIT_SERVICE_URL}/health",
        "analytics_service": f"{ANALYTICS_SERVICE_URL}/health",
        "ai_pipeline_service": f"{AI_SERVICE_URL}/health",
        "streaming_service": f"{STREAMING_SERVICE_URL}/health",
    }
    
    for name, url in targets.items():
        try:
            res = await client.get(url, timeout=2.0)
            services_status[name] = "UP" if res.status_code == 200 else f"WARN ({res.status_code})"
        except Exception:
            services_status[name] = "DOWN"

    return {
        "gateway": "UP",
        "cluster_healthy": all(v == "UP" for v in services_status.values()),
        "services": services_status
    }

@app.get("/api/v1/admin/tunnel-url")
async def get_tunnel_url(request: Request):
    """Lấy tunnel URL hoặc host hiện tại cho QR Code"""
    host = request.headers.get("host", "localhost:8000")
    protocol = "https" if "trycloudflare.com" in host or request.headers.get("x-forwarded-proto") == "https" else "http"
    return {"tunnel_url": f"{protocol}://{host}"}

# Reverse Proxy Handler cho mọi HTTP Method
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def reverse_proxy(request: Request, path: str):
    target_base = route_target("/" + path)
    target_url = f"{target_base}/{path}"
    if request.url.query:
        target_url += f"?{request.url.query}"
        
    logger.info(f"Proxying: {request.method} /{path} -> {target_url}")
    
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None)
    
    body = await request.body()
    
    try:
        downstream_req = client.build_request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body
        )
        response = await client.send(downstream_req)
        
        excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        resp_headers = {
            k: v for k, v in response.headers.items() if k.lower() not in excluded_headers
        }
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=resp_headers,
            media_type=response.headers.get("content-type")
        )
    except httpx.ConnectError:
        logger.error(f"Cannot connect to downstream service at: {target_url}")
        return JSONResponse(
            status_code=503,
            content={
                "error": "Service Unavailable",
                "detail": f"Downstream service at {target_base} is offline or unreachable.",
                "target_url": target_url
            }
        )
    except Exception as e:
        logger.error(f"Proxy error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Gateway Error", "detail": str(e)}
        )
