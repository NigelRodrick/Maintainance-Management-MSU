# Build MSU_Maintenance.exe with PyInstaller (Windows).
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "Installing build dependencies..."
pip install -q -r (Join-Path $Root 'packaging\requirements-exe.txt') pyinstaller

Write-Host "Running PyInstaller..."
pyinstaller (Join-Path $Root 'packaging\msu_maintenance.spec') --noconfirm
pyinstaller (Join-Path $Root 'packaging\msu_dependency_bootstrap.spec') --noconfirm

$exe = Join-Path $Root 'dist\MSU_Maintenance.exe'
if (Test-Path $exe) {
    Write-Host "OK: $exe"
} else {
    throw "Expected $exe"
}

$bootstrapExe = Join-Path $Root 'dist\MSU_Dependency_Bootstrapper.exe'
if (Test-Path $bootstrapExe) {
    Write-Host "OK: $bootstrapExe"
} else {
    throw "Expected $bootstrapExe"
}
