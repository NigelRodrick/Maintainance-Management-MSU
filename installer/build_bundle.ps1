# Build a Burn bootstrapper EXE: Python 3.12 x64 (if missing) + MSU Maintenance MSI.
# Requires WiX Toolset v3 with Bal and Util extensions (same as build_msi.ps1).
param(
    [string] $Version = "1.0.0",
    [string] $PythonVersion = "3.12.8"
)

$ErrorActionPreference = 'Stop'
$InstallerRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $InstallerRoot
$CacheDir = Join-Path $InstallerRoot 'cache'
$BundleDir = Join-Path $InstallerRoot 'bundle'
$DistDir = Join-Path $InstallerRoot 'dist'
$PythonExeName = "python-$PythonVersion-amd64.exe"
$PythonInstallerPath = Join-Path $CacheDir $PythonExeName
$PythonUrl = "https://www.python.org/ftp/python/$PythonVersion/$PythonExeName"

$wix = $env:WIX
if (-not $wix) {
    $candidates = @(
        "${env:ProgramFiles(x86)}\WiX Toolset v3.14",
        "${env:ProgramFiles(x86)}\WiX Toolset v3.11",
        "$env:ProgramFiles\WiX Toolset v3.14"
    )
    foreach ($c in $candidates) {
        if (Test-Path (Join-Path $c 'bin\candle.exe')) { $wix = $c; break }
    }
}
if (-not $wix) {
    throw "WiX Toolset v3 not found. Install from https://wixtoolset.org/docs/wix3/"
}

$candle = Join-Path $wix 'bin\candle.exe'
$light = Join-Path $wix 'bin\light.exe'

New-Item -ItemType Directory -Path $CacheDir -Force | Out-Null
New-Item -ItemType Directory -Path $DistDir -Force | Out-Null

if (-not (Test-Path $PythonInstallerPath)) {
    Write-Host "Downloading Python $PythonVersion installer..."
    Invoke-WebRequest -Uri $PythonUrl -OutFile $PythonInstallerPath -UseBasicParsing
}

Write-Host "Building MSI..."
& (Join-Path $InstallerRoot 'build_msi.ps1') -Version $Version

$msiName = "MSU_Maintenance_System_$Version.msi"
$msiPath = Join-Path $DistDir $msiName
if (-not (Test-Path $msiPath)) {
    throw "MSI not found: $msiPath"
}

$parts = $Version.Split('.')
while ($parts.Length -lt 4) { $parts += '0' }
$bundleWixVersion = "$($parts[0]).$($parts[1]).$($parts[2]).$($parts[3])"

$pythonAbs = (Resolve-Path $PythonInstallerPath).Path
$msiAbs = (Resolve-Path $msiPath).Path

$bundleObj = Join-Path $BundleDir 'Bundle.wixobj'
$exeOut = Join-Path $DistDir "MSU_Maintenance_System_Setup_$Version.exe"

Remove-Item $bundleObj -Force -ErrorAction SilentlyContinue

Write-Host "Compiling bundle (Burn)..."
Push-Location $BundleDir
try {
    & $candle -nologo `
        -ext "$wix\bin\WixUtilExtension.dll" `
        -ext "$wix\bin\WixBalExtension.dll" `
        "-dBundleVersion=$bundleWixVersion" `
        "-dPythonInstallerPath=$pythonAbs" `
        "-dMsiPath=$msiAbs" `
        Bundle.wxs
    if ($LASTEXITCODE -ne 0) { throw "candle failed for Bundle.wxs" }
} finally {
    Pop-Location
}

Write-Host "Linking bootstrapper EXE..."
& $light -nologo `
    -out $exeOut `
    -ext "$wix\bin\WixBalExtension.dll" `
    -ext "$wix\bin\WixUtilExtension.dll" `
    $bundleObj
if ($LASTEXITCODE -ne 0) { throw "light failed for bundle" }

Write-Host ""
Write-Host "Built: $exeOut"
Write-Host "This EXE installs Python 3.12 only if HKLM\SOFTWARE\Python\PythonCore\3.12\InstallPath is not set, then installs the application MSI."
