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
# 1. Acceso directo: "Ace Stream.lnk" (main.ps1)
# ============================================
$shortcut1Path = "$startMenuPath\Ace Stream.lnk"
$shortcut1 = $ws.CreateShortcut($shortcut1Path)
$shortcut1.TargetPath = "powershell.exe"
$shortcut1.Arguments = "-ExecutionPolicy Bypass -NoProfile -File `"$mainScriptPath`""
$shortcut1.WorkingDirectory = $appRoot
$shortcut1.IconLocation = $iconPath
$shortcut1.Description = "Ace Stream Manager"
$shortcut1.Save()
# ============================================
# 2. Acceso directo: "Lista Ace Stream.lnk"
# ============================================
$shortcut2Path = "$startMenuPath\Lista Ace Stream.lnk"
$shortcut2 = $ws.CreateShortcut($shortcut2Path)
$shortcut2.TargetPath = "powershell.exe"
$shortcut2.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$listaScriptPath`""
$shortcut2.WorkingDirectory = $appRoot
$shortcut2.IconLocation = $iconPath
$shortcut2.WindowStyle = 7  # Minimizado
$shortcut2.Description = "Lanzar lista Ace Stream"
$shortcut2.Save()
# ============================================
# Verificación
# ============================================
Write-Host ""
if (Test-Path $shortcut1Path) {
    Write-Host "El acceso directo 'Ace Stream.lnk' se ha creado correctamente." -ForegroundColor Green
}
else {
    Write-Host "Error al crear 'Ace Stream.lnk'." -ForegroundColor Red
}
if (Test-Path $shortcut2Path) {
    Write-Host "El acceso directo 'Lista Ace Stream.lnk' se ha creado correctamente." -ForegroundColor Green
}
else {
    Write-Host "Error al crear 'Lista Ace Stream.lnk'." -ForegroundColor Red
}
Write-Host ""
Write-Host "Ubicación: $startMenuPath" -ForegroundColor Cyan
