# MSU Maintenance System — create venv, install deps, run (SQLite dev by default)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

# Per-user venv + SQLite when installed under Program Files (MSI): not writable by normal users.
if ($Root -match '(?i)[\\/]Program Files[\\/]') {
    $dataRoot = Join-Path $env:LOCALAPPDATA 'MSUMaintenance'
    New-Item -ItemType Directory -Force -Path $dataRoot | Out-Null
    $env:MSU_INSTANCE_DIR = Join-Path $dataRoot 'instance'
    New-Item -ItemType Directory -Force -Path $env:MSU_INSTANCE_DIR | Out-Null
    $env:MSU_REPORTS_DIR = Join-Path $dataRoot 'reports'
    New-Item -ItemType Directory -Force -Path $env:MSU_REPORTS_DIR | Out-Null
    $venvDir = Join-Path $dataRoot 'venv'
} else {
    $venvDir = Join-Path $Root '.venv'
}

function Get-PythonExecutable {
    $skip = [regex]::Escape('WindowsApps')
    foreach ($name in @('python', 'python3')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd -and $cmd.Source -notmatch $skip) {
            try {
                $out = & $name -c "import sys; print(sys.executable)" 2>$null
                if ($LASTEXITCODE -eq 0 -and $out) { return $name.Trim() }
            } catch { }
        }
    }
    foreach ($path in @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "${env:ProgramFiles}\Python312\python.exe",
        "${env:ProgramFiles}\Python311\python.exe",
        "${env:ProgramFiles}\Python310\python.exe"
    )) {
        if (Test-Path $path) { return $path }
    }
    return $null
}

$py = Get-PythonExecutable
if (-not $py) {
    Write-Host "Python was not found. Install Python 3.10+ from https://www.python.org/downloads/"
    Write-Host "Or run: winget install Python.Python.3.12 --accept-package-agreements"
    exit 1
}

Write-Host "Using: $py"
if (-not (Test-Path $venvDir)) {
    Write-Host "Creating virtual environment..."
    & $py -m venv $venvDir
}

$pip = Join-Path $venvDir 'Scripts\pip.exe'
$python = Join-Path $venvDir 'Scripts\python.exe'
if (-not (Test-Path $python)) {
    Write-Host "Virtual environment is broken; re-run after deleting the .venv folder."
    exit 1
}

Write-Host "Installing dependencies (first run may take a few minutes) ..."
& $pip install --upgrade pip -q
& $pip install -r (Join-Path $Root 'requirements.txt')
if ($LASTEXITCODE -ne 0) {
    Write-Host "pip install failed."
    exit 1
}

$env:FLASK_ENV = 'development'
if (-not $env:USE_SQLITE) { $env:USE_SQLITE = '1' }

Write-Host "Starting server at http://127.0.0.1:5000  (Ctrl+C to stop)"
Write-Host "Demo users: demo@staff.msu.ac.zw and admin@staff.msu.ac.zw — password from MSU_DEMO_PASSWORD or default in .env.example"
& $python (Join-Path $Root 'run.py')
