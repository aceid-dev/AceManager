from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALLER_DIR = REPO_ROOT / "scripts" / "installer"

for path in (REPO_ROOT, INSTALLER_DIR):
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)
