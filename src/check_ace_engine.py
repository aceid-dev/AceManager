from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.functions import is_process_running, log_info, log_warning
from src.start_ace_engine import start_ace_engine


def test_ace_engine(*, prompt_user: bool = True) -> bool:
    if is_process_running("ace_engine"):
        log_info("El motor esta en ejecucion")
        return True

    log_warning("El motor NO esta en ejecucion")
    if not prompt_user:
        return False

    decision = input("Quieres iniciar el motor? [S/n]: ").strip().lower()
    if decision in {"", "y", "yes", "s", "si"}:
        return start_ace_engine()

    return False


if __name__ == "__main__":
    raise SystemExit(0 if test_ace_engine() else 1)
