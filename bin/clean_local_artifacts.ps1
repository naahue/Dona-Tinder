$ErrorActionPreference = 'Stop'
if (-not $PSScriptRoot) { throw 'Ejecutar como script.' }
$RepoRoot = Split-Path -Parent $PSScriptRoot
$DT = Join-Path $RepoRoot 'app'
if (-not (Test-Path -LiteralPath $DT)) {
    throw 'No encuentro carpeta app/. Ejecutá este script desde el clon que tiene docker-compose.yml en la raíz.'
}

$ComposeFile = Join-Path $RepoRoot 'docker-compose.yml'
$needComposeStop = (Test-Path -LiteralPath (Join-Path $DT '.compose_data')) -or (Test-Path -LiteralPath (Join-Path $DT 'media'))
if ($needComposeStop -and (Test-Path -LiteralPath $ComposeFile) -and (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host 'Deteniendo contenedores de Compose (por locks o rutas locales bajo app/media o .compose_data)...'
    Push-Location $RepoRoot
    try {
        docker compose stop -t 5 2>$null | Out-Null
        docker compose rm -f 2>$null | Out-Null
    } finally {
        Pop-Location
    }
    Start-Sleep -Seconds 6
}

function Get-ExtendedPath {
    param([Parameter(Mandatory)][string]$LiteralPath)
    $item = Get-Item -LiteralPath $LiteralPath -Force
    $full = $item.FullName
    if ($full.StartsWith('\\?\')) { return $full }
    if ($full.StartsWith('\\')) { return $full }
    return "\\?\$full"
}

function Clear-TreeWithRobocopy {
    param([Parameter(Mandatory)][string]$LiteralPath)
    $rcExe = Join-Path $env:SystemRoot 'System32\robocopy.exe'
    if (-not (Test-Path -LiteralPath $rcExe)) { return $false }
    $stamp = [Guid]::NewGuid().ToString('N').Substring(0, 12)
    $emptyDir = Join-Path $env:TEMP "dt_empty_$stamp"
    New-Item -ItemType Directory -Path $emptyDir -Force | Out-Null
    try {
        & $rcExe $emptyDir $LiteralPath /MIR /R:10 /W:2 /NJH /NJS /NP /NFL /NDL | Out-Null
        $exit = if ($null -ne $LASTEXITCODE) { $LASTEXITCODE } else { 0 }
        return ($exit -ge 0 -and $exit -lt 8)
    } finally {
        Remove-Item -LiteralPath $emptyDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

function Remove-ArtefactTree {
    param([Parameter(Mandatory)][string]$LiteralPath)
    if (-not (Test-Path -LiteralPath $LiteralPath)) { return }
    try {
        Get-ChildItem -LiteralPath $LiteralPath -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {
            $_.Attributes = 'Archive'
        }
    } catch { }
    try {
        & attrib.exe -R "$LiteralPath\*" /S /D 2>$null | Out-Null
    } catch { }
    try {
        Remove-Item -LiteralPath $LiteralPath -Recurse -Force -ErrorAction Stop
    } catch {
        Clear-TreeWithRobocopy -LiteralPath $LiteralPath | Out-Null
        try {
            Remove-Item -LiteralPath $LiteralPath -Recurse -Force -ErrorAction Stop
        } catch { }
    }
    if (Test-Path -LiteralPath $LiteralPath) {
        Clear-TreeWithRobocopy -LiteralPath $LiteralPath | Out-Null
        $ext = Get-ExtendedPath -LiteralPath $LiteralPath
        cmd.exe /c "rd /s /q `"$ext`"" | Out-Null
    }
    if (Test-Path -LiteralPath $LiteralPath) {
        $ext = Get-ExtendedPath -LiteralPath $LiteralPath
        cmd.exe /c "rd /s /q `"$ext`"" | Out-Null
        if (Test-Path -LiteralPath $LiteralPath) {
            throw @"
No se pudo borrar: $LiteralPath
- Cerrá Docker Desktop o ejecutá: docker compose stop
- Cerrá el IDE si tenés abierta app/media o app/.compose_data
- Reintentá este script
"@
        }
    }
}

if ((Test-Path -LiteralPath (Join-Path $DT '.compose_data')) -or (Test-Path -LiteralPath (Join-Path $DT 'media'))) {
    Start-Sleep -Seconds 2
}

$SQLite = Join-Path $DT 'db.sqlite3'
$dirs = @('.compose_data', 'media', 'sent_emails', 'staticfiles', '.run')
foreach ($d in $dirs) {
    $p = Join-Path $DT $d
    if (Test-Path -LiteralPath $p) {
        Remove-ArtefactTree -LiteralPath $p
        Write-Host "Eliminado: $p"
    }
}
if (Test-Path -LiteralPath $SQLite) {
    Remove-Item -LiteralPath $SQLite -Force
    Write-Host "Eliminado: $SQLite"
}
Write-Host 'Listo (artefactos locales bajo app/). Volúmenes: `docker compose down -v` o `bin\dc.cmd down -v`.'
