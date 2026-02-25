# Guia de Fix (Fix.exe)

Esta guia describe la herramienta para editar `config.ini` de forma interactiva.

La herramienta corresponde a:

- `Fix.exe` (herramienta distribuida)
- `scripts/fix.py` (codigo fuente de la herramienta)

## Objetivo

Permite ajustar rapidamente los valores de:

- `dominio`
- `lista`

en el archivo:

- `%APPDATA%\\ACEStream\\config.ini` (ruta principal)

## Ejecucion recomendada

Abre `Fix` desde Menu Inicio o desde el acceso directo del Escritorio.

```text
Fix.exe
```

Uso en desarrollo (opcional):

```bash
python scripts/fix.py
```

## Comportamiento del menu

Al iniciar:

- Muestra el valor actual de `dominio` y `lista`.
- Presenta opciones de cambio rapido entre listas predefinidas.
- Permite introducir una URL completa de lista.

Opciones:

- `1` a `N`: intercambios rapidos validos para la `lista` actual.
- Las listas predefinidas son:
  - `lista_acestream`
  - `lista_Icastresana`
  - `lista_ramses`
- Si la `lista` actual no coincide con una predefinida, no se muestran opciones rapidas.
- `7`: introduce una URL completa (`http://` o `https://`)
- `0`: salir

## Opcion 7 (URL completa)

Cuando introduces una URL valida, la herramienta separa:

- `dominio`: esquema + host + directorio
- `lista`: nombre de archivo final

Ejemplo:

- Entrada: `https://mi-servidor.com/canales/lista.m3u`
- Resultado:
  - `dominio = https://mi-servidor.com/canales`
  - `lista = lista.m3u`

Validaciones aplicadas:

- Debe comenzar por `http://` o `https://`.
- Debe incluir host valido.
- Debe terminar en nombre de archivo (no en `/`).

## Notas tecnicas

- Orden de busqueda de `config.ini`:
  - Carpeta del ejecutable `Fix.exe`
  - `%APPDATA%\\ACEStream\\config.ini`
  - `%APPDATA%\\ACEStream\\manager\\config.ini` (compatibilidad)
- Si `dominio` o `lista` no existen en `config.ini`, se anaden al final.
- Los cambios se guardan en disco en cada actualizacion.
- Si el archivo no existe, la herramienta finaliza con error.
