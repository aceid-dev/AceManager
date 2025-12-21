function Stop-AceEngine {
    # Define list of processes to stop
    $processNames = @(
        "ace_engine",
        "ace_update",
        "ace_player"
    )
    
    $anyStopped = $false
    $anyRunning = $false
    
    foreach ($processName in $processNames) {
        $processList = Get-Process $processName -ErrorAction SilentlyContinue
        
        if ($processList) {
            $anyRunning = $true
            Write-Host "Stopping $processName..."
            
            # Force stop all processes
            $processList | ForEach-Object {
                Stop-Process -Id $_.ID -Force
            }
            $anyStopped = $true
        }
    }
    
    if (-not $anyRunning) {
        Write-Host "Ace Stream Engine is not running"
    }
    elseif ($anyStopped) {
        Write-Host "Ace Stream Engine stopped"
    }
}
