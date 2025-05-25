@echo off
echo Running Hugging Face MCP Client with Weather Server...
echo.

:: Check if build directory exists
if not exist build\index.js (
  echo Building project first...
  call npm run build
  if %ERRORLEVEL% NEQ 0 (
    echo Build failed. Please check for errors and try again.
    pause
    exit /b 1
  )
)

:: Check for args
if "%~1"=="" (
  echo No weather server path provided. Using default...
  echo.
  node build\index.js ..\weather-server-typescript\build\index.js
) else (
  node build\index.js %*
)

pause
