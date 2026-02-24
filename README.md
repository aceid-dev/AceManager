# AceManager (Python Edition)

Gestor de Ace Stream reescrito completamente en Python para Windows.

Este proyecto genera ejecutables autocontenidos (`.exe`) listos para usar en equipos sin Python instalado.

## Caracteristicas

- Menu interactivo para iniciar, detener y verificar Ace Stream Engine.
- Reproduccion de IDs de Ace Stream en VLC.
- Lanzador auxiliar `ListaAceStream.exe` basado en `config.ini`.
- Utilidades compiladas: `Installer.exe` y `FixConfig.exe`.
- Build reproducible con `PyInstaller` y empaquetado `AceManager.zip`.
- Pipeline de release con Semantic Release.

## Requisitos de ejecucion (usuario final)

- Windows 10/11
- Ace Stream Engine instalado en `%APPDATA%\ACEStream\engine\ace_engine.exe`
- VLC instalado en `C:\Program Files\VideoLAN\VLC\vlc.exe` o `C:\Program Files (x86)\VideoLAN\VLC\vlc.exe`

No se requiere Python para ejecutar los `.exe` generados.

## Requisitos de build (solo desarrollo)

- Python 3.10+
- Dependencias de build:

```bash
python -m pip install -r requirements-build.txt
```

## Estructura principal

```text
src/
  main.py                # Menu principal (AceManager.exe)
  start_ace_engine.py    # Iniciar motor Ace Stream
  stop_ace_engine.py     # Detener procesos Ace Stream
  check_ace_engine.py    # Verificar estado del motor
  player.py              # Lanzar VLC con Ace ID
  common.py              # Utilidades compartidas
utils/
  lista_acestream.py     # Launcher automatico (ListaAceStream.exe)
.github/scripts/
  build.py               # Build de EXE + ZIP con PyInstaller
scripts/
  fix.py                 # Herramienta interactiva para editar config.ini
  installer/install.py   # Instalador local en Windows
```

## Uso desde codigo fuente

```bash
python src/main.py
```

### Comandos individuales

```bash
python src/start_ace_engine.py
python src/stop_ace_engine.py
python src/check_ace_engine.py
python src/player.py <ace_id>
python utils/lista_acestream.py
python scripts/installer/install.py
python scripts/fix.py
```

## Build de ejecutables

La guia completa esta en [docs/BUILD.md](docs/BUILD.md).

Build rapido:

```bash
python .github/scripts/build.py
```

Salida esperada:

- `AceManager.exe`
- `ListaAceStream.exe`
- `Installer.exe`
- `FixConfig.exe`
- `AceManager.zip`

## Guias adicionales

- Instalador: [docs/INSTALLER.md](docs/INSTALLER.md)
- Fix de config: [docs/FIXCONFIG.md](docs/FIXCONFIG.md)

## Configuracion

Archivo `config.ini`:

```ini
# Configuracion de AceManager
# Puedes poner el dominio de tu servidor aqui
dominio = https://aceid.short.gy

# Puedes poner el nombre de la lista (ej: lista_acestream)
# o una URL completa (ej: https://otro-sitio.com/lista.m3u)
lista = lista_acestream
```

Reglas de `lista`:

- Si contiene un Ace ID valido (40 chars), usa `http://127.0.0.1:6878/ace/getstream?id=<ID>`.
- Si es URL completa (`http://` o `https://`), se usa directamente.
- Si es ruta relativa, se combina con `dominio`.

## Troubleshooting rapido

- Engine no inicia:
  - Verifica `%APPDATA%\ACEStream\engine\ace_engine.exe`.
- VLC no encontrado:
  - Verifica instalacion en Program Files.
- Stream no reproduce:
  - Verifica ID valido de 40 caracteres.
  - Verifica que el engine este levantado en `127.0.0.1:6878`.

## Licencia

GPL-3.0 (ver `LICENSE`).
