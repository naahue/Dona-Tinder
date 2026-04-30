@echo off
REM Reset en Docker solo con Compose (mismo que vos a mano: down -v ; up -d).
setlocal
cd /d "%~dp0"
docker compose down -v
if errorlevel 1 exit /b %ERRORLEVEL%
docker compose up -d %*
exit /b %ERRORLEVEL%
