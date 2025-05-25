@echo off
echo MCP Client Test with Memory Optimizations
echo =======================================

cd "C:\Users\csiam\Documents\Local AI Interests\ai-mcp-quickstart-resources\open-model-mcp-client-typescript"

echo Building the project...
call npm run build
if %ERRORLEVEL% NEQ 0 (
  echo Build failed!
  pause
  exit /b %ERRORLEVEL%
)

echo.
echo Running MCP client with the weather server...

rem Set memory optimization environment variables
set OLLAMA_GPU_LAYERS=0
set OLLAMA_NUM_GPU=0
set OLLAMA_KEEP_ALIVE=0

node build/index.js "../weather-server-typescript/build/index.js"
