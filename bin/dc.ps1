param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ComposeArgs
)

$ErrorActionPreference = 'Stop'
$BinDir = $PSScriptRoot
if (-not $BinDir) {
    throw 'PSScriptRoot no disponible (ejecutar bin\dc.ps1 como archivo).'
}
$RepoRoot = Split-Path -Parent $BinDir

function Test-ComposeArgsContainUp([string[]]$Args) {
    foreach ($x in $Args) {
        if ($x -eq 'up') { return $true }
    }
    return $false
}

function Test-DockerPreUpCleanEnabled() {
    $v = $env:DOCKER_PRE_UP_CLEAN
    if ($null -ne $v -and $v.Trim() -ne '') {
        return $v.Trim().ToLower() -notin @('0', 'false', 'no')
    }
    $ef = Join-Path $RepoRoot '.env'
    if (-not (Test-Path -LiteralPath $ef)) { return $true }
    foreach ($line in Get-Content -LiteralPath $ef) {
        $t = $line.Trim()
        if ($t.Length -eq 0 -or $t.StartsWith('#')) { continue }
        if ($t -match '^\s*DOCKER_PRE_UP_CLEAN\s*=\s*(.+)$') {
            $val = $Matches[1].Trim().Trim('"').Trim("'").ToLower()
            return $val -notin @('0', 'false', 'no')
        }
    }
    return $true
}

Push-Location $RepoRoot
try {
    if ($ComposeArgs.Count -eq 0) {
        docker compose
        exit $LASTEXITCODE
    }

    if (Test-ComposeArgsContainUp -Args $ComposeArgs) {
        Write-Host '[dc] Antes de compose up: stop + rm (evita bloqueos si quedaron app/media o restos debajo de app/)...'
        docker compose stop -t 5 2>$null | Out-Null
        docker compose rm -f 2>$null | Out-Null
        Start-Sleep -Seconds 3
        if (Test-DockerPreUpCleanEnabled) {
            Write-Host '[dc] Pre-up: limpieza local bajo app/ (media, .compose_data viejo, etc.) — desactivá con DOCKER_PRE_UP_CLEAN=false'
            & (Join-Path $BinDir 'clean_local_artifacts.ps1')
        }
    }

    docker compose @ComposeArgs
    $composeExit = $LASTEXITCODE
    if ($composeExit -ne 0) {
        exit $composeExit
    }

    $isDown = $false
    $isVolumes = $false
    foreach ($a in $ComposeArgs) {
        if ($a -eq 'down') { $isDown = $true }
        if ($a -eq '-v' -or $a -eq '--volumes') { $isVolumes = $true }
    }
    if ($isDown -and $isVolumes) {
        Write-Host '[dc] down -v OK; pausa breve y limpieza de artefactos bajo app/...'
        Start-Sleep -Seconds 3
        Write-Host '[dc] limpiando carpetas locales bajo app/...'
        & (Join-Path $BinDir 'clean_local_artifacts.ps1')
    }
} finally {
    Pop-Location
}
