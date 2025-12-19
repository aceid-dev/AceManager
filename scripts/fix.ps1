# --- FUNCIONES DE LOG ---
function Write-LogError {
    param([string]$Message)
    Write-Host "$Message`n" -ForegroundColor Red
}

function Write-LogWarning {
    param([string]$Message)
    Write-Host "$Message`n" -ForegroundColor Yellow
}

function Write-LogInfo {
    param([string]$Message)
    Write-Host "$Message`n" -ForegroundColor Cyan
}

# --- CONFIGURACIÓN INICIAL ---
$filePath = "$env:APPDATA\ACEstream\manager\utils\lista_acestream.ps1"
$lists = @('lista_acestream', 'lista_Icastresana', 'lista_ramses')
# Guardar política actual y ajustar temporalmente
$currentPolicy = Get-ExecutionPolicy
if ($currentPolicy -ne 'RemoteSigned') {
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
}
# ---------------------------------------------------------
# Función: Obtiene la URL actual y la muestra
# ---------------------------------------------------------
function Show-URL {
    if (-not (Test-Path -Path $filePath)) {
        Write-LogError "Archivo NO ENCONTRADO: $filePath"
        return $null
    }
    $content = Get-Content -Path $filePath -Raw
    if ([string]::IsNullOrWhiteSpace($content)) {
        Write-LogWarning "Archivo EXISTE pero está vacío."
        return $null
    }
    # Buscar URL
    $url = [regex]::Matches($content, 'https?://[^\s"<>]+') | 
        Select-Object -ExpandProperty Value -First 1
    if ($url) {
        Write-LogInfo "URL Actual: $url"
    }
    else {
        Write-LogWarning "Archivo encontrado, pero NO contiene URL válida."
    }
    return $url
}
# ---------------------------------------------------------
# Función: Reemplaza texto en el archivo
# ---------------------------------------------------------
function Update-InFile {
    param([string]$Old, [string]$New)
    $content = Get-Content -Path $filePath -Raw
    if ($content -notlike "*$Old*") {
        Write-LogError "No se encontró '$Old' en el archivo."
        return
    }
    $newContent = $content -replace [regex]::Escape($Old), $New
    if ($content -ne $newContent) {
        Set-Content -Path $filePath -Value $newContent
        Write-LogInfo "Archivo actualizado: '$Old' -> '$New'"
    }
    else {
        Write-LogInfo "No hubo cambios."
    }
    Show-URL | Out-Null
    Read-Host "`nPulsa Enter para continuar..."
    
}
# ---------------------------------------------------------
# Función: Cambiar una lista predefinida (opciones 1-6)
# ---------------------------------------------------------
function Set-ListChange {
    param([int]$choice)
    $idx = [Math]::Floor(($choice - 1) / 2)
    $src = $lists[$idx]
    $others = $lists | Where-Object { $_ -ne $src }
    $dst = $others[($choice - 1) % 2]
    Update-InFile -Old $src -New $dst
}
# ---------------------------------------------------------
# Función: Reemplazo automático (machacar valor actual)
# ---------------------------------------------------------
function Set-ReplacementAutomatic {
    $current = Show-URL
    if ($current) {
        while ($true) {
            $new = Read-Host "Introduce la NUEVA URL (solo http/https)"
            if ([string]::IsNullOrWhiteSpace($new)) {
                Write-LogError "No puedes dejarlo vacío. Introduce una URL válida."
                continue
            }
            if ($new -match '^(https?://\S+)$') {
                break
            }
            Write-LogError "URL inválida. Debe empezar por http:// o https://"
            Write-LogInfo "Ejemplo:"
            Write-LogWarning "  - https://servidor.com/lista.m3u"
        }
        Update-InFile -Old $current -New $new
    }
    else {
        Set-ReplacementManual
    }
}
# ---------------------------------------------------------
# Función: Reemplazo manual clásico
# ---------------------------------------------------------
function Set-ReplacementManual {
    Write-LogWarning "No se encontró un valor actual. Reemplazo manual clásico:"
    $old = Read-Host "`nTexto a buscar"
    $new = Read-Host "Texto nuevo"
    if (-not $old) {
        Write-LogWarning "Operación cancelada (texto a buscar vacío)."
        Start-Sleep -Seconds 1
        return
    }
    Update-InFile -Old $old -New $new
}
# ---------------------------------------------------------
# Función: Mostrar menú
# ---------------------------------------------------------
function Show-Menu {
    Show-URL | Out-Null
    Write-Host "-----------------------------------"
    Write-Host "     Cambiar lista de canales"
    Write-Host "-----------------------------------"
    for ($i = 0; $i -lt $lists.Count; $i++) {
        $others = $lists | Where-Object { $_ -ne $lists[$i] }
        Write-Host "$($i * 2 + 1). '$($lists[$i])' -> '$($others[0])'"
        Write-Host "$($i * 2 + 2). '$($lists[$i])' -> '$($others[1])'"
    }
    Write-Host ""
    Write-Host "7. Reemplazo automático (machacar valor actual)"
    Write-Host "0. Salir"
    Write-Host "-----------------------------------"
}
# ---------------------------------------------------------
# Función: Controlador de opciones
# ---------------------------------------------------------
function Invoke-ChoiceHandler {
    param([string]$choice)
    switch ($choice) {
        { $_ -in 1..6 } {
            Set-ListChange -choice $choice
        }
        '7' {
            Set-ReplacementAutomatic
        }
        '0' {
            Write-LogInfo "Saliendo..."
            return $false
        }
        default {
            # Esperar a que el usuario pulse Enter
            Read-Host "Opción inválida. Pulsa Enter para continuar..." | Out-Null
        }
    }
    return $true
}
# ---------------------------------------------------------
# VERIFICACIÓN DE EXISTENCIA DEL ARCHIVO
# ---------------------------------------------------------
if (-not (Test-Path -Path $filePath)) {
    Write-LogError "El archivo '$filePath' no existe."
    Read-Host "Pulsa Enter para salir..."
    
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy $currentPolicy -Force
    exit
}
# ---------------------------------------------------------
# BUCLE PRINCIPAL
# ---------------------------------------------------------

$continue = $true
while ($continue) {
    Show-Menu
    $choice = Read-Host "Elige una opción"
    
    $continue = Invoke-ChoiceHandler $choice
}
# Restaurar política original
Set-ExecutionPolicy -Scope Process -ExecutionPolicy $currentPolicy -Force
