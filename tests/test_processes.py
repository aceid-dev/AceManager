from __future__ import annotations

import subprocess
from pathlib import Path

from src.functions import processes


def test_normalize_image_name_appends_exe() -> None:
    assert processes.normalize_image_name("vlc") == "vlc.exe"
    assert processes.normalize_image_name("VLC.EXE") == "VLC.EXE"


def test_is_process_running_checks_windows_tasklist_output(monkeypatch) -> None:
    result = subprocess.CompletedProcess(
        args=["tasklist"],
        returncode=0,
        stdout="vlc.exe                    123 Console                    1     10,000 K",
        stderr="",
    )

    monkeypatch.setattr(processes.os, "name", "nt", raising=False)
    monkeypatch.setattr(processes, "_run", lambda *args, **kwargs: result)

    assert processes.is_process_running("vlc") is True


def test_start_detached_process_returns_false_on_oserror(monkeypatch) -> None:
    def fake_popen(*args, **kwargs):
        raise OSError("boom")

    monkeypatch.setattr(processes.subprocess, "Popen", fake_popen)

    assert processes.start_detached_process("vlc.exe") is False


def test_start_detached_process_passes_hidden_creationflags_on_windows(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_popen(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return object()

    executable = Path("C:/Program Files/VideoLAN/VLC/vlc.exe")

    monkeypatch.setattr(processes.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(processes.os, "name", "nt", raising=False)
    monkeypatch.setattr(processes, "CREATE_NO_WINDOW", 1234)

    assert processes.start_detached_process(executable, ["http://stream"], hidden=True) is True
    assert captured["command"] == [str(executable), "http://stream"]
    assert captured["kwargs"] == {"creationflags": 1234}
