<#
.SYNOPSIS
    Script de compilacion para AceManager y utilidades.
    Une multiples archivos .ps1 en un solo ejecutable sincronizado con Semantic Release
    y genera un paquete ZIP de distribucion.
#>

param (
    [Parameter(HelpMessage = "Version del ejecutable (formato A.B.C.D)")]
    [string]$AppVersion = "1.0.0.0",
    [Parameter(HelpMessage = "Objetivos de build: All, AceManager, ListaAceStream")]
    [ValidateSet("All", "AceManager", "ListaAceStream")]
    [string[]]$Targets = @("All"),
    [Parameter(HelpMessage = "Omitir empaquetado ZIP")]
    [switch]$SkipPackage
)

# Configuracion de entorno: Errores estrictos y detencion ante fallos
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Localizar la raiz del proyecto basandose en la ubicacion del script
$repoRoot = Resolve-Path "$PSScriptRoot/../.."
Write-Host "`n[BUILD] Iniciando proceso de compilacion" -ForegroundColor Cyan
Write-Host "[INFO] Raiz detectada: $repoRoot" -ForegroundColor DarkGray
Write-Host "[INFO] Version de destino: $AppVersion" -ForegroundColor Yellow
Write-Host "---------------------------------------------------"

# Resolver objetivos reales manteniendo compatibilidad:
# - Sin parametros -> All (comportamiento CI/CD actual)
# - Con objetivo puntual -> build a demanda
$selectedTargets = @()
if ($Targets -contains "All") {
    $selectedTargets = @("AceManager", "ListaAceStream")
}
else {
    $selectedTargets = $Targets | Select-Object -Unique
}

$buildAceManager = $selectedTargets -contains "AceManager"
$buildListaAceStream = $selectedTargets -contains "ListaAceStream"

# Solo empaquetar cuando ambos ejecutables forman parte del build y no se fuerza omision
$shouldPackage = (-not $SkipPackage) -and $buildAceManager -and $buildListaAceStream

Write-Host "[INFO] Objetivos: $($selectedTargets -join ', ')" -ForegroundColor DarkGray
if ($shouldPackage) {
    Write-Host "[INFO] Empaquetado ZIP: habilitado" -ForegroundColor DarkGray
}
else {
    Write-Host "[INFO] Empaquetado ZIP: omitido" -ForegroundColor DarkGray
}

<#
.DESCRIPTION
    Funcion interna para procesar y compilar un conjunto de archivos.
#>
function Build-Target {
    param (
        [string[]]$Files,      # Lista de rutas relativas de archivos a unir
        [string]$OutputName,   # Nombre del archivo .exe final
        [string]$IconPath,     # Ruta al archivo .ico
        [string]$Title,        # Titulo del metadato del ejecutable
        [switch]$NoConsole     # Compilar como GUI sin consola
    )

    Write-Host "`n>> Preparando: $OutputName..." -ForegroundColor Blue

    # 1. Combinar archivos y limpiar dependencias locales
    $codigoUnificado = foreach ($f in $Files) {
        $rutaAbsoluta = Join-Path $repoRoot $f
        
        if (Test-Path $rutaAbsoluta) {
            Write-Host "   + Procesando: $f" -ForegroundColor Gray
            $contenido = Get-Content -Path $rutaAbsoluta -Raw

            <# 
               LIMPIEZA DE CODIGO:
               1. Eliminamos 'dot-sourcing' que use $PSScriptRoot ya que en el EXE 
                  todas las funciones estaran en el mismo archivo.
               2. Eliminamos bloques de ejecucion directa para que no se disparen 
                  al importar funciones.
            #>
            $contenidoLimpio = $contenido -replace '(?m)^\s*\.\s+["'']\$PSScriptRoot\\[^"'']+["'']', '# Import removido por build'
            $contenidoLimpio = $contenidoLimpio -replace '(?ms)#\s*Ejecutar solo si se llama directamente.*$', '# Bloque main removido'

            $contenidoLimpio
            "`n# --- Fin de seccion: $f ---`n"
        }
        else {
            Write-Host "   [ERROR] No se encontro el archivo: $f" -ForegroundColor Red
            throw "Archivo critico faltante: $f"
        }
    }

    # 2. Crear archivo temporal para la compilacion
    $tempScript = Join-Path $repoRoot "temp_$OutputName.ps1"
    try {
        $codigoUnificado | Set-Content -Path $tempScript -Encoding UTF8
        
        # 3. Llamada al compilador ps2exe
        $exePath = Join-Path $repoRoot "$OutputName.exe"
        Write-Host "   > Generando ejecutable..." -ForegroundColor DarkCyan
        
        $ps2exeParams = @{
            inputFile  = $tempScript
            outputFile = $exePath
            iconFile   = $IconPath
            title      = $Title
            version    = $AppVersion
        }
        if ($NoConsole) {
            $ps2exeParams.noConsole = $true
        }

        Invoke-ps2exe @ps2exeParams

        if (Test-Path $exePath) {
            Write-Host "   [OK] $OutputName.exe creado con exito." -ForegroundColor Green
        }
    }
    catch {
        # Extraemos el mensaje a una variable simple para evitar errores de simbolos
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

# Elimina archivos/carpetas con reintentos para evitar fallos por bloqueo temporal
function Remove-PathWithRetry {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [switch]$Recurse,
        [int]$MaxRetries = 3,
        [int]$DelayMs = 400
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    for ($attempt = 1; $attempt -le $MaxRetries; $attempt++) {
        try {
            if ($Recurse) {
                Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
            }
            else {
                Remove-Item -LiteralPath $Path -Force -ErrorAction Stop
            }
            return
        }
        catch {
            if ($attempt -ge $MaxRetries) {
                throw
            }
            Start-Sleep -Milliseconds $DelayMs
        }
    }
}

# --- EJECUCION DEL PROCESO ---

try {
    # 1. Compilacion de ejecutables seleccionados
    if ($buildAceManager) {
        Build-Target -Files @(
            "src/functions/pause.ps1",
            "src/Start-AceEngine.ps1",
            "src/Stop-AceEngine.ps1",
            "src/Check-AceEngine.ps1",
            "src/Start-Player.ps1",
            "src/main.ps1"
        ) -OutputName "AceManager" -IconPath "$repoRoot/icons/launcher.ico" -Title "Ace Manager"
    }

    if ($buildListaAceStream) {
        Build-Target -Files @(
            "src/functions/pause.ps1",
            "src/Start-AceEngine.ps1",
            "utils/lista_acestream.ps1"
        ) -OutputName "ListaAceStream" -IconPath "$repoRoot/icons/icon.ico" -Title "Lista AceStream Launcher" -NoConsole
    }

    # 2. Creacion del Paquete de Distribucion (ZIP) opcional
    if ($shouldPackage) {
        Write-Host "`n>> Iniciando empaquetado ZIP..." -ForegroundColor Yellow
        
        # Definir carpeta temporal para el paquete
        $packageDir = Join-Path $repoRoot "AceManager_v$AppVersion"
        Remove-PathWithRetry -Path $packageDir -Recurse
        New-Item -ItemType Directory -Path $packageDir | Out-Null

        # Asegurar config.ini (si no existe, generar uno por defecto)
        $configPath = Join-Path $repoRoot "config.ini"
        if (-not (Test-Path -LiteralPath $configPath)) {
            Write-Host "   [WARN] config.ini no encontrado. Se generara uno por defecto." -ForegroundColor Yellow
            @(
                "# Configuracion de AceManager"
                "# Puedes poner el dominio de tu servidor aqui"
                "dominio = https://aceid.short.gy"
                ""
                "# Puedes poner el nombre de la lista (ej: lista_acestream)"
                "# o una URL completa (ej: https://otro-sitio.com/lista.m3u)"
                "lista = lista_acestream"
            ) | Set-Content -LiteralPath $configPath -Encoding ASCII -ErrorAction Stop
        }

        # Copiar archivos necesarios al paquete
        Copy-Item (Join-Path $repoRoot "AceManager.exe") -Destination $packageDir -ErrorAction Stop
        Copy-Item (Join-Path $repoRoot "ListaAceStream.exe") -Destination $packageDir -ErrorAction Stop
        Copy-Item $configPath -Destination $packageDir -ErrorAction Stop

        # Crear el archivo ZIP final (con fallback si el nombre principal esta en uso)
        $zipPath = Join-Path $repoRoot "AceManager.zip"
        $tempZipPath = Join-Path $repoRoot ("AceManager_{0}.tmp.zip" -f ([guid]::NewGuid().ToString("N")))

        if (Test-Path -LiteralPath $zipPath) {
            try {
                Remove-PathWithRetry -Path $zipPath
            }
            catch {
                $zipPath = Join-Path $repoRoot ("AceManager_{0}.zip" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
                Write-Host "   [WARN] AceManager.zip en uso. Se generara: $([System.IO.Path]::GetFileName($zipPath))" -ForegroundColor Yellow
            }
        }

        try {
            if (Get-Command Compress-Archive -ErrorAction SilentlyContinue) {
                Compress-Archive -Path (Join-Path $packageDir '*') -DestinationPath $tempZipPath -Force -ErrorAction Stop
            }
            else {
                Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop
                [System.IO.Compression.ZipFile]::CreateFromDirectory($packageDir, $tempZipPath)
            }

            Move-Item -LiteralPath $tempZipPath -Destination $zipPath -Force -ErrorAction Stop
        }
        finally {
            if (Test-Path -LiteralPath $tempZipPath) {
                Remove-PathWithRetry -Path $tempZipPath
            }
        }

        Write-Host "   [OK] Paquete ZIP generado: $([System.IO.Path]::GetFileName($zipPath))" -ForegroundColor Green
        
        # Limpiar carpeta de empaquetado
        Remove-PathWithRetry -Path $packageDir -Recurse
    }
    else {
        Write-Host "`n[INFO] Empaquetado ZIP omitido por seleccion de objetivos." -ForegroundColor DarkGray
    }

    Write-Host "`n[OK] PROCESO FINALIZADO: Todo esta listo para el release." -ForegroundColor DarkGreen
}
catch {
    Write-Host "`n[ERROR] ERROR CRITICO durante el proceso de build." -ForegroundColor Red
    Write-Host "   [DETALLE] $($_.Exception.Message)" -ForegroundColor DarkRed
    if ($_.InvocationInfo -and $_.InvocationInfo.PositionMessage) {
        Write-Host "   [LINEA] $($_.InvocationInfo.PositionMessage)" -ForegroundColor DarkGray
    }
    exit 1
}
