Remove-Item metrics.json -ErrorAction SilentlyContinue

# Create Log if needed
if (-not (Test-Path log.txt)) {
    Write-Host "`nLog file not found, generating..." -ForegroundColor Cyan
    cmd /c "python ingester.py > log.txt"
}

$mapperCounts = 0, 1, 2, 4

function Build-Cmd( $n, $combiner, $sortReduce ) {
    if ( $n -eq 0 ) {
        $parts = @( "python mapper.py < log.txt" )
        if ( $combiner ) { $parts += "python sorter.py", "python combiner.py" }
        if ( $sortReduce ) { $parts += "python sorter.py", "python reducer.py" }
        else { $parts += "python reducer.py --dict" }
        return $parts -join " | "
    }

    $cmd = "python splitter.py -m $n"
    if ( -not $sortReduce ) { $cmd += " --dict" }
    if ( $combiner ) { $cmd += " --combiner"}
    return "$cmd < log.txt"
}

foreach ( $mapperEncode in $true, $false ) {
    $env:MAPPER_ENCODE = if ( $mapperEncode ) { "True" } else { "False" }
    $encodeLabel = if ( $mapperEncode ) { "map encode" } else { "reduce encode" }

    forech ( $combiner in $false, $true ) {
        $combinerLabel = if ( $combiner ) { "combine" } else { "no combine" }

        foreach ( $sortReduce ) {
            $reduceLabel = if ( $sortReduce ) { "sort reduce" } else { "dict reduce"}

            foreach ( $n in $mapperCounts ) {
                $mapperLabel = if ( $n -eq 0 ) { "single mapper" } else { "$n mapper" }

                $env:RUN_NAME "$mapperLabel - $combinerLabel - $encodeLabel - $reducerLabel"
                $cmd = Build-Cmd $n $combiner $sortReduce

                Write-Host "`n===== Running $env:RUN_NAME =====" -ForegroundColor Cyan
                Write-Host $cmd -ForegroundColor DarkGray
                cmd /c $cmd
            }
        }
    }
}

# Clean up environment variable
Remove-Item Env:RUN_NAME
Remove-Item Env:MAPPER_ENCODE

Write-Host "`n===== Report =====" -ForegroundColor Cyan
python reporter.py