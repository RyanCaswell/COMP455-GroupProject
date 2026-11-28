$env:MAPPER_ENCODE = "True"
$env:RUN_NAME = "hadoop"

Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan

function convertPath( $windowsPath ) {
    $full = [System.IO.Path]::GetFullPath( $windowsPath )
    $drive = $full.Substring( 0, 1 ).ToLower()
    $rest = $full.Substring( 2 ) -replace '\\', '/'
    return "/mnt/$drive$rest"
}

$projectRoot = (Get-Location).Path
$wslHadoopDir = convertPath (Join-Path $projectRoot "hadoopwsl")
$wslMetrics = convertPath (Join-Path $projectRoot "metrics.json")

# temporary shell to run the Hadoop commands in WSL
$shWindows = Join-Path $env:TEMP "comp455-hadoop-test.sh"
$shWsl = convertPath $shWindows

# Commands executed inside WSL
# pipeline fails if any command fails in the pipeline and is needed so be dont hang
#this assumes that everything is installed correctly and that the hadoop job will run successfully
$bash = @"
set -euo pipefail


export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export HADOOP_HOME="\`$HOME/hadoop"
export PATH="\`$PATH:\`$HADOOP_HOME/bin:\`$HADOOP_HOME/sbin"


cd "$wslHadoopDir"

# Remove output from previous runs hadoop will fail if output directory is not empty
rm -rf /tmp/hadoop-out /tmp/hadoop-metrics.json


"\`$HOME/comp455-venv/bin/python" ingester.py > /tmp/trips.csv

# Run the Hadoop job and record
/usr/bin/time -f "elapsed_seconds %e" -o /tmp/hadoop-time.txt \\
  hadoop jar "\`$HOME/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.5.0.jar" \\
    -files mapper.py,reducer.py,tracker.py \\
    -mapper "/usr/bin/python3 mapper.py" \\
    -reducer "/usr/bin/python3 reducer.py" \\
    -cmdenv MAPPER_ENCODE=True \\
    -cmdenv RUN_NAME=hadoop \\
    -cmdenv METRICS_PATH=/tmp/hadoop-metrics.json \\
    -input /tmp/trips.csv \\
    -output /tmp/hadoop-out \\
  > /tmp/hadoop-console.txt 2>&1


cat /tmp/hadoop-out/part-*
echo
cat /tmp/hadoop-time.txt


cat /tmp/hadoop-metrics.json >> "$wslMetrics"
"@

# Remove Windows line endings
$bash = $bash -replace "\`r\`n", "\`n"


$utf8 = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText( $shWindows, $bash, $utf8 )

# try to execute the script inside WSL 
$hadoopSuccessfull = $false

try {
    wsl bash "$shWsl"

    if ( $LASTEXITCODE -eq 0 ) {
        $hadoopSuccessfull = $true
    }
} catch {
    $hadoopSuccessfull = $false
} finally {
    
    Remove-Item $shWindows -ErrorAction SilentlyContinue
}

# Display an error if the Hadoop job fails
if ( -not $hadoopSuccessfull ) {
    Write-Host "Failed to run hadoop test, ensure WSL 2.0 and dependancys are installed following instructions in hadoopwsl/setup.txt"
}