Remove-Item metrics.json -ErrorAction SilentlyContinue

# Create Log if needed
if (-not (Test-Path log.jsonl)) {
    Write-Host "`nLog file not found, generating..." -ForegroundColor Cyan
    cmd /c "python ingester.py > log.jsonl"
}

$env:RUN_NAME = "single mapper"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
cmd /c "python mapper.py < log.jsonl | python sorter.py | python reducer.py"

$env:RUN_NAME = "pyspark"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
python pyspark_mapreduce.py

# Clean up environment variable
Remove-Item Env:RUN_NAME

Write-Host "`n===== Report =====" -ForegroundColor Cyan
python reporter.py