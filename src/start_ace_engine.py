from __future__ import annotations

import sys
import time
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.common import (
    get_ace_engine_path,
    is_process_running,
    log_info,
    log_step,
    log_success,
    log_warning,
    start_detached_process,
)


ACE_ENGINE_PROCESS = "ace_engine"


def start_ace_engine(timeout_seconds: int = 15) -> bool:
    engine_path = get_ace_engine_path()

    if not engine_path.exists():
        log_warning(f"No se encontro ACE Engine en: {engine_path}")
        return False

    if is_process_running(ACE_ENGINE_PROCESS):
        log_info("El motor ya esta en ejecucion")
        return True

    log_step("Iniciando motor...")
    if not start_detached_process(engine_path, hidden=True):
        log_warning("No se pudo lanzar el proceso de ACE Engine")
        return False

    log_info("Esperando a que el motor inicie...")
    for _ in range(timeout_seconds):
        if is_process_running(ACE_ENGINE_PROCESS):
            log_success("Motor iniciado correctamente")
            return True
        time.sleep(1)

    log_warning(f"El motor no inicio dentro de {timeout_seconds} segundos")
    return False


if __name__ == "__main__":
    raise SystemExit(0 if start_ace_engine() else 1)
