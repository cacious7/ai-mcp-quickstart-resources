# Run model comparison tests for different models
# This script tests multiple models and logs their performance

# Models to test
$models = @(
    "mistral-small3.1",
    "phi4-mini",
    "dolphin3"
)

# Create the results directory if it doesn't exist
$resultsDir = "test-results"
if (-not (Test-Path $resultsDir)) {
    New-Item -ItemType Directory -Path $resultsDir
}

# Create/clear the CSV headers file
$csvPath = Join-Path $resultsDir "model-tests.csv"
"timestamp,model,response_time_ms,status,error" | Out-File -FilePath $csvPath

Write-Host "Starting model comparison tests..."
Write-Host "===============================`n"

foreach ($model in $models) {
    Write-Host "Testing model: $model"
    Write-Host "-----------------------------"
    
    # Check if model is available in Ollama
    $modelExists = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" | 
                  Select-Object -ExpandProperty Content | 
                  ConvertFrom-Json | 
                  Select-Object -ExpandProperty models | 
                  Where-Object { $_.name -eq $model }
    
    if (-not $modelExists) {
        Write-Host "Model $model is not installed. Pulling from Ollama repository..."
        Invoke-WebRequest -Uri "http://localhost:11434/api/pull" -Method POST -Body "{`"name`":`"$model`"}" -ContentType "application/json"
    }
    
    # Update the .env file to use this model
    $envContent = Get-Content -Path ".env" -Raw
    $newEnvContent = $envContent -replace "OLLAMA_MODEL=.*", "OLLAMA_MODEL=$model"
    $newEnvContent | Out-File -FilePath ".env" -NoNewline
    
    # Build and run the test
    npm run build
    
    # Run the test
    Write-Host "Running test with $model..."
    node build/model-test.js
    
    Write-Host "`n-----------------------------`n"
}

Write-Host "Tests completed! See $csvPath for results"
Write-Host "===============================`n"

# Provide a simple summary
$results = Import-Csv -Path $csvPath
Write-Host "SUMMARY:"
foreach ($model in ($results | Select-Object -ExpandProperty model -Unique)) {
    $modelResults = $results | Where-Object { $_.model -eq $model }
    $avgTime = ($modelResults | Measure-Object -Property response_time_ms -Average).Average
    $success = ($modelResults | Where-Object { $_.status -eq "SUCCESS" }).Count
    $total = $modelResults.Count
    
    Write-Host "$model - Avg response time: $([math]::Round($avgTime,2))ms, Success rate: $success/$total"
}
