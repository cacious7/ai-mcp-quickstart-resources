# Run this script to test different Hugging Face models
# Usage: 
#   .\run-model-tests.ps1 [ModelName]
# Examples:
#   .\run-model-tests.ps1
#   .\run-model-tests.ps1 mistralai/Mistral-7B-Instruct-v0.2
#   .\run-model-tests.ps1 microsoft/phi-2
#   .\run-model-tests.ps1 meta-llama/Llama-2-7b-chat-hf

param (
    [string]$ModelName
)

Write-Host "🧪 Testing Hugging Face Models for MCP Client..." -ForegroundColor Cyan

# Build the project first
Write-Host "📦 Building project..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed. Exiting." -ForegroundColor Red
    exit 1
}

if ($ModelName) {
    Write-Host "🔍 Testing specific model: $ModelName" -ForegroundColor Green
    npm run verify:model -- --model $ModelName
} else {
    # Test the default model from .env
    Write-Host "🔍 Testing default model from .env file" -ForegroundColor Green
    npm run verify:model
}

Write-Host "`n✅ Model test completed" -ForegroundColor Green
Write-Host "`n📝 To use this model with weather server, run:" -ForegroundColor Cyan

if ($ModelName) {
    Write-Host "   npm start -- ../weather-server-typescript/build/index.js --model $ModelName" -ForegroundColor White
} else {
    Write-Host "   npm start -- ../weather-server-typescript/build/index.js" -ForegroundColor White
}

Write-Host "`nRemember to set your HUGGINGFACE_API_KEY in the .env file!" -ForegroundColor Yellow
