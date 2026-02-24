from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.common import (
    is_process_running,
    log_info,
    log_success,
    normalize_image_name,
    terminate_process,
)


PROCESS_NAMES = ("ace_engine", "ace_update", "ace_player")


def stop_ace_engine() -> None:
    any_running = False
    any_stopped = False

    for process_name in PROCESS_NAMES:
        image = normalize_image_name(process_name)
        if not is_process_running(image):
            continue

        any_running = True
        log_info(f"Deteniendo {process_name}...")
        if terminate_process(image):
            any_stopped = True

    if not any_running:
        log_info("Ace Stream Engine no esta en ejecucion")
    elif any_stopped:
        log_success("Ace Stream Engine detenido")


if __name__ == "__main__":
    stop_ace_engine()
