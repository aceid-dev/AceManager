<# 
.SYNOPSIS
Instalador AceManager - Version con deteccion automatica de archivos
.DESCRIPTION
Script que detecta automaticamente los instaladores sin importar el nombre exacto
#>

# Funcion de pausa simple
function Wait-KeyPress {
    param([string]$msg = "Presione cualquier tecla para continuar...")
    Write-Host ""
    Write-Host $msg -ForegroundColor Cyan
    try {
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    catch {
        $null = Read-Host "Presione ENTER"
    }
    Write-Host ""
}

# Verificar privilegios de administrador
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "  PRIVILEGIOS DE ADMINISTRADOR REQUERIDOS" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Elevando privilegios..." -ForegroundColor Cyan
    Write-Host "(Se abrira una nueva ventana como administrador)" -ForegroundColor DarkGray
    Write-Host ""
    
    $scriptPath = $PSCommandPath
    if (-not $scriptPath) {
        $scriptPath = Join-Path $env:TEMP "acemanager_install.ps1"
        $MyInvocation.MyCommand.ScriptBlock.ToString() | Out-File -FilePath $scriptPath -Encoding UTF8
    }
    
    $arguments = "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$scriptPath`""
    
    try {
        Start-Process powershell.exe -ArgumentList $arguments -Verb RunAs
        # Cerrar esta ventana inmediatamente para dejar solo la nueva
        Start-Sleep -Milliseconds 500
        exit
    }
    catch {
        Write-Host ""
        Write-Host "ERROR: No se pudo elevar privilegios" -ForegroundColor Red
        Write-Host ""
        Write-Host "SOLUCION MANUAL:" -ForegroundColor Yellow
        Write-Host "1. Clic derecho en PowerShell" -ForegroundColor White
        Write-Host "2. 'Ejecutar como administrador'" -ForegroundColor White
        Write-Host "3. Navegue a la carpeta de descargas:" -ForegroundColor White
        Write-Host "   cd $HOME\Downloads" -ForegroundColor Cyan
        Write-Host "4. Ejecute: .\install.ps1" -ForegroundColor Cyan
        Write-Host ""
        Wait-KeyPress
        exit
    }
}

# Inicio del script como administrador
Clear-Host
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  INSTALADOR ACEMANAGER" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Ejecutando como: $([System.Security.Principal.WindowsIdentity]::GetCurrent().Name)" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Determinar directorio de trabajo
# Prioridad: 1) PSScriptRoot, 2) Directorio actual, 3) Downloads
$BASE_DIR = $PSScriptRoot
if (-not $BASE_DIR -or $BASE_DIR -eq "") {
    $BASE_DIR = (Get-Location).Path
}
if (-not (Test-Path $BASE_DIR) -or $BASE_DIR -match "System32|Temp") {
    $BASE_DIR = Join-Path $HOME "Downloads"
}

Write-Host "Buscando archivos en: $BASE_DIR" -ForegroundColor Cyan
Write-Host ""

$ACE_DEST = Join-Path $env:APPDATA "ACEStream"
$ACEMANAGER_DEST = Join-Path $ACE_DEST "AceManager.exe"
$START_MENU = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$LINK_START = Join-Path $START_MENU "AceManager.lnk"
$LINK_DESKTOP = Join-Path ([Environment]::GetFolderPath("Desktop")) "AceManager.lnk"

$hasErrors = $false

try {
    # Buscar archivos con deteccion automatica
    Write-Host "[1/4] Buscando archivos necesarios..." -ForegroundColor Yellow
    
    # Buscar Ace Stream (cualquier version)
    $ACE_INSTALLER = Get-ChildItem -Path $BASE_DIR -Filter "*Ace*Stream*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
    
    # Buscar VLC (cualquier version)
    $VLC_INSTALLER = Get-ChildItem -Path $BASE_DIR -Filter "vlc*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
    
    # Buscar AceManager
    $ACEMANAGER_SRC = Get-ChildItem -Path $BASE_DIR -Filter "AceManager.exe" -ErrorAction SilentlyContinue | Select-Object -First 1

    # Verificar archivos encontrados
    $missingFiles = @()
    
    if (-not $ACE_INSTALLER) { 
        $missingFiles += "Ace Stream installer (Ace_Stream*.exe)"
    } else {
        Write-Host "  Encontrado: $($ACE_INSTALLER.Name)" -ForegroundColor Green
        $ACE_INSTALLER = $ACE_INSTALLER.FullName
    }
    
    if (-not $VLC_INSTALLER) { 
        $missingFiles += "VLC installer (vlc*.exe)"
    } else {
        Write-Host "  Encontrado: $($VLC_INSTALLER.Name)" -ForegroundColor Green
        $VLC_INSTALLER = $VLC_INSTALLER.FullName
    }
    
    if (-not $ACEMANAGER_SRC) { 
        $missingFiles += "AceManager.exe"
    } else {
        Write-Host "  Encontrado: $($ACEMANAGER_SRC.Name)" -ForegroundColor Green
        $ACEMANAGER_SRC = $ACEMANAGER_SRC.FullName
    }

    if ($missingFiles.Count -gt 0) {
        Write-Host ""
        Write-Host "ERROR: Faltan archivos necesarios:" -ForegroundColor Red
        foreach ($file in $missingFiles) {
            Write-Host "  - $file" -ForegroundColor Red
        }
        Write-Host ""
        Write-Host "Busque en: $BASE_DIR" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Si los archivos estan en otra carpeta:" -ForegroundColor Cyan
        Write-Host "  1. Abra PowerShell como administrador" -ForegroundColor White
        Write-Host "  2. Navegue a esa carpeta: cd 'C:\ruta\a\carpeta'" -ForegroundColor White
        Write-Host "  3. Ejecute: .\install.ps1" -ForegroundColor White
        throw "Archivos faltantes"
    }
    
    Write-Host ""
    Write-Host "  Todos los archivos encontrados correctamente!" -ForegroundColor Green

    # Verificar instalaciones existentes
    Write-Host ""
    Write-Host "[2/4] Verificando instalaciones..." -ForegroundColor Yellow
    
    $aceAlreadyInstalled = Test-Path $ACE_DEST
    
    $vlcPaths = @(
        "HKLM:\SOFTWARE\VideoLAN\VLC",
        "HKLM:\SOFTWARE\WOW6432Node\VideoLAN\VLC"
    )
    $vlcAlreadyInstalled = $false
    foreach ($path in $vlcPaths) {
        if (Test-Path $path) { 
            $vlcAlreadyInstalled = $true
            break
        }
    }
    
    if ($aceAlreadyInstalled) {
        Write-Host "  Ace Stream ya esta instalado" -ForegroundColor Green
    }
    if ($vlcAlreadyInstalled) {
        Write-Host "  VLC ya esta instalado" -ForegroundColor Green
    }
    
    # Instalar en paralelo si es necesario
    if (-not $aceAlreadyInstalled -or -not $vlcAlreadyInstalled) {
        Write-Host ""
        Write-Host "[3/4] Instalando software necesario..." -ForegroundColor Yellow
        Write-Host ""
        
        $aceProcess = $null
        $vlcProcess = $null
        
        # Iniciar Ace Stream si no esta instalado
        if (-not $aceAlreadyInstalled) {
            Write-Host "  Iniciando instalacion de Ace Stream..." -ForegroundColor Cyan
            Write-Host "  Archivo: $([System.IO.Path]::GetFileName($ACE_INSTALLER))" -ForegroundColor DarkGray
            $aceProcess = Start-Process -FilePath $ACE_INSTALLER -PassThru
        }
        
        # Iniciar VLC si no esta instalado
        if (-not $vlcAlreadyInstalled) {
            Write-Host "  Iniciando instalacion de VLC (modo silencioso)..." -ForegroundColor Cyan
            Write-Host "  Archivo: $([System.IO.Path]::GetFileName($VLC_INSTALLER))" -ForegroundColor DarkGray
            $vlcProcess = Start-Process -FilePath $VLC_INSTALLER -ArgumentList "/S" -PassThru
        }
        
        Write-Host ""
        Write-Host "  INSTALACIONES EN PARALELO" -ForegroundColor Yellow
        Write-Host "  =========================" -ForegroundColor Yellow
        if (-not $aceAlreadyInstalled) {
            Write-Host "  - Complete el asistente de Ace Stream" -ForegroundColor White
            Write-Host "  - CIERRE todas las ventanas cuando termine" -ForegroundColor White
        }
        if (-not $vlcAlreadyInstalled) {
            Write-Host "  - VLC se instala automaticamente en segundo plano" -ForegroundColor White
        }
        Write-Host ""
        Write-Host "  Monitoreando progreso..." -ForegroundColor Cyan
        Write-Host ""
        
        # Monitorear ambas instalaciones
        $timeout = 300
        $elapsed = 0
        $checkInterval = 3
        $aceComplete = $aceAlreadyInstalled
        $vlcComplete = $vlcAlreadyInstalled
        
        while ((-not $aceComplete -or -not $vlcComplete) -and $elapsed -lt $timeout) {
            Start-Sleep -Seconds $checkInterval
            $elapsed += $checkInterval
            
            # Verificar Ace Stream
            if (-not $aceComplete -and (Test-Path $ACE_DEST)) {
                $aceComplete = $true
                Write-Host "  [✓] Ace Stream instalado correctamente" -ForegroundColor Green
            }
            
            # Verificar VLC
            if (-not $vlcComplete) {
                foreach ($path in $vlcPaths) {
                    if (Test-Path $path) { 
                        $vlcComplete = $true
                        Write-Host "  [✓] VLC instalado correctamente" -ForegroundColor Green
                        break
                    }
                }
            }
            
            # Mensaje de progreso cada 15 segundos
            if ((-not $aceComplete -or -not $vlcComplete) -and ($elapsed % 15 -eq 0)) {
                $pending = @()
                if (-not $aceComplete) { $pending += "Ace Stream" }
                if (-not $vlcComplete) { $pending += "VLC" }
                Write-Host "  Esperando: $($pending -join ', ')... ($elapsed seg)" -ForegroundColor DarkGray
            }
        }
        
        # Verificacion final
        Write-Host ""
        if (-not $aceComplete) {
            Write-Host "  ATENCION: Ace Stream requiere atencion manual" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "  Complete la instalacion y cierre el instalador" -ForegroundColor Cyan
            Write-Host "  Presione cualquier tecla cuando este listo..." -ForegroundColor Cyan
            Write-Host ""
            
            Wait-KeyPress
            
            if (-not (Test-Path $ACE_DEST)) {
                Write-Host "  ERROR: Ace Stream no se instalo correctamente" -ForegroundColor Red
                Write-Host "  Ruta esperada: $ACE_DEST" -ForegroundColor DarkGray
                $hasErrors = $true
            }
            else {
                Write-Host "  [✓] Ace Stream verificado" -ForegroundColor Green
            }
        }
        
        if (-not $vlcComplete) {
            Write-Host "  Advertencia: VLC puede no estar completamente instalado" -ForegroundColor Yellow
            Write-Host "  Puede instalarlo manualmente: https://www.videolan.org/" -ForegroundColor DarkGray
        }
    }
    else {
        Write-Host ""
        Write-Host "[3/4] Software ya instalado, saltando..." -ForegroundColor Green
    }

    # Instalar AceManager
    Write-Host ""
    Write-Host "[4/4] Instalando AceManager..." -ForegroundColor Yellow
    
    # Crear directorio si no existe
    if (-not (Test-Path $ACE_DEST)) {
        $null = New-Item -Path $ACE_DEST -ItemType Directory -Force
        Write-Host "  Creando directorio: $ACE_DEST" -ForegroundColor DarkGray
    }
    
    # Copiar AceManager
    Copy-Item -Path $ACEMANAGER_SRC -Destination $ACEMANAGER_DEST -Force
    Write-Host "  AceManager.exe copiado a: $ACE_DEST" -ForegroundColor Green
    
    # Crear accesos directos con "Ejecutar como administrador"
    Write-Host "  Creando accesos directos..." -ForegroundColor Cyan
    
    $shortcuts = @(
        @{ Path = $LINK_START; Name = "Menu Inicio" },
        @{ Path = $LINK_DESKTOP; Name = "Escritorio" }
    )
    
    $successCount = 0
    
    foreach ($shortcutInfo in $shortcuts) {
        try {
            # Crear el acceso directo basico
            $shell = New-Object -ComObject WScript.Shell
            $shortcut = $shell.CreateShortcut($shortcutInfo.Path)
            $shortcut.TargetPath = $ACEMANAGER_DEST
            $shortcut.WorkingDirectory = $ACE_DEST
            $shortcut.IconLocation = "$ACEMANAGER_DEST,0"
            $shortcut.Description = "AceManager - Gestor de enlaces Ace Stream"
            $shortcut.Save()
            
            # Modificar el acceso directo para "Ejecutar como administrador"
            $bytes = [System.IO.File]::ReadAllBytes($shortcutInfo.Path)
            $bytes[0x15] = $bytes[0x15] -bor 0x20
            [System.IO.File]::WriteAllBytes($shortcutInfo.Path, $bytes)
            
            Write-Host "    [✓] $($shortcutInfo.Name)" -ForegroundColor Green
            $successCount++
        }
        catch {
            Write-Host "    [✗] $($shortcutInfo.Name): $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    
    if ($successCount -eq 0) {
        Write-Host "  No se pudieron crear accesos directos automaticamente" -ForegroundColor Yellow
        Write-Host "  Puede crear uno manualmente desde: $ACEMANAGER_DEST" -ForegroundColor DarkGray
    }
    elseif ($successCount -lt $shortcuts.Count) {
        Write-Host "  Algunos accesos directos se crearon correctamente" -ForegroundColor Yellow
    }

    # Resumen final
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    if ($hasErrors) {
        Write-Host "  INSTALACION COMPLETADA CON ADVERTENCIAS" -ForegroundColor Yellow
    }
    else {
        Write-Host "  INSTALACION COMPLETADA CON EXITO!" -ForegroundColor Green
    }
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "COMO USAR ACEMANAGER:" -ForegroundColor White
    Write-Host ""
    Write-Host "  OPCION 1: Doble clic en el icono del Escritorio" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  OPCION 2: Busque 'AceManager' en el Menu Inicio" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  OPCION 3: Ejecute directamente desde:" -ForegroundColor Cyan
    Write-Host "  $ACEMANAGER_DEST" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "NOTA IMPORTANTE:" -ForegroundColor Yellow
    Write-Host "  Ace Stream puede requerir REINICIAR el equipo" -ForegroundColor Yellow
    Write-Host "  para funcionar correctamente la primera vez." -ForegroundColor Yellow
}
catch {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "  ERROR CRITICO DURANTE LA INSTALACION" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Detalles del error:" -ForegroundColor Yellow
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Ubicacion de error:" -ForegroundColor Yellow
    Write-Host $_.InvocationInfo.PositionMessage -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "POSIBLES SOLUCIONES:" -ForegroundColor Cyan
    Write-Host "  1. Desactive el antivirus temporalmente" -ForegroundColor White
    Write-Host "  2. Verifique que los 3 archivos .exe esten en la misma carpeta" -ForegroundColor White
    Write-Host "  3. Ejecute desde una ruta sin caracteres especiales" -ForegroundColor White
    Write-Host "  4. Verifique permisos de escritura en: $env:APPDATA" -ForegroundColor White
    Write-Host "  5. Ejecute manualmente cada instalador como administrador" -ForegroundColor White
    Write-Host ""
    
    $hasErrors = $true
}

# Pausa final
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
if ($hasErrors) {
    Write-Host "Revise los mensajes anteriores" -ForegroundColor Yellow
}
else {
    Write-Host "Instalacion completa" -ForegroundColor Green
}
Write-Host "==========================================" -ForegroundColor Cyan

Wait-KeyPress -msg "Presione cualquier tecla para cerrar..."
