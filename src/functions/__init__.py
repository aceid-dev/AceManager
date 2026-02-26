"""Helper functions for CLI flows."""
from __future__ import annotations

from .acestream import build_stream_url, get_ace_engine_path
from .logs import (
    colorize,
    log,
    log_error,
    log_info,
    log_step,
    log_success,
    log_warning,
)
from .processes import (
    CREATE_NO_WINDOW,
    is_process_running,
    normalize_image_name,
    start_detached_process,
    terminate_process,
)
from .ui import clear_screen
from .vlc import get_vlc_candidates, get_vlc_path

__all__ = [
    "CREATE_NO_WINDOW",
    "build_stream_url",
    "clear_screen",
    "colorize",
    "get_ace_engine_path",
    "get_vlc_candidates",
    "get_vlc_path",
    "is_process_running",
    "log",
    "log_error",
    "log_info",
    "log_step",
    "log_success",
    "log_warning",
    "normalize_image_name",
    "start_detached_process",
    "terminate_process",
]
