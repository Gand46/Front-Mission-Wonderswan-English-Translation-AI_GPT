@echo off
setlocal
if "%~1"=="" goto usage
if not "%~2"=="" goto custom
python "%~dp0tools\build_v032.py" "%~1" "%~dp0Front_Mission_WSC_English_v0.32_TEST.wsc"
exit /b %errorlevel%
:custom
python "%~dp0tools\build_v032.py" "%~1" "%~2"
exit /b %errorlevel%
:usage
echo Uso: APPLY_FROM_CLEAN.bat "ROM_limpia.wsc" ["salida.wsc"]
echo Requiere Python 3. No sobrescribe una salida existente.
exit /b 2
