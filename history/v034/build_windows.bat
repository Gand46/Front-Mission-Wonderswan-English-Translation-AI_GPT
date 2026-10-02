@echo off
setlocal
if "%~2"=="" (
 echo Uso: build_windows.bat "ROM_original.bin" "Front_Mission_v034_TEST.wsc"
 exit /b 2
)
py -3 "%~dp0tools\build_v034.py" "%~1" "%~2"
exit /b %errorlevel%
