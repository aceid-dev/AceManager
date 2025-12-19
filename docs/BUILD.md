# Guia de Build (Python + PyInstaller)

Esta guia explica como generar:

- `AceManager.exe`
- `ListaAceStream.exe`
- `AceManager.zip`

Los ejecutables son autocontenidos y no requieren Python en el equipo final.

## Requisitos

- Windows
- Python 3.10+

Instalar dependencias de build:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt
```

## Build rapido

Desde la raiz del repo:

```bash
python .github/scripts/build.py
```

Genera por defecto:

- `AceManager.exe`
- `ListaAceStream.exe`
- `AceManager.zip`

## Parametros del script

`build.py` acepta:

- `--app-version A.B.C.D`: version de archivo de los EXE (por defecto `1.0.0.0`)
- `--targets All|AceManager|ListaAceStream`: objetivos a compilar
- `--skip-package`: omite la generacion del ZIP

Ejemplos:

```bash
# Solo ListaAceStream.exe
python .github/scripts/build.py --targets ListaAceStream

# Solo AceManager.exe
python .github/scripts/build.py --targets AceManager

# Ambos EXE sin ZIP
python .github/scripts/build.py --targets AceManager ListaAceStream --skip-package

# Build completo con version explicita
python .github/scripts/build.py --app-version 1.2.3.0
```

## Reglas de empaquetado

- El ZIP solo se crea si se compilan ambos objetivos y no se usa `--skip-package`.
- Si falta `config.ini`, el build genera uno por defecto.
- Si `AceManager.zip` esta en uso, se crea `AceManager_<timestamp>.zip`.

## CI/CD y release

- Workflow: `.github/workflows/build-exe.yml`
- Script: `.github/scripts/build.py`
- Semantic Release: `.releaserc.json`

Comando usado por Semantic Release:

```bash
python ./.github/scripts/build.py --app-version ${nextRelease.version}.0
```
