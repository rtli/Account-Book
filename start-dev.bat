@echo off
echo ====================================
echo   Account Book - Development Server
echo ====================================
echo.

REM Start backend
echo [1/2] Starting backend server (port 8000)...
start "Backend" cmd /c "cd /d %~dp0 && uv run uvicorn backend.main:app --reload --port 8000"

REM Wait for backend to be ready
timeout /t 3 /nobreak > nul

REM Start frontend
echo [2/2] Starting frontend dev server (port 5173)...
start "Frontend" cmd /c "cd /d %~dp0\frontend && npm run dev"

echo.
echo Both servers are starting...
echo   Backend:  http://127.0.0.1:8000/docs (API docs)
echo   Frontend: http://localhost:5173 (Web UI)
echo.
echo Close both terminal windows to stop the servers.
pause
