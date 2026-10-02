@echo off
if "%~2"=="" (
  echo Uso: build_windows.bat "ROM_original_o_v034.wsc" "Front_Mission_v035_TEST.wsc"
  exit /b 2
)
python "%~dp0tools\build_v035.py" "%~1" "%~2"
exit /b %errorlevel%
