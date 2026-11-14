@echo off
chcp 65001 >nul
title [WarRemnantsVoice] - Backend FastAPI (Port 8000)
echo ==========================================================
echo  🎖️ KHOI DONG BACKEND AI PIPELINE SERVICE (PORT 8000)
echo ==========================================================
cd /d "%~dp0services\ai-pipeline-service"

set "PY_CMD=python"

if exist "C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe" (
    set "PY_CMD=C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe"
    goto :run_server
)

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=python"
    goto :run_server
)

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=py -3"
    goto :run_server
)

:run_server
echo [INFO] Su dung Python tai: %PY_CMD%
echo [INFO] Dang khoi dong FastAPI tai http://0.0.0.0:8000 ...
echo ==========================================================
"%PY_CMD%" -m uvicorn main_fastapi:app --host 0.0.0.0 --port 8000 --reload
pause
