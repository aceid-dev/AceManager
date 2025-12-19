. "$PSScriptRoot\Stop-AceEngine.ps1"
. "$PSScriptRoot\Check-AceEngine.ps1"
. "$PSScriptRoot\Start-AceEngine.ps1"
. "$PSScriptRoot\Start-Player.ps1"
. "$PSScriptRoot\functions\pause.ps1"

$MainMenu = {
    Write-Host " ***************************"
    Write-Host " *           Menu          *" 
    Write-Host " ***************************" 
    Write-Host 
    Write-Host " 1.) Start Ace Stream Engine" 
    Write-Host " 2.) Stop Ace Stream Engine"
    Write-Host " 3.) Check Ace Stream Engine" 
    Write-Host " 4.) Play Ace Stream ID" 
    Write-Host " 0.) Quit"
    Write-Host 
    Write-Host "Select an option and press Enter: " -NoNewline
}

Clear-Host

# Iniciar el engine automáticamente al abrir la aplicación
Write-Host "Initializing Ace Stream Engine..." -ForegroundColor Cyan
Start-AceEngine | Out-Null
Write-Host ""

do { 
    Invoke-Command $MainMenu
    $Select = Read-Host

    if (($Select -eq "") -or ($Select -notmatch "^[0-4]$")) {
        Read-Host "Opción inválida. Pulsa Enter para continuar..." | Out-Null
        Clear-Host
    }
    else {
        switch ($Select) {
            1 {
                Start-AceEngine | Out-Null
                Pause
                Clear-Host
            }
            2 {
                Stop-AceEngine | Out-Null
                Pause
                Clear-Host
            }
            3 {
                Test-AceEngine | Out-Null
                Pause
                Clear-Host
            }
            4 {
                Test-AceEngine | Out-Null
                Start-Player | Out-Null
                Pause
                Clear-Host
            }
        }
    }
}
while ($Select -ne 0)