# Build MSU_Maintenance_System_<version>.msi using WiX Toolset v3.x (Heat + Candle + Light).
# Prerequisite: install WiX v3.11+ from https://wixtoolset.org/docs/wix3/ (sets %WIX% to e.g. C:\Program Files (x86)\WiX Toolset v3.14\)
param(
    [string] $Version = "1.0.0"
)

$ErrorActionPreference = 'Stop'
$InstallerRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $InstallerRoot
$SourceApp = Join-Path $RepoRoot 'msu_maintenance_system'
$StageRoot = Join-Path $InstallerRoot '_stage'
$WixDir = Join-Path $InstallerRoot 'wix'
$OutDir = Join-Path $InstallerRoot 'dist'
$HeatOut = Join-Path $WixDir 'HarvestedFiles.wxs'
$ObjDir = Join-Path $WixDir 'obj'
Remove-Item $ObjDir -Recurse -Force -ErrorAction SilentlyContinue

if (-not (Test-Path $SourceApp)) {
    throw "Application folder not found: $SourceApp"
}

$wix = $env:WIX
if (-not $wix) {
    $candidates = @(
        "${env:ProgramFiles(x86)}\WiX Toolset v3.14",
        "${env:ProgramFiles(x86)}\WiX Toolset v3.11",
        "$env:ProgramFiles\WiX Toolset v3.14"
    )
    foreach ($c in $candidates) {
        if (Test-Path (Join-Path $c 'bin\heat.exe')) { $wix = $c; break }
    }
}
if (-not $wix -or -not (Test-Path (Join-Path $wix 'bin\heat.exe'))) {
    throw "WiX Toolset v3 not found. Install from https://wixtoolset.org/docs/wix3/ and ensure `%WIX%` points to the install folder, or install under Program Files (x86)\WiX Toolset v3.14"
}

$heat = Join-Path $wix 'bin\heat.exe'
$candle = Join-Path $wix 'bin\candle.exe'
$light = Join-Path $wix 'bin\light.exe'

Write-Host "Staging application files..."
Remove-Item $StageRoot -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $StageRoot -Force | Out-Null

# Mirror app tree into _stage so Heat roots files under INSTALLFOLDER (Program Files\...\run_app.bat).
$robolog = Join-Path $env:TEMP 'msu_robocopy.log'
robocopy $SourceApp $StageRoot /MIR `
    /XD .venv __pycache__ .git .pytest_cache htmlcov instance `
    /XF *.pyc *.db /NFL /NDL /NJH /NJS /nc /ns /np /LOG:$robolog | Out-Null
$rc = $LASTEXITCODE
if ($rc -ge 8) {
    throw "robocopy failed with exit code $rc (see $robolog)"
}

Write-Host "Running Heat on staged tree..."
# -srd: do not create a directory row for _stage; put app files directly under INSTALLFOLDER.
& $heat dir $StageRoot `
    -cg HarvestedApp `
    -dr INSTALLFOLDER `
    -gg `
    -sfrag `
    -srd `
    -scom `
    -sreg `
    -ke `
    -var var.HarvestSource `
    -out $HeatOut
if ($LASTEXITCODE -ne 0) { throw "heat.exe failed" }

$parts = $Version.Split('.')
while ($parts.Length -lt 4) { $parts += '0' }
$wixVersion = "$($parts[0]).$($parts[1]).$($parts[2]).$($parts[3])"

New-Item -ItemType Directory -Path $ObjDir -Force | Out-Null
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

$productWxs = Join-Path $WixDir 'Product.wxs'
$msiOut = Join-Path $OutDir "MSU_Maintenance_System_$Version.msi"

Write-Host "Compiling ($wixVersion)..."
Push-Location $ObjDir
try {
    & $candle -nologo `
        -dProductVersion=$wixVersion `
        -dHarvestSource=$StageRoot `
        -arch x64 `
        $productWxs `
        $HeatOut
    if ($LASTEXITCODE -ne 0) { throw "candle.exe failed" }
} finally {
    Pop-Location
}

$productObj = Join-Path $ObjDir 'Product.wixobj'
$harvestObj = Join-Path $ObjDir 'HarvestedFiles.wixobj'
if (-not (Test-Path $harvestObj)) {
    throw "Expected $harvestObj — check Heat output file name."
}

Write-Host "Linking MSI..."
& $light -nologo `
    -out $msiOut `
    -ext "$wix\bin\WixUIExtension.dll" `
    -cultures:en-us `
    $productObj `
    $harvestObj
if ($LASTEXITCODE -ne 0) { throw "light.exe failed" }

Write-Host ""
Write-Host "Built: $msiOut"
Write-Host "Install requires: Python 3.10+ (64-bit) on the target PC. First launch creates venv under %LOCALAPPDATA%\MSUMaintenance."
