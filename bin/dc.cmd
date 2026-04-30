@echo off
REM Llama bin\dc.ps1 (Compose + limpieza tras down -v). Ver README en la raíz del repo.
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0dc.ps1" %*
