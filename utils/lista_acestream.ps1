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

function Import-SrcFunctions {
    param(
        [string]$BasePath
    )

    $candidateSrcRoots = @()
    if (-not [string]::IsNullOrWhiteSpace($PSScriptRoot)) {
        $candidateSrcRoots += (Join-Path $PSScriptRoot "..\src")
    }
    if (-not [string]::IsNullOrWhiteSpace($BasePath)) {
        $candidateSrcRoots += (Join-Path $BasePath "..\src")
        $candidateSrcRoots += (Join-Path $BasePath "src")
    }
    if (-not [string]::IsNullOrWhiteSpace($env:APPDATA)) {
        $candidateSrcRoots += (Join-Path $env:APPDATA "ACEStream\manager\src")
    }

    $scriptsToImport = @(
        "Start-AceEngine.ps1",
        "Start-Player.ps1"
    )
    $importedScripts = @{}

    foreach ($srcRoot in ($candidateSrcRoots | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -Unique)) {
        foreach ($scriptName in $scriptsToImport) {
            if ($importedScripts.ContainsKey($scriptName)) {
                continue
            }

            $scriptPath = Join-Path $srcRoot $scriptName
            if (Test-Path -LiteralPath $scriptPath) {
                . $scriptPath
                $importedScripts[$scriptName] = $true
            }
        }
    }
}

function Get-AceStreamIdFromInput {
    param(
        [string]$InputValue
    )

    if ([string]::IsNullOrWhiteSpace($InputValue)) {
        return $null
    }

    $candidate = $InputValue.Trim()

    $directMatch = [regex]::Match(
        $candidate,
        "^(?:acestream://)?(?<id>[A-Za-z0-9]{40})$",
        [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
    )
    if ($directMatch.Success) {
        return $directMatch.Groups["id"].Value
    }

    try {
        $decoded = [System.Uri]::UnescapeDataString($candidate)
    }
    catch {
        $decoded = $candidate
    }

    $queryMatch = [regex]::Match(
        $decoded,
        "(?i)(?:[?&]id=)(?<id>[A-Za-z0-9]{40})(?:$|[&#/])"
    )
    if ($queryMatch.Success) {
        return $queryMatch.Groups["id"].Value
    }

    $schemeMatch = [regex]::Match(
        $decoded,
        "(?i)acestream://(?<id>[A-Za-z0-9]{40})(?:$|[^A-Za-z0-9])"
    )
    if ($schemeMatch.Success) {
        return $schemeMatch.Groups["id"].Value
    }

    return $null
}

function Get-VlcPath {
    $vlcCandidates = @()
    if ($env:ProgramFiles) {
        $vlcCandidates += (Join-Path $env:ProgramFiles "VideoLAN\VLC\vlc.exe")
    }
    if (${env:ProgramFiles(x86)}) {
        $vlcCandidates += (Join-Path ${env:ProgramFiles(x86)} "VideoLAN\VLC\vlc.exe")
    }

    foreach ($candidate in $vlcCandidates) {
        if (-not [string]::IsNullOrWhiteSpace($candidate) -and (Test-Path -LiteralPath $candidate)) {
            return $candidate
        }
    }

    return $null
}

function Start-AcePlayback {
    param(
        [Parameter(Mandatory = $true)]
        [string]$AceId
    )

    $startPlayerCommand = Get-Command -Name "Start-Player" -CommandType Function -ErrorAction SilentlyContinue
    if (-not $startPlayerCommand) {
        return $false
    }

    $defaultVlcPath = $null
    if (-not [string]::IsNullOrWhiteSpace($env:ProgramFiles)) {
        $defaultVlcPath = Join-Path $env:ProgramFiles "VideoLAN\VLC\vlc.exe"
    }

    if ([string]::IsNullOrWhiteSpace($defaultVlcPath) -or (-not (Test-Path -LiteralPath $defaultVlcPath))) {
        return $false
    }

    Start-Player -AceId $AceId | Out-Null
    return $true
}

try {
    try {
        Import-SrcFunctions -BasePath $scriptBase
    }
    catch {
        Stop-SilentExecution -Message "Error al dot-sourcear funciones desde src." -ErrorRecord $_
    }

    if (-not (Get-Command -Name "Start-AceEngine" -CommandType Function -ErrorAction SilentlyContinue)) {
        Stop-SilentExecution -Message "No se encontro la funcion Start-AceEngine en src." -ErrorRecord $null
    }

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
        $engineStarted = [bool](Start-AceEngine)
    }
    catch {
        Stop-SilentExecution -Message "Excepcion al iniciar Ace Engine." -ErrorRecord $_
    }

    if (-not $engineStarted) {
        Stop-SilentExecution -Message "Ace Engine no pudo iniciarse." -ErrorRecord $null
    }

    if ($aceId) {
        try {
            if (Start-AcePlayback -AceId $aceId) {
                exit 0
            }
        }
        catch {
            Stop-SilentExecution -Message "Excepcion al reproducir Ace ID con Start-Player." -ErrorRecord $_
        }
    }

    $vlcPath = Get-VlcPath
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
