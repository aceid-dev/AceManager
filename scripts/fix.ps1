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
$configPath = Join-Path $env:APPDATA "ACEstream\manager"
$configFile = "config.ini"
$filePath   = Join-Path $configPath $configFile

$lists = @('lista_acestream', 'lista_Icastresana', 'lista_ramses')

# Guardar política actual y ajustar temporalmente
$currentPolicy = Get-ExecutionPolicy
if ($currentPolicy -ne 'RemoteSigned') {
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
}

# ---------------------------------------------------------
# Función: Muestra los valores actuales de dominio y lista
# ---------------------------------------------------------
function Show-CurrentConfig {
    if (-not (Test-Path -Path $filePath)) {
        Write-LogError "Archivo NO ENCONTRADO: $filePath"
        return
    }

    $content = Get-Content -Path $filePath -Raw

    $dominioMatch = [regex]::Match($content, '^\s*dominio\s*=\s*(.+)', [System.Text.RegularExpressions.RegexOptions]::Multiline)
    $listaMatch   = [regex]::Match($content, '^\s*lista\s*=\s*(.+)',   [System.Text.RegularExpressions.RegexOptions]::Multiline)

    if ($dominioMatch.Success) {
        Write-LogInfo "Dominio actual: $($dominioMatch.Groups[1].Value.Trim())"
    } else {
        Write-LogWarning "No se encontró clave 'dominio'."
    }

    if ($listaMatch.Success) {
        Write-LogInfo "Lista actual:   $($listaMatch.Groups[1].Value.Trim())"
    } else {
        Write-LogWarning "No se encontró clave 'lista'."
    }
}

# ---------------------------------------------------------
# Función auxiliar: Actualiza o añade una clave en el ini
# ---------------------------------------------------------
function Update-IniKey {
    param(
        [string]$Key,
        [string]$Value
    )

    $content = Get-Content -Path $filePath -Raw

    if ([regex]::IsMatch($content, "^\s*$Key\s*=\s*.+", [System.Text.RegularExpressions.RegexOptions]::Multiline)) {
        $newContent = [regex]::Replace($content, "^\s*$Key\s*=\s*.+", "$Key = $Value", [System.Text.RegularExpressions.RegexOptions]::Multiline)
    } else {
        $newContent = $content.TrimEnd() + "`n$Key = $Value`n"
        Write-LogWarning "Clave '$Key' no existía. Se ha añadido al final."
    }

    if ($content -ne $newContent) {
        Set-Content -Path $filePath -Value $newContent
        Write-LogInfo "Actualizado: $Key = $Value"
    }
}

# ---------------------------------------------------------
# Función: Cambiar rápidamente entre listas predefinidas (1-6)
# ---------------------------------------------------------
function Set-ListChange {
    param([int]$choice)
    $idx = [Math]::Floor(($choice - 1) / 2)
    $others = $lists | Where-Object { $_ -ne $lists[$idx] }
    $dst = $others[($choice - 1) % 2]
    Update-IniKey -Key "lista" -Value $dst
    Read-Host "`nPulsa Enter para continuar..."
}

# ---------------------------------------------------------
# Opción 7: Solo introducir URL completa → separa y aplica dominio + lista
# ---------------------------------------------------------
function Set-ReplacementAutomatic {
    while ($true) {
        $input = Read-Host "`nIntroduce la URL completa de la lista (ej: https://servidor.com/ruta/lista.m3u)"
        $input = $input.Trim()

        if ([string]::IsNullOrWhiteSpace($input)) {
            Write-LogError "No puedes dejarlo vacío."
            continue
        }

        if (-not ($input -match '^https?://')) {
            Write-LogError "La URL debe empezar por http:// o https://"
            continue
        }

        try {
            $uri = [System.Uri]::new($input)

            # Construir la base URL (scheme + host + port si no es estándar)
            $baseUrl = $uri.Scheme + "://" + $uri.Host
            if ($uri.Port -ne -1 -and 
                -not (($uri.Scheme -eq "http" -and $uri.Port -eq 80) -or 
                      ($uri.Scheme -eq "https" -and $uri.Port -eq 443))) {
                $baseUrl += ":" + $uri.Port
            }

            # Obtener la ruta completa
            $fullPath = $uri.AbsolutePath
            
            # Encontrar la última barra para separar directorio de archivo
            $lastSlashIndex = $fullPath.LastIndexOf('/')
            
            if ($lastSlashIndex -eq -1) {
                # No hay barra, toda la ruta es el archivo
                $fileName = $fullPath
            } elseif ($lastSlashIndex -eq 0) {
                # Archivo en la raíz (ej: /fichero.m3u)
                $fileName = $fullPath.Substring(1)
            } else {
                # Hay directorios (ej: /ruta/fichero.m3u)
                $directory = $fullPath.Substring(0, $lastSlashIndex)
                $fileName = $fullPath.Substring($lastSlashIndex + 1)
                $baseUrl += $directory
            }

            if ([string]::IsNullOrWhiteSpace($fileName)) {
                Write-LogError "La URL no termina con un nombre de archivo válido."
                Write-LogInfo "Ejemplos válidos:"
                Write-LogInfo "  https://bit.ly/asdf1234"
                Write-LogInfo "  https://midominio.com/fichero.m3u"
                Write-LogInfo "  https://servidor.com/ruta/lista.m3u"
                continue
            }

            # Aplicar cambios
            Update-IniKey -Key "dominio" -Value $baseUrl
            Update-IniKey -Key "lista"   -Value $fileName

            Write-Host ""
            Write-LogInfo "¡URL aplicada correctamente!"
            Write-LogInfo "   dominio = $baseUrl"
            Write-LogInfo "   lista   = $fileName"

            Read-Host "`nPulsa Enter para continuar..."
            return
        }
        catch {
            Write-LogError "Error al procesar la URL: $($_.Exception.Message)"
            Write-LogInfo "Ejemplos válidos:"
            Write-LogInfo "  https://bit.ly/asdf1234"
            Write-LogInfo "  https://midominio.com/fichero.m3u"
            Write-LogInfo "  https://servidor.com/ruta/lista.m3u"
            Write-Host ""
        }
    }
}

# ---------------------------------------------------------
# Función: Mostrar menú
# ---------------------------------------------------------
function Show-Menu {
    Clear-Host
    Show-CurrentConfig
    Write-Host "`n-----------------------------------"
    Write-Host "     Cambiar lista de canales"
    Write-Host "-----------------------------------"
    for ($i = 0; $i -lt $lists.Count; $i++) {
        $others = $lists | Where-Object { $_ -ne $lists[$i] }
        Write-Host "$($i * 2 + 1). '$($lists[$i])' → '$($others[0])'"
        Write-Host "$($i * 2 + 2). '$($lists[$i])' → '$($others[1])'"
    }
    Write-Host ""
    Write-Host "7. Introducir nueva URL completa"
    Write-Host "0. Salir"
    Write-Host "-----------------------------------"
}

# ---------------------------------------------------------
# Controlador de opciones
# ---------------------------------------------------------
function Invoke-ChoiceHandler {
    param([string]$choice)
    switch ($choice) {
        { $_ -in 1..6 } { Set-ListChange -choice ([int]$_) }
        '7'             { Set-ReplacementAutomatic }
        '0'             {
            Write-LogInfo "Saliendo..."
            return $false
        }
        default         {
            Read-Host "Opción inválida. Pulsa Enter para continuar..." | Out-Null
        }
    }
    return $true
}

# ---------------------------------------------------------
# VERIFICACIÓN DE ARCHIVO
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
    $choice = Read-Host "`nElige una opción"
    $continue = Invoke-ChoiceHandler $choice
}

# Restaurar política original
Set-ExecutionPolicy -Scope Process -ExecutionPolicy $currentPolicy -Force