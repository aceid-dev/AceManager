from __future__ import annotations

import ctypes
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence

CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

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


def _format_log(level: str, message: str) -> str:
    tag = level.upper().strip() or "INFO"
    base = f"[{tag}] {message}"
    if not _USE_COLOR:
        return base

    color = _LEVEL_COLORS.get(tag, "")
    if not color:
        return base

    return f"{color}{base}{_COLOR_RESET}"


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


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def normalize_image_name(name: str) -> str:
    value = name.strip()
    if not value.lower().endswith(".exe"):
        value = f"{value}.exe"
    return value


def _run(
    args: Sequence[str],
    *,
    capture_output: bool = False,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        text=True,
        encoding="utf-8",
        errors="ignore",
        capture_output=capture_output,
        check=check,
        creationflags=CREATE_NO_WINDOW if os.name == "nt" else 0,
    )


def is_process_running(image_name: str) -> bool:
    image = normalize_image_name(image_name)

    if os.name == "nt":
        try:
            result = _run(
                ["tasklist", "/FI", f"IMAGENAME eq {image}"],
                capture_output=True,
            )
        except FileNotFoundError:
            return False

        return image.lower() in result.stdout.lower()

    process_name = image.removesuffix(".exe")
    try:
        result = _run(["pgrep", "-f", process_name], capture_output=True)
    except FileNotFoundError:
        return False

    return result.returncode == 0


def terminate_process(image_name: str) -> bool:
    image = normalize_image_name(image_name)

    if os.name == "nt":
        try:
            result = _run(["taskkill", "/IM", image, "/F"], capture_output=True)
        except FileNotFoundError:
            return False

        output = f"{result.stdout}\n{result.stderr}".lower()
        if "no tasks are running" in output:
            return False
        if "no se ha encontrado" in output:
            return False
        return result.returncode == 0

    process_name = image.removesuffix(".exe")
    try:
        result = _run(["pkill", "-f", process_name], capture_output=True)
    except FileNotFoundError:
        return False

    return result.returncode == 0


def start_detached_process(
    executable: str | Path,
    args: Sequence[str] | None = None,
    *,
    hidden: bool = False,
) -> bool:
    command = [str(executable)]
    if args:
        command.extend(str(arg) for arg in args)

    popen_kwargs: dict[str, object] = {}
    if hidden and os.name == "nt" and CREATE_NO_WINDOW:
        popen_kwargs["creationflags"] = CREATE_NO_WINDOW

    try:
        subprocess.Popen(command, **popen_kwargs)
    except OSError:
        return False

    return True


def get_ace_engine_path() -> Path:
    appdata = os.environ.get("APPDATA", "")
    return Path(appdata) / "ACEStream" / "engine" / "ace_engine.exe"


def get_vlc_candidates() -> list[Path]:
    candidates: list[Path] = []

    for env_name in ("ProgramFiles", "ProgramFiles(x86)"):
        root = os.environ.get(env_name)
        if root:
            candidates.append(Path(root) / "VideoLAN" / "VLC" / "vlc.exe")

    return candidates


def get_vlc_path() -> Path | None:
    for candidate in get_vlc_candidates():
        if candidate.exists():
            return candidate

    return None


def build_stream_url(ace_id: str) -> str:
    return f"http://127.0.0.1:6878/ace/getstream?id={ace_id}"
