from __future__ import annotations

import sys
import time
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.common import get_ace_engine_path, is_process_running, start_detached_process


ACE_ENGINE_PROCESS = "ace_engine"


def start_ace_engine(timeout_seconds: int = 15) -> bool:
    engine_path = get_ace_engine_path()

    if not engine_path.exists():
        print(f"WARNING: ACE Engine not found at: {engine_path}")
        return False

    if is_process_running(ACE_ENGINE_PROCESS):
        print("Engine is already running")
        return True

    print("Starting engine...")
    if not start_detached_process(engine_path, hidden=True):
        print("WARNING: Failed to launch ACE Engine process")
        return False

    print("Waiting for engine to start...")
    for _ in range(timeout_seconds):
        if is_process_running(ACE_ENGINE_PROCESS):
            print("Engine started")
            return True
        time.sleep(1)

    print(f"WARNING: Engine failed to start within {timeout_seconds} seconds")
    return False


if __name__ == "__main__":
    raise SystemExit(0 if start_ace_engine() else 1)
