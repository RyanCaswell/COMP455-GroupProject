Remove-Item metrics.json -ErrorAction SilentlyContinue

# Create Log if needed
if (-not (Test-Path log.jsonl)) {
    Write-Host "`nLog file not found, generating..." -ForegroundColor Cyan
    cmd /c "python ingester.py > log.jsonl"
}

$env:MAPPER_ENCODE = "True"

$env:RUN_NAME = "4 mappers - mapper encode - sort reduce"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
cmd /c "python splitter.py -m 4 --combiner < log.jsonl"

# Clean up environment variable
Remove-Item Env:RUN_NAME
Remove-Item Env:MAPPER_ENCODE

Write-Host "`n===== Report =====" -ForegroundColor Cyan
python reporter.py