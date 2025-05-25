@echo off
echo Setting up Hugging Face MCP Client...
echo.

:: Build if needed
if not exist build\setup-models.js (
  echo Building project first...
  call npm run build
  if %ERRORLEVEL% NEQ 0 (
    echo Build failed. Please check for errors and try again.
    pause
    exit /b 1
  )
)

:: Run setup
node build\setup-models.js

pause
