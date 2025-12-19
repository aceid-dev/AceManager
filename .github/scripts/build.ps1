# ============================================
# Build script AceManager (Multi-target + Auto-version)
# Ubicación: .github/scripts/build.ps1
# ============================================

param (
    [string]$AppVersion = "1.0.0.0" # Valor por defecto
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path "$PSScriptRoot/../.."
Write-Host "--- Iniciando proceso de compilación ---" -ForegroundColor Cyan
Write-Host "Versión asignada: $AppVersion" -ForegroundColor Yellow

# --- FUNCIÓN DE COMPILACIÓN ---
function Build-Target {
    param (
        [string[]]$Files,
        [string]$OutputName,
        [string]$IconPath,
        [string]$Title
    )

    Write-Host "`n>> Compilando: $OutputName" -ForegroundColor Blue

    $codigoUnificado = foreach ($f in $Files) {
        $rutaCompleta = Join-Path $repoRoot $f
        if (Test-Path $rutaCompleta) {
            $contenido = Get-Content -Path $rutaCompleta -Raw
            # Limpieza de imports y auto-ejecución
            $contenidoLimpio = $contenido -replace '(?m)^\s*\.\s+"\$PSScriptRoot\\[^"]+"', '# Removido'
            $contenidoLimpio = $contenidoLimpio -replace "(?m)^\s*\.\s+'\$PSScriptRoot\\[^']+'", '# Removido'
            $contenidoLimpio = $contenidoLimpio -replace '(?ms)#\s*Ejecutar solo si se llama directamente.*$', '# Removido'
            
            $contenidoLimpio
            "`n# --- Fin de archivo: $f ---`n"
        } else {
            Write-Error "Archivo no encontrado: $rutaCompleta"
            exit 1
        }
    }

    $tempScript = Join-Path $repoRoot "temp_$OutputName.ps1"
    $codigoUnificado | Set-Content -Path $tempScript -Encoding UTF8

    $params = @{
        inputFile  = $tempScript
        outputFile = Join-Path $repoRoot "$OutputName.exe"
        title      = $Title
        version    = $AppVersion # Usamos la versión recibida por parámetro
    }

    if (Test-Path $IconPath) { $params.Add("iconFile", $IconPath) }

    Invoke-ps2exe @params
    if (Test-Path $tempScript) { Remove-Item $tempScript -Force }
    Write-Host "✅ Archivo $OutputName.exe generado con éxito." -ForegroundColor Green
}

# --- EJECUCIÓN DE LOS OBJETIVOS ---

# 1. AceManager Principal
$archivosMain = @(
    "src/functions/pause.ps1",
    "src/Start-AceEngine.ps1",
    "src/Stop-AceEngine.ps1",
    "src/Check-AceEngine.ps1",
    "src/Start-Player.ps1",
    "src/main.ps1"
)
Build-Target -Files $archivosMain -OutputName "AceManager" -IconPath (Join-Path $repoRoot "icons/launcher.ico") -Title "Ace Stream Engine Controller"

# 2. Lista AceStream
$archivosUtils = @(
    "src/functions/pause.ps1",
    "src/Start-AceEngine.ps1",
    "utils/lista_acestream.ps1"
)
Build-Target -Files $archivosUtils -OutputName "ListaAceStream" -IconPath (Join-Path $repoRoot "icons/icon.ico") -Title "AceStream List Launcher"

Write-Host "`n🚀 Proceso finalizado correctamente." -ForegroundColor DarkGreen