# utils\lista_acestream.ps1

# Ruta absoluta al script actual
$scriptDir = $PSScriptRoot  # = ...\ACEStream\utils

# Ruta al directorio raíz (un nivel arriba)
$rootDir = Split-Path $scriptDir -Parent
$functionPath = Join-Path $rootDir "Start-AceEngine.ps1"

# Validar existencia
if (-not (Test-Path $functionPath)) {
    Write-Host "Error: No se encontro Start-AceEngine.ps1 en: $functionPath" -ForegroundColor Red
    Pause
    exit 1
}

# Cargar la función
. $functionPath

# Verificar que se cargó
if (-not (Get-Command Start-AceEngine -ErrorAction SilentlyContinue)) {
    Write-Host "Error: La funcion 'Start-AceEngine' no se cargo." -ForegroundColor Red
    Pause
    exit 1
}

# Intentar iniciar el motor
if (Start-AceEngine) {
    $url = "https://aceid.short.gy/lista_acestream"
    $url = $url.Trim()
    
    $vlcPath = "${env:ProgramFiles}\VideoLAN\VLC\vlc.exe"

    if (Test-Path $vlcPath) {
        Start-Process -FilePath $vlcPath -ArgumentList "`"$url`"", "--no-playlist-autostart"
        Write-Host "VLC iniciado con la lista" -ForegroundColor Green
    } else {
        Write-Host "Error: VLC no encontrado en: $vlcPath" -ForegroundColor Red
        Pause
    }
} else {
    Write-Host "Error: No se pudo iniciar el motor ACEStream." -ForegroundColor Red
    Pause
}

