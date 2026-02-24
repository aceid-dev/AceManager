from __future__ import annotations

import ctypes
import os
import sys

_COLOR_RESET = "\033[0m"
_LEVEL_COLORS = {
    "PASO": "\033[94m",
    "INFO": "\033[96m",
    "EXITO": "\033[92m",
    "AVISO": "\033[93m",
    "ERROR": "\033[91m",
}


def _enable_windows_ansi() -> bool:
    if os.name != "nt":
        return True

    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)) == 0:
            return False
        if kernel32.SetConsoleMode(handle, mode.value | 0x0004) == 0:
            return False
    except OSError:
        return False

    return True


_USE_COLOR = sys.stdout.isatty() and _enable_windows_ansi()


def _normalize_level(level: str) -> str:
    return level.upper().strip() or "INFO"


def _format_log(level: str, message: str) -> str:
    tag = _normalize_level(level)
    base = f"[{tag}] {message}"
    if not _USE_COLOR:
        return base

    color = _LEVEL_COLORS.get(tag, "")
    if not color:
        return base

    return f"{color}{base}{_COLOR_RESET}"


def colorize(level: str, message: str) -> str:
    tag = _normalize_level(level)
    if not _USE_COLOR:
        return message

    color = _LEVEL_COLORS.get(tag, "")
    if not color:
        return message

    return f"{color}{message}{_COLOR_RESET}"


def log(level: str, message: str) -> None:
    print(_format_log(level, message))


def log_step(message: str) -> None:
    log("PASO", message)


def log_info(message: str) -> None:
    log("INFO", message)


def log_success(message: str) -> None:
    log("EXITO", message)


def log_warning(message: str) -> None:
    log("AVISO", message)


def log_error(message: str) -> None:
    log("ERROR", message)
