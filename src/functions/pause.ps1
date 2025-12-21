
function Pause {
    param($message = 'Press Enter to continue...')
    Read-Host -Prompt $message | Out-Null
    Write-Host ""
}
