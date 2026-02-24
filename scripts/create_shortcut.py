from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.common import log_error, log_info, log_success


def escape_ps(value: str) -> str:
    return value.replace("'", "''")


def create_shortcut(shortcut_path: Path, target_path: Path, working_dir: Path, description: str) -> None:
    script = (
        "$ws=New-Object -ComObject WScript.Shell;"
        f"$s=$ws.CreateShortcut('{escape_ps(str(shortcut_path))}');"
        f"$s.TargetPath='{escape_ps(str(target_path))}';"
        f"$s.WorkingDirectory='{escape_ps(str(working_dir))}';"
        f"$s.IconLocation='{escape_ps(str(target_path))},0';"
        f"$s.Description='{escape_ps(description)}';"
        "$s.Save();"
    )

    subprocess.run(
        ["powershell", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        check=True,
    )


def main() -> int:
    if os.name != "nt":
        log_error("Este script solo es compatible con Windows.")
        return 1

    appdata = Path(os.environ.get("APPDATA", ""))
    app_root = appdata / "ACEStream"
    start_menu = appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs"

    target = app_root / "ListaAceStream.exe"
    shortcut = start_menu / "Lista Ace Stream.lnk"

    if not target.exists():
        log_error(f"Ejecutable no encontrado: {target}")
        return 1

    shortcut.parent.mkdir(parents=True, exist_ok=True)
    create_shortcut(
        shortcut_path=shortcut,
        target_path=target,
        working_dir=app_root,
        description="Lanzar lista Ace Stream",
    )

    if shortcut.exists():
        log_success("El acceso directo 'Lista Ace Stream.lnk' se creo correctamente.")
        log_info(f"Ubicacion: {shortcut.parent}")
        return 0

    log_error("Error al crear 'Lista Ace Stream.lnk'.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
