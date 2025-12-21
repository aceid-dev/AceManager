# utils\lista_acestream.ps1
# ---------------------------------------------------------
# Localizar el archivo de configuración al lado del ejecutable
$iniPath = Join-Path $PSScriptRoot "config.ini"

if (Test-Path $iniPath) {
    try {
        # Leer el contenido y convertirlo en un objeto de configuración
        $iniContent = Get-Content $iniPath -Raw
        $config = ConvertFrom-StringData -StringData $iniContent
        
        # Extraer y limpiar valores
        $dominioBase = $config.dominio.Trim().TrimEnd('/')
        $entradaLista = $config.lista.Trim()

        # LÓGICA INTELIGENTE: Detectar si es una URL completa o un nombre corto
        if ($entradaLista -match "^https?://") {
            $urlFinal = $entradaLista
            Write-Host "Cargando URL externa personalizada: $urlFinal" -ForegroundColor Yellow
        } else {
            $urlFinal = "$dominioBase/$entradaLista.m3u"
            Write-Host "Cargando lista desde servidor: $entradaLista" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "Error: El formato de config.ini es incorrecto (Clave = Valor)." -ForegroundColor Red
        Pause; exit 1
    }
} else {
    Write-Host "Error crítico: No se encuentra config.ini." -ForegroundColor Red
    Pause; exit 1
}

# --- Lanzar AceEngine y VLC ---
. $PSScriptRoot "..\src\Start-AceEngine.ps1"

if (Start-AceEngine) {
    $vlcPath = "${env:ProgramFiles}\VideoLAN\VLC\vlc.exe"
    if (Test-Path $vlcPath) {
        Start-Process -FilePath $vlcPath -ArgumentList "`"$urlFinal`"", "--no-playlist-autostart"
        Write-Host "VLC iniciado con la URL: $urlFinal" -ForegroundColor Green
    } else {
        Write-Host "Error: VLC no encontrado." -ForegroundColor Red
        Pause
    }
}