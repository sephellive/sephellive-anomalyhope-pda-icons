param(
    [Parameter(Mandatory = $true)]
    [string]$GamePath,
    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'

$game = (Resolve-Path -LiteralPath $GamePath).Path
$output = [System.IO.Path]::GetFullPath($OutputPath)
$converter = Join-Path $game 'tools\converter.exe'
$archives = @(
    (Join-Path $game 'db\configs\configs.db0'),
    (Join-Path $game 'db\configs\scripts.db0'),
    (Join-Path $game 'db\textures\textures_ui.db0')
)

if (-not (Test-Path -LiteralPath $converter -PathType Leaf)) {
    throw "Anomaly converter.exe was not found under $game\tools"
}
foreach ($archive in $archives) {
    if (-not (Test-Path -LiteralPath $archive -PathType Leaf)) {
        throw "Required Anomaly archive is missing: $archive"
    }
}
if (Test-Path -LiteralPath $output) {
    throw "Output path must not already exist: $output"
}
if ($output.StartsWith($game + [System.IO.Path]::DirectorySeparatorChar,
        [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Output path must be outside the Anomaly installation.'
}

New-Item -ItemType Directory -Path $output | Out-Null
$destinations = @(
    (Join-Path $output 'configs'),
    (Join-Path $output 'scripts'),
    (Join-Path $output 'textures')
)
for ($index = 0; $index -lt $archives.Count; $index++) {
    New-Item -ItemType Directory -Path $destinations[$index] | Out-Null
    & $converter -unpack -xdb $archives[$index] -dir $destinations[$index]
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to extract $($archives[$index]) (exit $LASTEXITCODE)"
    }
}

$required = @(
    (Join-Path $output 'configs\configs\ui\map_spots.xml'),
    (Join-Path $output 'configs\configs\ui\map_spots_16.xml'),
    (Join-Path $output 'configs\configs\ui\textures_descr'),
    (Join-Path $output 'textures\textures\ui')
)
foreach ($path in $required) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Extraction completed but expected resources were not found: $path"
    }
}

Write-Output "Extracted base PDA resources to $output"
