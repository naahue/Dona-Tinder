$ErrorActionPreference = 'Stop'
if (-not $PSScriptRoot) { throw 'Ejecutar como script.' }
& (Join-Path $PSScriptRoot 'dc.ps1') down -v
