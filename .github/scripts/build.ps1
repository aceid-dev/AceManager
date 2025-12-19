# ============================================
# Build script AceManager
# Ubicación: .github/scripts/build.ps1
# ============================================

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# 1. Resolver la raíz del repositorio
$repoRoot = Resolve-Path "$PSScriptRoot/../.."

Write-Host "Raíz del repositorio: $repoRoot" -ForegroundColor Cyan

# 2. Definir la lista de archivos (relativos a src/)
$archivos = @(
    "functions/pause.ps1",
    "Start-AceEngine.ps1",
    "Stop-AceEngine.ps1",
    "Check-AceEngine.ps1",
    "Start-Player.ps1",
    "main.ps1"
)

# 3. Combinar el código en memoria eliminando imports y auto-ejecución
$codigoUnificado = foreach ($f in $archivos) {

    $rutaCompleta = Join-Path $repoRoot "src/$f"

    if (Test-Path $rutaCompleta) {

        Write-Host "Procesando: src/$f" -ForegroundColor Gray

        $contenido = Get-Content -Path $rutaCompleta -Raw

        # Eliminar dot-sourcing con $PSScriptRoot
        $contenidoLimpio = $contenido -replace '(?m)^\s*\.\s+"\$PSScriptRoot\\[^"]+"', '# Línea removida por build'
        $contenidoLimpio = $contenidoLimpio -replace "(?m)^\s*\.\s+'\$PSScriptRoot\\[^']+'", '# Línea removida por build'

        # Eliminar bloques de auto-ejecución
        $contenidoLimpio = $contenidoLimpio -replace `
            '(?ms)#\s*Ejecutar solo si se llama directamente.*$', `
            '# Bloque de auto-ejecución removido por build'
            
        # Eliminar Limpieza de pan
        $contenidoLimpio = $contenidoLimpio -replace `
            'Clear-Host'`

        $contenidoLimpio
        "`n# --- Fin de archivo: src/$f ---`n"
    }
    else {
        Write-Error "Archivo no encontrado: src/$f"
        exit 1
    }
}

# 4. Crear script temporal
$tempScript = Join-Path $repoRoot "bundle_temp.ps1"

$codigoUnificado | Set-Content -Path $tempScript -Encoding UTF8

Write-Host "Script temporal creado: $tempScript" -ForegroundColor Green

# 5. Compilar a EXE con ps2exe
$rutaIcono = Join-Path $repoRoot "utils/launcher.ico"

$params = @{
    inputFile  = $tempScript
    outputFile = Join-Path $repoRoot "AceManager.exe"
    title      = "Ace Stream Engine Controller"
    version    = "1.0.0.0"
}

if (Test-Path $rutaIcono) {
    $params.Add("iconFile", $rutaIcono)
    Write-Host "Icono aplicado: utils/launcher.ico" -ForegroundColor Green
}
else {
    Write-Warning "Icono no encontrado, se usará icono genérico."
}

Invoke-ps2exe @params

# 6. Limpieza
if (Test-Path $tempScript) {
    Remove-Item $tempScript -Force
    Write-Host "Archivo temporal eliminado." -ForegroundColor DarkGray
}

Write-Host "✅ Compilación finalizada con éxito." -ForegroundColor Green
