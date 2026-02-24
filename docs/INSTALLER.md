# Guia del Instalador (Installer.exe / install.py)

Esta guia describe como funciona el instalador de AceManager en Windows.

El instalador corresponde a:

- `scripts/installer/install.py` (codigo fuente)
- `Installer.exe` (binario generado por build)

## Objetivo

El instalador deja listo el entorno para usar AceManager:

- Verifica e instala (si hace falta) `Ace Stream` y `VLC`.
- Copia `AceManager.exe` y `ListaAceStream.exe` en `%APPDATA%\\ACEStream`.
- Crea accesos directos de `AceManager` en Menu Inicio y Escritorio.

## Archivos esperados en la carpeta de ejecucion

Siempre requeridos:

- `AceManager.exe`
- `ListaAceStream.exe`

Requeridos solo si el software aun no esta instalado:

- Instalador de Ace Stream (`*Ace*Stream*.exe`)
- Instalador de VLC (`vlc*.exe`)

Si Ace Stream y/o VLC ya estan instalados, el instalador omite esos requisitos automaticamente.

## Ejecucion

Desde codigo fuente:

```bash
python scripts/installer/install.py
```

Desde binario:

```text
Installer.exe
```

El instalador solicita elevacion de privilegios (administrador) al inicio.

## Flujo de instalacion

1. Busca archivos necesarios en la carpeta actual (o `Downloads` en escenarios de fallback).
2. Detecta si Ace Stream y VLC ya estan instalados:
   - Ace Stream: `%APPDATA%\\ACEStream\\engine\\ace_engine.exe`
   - VLC: claves de registro de VideoLAN
3. Instala solo lo que falte:
   - Ace Stream: ejecucion normal del instalador
   - VLC: ejecucion en modo silencioso (`/S`)
4. Instala/actualiza ejecutables de AceManager.

## Actualizacion de ejecutables existentes

Si ya existe alguno de estos archivos en destino:

- `%APPDATA%\\ACEStream\\AceManager.exe`
- `%APPDATA%\\ACEStream\\ListaAceStream.exe`

el instalador pregunta si deseas actualizarlos.

- Si respondes `s`, reemplaza el archivo.
- Si respondes `n`, conserva la version existente.

## Resultado esperado

- `%APPDATA%\\ACEStream\\AceManager.exe`
- `%APPDATA%\\ACEStream\\ListaAceStream.exe`
- `%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\AceManager.lnk`
- `%USERPROFILE%\\Desktop\\AceManager.lnk`

## Errores comunes

- "Faltan archivos necesarios":
  - Verifica que `AceManager.exe` y `ListaAceStream.exe` esten junto al instalador.
  - Si Ace Stream o VLC no estan instalados, agrega tambien sus instaladores.
- No eleva permisos:
  - Ejecuta `Installer.exe` como administrador.
