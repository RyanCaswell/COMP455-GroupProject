Remove-Item metrics.json -ErrorAction SilentlyContinue

# Check requirments
$output = pip install --dryrun -r requirements.txt 2>&1 | Out-String

if ( $output -match "Would install" ) {
    Write-Host "Missing packages. Please run 'pip install -r requirements.txt' and try again." -ForegroundColor Red
    Exit
}

# Create Log if needed
if (-not (Test-Path data\log.txt)) {
    Write-Host "`nLog file not found, generating..." -ForegroundColor Cyan
    cmd /c "python ingester.py > data\log.txt"
}

$mapperCounts = 0, 1, 2, 4

function Build-Cmd( $n, $combiner, $sortReduce, $joinSide ) {
    if ( $n -eq 0 ) {
        $parts = @( "python mapper.py --join $joinSide < data\log.txt" )
        if ( $combiner ) { $parts += "python sorter.py", "python combiner.py" }
        if ( $sortReduce ) { $parts += "python sorter.py", "python reducer.py --join $joinSide" }
        else { $parts += "python reducer.py --dict --join $joinSide" }
        
        return $parts -join " | "
    }

    $cmd = "python splitter.py -m $n"
    if ( -not $sortReduce ) { $cmd += " --dict" }
    if ( $combiner ) { $cmd += " --combiner"}
    $cmd += " --join $joinSide"

    return "$cmd < data\log.txt"
}

foreach ( $mapJoin in $true, $false ) {
    $joinLabel = if ( $mapJoin ) { "map" } else { "reduce" }

    foreach ( $combiner in $false, $true ) {
        $combinerLabel = if ( $combiner ) { "combine" } else { "no combine" }

        foreach ( $sortReduce in $false, $true ) {
            $reduceLabel = if ( $sortReduce ) { "sort reduce" } else { "dict reduce"}

            foreach ( $n in $mapperCounts ) {
                $mapperLabel = if ( $n -eq 0 ) { "single mapper" } else { "$n mapper" }

                $env:RUN_NAME = "$mapperLabel - $combinerLabel - $joinLabel join - $reduceLabel"
                $cmd = Build-Cmd $n $combiner $sortReduce $joinLabel

                Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
                Write-Host $cmd -ForegroundColor DarkGray
                cmd /c $cmd
            }
        }
    }
}

# Clean up environment variable
Remove-Item Env:RUN_NAME

Write-Host "`n===== Report =====" -ForegroundColor Cyan
python reporter.py