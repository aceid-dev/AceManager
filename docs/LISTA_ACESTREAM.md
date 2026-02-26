# Guia de ListaAceStream (ListaAceStream.exe)

Esta guia documenta el lanzador de listas Ace Stream.

La herramienta corresponde a:

- `ListaAceStream.exe` (herramienta distribuida)
- `src/functions/lista_acestream.py` (codigo fuente de la herramienta)

## Objetivo

Iniciar reproduccion en VLC a partir de `config.ini`:

1. Resuelve la URL final usando `dominio` + `lista` o una URL directa.
2. Inicia Ace Stream Engine si no esta en ejecucion.
3. Lanza VLC con la URL final.

## Rutas de `config.ini`

La herramienta busca `config.ini` en este orden:

1. Misma carpeta de la herramienta o `.exe`
2. Raiz del repo (`config.ini`) cuando se ejecuta desde codigo fuente
3. `%APPDATA%\ACEStream\manager\config.ini`

Si no encuentra el archivo, termina con error y escribe log.

## Formato de configuracion

Ejemplo:

```ini
dominio = https://aceid.short.gy
lista = lista_acestream
```

Reglas:

- Si `lista` empieza por `http://` o `https://`, se usa como URL final.
- Si `lista` es relativa, se construye: `dominio + "/" + lista`.
- Si `lista` esta vacia, finaliza con error.
- Si `dominio` esta vacio y `lista` es relativa, finaliza con error.

## Ejecucion recomendada

Abre `ListaAceStream` desde Menu Inicio o desde el acceso directo del Escritorio.

```text
ListaAceStream.exe
```

Uso en desarrollo (opcional):

```bash
python src/functions/lista_acestream.py
```

## Flujo interno

1. Carga y valida `config.ini`.
2. Inicia Ace Engine mediante `src/start_ace_engine.py`.
3. Localiza VLC en Program Files.
4. Ejecuta VLC con:
   - `<url_final>`
   - `--no-playlist-autostart`

## Log de errores

En caso de error, guarda detalle en:

- `lista_acestream_error.log` en la misma carpeta de la herramienta o `.exe`

Incluye:

- Timestamp
- Mensaje de error
- Excepcion y stack trace (si aplica)

## Codigos de salida

- `0`: ejecucion correcta
- `1`: error de configuracion, entorno o arranque

## Errores comunes

- `config.ini` no encontrado:
  - Verifica rutas esperadas.
- `VLC no encontrado en Program Files`:
  - Instala VLC en `Program Files` o `Program Files (x86)`.
- `Ace Engine no pudo iniciarse`:
  - Verifica instalacion de Ace Stream en `%APPDATA%\ACEStream\engine\`.
