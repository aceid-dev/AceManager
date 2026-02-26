from __future__ import annotations

import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import NoReturn

PROJECT_ROOT = Path(__file__).resolve().parents[2]
try:
    from src.functions import get_vlc_path, start_detached_process
    from src.start_ace_engine import start_ace_engine
except ImportError:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from src.functions import get_vlc_path, start_detached_process
    from src.start_ace_engine import start_ace_engine


def resolve_script_base() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    if "__file__" in globals():
        return Path(__file__).resolve().parent

    return Path.cwd()


SCRIPT_BASE = resolve_script_base()
LOG_PATH = SCRIPT_BASE / "lista_acestream_error.log"


def write_error_log(message: str, error: BaseException | None = None) -> None:
    lines = [f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}"]

    if error is not None:
        lines.append(f"Exception: {error}")
        lines.extend(traceback.format_exception(type(error), error, error.__traceback__))

    lines.append("")
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def stop_silent_execution(message: str, error: BaseException | None = None) -> "NoReturn":
    write_error_log(message, error)
    raise SystemExit(1)


def parse_ini_config(path: Path) -> dict[str, str]:
    config: dict[str, str] = {}
    content = path.read_text(encoding="utf-8", errors="ignore")

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith(";"):
            continue
        if "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        config[key.strip().lower()] = value.strip()

    return config


def find_config_ini() -> Path | None:
    candidates = [SCRIPT_BASE / "config.ini"]

    if not getattr(sys, "frozen", False):
        candidates.append(PROJECT_ROOT / "config.ini")

    appdata = os.environ.get("APPDATA")
    if appdata:
        candidates.append(Path(appdata) / "ACEStream" / "manager" / "config.ini")

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def main() -> int:
    try:
        ini_path = find_config_ini()
        if not ini_path:
            stop_silent_execution("No se encuentra config.ini en rutas esperadas.")

        config = parse_ini_config(ini_path)
        dominio_base = config.get("dominio", "").strip().rstrip("/")
        entrada_lista = config.get("lista", "").strip()

        if not entrada_lista:
            stop_silent_execution("La clave 'lista' en config.ini esta vacia.")

        if entrada_lista.lower().startswith(("http://", "https://")):
            url_final = entrada_lista
        else:
            if not dominio_base:
                stop_silent_execution("La clave 'dominio' en config.ini esta vacia.")
            url_final = f"{dominio_base}/{entrada_lista.lstrip('/')}"

        try:
            engine_started = bool(start_ace_engine())
        except Exception as error:
            stop_silent_execution("Excepcion al iniciar Ace Engine.", error)

        if not engine_started:
            stop_silent_execution("Ace Engine no pudo iniciarse.")

        vlc_path = get_vlc_path()
        if not vlc_path:
            stop_silent_execution("VLC no encontrado en Program Files.")

        if not url_final:
            stop_silent_execution("URL final vacia tras procesar config.ini.")

        if not start_detached_process(vlc_path, [url_final, "--no-playlist-autostart"]):
            stop_silent_execution("No se pudo iniciar VLC con la URL final.")

        return 0
    except SystemExit as exit_code:
        if isinstance(exit_code.code, int):
            return exit_code.code
        return 1
    except Exception as error:
        stop_silent_execution("Error no controlado en lista_acestream.py.", error)


if __name__ == "__main__":
    raise SystemExit(main())
