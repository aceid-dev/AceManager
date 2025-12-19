# utils\Create-Shortcut.ps1
$startMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
# Ruta base de la app (raíz del proyecto)
$appRoot = "$env:APPDATA\ACEStream\manager"
$utilsPath = "$appRoot\utils"
# Rutas de scripts
$mainScriptPath = "$appRoot\main.ps1"
$listaScriptPath = "$utilsPath\lista_acestream.ps1"
$iconPath = "$utilsPath\icon.ico"
# Verificar que los scripts existen
if (-not (Test-Path $mainScriptPath)) {
    Write-Error "Error: Script no encontrado: $mainScriptPath"
    exit 1
}
if (-not (Test-Path $listaScriptPath)) {
    Write-Error "Error: Script no encontrado: $listaScriptPath"
    exit 1
}
# Crear objeto COM para accesos directos
$ws = New-Object -ComObject WScript.Shell
# ============================================
# 1. Acceso directo: "Lista Ace Stream.lnk"
# ============================================
$shortcutPath = "$startMenuPath\Lista Ace Stream.lnk"
$shortcut = $ws.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "powershell.exe"
$shortcut.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$listaScriptPath`""
$shortcut.WorkingDirectory = $appRoot
$shortcut.IconLocation = $iconPath
$shortcut.WindowStyle = 7  # Minimizado
$shortcut.Description = "Lanzar lista Ace Stream"
$shortcut.Save()
# ============================================
# Verificación
# ============================================
Write-Host ""
if (Test-Path $shortcutPath) {
    Write-Host "El acceso directo 'Lista Ace Stream.lnk' se ha creado correctamente." -ForegroundColor Green
}
else {
    Write-Host "Error al crear 'Lista Ace Stream.lnk'." -ForegroundColor Red
}
Write-Host ""
Write-Host "Ubicación: $startMenuPath" -ForegroundColor Cyan
