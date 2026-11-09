"""
test_api_endpoints.py — Integration Tests cho FastAPI Endpoints của AI Pipeline
Thành viên 2: AI & Pipeline Processing Services
"""

import pytest
from fastapi.testclient import TestClient
from main_fastapi import app

@pytest.fixture(scope="module")
def client():
    """Sử dụng context manager để kích hoạt FastAPI lifespan (khởi tạo DB & seed)"""
    with TestClient(app) as test_client:
        yield test_client

def test_health_check_endpoint(client):
    """Kiểm tra healthcheck endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data

def test_supported_languages_endpoint(client):
    """Kiểm tra lấy danh mục 15 ngôn ngữ từ database"""
    response = client.get("/api/v1/languages")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 15
    codes = [l["code"] for l in data]
    assert "vi" in codes
    assert "en" in codes
    assert "fr" in codes

def test_glossary_endpoint(client):
    """Kiểm tra lấy từ điển thuật ngữ lịch sử"""
    response = client.get("/api/v1/glossary")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 7

def test_nlp_normalize_endpoint(client):
    """Kiểm tra API chuẩn hóa văn bản NLP"""
    payload = {"text": "   chuẩn   hóa   câu   từ,ngữ pháp.  "}
    response = client.post("/api/v1/ai/nlp/normalize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["normalized_text"] == "Chuẩn hóa câu từ, ngữ pháp."

def test_pipeline_jobs_api(client):
    """Kiểm tra tạo job và kiểm tra trạng thái job qua API"""
    payload = {
        "exhibit_id": "test-ex-001",
        "exhibit_code": "M107-175",
        "target_languages": ["en", "fr"],
        "priority": 2
    }
    create_res = client.post("/api/v1/pipeline/jobs", json=payload)
    assert create_res.status_code == 200
    create_data = create_res.json()
    assert create_data["status"] == "queued"
    job_id = create_data["job"]["id"]

    # Tra cứu lại job
    get_res = client.get(f"/api/v1/pipeline/jobs/{job_id}")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["exhibit_code"] == "M107-175"
    assert get_data["status"] == "pending"
