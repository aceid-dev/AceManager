# ============================================
# Build script AceManager (Multi-target)
# Ubicación: .github/scripts/build.ps1
# ============================================

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path "$PSScriptRoot/../.."
Write-Host "Raíz del repositorio: $repoRoot" -ForegroundColor Cyan

# --- FUNCIÓN DE COMPILACIÓN ---
function Build-Target {
    param (
        [string[]]$Files,        # Lista de archivos a combinar (relativos a la raíz)
        [string]$OutputName,     # Nombre del EXE resultante
        [string]$IconPath,       # Ruta al icono
        [string]$Title           # Título del ejecutable
    )

    Write-Host "--- Iniciando compilación de: $OutputName ---" -ForegroundColor Blue

    $codigoUnificado = foreach ($f in $Files) {
        $rutaCompleta = Join-Path $repoRoot $f

        if (Test-Path $rutaCompleta) {
            Write-Host "  > Procesando: $f" -ForegroundColor Gray
            $contenido = Get-Content -Path $rutaCompleta -Raw

            # Limpiar importaciones de $PSScriptRoot (dot-sourcing)
            $contenidoLimpio = $contenido -replace '(?m)^\s*\.\s+"\$PSScriptRoot\\[^"]+"', '# Línea removida por build'
            $contenidoLimpio = $contenidoLimpio -replace "(?m)^\s*\.\s+'\$PSScriptRoot\\[^']+'", '# Línea removida por build'

            # Eliminar bloques de auto-ejecución
            $contenidoLimpio = $contenidoLimpio -replace '(?ms)#\s*Ejecutar solo si se llama directamente.*$', '# Bloque de auto-ejecución removido'

            $contenidoLimpio
            "`n# --- Fin de archivo: $f ---`n"
        }
        else {
            Write-Error "Archivo no encontrado: $rutaCompleta"
            exit 1
        }
    }

    # Crear script temporal
    $tempScript = Join-Path $repoRoot "temp_$OutputName.ps1"
    $codigoUnificado | Set-Content -Path $tempScript -Encoding UTF8

    # Parámetros para ps2exe
    $params = @{
        inputFile  = $tempScript
        outputFile = Join-Path $repoRoot "$OutputName.exe"
        title      = $Title
        version    = "1.0.0.0"
    }

    if (Test-Path $IconPath) {
        $params.Add("iconFile", $IconPath)
        Write-Host "  > Icono aplicado: $IconPath" -ForegroundColor Green
    }

    Invoke-ps2exe @params

    # Limpieza
    if (Test-Path $tempScript) { Remove-Item $tempScript -Force }
    Write-Host "✅ Generado: $OutputName.exe`n" -ForegroundColor Green
}

# --- DEFINICIÓN DE OBJETIVOS (TARGETS) ---

# 1. Compilar AceManager (El principal)
$archivosMain = @(
    "src/functions/pause.ps1",
    "src/Start-AceEngine.ps1",
    "src/Stop-AceEngine.ps1",
    "src/Check-AceEngine.ps1",
    "src/Start-Player.ps1",
    "src/main.ps1"
)
Build-Target -Files $archivosMain -OutputName "AceManager" -IconPath (Join-Path $repoRoot "icons/launcher.ico") -Title "Ace Stream Engine Controller"

# 2. Compilar Lista AceStream (El nuevo utilitario)
# Nota: Incluimos Start-AceEngine porque lista_acestream.ps1 lo usa
$archivosUtils = @(
    "src/functions/pause.ps1",
    "src/Start-AceEngine.ps1",
    "utils/lista_acestream.ps1"
)
Build-Target -Files $archivosUtils -OutputName "ListaAceStream" -IconPath (Join-Path $repoRoot "icons/icon.ico") -Title "AceStream List Launcher"

Write-Host "🚀 Todos los ejecutables han sido compilados con éxito." -ForegroundColor DarkGreen