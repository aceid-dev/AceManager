from __future__ import annotations

import os
from pathlib import Path


def get_vlc_candidates() -> list[Path]:
    candidates: list[Path] = []

    for env_name in ("ProgramFiles", "ProgramFiles(x86)"):
        root = os.environ.get(env_name)
        if root:
            candidates.append(Path(root) / "VideoLAN" / "VLC" / "vlc.exe")

    return candidates


def get_vlc_path() -> Path | None:
    for candidate in get_vlc_candidates():
        if candidate.exists():
            return candidate

    return None
