@echo off
setlocal
python "%~dp0tools\validate_native_evidence.py"
if errorlevel 1 exit /b %errorlevel%

if "%~1"=="" (
  echo Evidencia incluida validada. Para reconstruir y auditar:
  echo validate_windows.bat "ROM_original.bin" "salida_v035.wsc"
  exit /b 0
)
if "%~2"=="" (
  echo Falta la ruta de salida.
  exit /b 2
)
if exist "%~2" (
  echo La salida ya existe: %~2
  exit /b 2
)
python "%~dp0tools\build_v035.py" "%~1" "%~2"
if errorlevel 1 exit /b %errorlevel%
python "%~dp0tools\audit_v035.py" "%~1" "%~2"
exit /b %errorlevel%
