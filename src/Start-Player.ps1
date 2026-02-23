function Start-Player {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false, Position = 0)]
        [string]$AceId
    )

    # Stop any existing VLC instances
    $processList = Get-Process "vlc" -ErrorAction SilentlyContinue
    if ($processList) {
        Write-Host "Stopping existing VLC instance..."
        $processList | ForEach-Object {
            Stop-Process -Id $_.ID -Force
        }
    }
    
    # Prompt for Ace Stream ID if not provided
    if (-not $AceId) {
        $AceId = Read-Host -Prompt 'Enter Ace Stream ID'
    }

    if ($AceId) {
        $rawInput = $AceId.Trim()
        $decodedInput = $rawInput
        try {
            $decodedInput = [System.Uri]::UnescapeDataString($rawInput)
        }
        catch {
            $decodedInput = $rawInput
        }

        # Accept pure ID, acestream://ID, and URLs containing id=<ID>
        $idMatch = [regex]::Match(
            $decodedInput,
            '(?i)^(?:acestream://)?(?<id>[a-zA-Z0-9]{40})$'
        )

        if (-not $idMatch.Success) {
            $idMatch = [regex]::Match(
                $decodedInput,
                '(?i)(?:[?&]id=)(?<id>[a-zA-Z0-9]{40})(?:$|[&#/])'
            )
        }

        if (-not $idMatch.Success) {
            $idMatch = [regex]::Match(
                $decodedInput,
                '(?i)acestream://(?<id>[a-zA-Z0-9]{40})(?:$|[^a-zA-Z0-9])'
            )
        }

        if ($idMatch.Success) {
            $AceId = $idMatch.Groups['id'].Value
        }
        else {
            $AceId = $decodedInput
        }

        # Validate that AceId is exactly 40 alphanumeric characters
        if ($AceId -notmatch '^[a-zA-Z0-9]{40}$') {
            Write-Warning "Invalid Ace Stream ID. Must be exactly 40 alphanumeric characters."
            Write-Host "Provided value: $rawInput"
            Write-Host "Resolved ID: $AceId (Length: $($AceId.Length))"
            return
        }

        $vlcPath = "$Env:ProgramFiles\VideoLAN\VLC\vlc.exe"
        if (Test-Path $vlcPath) {
            Start-Process -FilePath $vlcPath -ArgumentList "http://127.0.0.1:6878/ace/getstream?id=$AceId"
            Write-Host "Starting stream with ID: $AceId"
        }
        else {
            Write-Warning "VLC not found at: $vlcPath"
        }
    }
    else {
        Write-Host "No Ace Stream ID provided"
    }
}
# Ejecutar solo si se llama directamente (no cuando se importa con ".")
if ($MyInvocation.InvocationName -ne '.') {
    Start-Player
}
