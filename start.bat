@echo off
cd /d "%~dp0"

REM Start backend in a separate window
start "Backend" cmd /k "cd /d "%~dp0" && python start_backend.py"

REM Start frontend in a separate window
start "Frontend" cmd /k "cd /d "%~dp0\frontend" && npm run dev"

REM Optional: keep the command window open briefly so the user can see the launcher output
ping 127.0.0.1 -n 2 > nul
