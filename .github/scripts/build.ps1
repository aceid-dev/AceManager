<#
.SYNOPSIS
    Script de compilación para AceManager y utilidades.
    Une múltiples archivos .ps1 en un solo ejecutable sincronizado con Semantic Release.
#>

param (
    [Parameter(HelpMessage = "Versión del ejecutable (formato A.B.C.D)")]
    [string]$AppVersion = "1.0.0.0" 
)

# Configuración de entorno: Errores estrictos y detención ante fallos
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Localizar la raíz del proyecto basándose en la ubicación del script
$repoRoot = Resolve-Path "$PSScriptRoot/../.."
Write-Host "`n[BUILD] Iniciando proceso de compilación" -ForegroundColor Cyan
Write-Host "[INFO] Raíz detectada: $repoRoot" -ForegroundColor DarkGray
Write-Host "[INFO] Versión de destino: $AppVersion" -ForegroundColor Yellow
Write-Host "---------------------------------------------------"

<#
.DESCRIPTION
    Función interna para procesar y compilar un conjunto de archivos.
#>
function Build-Target {
    param (
        [string[]]$Files,      # Lista de rutas relativas de archivos a unir
        [string]$OutputName,   # Nombre del archivo .exe final
        [string]$IconPath,     # Ruta al archivo .ico
        [string]$Title         # Título del metadato del ejecutable
    )

    Write-Host "`n>> Preparando: $OutputName..." -ForegroundColor Blue

    # 1. Combinar archivos y limpiar dependencias locales
    $codigoUnificado = foreach ($f in $Files) {
        $rutaAbsoluta = Join-Path $repoRoot $f
        
        if (Test-Path $rutaAbsoluta) {
            Write-Host "   + Procesando: $f" -ForegroundColor Gray
            $contenido = Get-Content -Path $rutaAbsoluta -Raw

            <# 
               LIMPIEZA DE CÓDIGO:
               1. Eliminamos 'dot-sourcing' que use $PSScriptRoot ya que en el EXE 
                  todas las funciones estarán en el mismo archivo.
               2. Eliminamos bloques de ejecución directa para que no se disparen 
                  al importar funciones.
            #>
            $contenidoLimpio = $contenido -replace '(?m)^\s*\.\s+["'']\$PSScriptRoot\\[^"'']+["'']', '# Import removido por build'
            $contenidoLimpio = $contenidoLimpio -replace '(?ms)#\s*Ejecutar solo si se llama directamente.*$', '# Bloque main removido'

            $contenidoLimpio
            "`n# --- Fin de sección: $f ---`n"
        }
        else {
            Write-Host "   [ERROR] No se encontró el archivo: $f" -ForegroundColor Red
            throw "Archivo crítico faltante: $f"
        }
    }

    # 2. Crear archivo temporal para la compilación
    $tempScript = Join-Path $repoRoot "temp_$OutputName.ps1"
    try {
        $codigoUnificado | Set-Content -Path $tempScript -Encoding UTF8
        
        # 3. Llamada al compilador ps2exe
        $exePath = Join-Path $repoRoot "$OutputName.exe"
        Write-Host "   > Generando ejecutable..." -ForegroundColor DarkCyan
        
        Invoke-ps2exe -inputFile $tempScript `
            -outputFile $exePath `
            -iconFile $IconPath `
            -title $Title `
            -version $AppVersion

        if (Test-Path $exePath) {
            Write-Host "   [OK] $OutputName.exe creado con éxito." -ForegroundColor Green
        }
    }
    catch {
        # Extraemos el mensaje a una variable simple para evitar errores de símbolos (: o $)
        $errorMessage = $_.Exception.Message
        Write-Host "   [ERROR] Fallo la compilacion de $OutputName" -ForegroundColor Red
        Write-Host "   [DETALLE] $errorMessage" -ForegroundColor DarkRed
        exit 1
    }
    finally {
        # Limpiar el archivo temporal siempre, incluso si hay error
        if (Test-Path $tempScript) { 
            Remove-Item $tempScript -Force 
            Write-Host "   [INFO] Limpieza de temporales completada." -ForegroundColor DarkGray
        }
    }
}

# --- DEFINICIÓN DE OBJETIVOS (TARGETS) ---

try {
    # 1. Compilación del AceManager Principal
    Build-Target -Files @(
        "src/functions/pause.ps1",
        "src/Start-AceEngine.ps1",
        "src/Stop-AceEngine.ps1",
        "src/Check-AceEngine.ps1",
        "src/Start-Player.ps1",
        "src/main.ps1"
    ) -OutputName "AceManager" -IconPath "$repoRoot/icons/launcher.ico" -Title "Ace Stream Engine Controller"

    # 2. Compilación de la utilidad Lista AceStream
    Build-Target -Files @(
        "src/functions/pause.ps1",
        "src/Start-AceEngine.ps1",
        "utils/lista_acestream.ps1"
    ) -OutputName "ListaAceStream" -IconPath "$repoRoot/icons/icon.ico" -Title "AceStream List Launcher"

    Write-Host "`n🚀 PROCESO FINALIZADO: Todos los ejecutables están listos." -ForegroundColor DarkGreen
}
catch {
    Write-Host "`n❌ ERROR CRÍTICO durante el proceso de build." -ForegroundColor Red
    exit 1
}