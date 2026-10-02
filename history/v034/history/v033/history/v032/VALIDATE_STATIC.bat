@echo off
setlocal
if "%~2"=="" goto usage
python -m unittest discover -s "%~dp0tools" -p "test_*.py" -v
if errorlevel 1 exit /b 1
python "%~dp0tools\validate_v032.py" --clean "%~1" --rom "%~2"
exit /b %errorlevel%
:usage
echo Uso: VALIDATE_STATIC.bat "ROM_limpia.wsc" "ROM_v032_TEST.wsc"
exit /b 2
