Remove-Item metrics.json -ErrorAction SilentlyContinue

# Create Log if needed
if (-not (Test-Path log.jsonl)) {
    Write-Host "`nLog file not found, generating..." -ForegroundColor Cyan
    cmd /c "python ingester.py > log.jsonl"
}

$env:MAPPER_ENCODE = "True"

$env:RUN_NAME = "single mapper - mapper encode - sort reducer"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
cmd /c "python mapper.py < log.jsonl | python sorter.py | python reducer.py"

$env:RUN_NAME = "single mapper - mapper encode encode - dict reducer"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
cmd /c "python mapper.py < log.jsonl | python reducerDict.py"

$env:RUN_NAME = "1 mappers - mapper encode - sort reduce"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
cmd /c "python splitter.py -m 1 < log.jsonl"

$env:RUN_NAME = "2 mappers - mapper encode - sort reduce"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
cmd /c "python splitter.py -m 2 < log.jsonl"

$env:RUN_NAME = "4 mappers - mapper encode - sort reduce"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
cmd /c "python splitter.py -m 4 < log.jsonl"


$env:MAPPER_ENCODE = "True"

$env:RUN_NAME = "single mapper - reducer encode - sort reducer"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
cmd /c "python mapper.py < log.jsonl | python sorter.py | python reducer.py"

$env:RUN_NAME = "single mapper - reducer encode encode - dict reducer"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
cmd /c "python mapper.py < log.jsonl | python reducerDict.py"

$env:RUN_NAME = "1 mappers - reducer encode - sort reduce"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
cmd /c "python splitter.py -m 1 < log.jsonl"

$env:RUN_NAME = "2 mappers - reducer encode - sort reduce"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
cmd /c "python splitter.py -m 2 < log.jsonl"

$env:RUN_NAME = "4 mappers - reducer encode - sort reduce"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
cmd /c "python splitter.py -m 4 < log.jsonl"

$env:RUN_NAME = "4 mappers - reducer encode - dict reduce"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
cmd /c "python splitter.py -m 4 --dict < log.jsonl"

$env:RUN_NAME = "pyspark"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
python pyspark_mapreduce.py

# Clean up environment variable
Remove-Item Env:RUN_NAME
Remove-Item Env:MAPPER_ENCODE

Write-Host "`n===== Report =====" -ForegroundColor Cyan
python reporter.py