# Guia de FixConfig (FixConfig.exe / fix.py)

Esta guia describe la herramienta para editar `config.ini` de forma interactiva.

Corresponde a:

- `scripts/fix.py` (codigo fuente)
- `FixConfig.exe` (binario generado por build)

## Objetivo

Permite ajustar rapidamente los valores de:

- `dominio`
- `lista`

en el archivo:

- `%APPDATA%\\ACEstream\\manager\\config.ini`

## Ejecucion

Desde codigo fuente:

```bash
python scripts/fix.py
```

Desde binario:

```text
FixConfig.exe
```

## Comportamiento del menu

Al iniciar:

- Muestra el valor actual de `dominio` y `lista`.
- Presenta opciones de cambio rapido entre listas predefinidas.
- Permite introducir una URL completa de lista.

Opciones:

- `1` a `6`: intercambios directos entre:
  - `lista_acestream`
  - `lista_Icastresana`
  - `lista_ramses`
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

- Si `dominio` o `lista` no existen en `config.ini`, se anaden al final.
- Los cambios se guardan en disco en cada actualizacion.
- Si el archivo no existe, la herramienta finaliza con error.
