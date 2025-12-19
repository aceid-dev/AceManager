from __future__ import annotations

import os
import subprocess
from pathlib import Path


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
        print("Este script solo es compatible con Windows.")
        return 1

    appdata = Path(os.environ.get("APPDATA", ""))
    app_root = appdata / "ACEStream"
    start_menu = appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs"

    target = app_root / "ListaAceStream.exe"
    shortcut = start_menu / "Lista Ace Stream.lnk"

    if not target.exists():
        print(f"Error: ejecutable no encontrado: {target}")
        return 1

    shortcut.parent.mkdir(parents=True, exist_ok=True)
    create_shortcut(
        shortcut_path=shortcut,
        target_path=target,
        working_dir=app_root,
        description="Lanzar lista Ace Stream",
    )

    if shortcut.exists():
        print("El acceso directo 'Lista Ace Stream.lnk' se ha creado correctamente.")
        print(f"Ubicacion: {shortcut.parent}")
        return 0

    print("Error al crear 'Lista Ace Stream.lnk'.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
