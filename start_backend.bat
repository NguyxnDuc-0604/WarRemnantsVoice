@echo off
chcp 65001 >nul
title [WarRemnantsVoice] - Backend FastAPI (Port 8000)
echo ==========================================================
echo  🎖️ KHOI DONG BACKEND AI PIPELINE SERVICE (PORT 8000)
echo ==========================================================
cd /d "%~dp0services\ai-pipeline-service"

if not exist "venv" (
    echo [INFO] Tao moi truong ao Python venv...
    python -m venv venv || py -3 -m venv venv
)

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo [INFO] Kiem tra va cai dat thu vien Python...
pip install -r requirements.txt

echo.
echo [INFO] Dang chay FastAPI Server tai http://0.0.0.0:8000
echo ==========================================================
uvicorn main_fastapi:app --host 0.0.0.0 --port 8000 --reload
pause
