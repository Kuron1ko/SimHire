param(
  [string]$OpenApiPath = "",
  [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$DefaultOpenApiPath = Join-Path $RepoRoot "services\api\openapi.json"
$DefaultOutputPath = Join-Path $RepoRoot "apps\web\src\types\generated\api.ts"

if ([string]::IsNullOrWhiteSpace($OpenApiPath)) {
  $OpenApiPath = $DefaultOpenApiPath
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
  $OutputPath = $DefaultOutputPath
}

& (Join-Path $PSScriptRoot "export-openapi.ps1") -OutputPath $OpenApiPath

$OutputDirectory = Split-Path -Parent $OutputPath
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null

npx --yes openapi-typescript $OpenApiPath -o $OutputPath
