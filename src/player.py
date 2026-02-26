from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.functions import (
    build_stream_url,
    get_vlc_path,
    is_process_running,
    log_info,
    log_success,
    log_warning,
    start_detached_process,
    terminate_process,
)


ACE_ID_PATTERNS = (
    re.compile(r"(?i)^(?:acestream://)?(?P<id>[a-z0-9]{40})$"),
    re.compile(r"(?i)(?:[?&]id=)(?P<id>[a-z0-9]{40})(?:$|[&#/])"),
    re.compile(r"(?i)acestream://(?P<id>[a-z0-9]{40})(?:$|[^a-z0-9])"),
)


def extract_ace_stream_id(input_value: str | None) -> str | None:
    if not input_value:
        return None

    candidate = input_value.strip()
    decoded = unquote(candidate)

    for value in (candidate, decoded):
        for pattern in ACE_ID_PATTERNS:
            match = pattern.search(value)
            if match:
                return match.group("id")

    return None


def stop_existing_vlc() -> None:
    if is_process_running("vlc"):
        log_info("Deteniendo instancia de VLC en ejecucion...")
        terminate_process("vlc")


def start_player(ace_id: str | None = None, *, prompt_if_missing: bool = True) -> bool:
    stop_existing_vlc()

    if not ace_id and prompt_if_missing:
        ace_id = input("Introduce el ID de Ace Stream: ").strip()

    if not ace_id:
        log_warning("No se proporciono un ID de Ace Stream")
        return False

    raw_input = ace_id.strip()
    resolved_id = extract_ace_stream_id(raw_input)
    if not resolved_id:
        resolved_id = unquote(raw_input)

    if not re.fullmatch(r"[a-zA-Z0-9]{40}", resolved_id):
        log_warning("ID de Ace Stream invalido. Debe tener 40 caracteres alfanumericos.")
        log_info(f"Valor recibido: {raw_input}")
        log_info(f"ID resuelto: {resolved_id} (Longitud: {len(resolved_id)})")
        return False

    vlc_path = get_vlc_path()
    if not vlc_path:
        log_warning("No se encontro VLC en Program Files")
        return False

    stream_url = build_stream_url(resolved_id)
    if not start_detached_process(vlc_path, [stream_url]):
        log_warning("No se pudo iniciar VLC")
        return False

    log_success(f"Iniciando stream con ID: {resolved_id}")
    return True


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inicia VLC con un ID de Ace Stream")
    parser.add_argument("ace_id", nargs="?", help="ID de Ace Stream o URL que contenga id=<ID>")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    raise SystemExit(0 if start_player(args.ace_id, prompt_if_missing=not bool(args.ace_id)) else 1)
