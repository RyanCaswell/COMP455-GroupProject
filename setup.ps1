# Create venv if needed
if ( -not ( Test-Path ".venv" ) ) {
    Write-Host "Creating .venv..." -ForegroundColor Cyan
    python -m venv .venv
}

# Activate venv if needed
if ( -not $env:VIRTUAL_ENV ) {
    Write-Host "Activating virtual enviroment..." -ForegroundColor Cyan
    . .\.venv\Scripts\Activate.ps1
}

# Activate venv if needed
if ( -not $env:VIRTUAL_ENV ) {
    Write-Host "Unable to launch virtual enviroment." -ForegroundColor Red
    Break
}

# Install requirements if new


# Check requirments
$output = pip install --dryrun -r requirements.txt 2>&1 | Out-String

if ( $output -match "Would install" ) {
    Write-Host "Installing missing packages..." -ForegroundColor Cyan
    pip install -r requirements
} else {
    Write-Host "Packages already found." -ForegroundColor Green
}

Write-Host "Setup complete!" -ForegroundColor Green