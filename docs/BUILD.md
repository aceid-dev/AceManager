# Guia de Build

Esta guia explica como generar `AceManager.exe`, `ListaAceStream.exe` y `AceManager.zip`.

## Resumen

- Script de build: `.github/scripts/build.ps1`
- Shells soportadas: Windows PowerShell 5.1 y PowerShell 7
- Comportamiento por defecto (compatible con CI/CD): compila ambos EXE y genera `AceManager.zip`

## Requisitos

- Windows
- PowerShell 5.1+ o PowerShell 7+
- Modulo `ps2exe` instalado

Instalar `ps2exe`:

```powershell
Install-Module ps2exe -Scope CurrentUser -Force -AllowClobber
```

## Build Rapido

Desde la raiz del repo:

```powershell
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File .github/scripts/build.ps1
```

Genera:

- `AceManager.exe`
- `ListaAceStream.exe`
- `AceManager.zip`

## Parametros del Script

`build.ps1` acepta:

- `-AppVersion <A.B.C.D>`: version de archivo para los EXE
- `-Targets <All|AceManager|ListaAceStream>`: objetivos a compilar
- `-SkipPackage`: omite la generacion del ZIP

Ejemplos:

```powershell
# Solo ListaAceStream.exe
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File .github/scripts/build.ps1 -Targets ListaAceStream

# Solo AceManager.exe
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File .github/scripts/build.ps1 -Targets AceManager

# Ambos EXE sin ZIP
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File .github/scripts/build.ps1 -Targets AceManager,ListaAceStream -SkipPackage

# Build completo con version explicita
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File .github/scripts/build.ps1 -AppVersion 1.2.3.0
```

## Reglas de Empaquetado

- El ZIP solo se genera cuando se compilan ambos objetivos y no se usa `-SkipPackage`.
- Si falta `config.ini` en la raiz del repo, el build genera uno por defecto.
- Si `AceManager.zip` esta bloqueado/en uso, el build crea un ZIP con timestamp.

## Compatibilidad con CI/CD

La invocacion por defecto se mantiene compatible:

```powershell
powershell ./.github/scripts/build.ps1 -AppVersion ${nextRelease.version}.0
```

Ese comando es el que usa Semantic Release en `.releaserc.json`.

Archivos relacionados:

- `.github/workflows/build-exe.yml`
- `.releaserc.json`

## Notas

- `ListaAceStream.exe` se compila con `-noConsole` (sin ventana de consola).
- El build usa archivos temporales `temp_*.ps1` y los limpia al final.
- En errores criticos, el script muestra detalle y linea donde fallo.
