from __future__ import annotations

import subprocess
from pathlib import Path


def escape_ps(value: str) -> str:
    return value.replace("'", "''")


def create_shortcut(path: Path, target: Path, working_dir: Path, description: str) -> None:
    ps_script = (
        "$shell=New-Object -ComObject WScript.Shell;"
        f"$shortcut=$shell.CreateShortcut('{escape_ps(str(path))}');"
        f"$shortcut.TargetPath='{escape_ps(str(target))}';"
        f"$shortcut.WorkingDirectory='{escape_ps(str(working_dir))}';"
        f"$shortcut.IconLocation='{escape_ps(str(target))},0';"
        f"$shortcut.Description='{escape_ps(description)}';"
        "$shortcut.Save();"
    )

    subprocess.run(
        ["powershell", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        check=True,
    )

    # Activa el flag "Run as administrator" en el acceso directo.
    data = bytearray(path.read_bytes())
    if len(data) > 0x15:
        data[0x15] = data[0x15] | 0x20
        path.write_bytes(data)
