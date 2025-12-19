function Start-AceEngine {
    $enginePath = "$env:APPDATA\ACEStream\engine\ace_engine.exe"

    if (-not (Test-Path $enginePath)) {
        Write-Warning "ACE Engine not found at: $enginePath"
        return $false
    }

    if ($null -eq (Get-Process -Name ace_engine -ErrorAction SilentlyContinue)) {
        Write-Host "Starting engine..."
        Start-Process -FilePath $enginePath -WindowStyle Hidden

        Write-Host "Waiting for engine to start..."
        # Esperar hasta 15 segundos mÃ¡ximo
        $timeout = 15
        $count = 0
        while ($count -lt $timeout -and $null -eq (Get-Process -Name ace_engine -ErrorAction SilentlyContinue)) {
            Start-Sleep -Seconds 1
            $count++
        }

        if ($count -lt $timeout) {
            Write-Host "Engine started"
            return $true
        }
        else {
            Write-Warning "Engine failed to start within $timeout seconds"
            return $false
        }
    }
    else {
        Write-Host "Engine is already running"
        return $true
    }
}

# Ejecutar solo si se llama directamente (no cuando se importa con ".")
if ($MyInvocation.InvocationName -ne '.') {
    Start-AceEngine
}
