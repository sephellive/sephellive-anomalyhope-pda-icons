[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [string]$ArchivePath,

    [string]$TexconvPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$python = Get-Command python.exe -ErrorAction Stop

if ([string]::IsNullOrWhiteSpace($TexconvPath)) {
    $TexconvPath = (Get-Command texconv.exe -ErrorAction Stop).Source
}
$resolvedTexconv = (Resolve-Path -LiteralPath $TexconvPath).Path
$resolvedOutput = [System.IO.Path]::GetFullPath($OutputPath)
if (Test-Path -LiteralPath $resolvedOutput) {
    throw "OutputPath must not already exist: $resolvedOutput"
}

& $python.Source -c 'from PIL import Image' 2>$null
if ($LASTEXITCODE -ne 0) {
    throw 'Pillow is missing. Run: python -m pip install -r requirements.txt'
}

& $python.Source (Join-Path $PSScriptRoot 'build_icons.py') `
    --manifest (Join-Path $repositoryRoot 'assets\manifest\icons.json') `
    --output-root $resolvedOutput `
    --texconv $resolvedTexconv
if ($LASTEXITCODE -ne 0) { throw 'PDA icon build failed.' }

& $python.Source (Join-Path $PSScriptRoot 'validate_icon_build.py') `
    --manifest (Join-Path $repositoryRoot 'assets\manifest\icons.json') `
    --output-root $resolvedOutput
if ($LASTEXITCODE -ne 0) { throw 'PDA icon validation failed.' }

if (-not [string]::IsNullOrWhiteSpace($ArchivePath)) {
    $resolvedArchive = [System.IO.Path]::GetFullPath($ArchivePath)
    $archiveParent = Split-Path -Parent $resolvedArchive
    New-Item -ItemType Directory -Path $archiveParent -Force | Out-Null
    Compress-Archive -Path (Join-Path $resolvedOutput 'gamedata') -DestinationPath $resolvedArchive -Force
    Write-Host "MO2 archive: $resolvedArchive"
}
Write-Host "MO2-ready add-on: $resolvedOutput"
