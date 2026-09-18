@echo off
title TRIPWIRE Launcher
echo ===================================================
echo   Starting TRIPWIRE Backend and Frontend Servers
echo ===================================================
echo.

cd /d "%~dp0"

echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "Tripwire Backend" cmd /k "cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting React Vite Frontend on http://127.0.0.1:5173 ...
start "Tripwire Frontend" cmd /k "cd frontend && npm run dev -- --host 127.0.0.1 --port 5173"

timeout /t 4 /nobreak >nul

echo.
echo Launching Tripwire in browser...
start http://127.0.0.1:5173

echo.
echo ===================================================
echo   TRIPWIRE is now running!
echo   Frontend: http://127.0.0.1:5173 (or http://localhost:5173)
echo   Backend:  http://127.0.0.1:8000/docs
echo.
echo   NOTE: Keep the two command prompt windows OPEN!
echo         Closing them stops the servers.
echo ===================================================
pause
