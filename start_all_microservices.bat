@echo off
chcp 65001 >nul
title [WarRemnantsVoice] - Khoi Dong He Thong Microservices
echo =========================================================================
echo  🎖️ KHOI DONG TOAN BO HE THONG MICROSERVICES (WarRemnantsVoice)
echo =========================================================================
echo.

set "ROOT_DIR=%~dp0"
set "PY_CMD=python"

if exist "C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe" (
    set "PY_CMD=C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe"
    goto :find_py_done
)

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=python"
    goto :find_py_done
)

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=py -3"
    goto :find_py_done
)

:find_py_done
echo [INFO] Python su dung: %PY_CMD%
echo [INFO] Dang khoi dong 5 Backend Microservices + Frontend React...
echo.

:: 1. Khoi dong Exhibit Service (Port 8001)
echo [1/6] Khoi dong Exhibit Service tai Port 8001...
start "🏛️ [Port 8001] Exhibit Core Service" cmd /k "cd /d "%ROOT_DIR%services\exhibit-service" && "%PY_CMD%" -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 2 /nobreak >nul

:: 2. Khoi dong Analytics Service (Port 8002)
echo [2/6] Khoi dong Analytics Service tai Port 8002...
start "📊 [Port 8002] Analytics & Monitoring Service" cmd /k "cd /d "%ROOT_DIR%services\analytics-service" && "%PY_CMD%" -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload"
timeout /t 2 /nobreak >nul

:: 3. Khoi dong AI Pipeline Service (Port 8003)
echo [3/6] Khoi dong AI Pipeline Service tai Port 8003...
start "🤖 [Port 8003] AI Pipeline Service" cmd /k "cd /d "%ROOT_DIR%services\ai-pipeline-service" && "%PY_CMD%" -m uvicorn app.main_service:app --host 0.0.0.0 --port 8003 --reload"
timeout /t 2 /nobreak >nul

:: 4. Khoi dong Media & Streaming Service (Port 8004)
echo [4/6] Khoi dong Media Streaming Service tai Port 8004...
start "🎵 [Port 8004] Media & Streaming Service" cmd /k "cd /d "%ROOT_DIR%services\streaming-service" && "%PY_CMD%" -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload"
timeout /t 2 /nobreak >nul

:: 5. Khoi dong API Gateway (Port 8000)
echo [5/6] Khoi dong API Gateway tai Port 8000...
start "🌐 [Port 8000] API Gateway Service" cmd /k "cd /d "%ROOT_DIR%services\gateway-service" && "%PY_CMD%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 2 /nobreak >nul

:: 6. Khoi dong Frontend React (Port 5173)
echo [6/6] Khoi dong Frontend React tai Port 5173...
start "⚛️ [Port 5173] Frontend React Vite" cmd /k "cd /d "%ROOT_DIR%services\frontend" && npm run dev"

echo.
echo =========================================================================
echo  ✅ TOAN BO HE THONG MICROSERVICES DA DUOC KHOI DONG THANH CONG!
echo =========================================================================
echo  - API Gateway:    http://localhost:8000
echo  - Health Check:   http://localhost:8000/health
echo  - Exhibit Svc:    http://localhost:8001
echo  - Analytics Svc:  http://localhost:8002
echo  - AI Pipeline:    http://localhost:8003
echo  - Streaming Svc:  http://localhost:8004
echo  - Frontend Web:   http://localhost:5173
echo.
echo  Dong cua so nay khong tat cac service. De tat tat ca, hay chay stop_all_microservices.bat.
echo =========================================================================
pause
