from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.common import is_process_running
from src.start_ace_engine import start_ace_engine


def test_ace_engine(*, prompt_user: bool = True) -> bool:
    if is_process_running("ace_engine"):
        print("Engine is running")
        return True

    print("Engine is NOT running")
    if not prompt_user:
        return False

    decision = input("Do you want to start engine? [Y/n]: ").strip().lower()
    if decision in {"", "y", "yes", "s", "si"}:
        return start_ace_engine()

    return False


if __name__ == "__main__":
    raise SystemExit(0 if test_ace_engine() else 1)
