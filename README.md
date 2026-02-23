# Ace Stream PowerShell Manager

Sistema de gestión para Ace Stream Engine mediante scripts de PowerShell que permite controlar el motor de streaming y reproducir contenido mediante VLC.

## Descripción General

Este conjunto de scripts proporciona una interfaz de menú interactiva para gestionar Ace Stream Engine en Windows. Permite iniciar, detener y verificar el estado del motor, así como reproducir contenido utilizando identificadores de Ace Stream a través de VLC Media Player.

## Requisitos

- Windows con PowerShell 5.1 o superior
- Ace Stream Engine instalado en `%APPDATA%\ACEStream\engine\`
- VLC Media Player instalado en `C:\Program Files\VideoLAN\VLC\`

## Estructura de Archivos

```bash
├── main.ps1                    # Script principal con menú interactivo
├── Start-AceEngine.ps1         # Inicia el motor de Ace Stream
├── Stop-AceEngine.ps1          # Detiene el motor de Ace Stream
├── Check-AceEngine.ps1         # Verifica estado del motor
├── Start-Player.ps1            # Inicia VLC con stream de Ace Stream
└── functions/
    └── pause.ps1               # Función auxiliar de pausa
```

## Uso

## Build

La documentacion completa de compilacion esta en `docs/BUILD.md`.

### Ejecución Principal

```powershell
.\main.ps1
```

Este comando inicia el menú interactivo con las siguientes opciones:

1. **Start Ace Stream Engine** - Inicia el motor de Ace Stream
2. **Stop Ace Stream Engine** - Detiene el motor de Ace Stream
3. **Check Ace Stream Engine** - Verifica si el motor está en ejecución
4. **Play Ace Stream ID** - Reproduce un stream mediante su ID
5. **Quit** - Salir del programa

### Ejecución Individual de Scripts

También puedes ejecutar cada función de forma independiente:

```powershell
# Iniciar motor
.\Start-AceEngine.ps1

# Detener motor
.\Stop-AceEngine.ps1

# Reproducir un stream
.\Start-Player.ps1 -AceId "tu_id_de_40_caracteres"
```

---

## Documentación Detallada de Funciones

### 📄 main.ps1

**Propósito**: Script principal que proporciona un menú interactivo para gestionar Ace Stream.

**Funcionalidad**:

- Importa todos los scripts necesarios mediante dot-sourcing (`. $PSScriptRoot\...`)
- Muestra un menú ASCII con 5 opciones
- Valida la entrada del usuario (solo acepta números del 0 al 4)
- Ejecuta la función correspondiente según la selección
- Mantiene un bucle hasta que el usuario selecciona "0" para salir
- Limpia la pantalla entre operaciones para mejor legibilidad

**Validación de entrada**:

- Detecta entradas vacías o inválidas
- Muestra mensaje de error en español: "Opción inválida. Pulsa Enter para continuar..."
- Utiliza expresiones regulares para validar: `^[0-4]$`

---

### 📄 Start-AceEngine.ps1

**Función**: `Start-AceEngine`

**Propósito**: Inicia el proceso de Ace Stream Engine si no está en ejecución.

**Funcionalidad detallada**:

1. **Verificación de existencia**:

   - Busca el ejecutable en: `$env:APPDATA\ACEStream\engine\ace_engine.exe`
   - Si no existe, muestra advertencia y retorna `$false`

2. **Verificación de estado**:

   - Comprueba si el proceso `ace_engine` ya está en ejecución
   - Si ya está corriendo, informa al usuario y retorna `$true`

3. **Inicio del motor**:

   - Inicia el proceso con ventana oculta (`-WindowStyle Hidden`)
   - Implementa un sistema de espera con timeout de 15 segundos
   - Verifica cada segundo si el proceso se ha iniciado

4. **Validación de inicio exitoso**:
   - Si el proceso se inicia antes del timeout: retorna `$true`
   - Si excede el timeout: muestra advertencia y retorna `$false`

**Valores de retorno**:

- `$true`: Motor iniciado exitosamente o ya estaba corriendo
- `$false`: Motor no encontrado o falló al iniciar

**Característica especial**:

- Incluye protección para evitar ejecución automática cuando se importa con dot-sourcing
- Solo se ejecuta automáticamente si se llama directamente

---

### 📄 Stop-AceEngine.ps1

**Función**: `Stop-AceEngine`

**Propósito**: Detiene todos los procesos relacionados con Ace Stream Engine.

**Procesos que detiene**:

1. `ace_engine` - Motor principal de Ace Stream
2. `ace_update` - Servicio de actualización
3. `ace_player` - Reproductor integrado

**Funcionalidad detallada**:

1. **Búsqueda de procesos**:

   - Itera sobre la lista de procesos definidos
   - Utiliza `-ErrorAction SilentlyContinue` para evitar errores si el proceso no existe

2. **Detención forzada**:

   - Usa `Stop-Process -Force` para garantizar el cierre
   - Detiene todas las instancias de cada proceso encontrado
   - Muestra mensaje indicando qué proceso se está deteniendo

3. **Mensajes informativos**:
   - Si ningún proceso está corriendo: "Ace Stream Engine is not running"
   - Si se detienen procesos: "Ace Stream Engine stopped"

**Ventaja del método**:

- Limpieza completa de todos los componentes de Ace Stream
- Previene procesos huérfanos o servicios residuales

---

### 📄 Check-AceEngine.ps1

**Función**: `Test-AceEngine`

**Propósito**: Verifica el estado del motor y ofrece iniciarlo si no está corriendo.

**Funcionalidad detallada**:

1. **Importación de dependencias**:

   - Importa `Start-AceEngine.ps1` para poder iniciar el motor si es necesario

2. **Verificación de estado**:

   - Comprueba si el proceso `ace_engine` está en ejecución
   - Limpia la pantalla antes de mostrar el resultado

3. **Interacción si no está corriendo**:

   - Muestra: "Engine is NOT running"
   - Presenta un menú de confirmación con opciones `&Yes` y `&No`
   - Si el usuario selecciona "Yes" (opción 0), inicia el motor automáticamente
   - Usa `| Out-Null` para suprimir la salida de `Start-AceEngine`

4. **Confirmación si está corriendo**:
   - Simplemente muestra: "Engine is running"

**Parámetros**:

- `[CmdletBinding()]`: Proporciona funcionalidad avanzada de cmdlet

**Uso interactivo**:
Esta función es especialmente útil en el menú principal, ya que combina verificación y acción en un solo paso.

---

### 📄 Start-Player.ps1

**Función**: `Start-Player`

**Propósito**: Reproduce streams de Ace Stream utilizando VLC Media Player.

**Parámetros**:

- `$AceId` (opcional): Identificador de Ace Stream de 40 caracteres alfanuméricos

**Funcionalidad detallada**:

1. **Limpieza de instancias previas**:

   - Busca y detiene cualquier instancia de VLC en ejecución
   - Usa `Stop-Process -Force` para garantizar el cierre
   - Previene conflictos de múltiples streams

2. **Solicitud de ID**:

   - Si no se proporciona `$AceId` como parámetro, solicita al usuario ingresarlo
   - Permite flexibilidad en el uso interactivo y por script

3. **Procesamiento del ID**:

   - Elimina el prefijo `acestream://` si está presente usando regex: `'^acestream://', ''`
   - Normaliza el input para aceptar diferentes formatos

4. **Validación estricta**:

   - Verifica que el ID sea exactamente 40 caracteres alfanuméricos
   - Usa regex: `^[a-zA-Z0-9]{40}$`
   - Si es inválido, muestra:
     - Mensaje de advertencia
     - El ID proporcionado
     - La longitud del ID para facilitar depuración

5. **Verificación de VLC**:

   - Comprueba que VLC existe en: `C:\Program Files\VideoLAN\VLC\vlc.exe`
   - Muestra advertencia si no se encuentra

6. **Inicio del stream**:
   - Construye URL local: `http://127.0.0.1:6878/ace/getstream?id=$AceId`
   - Inicia VLC con el stream como argumento
   - Muestra confirmación con el ID utilizado

**Características especiales**:

- Incluye protección contra ejecución automática cuando se importa
- Proporciona mensajes claros de error para facilitar troubleshooting

**Formato de URL**:
El stream se solicita al motor local de Ace Stream en el puerto 6878, que es el puerto estándar del motor.

---

## Flujo de Trabajo Típico

1. **Usuario ejecuta `main.ps1`**
2. **Selecciona opción 1**: Inicia el motor de Ace Stream
   - El script verifica si ya está corriendo
   - Lo inicia si es necesario
   - Espera confirmación de inicio exitoso
3. **Selecciona opción 4**: Reproduce un stream
   - Verifica automáticamente que el motor esté corriendo
   - Solicita el ID del stream
   - Detiene VLC si está corriendo
   - Inicia VLC con el nuevo stream
4. **Selecciona opción 2**: Cuando termina, detiene el motor
   - Cierra todos los procesos relacionados
5. **Selecciona opción 0**: Sale del programa

## Notas Técnicas

### Puerto y Comunicación

- Ace Stream Engine escucha en `127.0.0.1:6878`
- La comunicación con el motor es mediante HTTP local
- No se requiere configuración de firewall para uso local

### Manejo de Errores

- Todos los scripts usan `-ErrorAction SilentlyContinue` para operaciones que pueden fallar
- Se proporcionan mensajes claros en caso de error
- Se validan rutas de archivos antes de ejecutar

### Seguridad

- Los procesos se detienen con `-Force` para garantizar limpieza completa
- VLC se inicia con URL local únicamente
- No se exponen puertos externos

## Posibles Mejoras Futuras

- Agregar logging de operaciones
- Implementar configuración de rutas personalizadas
- Añadir lista de streams favoritos
- Implementar verificación de conectividad del motor
- Agregar soporte para múltiples reproductores

## Solución de Problemas

### El motor no inicia

- Verificar que Ace Stream esté instalado correctamente
- Comprobar la ruta: `%APPDATA%\ACEStream\engine\ace_engine.exe`
- Ejecutar como administrador si hay problemas de permisos

### VLC no se encuentra

- Verificar instalación de VLC en `C:\Program Files\VideoLAN\VLC\`
- Si está en otra ubicación, modificar `$vlcPath` en `Start-Player.ps1`

### El stream no reproduce

- Verificar que el motor esté corriendo (opción 3)
- Comprobar que el ID de Ace Stream sea válido (40 caracteres)
- Verificar conectividad a internet para streams remotos

## Licencia y Créditos

Scripts desarrollados para facilitar la gestión de Ace Stream Engine en entornos Windows mediante PowerShell.

---

**Versión**: 1.0  
**Compatible con**: PowerShell 5.1+, Windows 10/11
