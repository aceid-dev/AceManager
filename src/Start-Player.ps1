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
        # Remove acestream:// prefix if present
        $AceId = $AceId -replace '^acestream://', ''
        
        # Validate that AceId is exactly 40 alphanumeric characters
        if ($AceId -notmatch '^[a-zA-Z0-9]{40}$') {
            Write-Warning "Invalid Ace Stream ID. Must be exactly 40 alphanumeric characters."
            Write-Host "Provided ID: $AceId (Length: $($AceId.Length))"
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
