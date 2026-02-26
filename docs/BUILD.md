# Guia de Build (Python + PyInstaller)

Esta guia explica como generar:

- `AceManager.exe`
- `ListaAceStream.exe`
- `Installer.exe`
- `Fix.exe`
- `AceManager.zip`

Contenido de `AceManager.zip`:

- `AceManager.exe`
- `ListaAceStream.exe`
- `Fix.exe`
- `config.ini`

Los ejecutables son autocontenidos y no requieren Python en el equipo final.

## Requisitos

- Windows
- Python 3.10+

La herramienta de build ahora crea automaticamente `/.venv-build` e instala dependencias desde `requirements-build.txt`.

Instalacion manual (opcional) de dependencias de build:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt
```

## Build rapido

Desde la raiz del repo:

```bash
python scripts/build/build.py
```

Genera por defecto:

- `AceManager.exe`
- `ListaAceStream.exe`
- `Installer.exe`
- `Fix.exe`
- `AceManager.zip`

El empaquetado incluye todo menos el instalador (`Installer.exe`).

## Parametros de la herramienta de build

`build.py` acepta:

- `--app-version A.B.C.D`: version de archivo de los EXE (por defecto `1.0.0.0`)
- `--targets All|AceManager|ListaAceStream|Installer|Fix`: objetivos a compilar
- `--skip-package`: omite la generacion del ZIP

Ejemplos:

```bash
# Solo AceManager.exe
python scripts/build/build.py --targets AceManager

# Solo Installer.exe
python scripts/build/build.py --targets Installer

# Solo ListaAceStream.exe
python scripts/build/build.py --targets ListaAceStream

# Solo Fix.exe
python scripts/build/build.py --targets Fix

# Ambos EXE sin ZIP
python scripts/build/build.py --targets AceManager Installer ListaAceStream Fix --skip-package

# Build completo con version explicita
python scripts/build/build.py --app-version 1.2.3.0
```

## Reglas de empaquetado

- El ZIP solo se crea si se compilan todos los objetivos y no se usa `--skip-package`.
- `AceManager.zip` incluye `AceManager.exe`, `ListaAceStream.exe`, `Fix.exe` y `config.ini`.
- En GitHub Release se publican: `Installer.exe` y `AceManager.zip`.
- Si falta `config.ini`, el build genera uno por defecto.
- Si un ZIP esta en uso, se genera con sufijo `<timestamp>`.

## CI/CD y release

- Workflow: `.github/workflows/build-exe.yml`
- Herramienta de build: `scripts/build/build.py`
- Semantic Release: `.releaserc.json`

Comando usado por Semantic Release:

```bash
python ./scripts/build/build.py --app-version ${nextRelease.version}.0
```

## Ver tambien

- Instalador: [INSTALLER.md](INSTALLER.md)
- Fix de config: [FIXCONFIG.md](FIXCONFIG.md)
