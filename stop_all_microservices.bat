@echo off
chcp 65001 >nul
title [WarRemnantsVoice] - Dung He Thong Microservices
echo =========================================================================
echo  🛑 DANG DUNG CAC DICH VU MICROSERVICES (Port 8000, 8001, 8002, 8003, 8004, 5173)...
echo =========================================================================

for %%P in (8000 8001 8002 8003 8004 5173) do (
    echo [INFO] Kiem tra va giai phong Port %%P...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%%P" ^| findstr "LISTENING"') do (
        echo [-] Dung tien trinh PID %%a tren Port %%P...
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo.
echo =========================================================================
echo  ✅ DA DUNG TOAN BO CAC TIEN TRINH MICROSERVICES!
echo =========================================================================
pause
