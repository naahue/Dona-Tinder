@echo off
REM Entrada corta desde la raíz: reenvía a bin\dc.ps1 (ver README).
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0bin\dc.ps1" %*
