from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.common import build_stream_url, get_vlc_path, is_process_running, start_detached_process, terminate_process


ACE_ID_PATTERNS = (
    re.compile(r"(?i)^(?:acestream://)?(?P<id>[a-z0-9]{40})$"),
    re.compile(r"(?i)(?:[?&]id=)(?P<id>[a-z0-9]{40})(?:$|[&#/])"),
    re.compile(r"(?i)acestream://(?P<id>[a-z0-9]{40})(?:$|[^a-z0-9])"),
)


def extract_ace_stream_id(input_value: str | None) -> str | None:
    if not input_value:
        return None

    candidate = input_value.strip()
    decoded = unquote(candidate)

    for value in (candidate, decoded):
        for pattern in ACE_ID_PATTERNS:
            match = pattern.search(value)
            if match:
                return match.group("id")

    return None


def stop_existing_vlc() -> None:
    if is_process_running("vlc"):
        print("Stopping existing VLC instance...")
        terminate_process("vlc")


def start_player(ace_id: str | None = None, *, prompt_if_missing: bool = True) -> bool:
    stop_existing_vlc()

    if not ace_id and prompt_if_missing:
        ace_id = input("Enter Ace Stream ID: ").strip()

    if not ace_id:
        print("No Ace Stream ID provided")
        return False

    raw_input = ace_id.strip()
    resolved_id = extract_ace_stream_id(raw_input)
    if not resolved_id:
        resolved_id = unquote(raw_input)

    if not re.fullmatch(r"[a-zA-Z0-9]{40}", resolved_id):
        print("WARNING: Invalid Ace Stream ID. Must be exactly 40 alphanumeric characters.")
        print(f"Provided value: {raw_input}")
        print(f"Resolved ID: {resolved_id} (Length: {len(resolved_id)})")
        return False

    vlc_path = get_vlc_path()
    if not vlc_path:
        print("WARNING: VLC not found in Program Files")
        return False

    stream_url = build_stream_url(resolved_id)
    if not start_detached_process(vlc_path, [stream_url]):
        print("WARNING: Failed to launch VLC")
        return False

    print(f"Starting stream with ID: {resolved_id}")
    return True


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch VLC with an Ace Stream ID")
    parser.add_argument("ace_id", nargs="?", help="Ace Stream ID or URL containing id=<ID>")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    raise SystemExit(0 if start_player(args.ace_id, prompt_if_missing=not bool(args.ace_id)) else 1)
