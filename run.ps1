Remove-Item metrics.json -ErrorAction SilentlyContinue

$env:RUN_NAME = "single mapper"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
cmd /c "python ingester.py | python mapper.py | python sorter.py | python reducer.py"

$env:RUN_NAME = "pyspark"
Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
python pyspark_mapreduce.py

# Clean up environment variable
Remove-Item Env:RUN_NAME

Write-Host "`n===== Report =====" -ForegroundColor Cyan
python reporter.py