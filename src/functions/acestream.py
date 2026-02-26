from __future__ import annotations

import os
from pathlib import Path


def get_ace_engine_path() -> Path:
    appdata = os.environ.get("APPDATA", "")
    return Path(appdata) / "ACEStream" / "engine" / "ace_engine.exe"


def build_stream_url(ace_id: str) -> str:
    return f"http://127.0.0.1:6878/ace/getstream?id={ace_id}"
