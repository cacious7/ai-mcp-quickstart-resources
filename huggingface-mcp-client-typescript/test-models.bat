@echo off
echo Testing Hugging Face models...
echo.

:: Check for args
if "%~1"=="" (
  echo Using default model from .env file
  powershell -ExecutionPolicy Bypass -File run-model-tests.ps1
) else (
  echo Testing model: %1
  powershell -ExecutionPolicy Bypass -File run-model-tests.ps1 %1
)

pause
