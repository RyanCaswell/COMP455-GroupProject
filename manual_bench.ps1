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

$runList = @()

foreach ( $runLabel in "Run 1", "Run 2"  ) {
    $n = -1
    $mapJoin = -1
    $combiner = -1
    $sortReduce = -1

    Write-Host " --==+==-- Select options for $runLabel --==+==--" -ForegroundColor Cyan

    while ( $n -lt 1 -or $n -gt 8 ) {
        $n = [int]( Read-Host -Prompt "How man mappers would you like to run ( 1 to 8 )? " )
    }

    while ( $mapJoin -lt 1 -or $mapJoin -gt 2 ) {
        $mapJoin = [int]( Read-Host -Prompt "How do you want to join the data?`n    1 = Map Side`n    2 = Reduce side`n" )
    }

    while ( $combiner -lt 1 -or $combiner -gt 2 ) {
        $combiner = [int]( Read-Host -Prompt "Do you want to use a combiner?`n    1 = Yes`n    2 = No`n" )
    }

    while ( $sortReduce -lt 1 -or $sortReduce -gt 2 ) {
        $sortReduce = [int]( Read-Host -Prompt "What kind of reducer?`n    1 = Sorted`n    2 = Dictionary`n" )
    }

    $runList += [PSCustomObject]@{
        Mappers = $n
        mapJoin = ( $mapJoin -eq 1 )
        combiner = ( $combiner -eq 1 )
        sortReduce = ( $sortReduce -eq 1 )
    }
}

foreach ( $run in $runList ) {
    # Set Labels
    $mapperLabel = "$($run.Mappers) mapper"
    $joinLabel = if ( $run.mapJoin ) { "map" } else { "reduce" }
    $combinerLabel = if ( $run.combiner ) { "combine" } else { "no combine" }
    $reduceLabel = if ( $rin.sortReduce ) { "sort reduce" } else { "dict reduce"}

    # Build and run
    $env:RUN_NAME = "$runLabel - $mapperLabel - $combinerLabel - $joinLabel side - $reduceLabel"
    $cmd = Build-Cmd $run.Mappers $run.combiner $run.sortReduce $joinLabel

    Write-Host "`n===== $env:RUN_NAME =====" -ForegroundColor Cyan
    Write-Host $cmd -ForegroundColor DarkGray
    cmd /c $cmd
}

# Clean up environment variable
Remove-Item Env:RUN_NAME

Write-Host "`n===== Report =====" -ForegroundColor Cyan
python reporter.py