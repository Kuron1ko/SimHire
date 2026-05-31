param(
  [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ApiRoot = Join-Path $RepoRoot "services\api"

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
  $OutputPath = Join-Path $ApiRoot "openapi.json"
}

Push-Location $ApiRoot
try {
  $oldPythonPath = $env:PYTHONPATH
  if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
    $env:PYTHONPATH = $ApiRoot
  } else {
    $env:PYTHONPATH = "$ApiRoot$([IO.Path]::PathSeparator)$oldPythonPath"
  }

  python -m app.export_openapi --output $OutputPath
}
finally {
  $env:PYTHONPATH = $oldPythonPath
  Pop-Location
}
