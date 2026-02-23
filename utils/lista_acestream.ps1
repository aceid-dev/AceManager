# utils\lista_acestream.ps1

# Resolver ruta base de forma robusta (script .ps1 o exe compilado)
$scriptBase = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($scriptBase) -and $MyInvocation.MyCommand.Path) {
    $scriptBase = Split-Path -Parent $MyInvocation.MyCommand.Path
}
if ([string]::IsNullOrWhiteSpace($scriptBase)) {
    $scriptBase = [System.AppDomain]::CurrentDomain.BaseDirectory
}
if ([string]::IsNullOrWhiteSpace($scriptBase)) {
    $scriptBase = (Get-Location).Path
}

$logPath = Join-Path $scriptBase "lista_acestream_error.log"

function Write-ErrorLog {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,
        [System.Management.Automation.ErrorRecord]$ErrorRecord
    )

    $lines = @()
    $lines += "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"

    if ($ErrorRecord) {
        if ($ErrorRecord.Exception -and $ErrorRecord.Exception.Message) {
            $lines += "Exception: $($ErrorRecord.Exception.Message)"
        }
        if ($ErrorRecord.InvocationInfo -and $ErrorRecord.InvocationInfo.PositionMessage) {
            $lines += "Position: $($ErrorRecord.InvocationInfo.PositionMessage)"
        }
        if ($ErrorRecord.ScriptStackTrace) {
            $lines += "Stack: $($ErrorRecord.ScriptStackTrace)"
        }
    }

    $lines += ""
    Add-Content -LiteralPath $logPath -Value ($lines -join [Environment]::NewLine) -Encoding UTF8
}

function Stop-SilentExecution {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,
        [System.Management.Automation.ErrorRecord]$ErrorRecord
    )

    Write-ErrorLog -Message $Message -ErrorRecord $ErrorRecord
    exit 1
}

function Start-AceEngineSilent {
    param(
        [int]$TimeoutSeconds = 15
    )

    if (Get-Process -Name "ace_engine" -ErrorAction SilentlyContinue) {
        return $true
    }

    $enginePath = Join-Path $env:APPDATA "ACEStream\engine\ace_engine.exe"
    if (-not (Test-Path -LiteralPath $enginePath)) {
        return $false
    }

    Start-Process -FilePath $enginePath -WindowStyle Hidden -ErrorAction Stop | Out-Null

    $elapsed = 0
    while ($elapsed -lt $TimeoutSeconds) {
        if (Get-Process -Name "ace_engine" -ErrorAction SilentlyContinue) {
            return $true
        }
        Start-Sleep -Seconds 1
        $elapsed++
    }

    return $false
}

function Get-AceStreamIdFromInput {
    param(
        [string]$InputValue
    )

    if ([string]::IsNullOrWhiteSpace($InputValue)) {
        return $null
    }

    $candidate = $InputValue.Trim()

    # Caso directo: ID puro o acestream://ID
    $directMatch = [regex]::Match(
        $candidate,
        "^(?:acestream://)?(?<id>[A-Za-z0-9]{40})$",
        [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
    )
    if ($directMatch.Success) {
        return $directMatch.Groups["id"].Value
    }

    # Decodificar por si viene como URL encoded
    try {
        $decoded = [System.Uri]::UnescapeDataString($candidate)
    }
    catch {
        $decoded = $candidate
    }

    # URL tipo VLC: ...?id=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    $queryMatch = [regex]::Match(
        $decoded,
        "(?i)(?:[?&]id=)(?<id>[A-Za-z0-9]{40})(?:$|[&#/])"
    )
    if ($queryMatch.Success) {
        return $queryMatch.Groups["id"].Value
    }

    # Texto con acestream://ID incrustado
    $schemeMatch = [regex]::Match(
        $decoded,
        "(?i)acestream://(?<id>[A-Za-z0-9]{40})(?:$|[^A-Za-z0-9])"
    )
    if ($schemeMatch.Success) {
        return $schemeMatch.Groups["id"].Value
    }

    return $null
}

try {
    # Buscar config.ini en rutas candidatas
    $iniCandidates = @(
        (Join-Path $scriptBase "config.ini"),
        (Join-Path $env:APPDATA "ACEStream\manager\config.ini")
    )

    $iniPath = $null
    foreach ($candidate in $iniCandidates) {
        if (-not [string]::IsNullOrWhiteSpace($candidate) -and (Test-Path -LiteralPath $candidate)) {
            $iniPath = $candidate
            break
        }
    }

    if (-not $iniPath) {
        Stop-SilentExecution -Message "No se encuentra config.ini en rutas esperadas." -ErrorRecord $null
    }

    # Leer configuracion
    $iniContent = Get-Content -LiteralPath $iniPath -Raw -ErrorAction Stop
    $config = ConvertFrom-StringData -StringData $iniContent

    $dominioBase = [string]$config.dominio
    $entradaLista = [string]$config.lista
    $dominioBase = $dominioBase.Trim().TrimEnd("/")
    $entradaLista = $entradaLista.Trim()

    if ([string]::IsNullOrWhiteSpace($entradaLista)) {
        Stop-SilentExecution -Message "La clave 'lista' en config.ini esta vacia." -ErrorRecord $null
    }

    $aceId = Get-AceStreamIdFromInput -InputValue $entradaLista
    if ($aceId) {
        $urlFinal = "http://127.0.0.1:6878/ace/getstream?id=$aceId"
    }
    elseif ($entradaLista -match "^https?://") {
        $urlFinal = $entradaLista
    }
    else {
        if ([string]::IsNullOrWhiteSpace($dominioBase)) {
            Stop-SilentExecution -Message "La clave 'dominio' en config.ini esta vacia." -ErrorRecord $null
        }

        $urlFinal = "$dominioBase/$($entradaLista.TrimStart('/'))"
    }

    try {
        $engineStarted = Start-AceEngineSilent -TimeoutSeconds 15
    }
    catch {
        Stop-SilentExecution -Message "Excepcion al iniciar Ace Engine en modo silencioso." -ErrorRecord $_
    }

    if (-not $engineStarted) {
        Stop-SilentExecution -Message "Ace Engine no pudo iniciarse en modo silencioso." -ErrorRecord $null
    }

    # Resolver VLC
    $vlcCandidates = @()
    if ($env:ProgramFiles) {
        $vlcCandidates += (Join-Path $env:ProgramFiles "VideoLAN\VLC\vlc.exe")
    }
    if (${env:ProgramFiles(x86)}) {
        $vlcCandidates += (Join-Path ${env:ProgramFiles(x86)} "VideoLAN\VLC\vlc.exe")
    }

    $vlcPath = $null
    foreach ($candidate in $vlcCandidates) {
        if (-not [string]::IsNullOrWhiteSpace($candidate) -and (Test-Path -LiteralPath $candidate)) {
            $vlcPath = $candidate
            break
        }
    }

    if (-not $vlcPath) {
        Stop-SilentExecution -Message "VLC no encontrado en Program Files." -ErrorRecord $null
    }

    if ([string]::IsNullOrWhiteSpace($urlFinal)) {
        Stop-SilentExecution -Message "URL final vacia tras procesar config.ini." -ErrorRecord $null
    }

    Start-Process -FilePath $vlcPath -ArgumentList "`"$urlFinal`"", "--no-playlist-autostart" -ErrorAction Stop | Out-Null
    exit 0
}
catch {
    Stop-SilentExecution -Message "Error no controlado en lista_acestream.ps1." -ErrorRecord $_
}
