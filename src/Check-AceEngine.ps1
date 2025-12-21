. "$PSScriptRoot\Start-AceEngine.ps1"

function Test-AceEngine {
    [CmdletBinding()]
    param()

    if ($Null -eq (Get-Process ace_engine -ErrorAction SilentlyContinue)) {
        Write-Host "Engine is NOT running"
        
        $question = "Do you want to start engine?"
        $choices = '&Yes', '&No'
        $decision = $Host.UI.PromptForChoice($title, $question, $choices, 0)
        
        if ($decision -eq 0) {
            Start-AceEngine | Out-Null
        }
    }
    else {
        Write-Host "Engine is running"
    }
}
