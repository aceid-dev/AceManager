from __future__ import annotations

import ctypes
import sys
from pathlib import Path


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except OSError:
        return False


def elevate(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv
    params = " ".join(f'"{arg}"' for arg in args)
    result = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    if result <= 32:
        raise RuntimeError("No se pudo elevar privilegios")


def wait_keypress(log_info, message: str = "Presiona Enter para continuar...") -> None:
    print()
    log_info(message)
    input()


def ask_yes_no(log_warning, question: str, *, default: bool = True) -> bool:
    suffix = "[S/n]" if default else "[s/N]"
    while True:
        answer = input(f"{question} {suffix}: ").strip().lower()
        if not answer:
            return default
        if answer in {"s", "si", "y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        log_warning("Respuesta invalida. Escribe 's' o 'n'.")


def resolve_base_dir(script_path: Path) -> Path:
    base_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else script_path.resolve().parent
    if not base_dir.exists() or any(token in str(base_dir) for token in ("System32", "Temp")):
        return Path.home() / "Downloads"
    return base_dir
