Remove-Item metrics.json -ErrorAction SilentlyContinue

# Create Log if needed
if (-not (Test-Path log.txt)) {
    Write-Host "`nLog file not found, generating..." -ForegroundColor Cyan
    cmd /c "python ingester.py > log.txt"
}

# $env:MAPPER_ENCODE = "True"

# $env:RUN_NAME = "4 mappers - mapper encode - sort reduce"
# Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
# cmd /c "python splitter.py -m 4 < log.txt"

$env:MAPPER_ENCODE = "False"

$env:RUN_NAME = "4 mappers - reducer encode - sort reduce"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
cmd /c "python splitter.py -m 4 < log.txt"

$env:RUN_NAME = "pyspark"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
python pyspark_mapreduce.py

# Clean up environment variable
Remove-Item Env:RUN_NAME
Remove-Item Env:MAPPER_ENCODE

Write-Host "`n===== Report =====" -ForegroundColor Cyan
python reporter.py