#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_modules.cli import parse_args
from build_modules.config import REPO_ROOT, TARGET_SPECS, TARGETS_ALL
from build_modules.environment import ensure_build_environment
from build_modules.logging_utils import log
from build_modules.pyinstaller_runner import run_pyinstaller
from build_modules.release_packager import package_release
from build_modules.targets import normalize_targets
from build_modules.versioning import parse_version


def main() -> int:
    if os.name != "nt":
        log("[ERROR] La generacion de .exe con este proyecto requiere Windows.")
        log("[INFO] Ejecuta el build en windows-latest o en un equipo Windows.")
        return 1

    args = parse_args()

    try:
        parse_version(args.app_version)
    except ValueError as error:
        log(f"[ERROR] {error}")
        return 1

    try:
        selected_targets = normalize_targets(args.targets)
    except ValueError as error:
        log(f"[ERROR] {error}")
        return 1

    should_package = (not args.skip_package) and selected_targets == TARGETS_ALL

    log("\n[BUILD] Iniciando proceso de compilacion")
    log(f"[INFO] Raiz detectada: {REPO_ROOT}")
    log(f"[INFO] Version de destino: {args.app_version}")
    log(f"[INFO] Objetivos: {', '.join(sorted(selected_targets))}")
    log(f"[INFO] Empaquetado ZIP: {'habilitado' if should_package else 'omitido'}")

    try:
        build_python = ensure_build_environment()

        for target in sorted(selected_targets):
            spec = TARGET_SPECS[target]
            run_pyinstaller(
                python_executable=build_python,
                entry_script=spec["entry_script"],
                output_name=spec["output_name"],
                icon_path=spec["icon_path"],
                product_title=spec["product_title"],
                app_version=args.app_version,
                windowed=spec["windowed"],
            )

        if should_package:
            package_release(args.app_version)
        else:
            log("\n[INFO] Empaquetado ZIP omitido por seleccion de objetivos")

        log("\n[OK] PROCESO FINALIZADO: Todo esta listo para el release")
        return 0
    except Exception as error:
        log("\n[ERROR] ERROR CRITICO durante el proceso de build")
        log(f"[DETALLE] {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
