@echo off
chcp 65001 >nul
title [WarRemnantsVoice] - Cloudflare Public Tunnel

cd /d "%~dp0"

if exist "start_tunnel.ps1" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_tunnel.ps1"
    goto :end
)

if exist "cloudflared.exe" (
    echo ====================================================================
    echo  🚀 DANG KHOI TAO CLOUDFLARE TUNNEL...
    echo  * Chu y: Cuon len phia tren de tim dong link https://xxx.trycloudflare.com
    echo ====================================================================
    .\cloudflared.exe tunnel --url http://localhost:5173
    goto :end
)

echo [LOI] Khong tim thay cloudflared.exe!
pause

:end
pause
