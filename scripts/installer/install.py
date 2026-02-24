from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALLER_DIR = Path(__file__).resolve().parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(INSTALLER_DIR) not in sys.path:
    sys.path.insert(0, str(INSTALLER_DIR))

from src.common import log_error, log_info, log_step, log_success, log_warning
from installer_flow import build_paths, run_installation
from installer_system import elevate, is_admin, resolve_base_dir, wait_keypress


def main() -> int:
    if os.name != "nt":
        log_error("Este instalador solo es compatible con Windows.")
        return 1

    if not is_admin():
        try:
            log_step("Elevando privilegios de administrador...")
            elevate()
            return 0
        except Exception as error:
            log_error("No se pudo elevar privilegios")
            log_error(str(error))
            wait_keypress(log_info)
            return 1

    log_step("==========================================")
    log_step("INSTALADOR ACEMANAGER")
    log_step("==========================================")

    base_dir = resolve_base_dir(Path(__file__))
    log_info(f"Buscando archivos en: {base_dir}")

    paths = build_paths(base_dir)
    has_errors = False

    try:
        if run_installation(paths):
            has_errors = True
    except Exception as error:
        log_error("ERROR CRITICO DURANTE LA INSTALACION")
        log_error(str(error))
        has_errors = True

    if has_errors:
        log_warning("Instalacion finalizada con advertencias")
    else:
        log_success("Instalacion finalizada correctamente")

    wait_keypress(log_info, "Pulsa Enter para cerrar...")
    return 0 if not has_errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
