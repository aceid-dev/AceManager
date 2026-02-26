from __future__ import annotations

import subprocess
from pathlib import Path

from build.config import PYI_ROOT, REPO_ROOT
from build.logging_utils import log
from build.versioning import build_version_file


def run_pyinstaller(
    *,
    python_executable: Path,
    entry_script: Path,
    output_name: str,
    icon_path: Path,
    product_title: str,
    app_version: str,
    windowed: bool = False,
) -> None:
    if not python_executable.exists():
        raise FileNotFoundError(
            f"No se encontro el Python del entorno virtual: {python_executable}"
        )

    if not entry_script.exists():
        raise FileNotFoundError(f"No se encontro el entrypoint: {entry_script}")

    log(f"\n>> Preparando: {output_name}.exe")
    version_file = build_version_file(app_version, product_title)

    work_path = PYI_ROOT / "build" / output_name
    spec_path = PYI_ROOT / "spec" / output_name
    work_path.mkdir(parents=True, exist_ok=True)
    spec_path.mkdir(parents=True, exist_ok=True)

    args = [
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name",
        output_name,
        "--distpath",
        str(REPO_ROOT),
        "--workpath",
        str(work_path),
        "--specpath",
        str(spec_path),
        "--version-file",
        str(version_file),
    ]

    if icon_path.exists():
        args.extend(["--icon", str(icon_path)])

    if windowed:
        args.append("--windowed")

    args.append(str(entry_script))

    subprocess.run(
        [str(python_executable), "-m", "PyInstaller", *args],
        check=True,
        cwd=REPO_ROOT,
    )

    output_exe = REPO_ROOT / f"{output_name}.exe"
    if not output_exe.exists():
        raise RuntimeError(f"No se genero {output_name}.exe")

    log(f"   [OK] {output_name}.exe creado con exito")
