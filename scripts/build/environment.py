from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from build.config import BUILD_VENV, REQUIREMENTS_BUILD
from build.logging_utils import log


def get_venv_python() -> Path:
    if os.name == "nt":
        return BUILD_VENV / "Scripts" / "python.exe"
    return BUILD_VENV / "bin" / "python"


def ensure_build_environment() -> Path:
    if not REQUIREMENTS_BUILD.exists():
        raise FileNotFoundError(
            f"No se encontro el archivo de dependencias: {REQUIREMENTS_BUILD}"
        )

    venv_python = get_venv_python()

    if not venv_python.exists():
        log(f"[INFO] Creando entorno virtual de build en: {BUILD_VENV}")
        subprocess.run(
            [sys.executable, "-m", "venv", str(BUILD_VENV)],
            check=True,
        )
    else:
        log(f"[INFO] Entorno virtual detectado: {BUILD_VENV}")

    log("[INFO] Instalando dependencias de build")
    subprocess.run(
        [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
        check=True,
    )
    subprocess.run(
        [str(venv_python), "-m", "pip", "install", "-r", str(REQUIREMENTS_BUILD)],
        check=True,
    )

    return venv_python
