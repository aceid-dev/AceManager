from __future__ import annotations

from pathlib import Path

from src import player


ACE_ID = "0123456789abcdef0123456789abcdef01234567"


def test_extract_ace_stream_id_accepts_plain_id() -> None:
    assert player.extract_ace_stream_id(ACE_ID) == ACE_ID


def test_extract_ace_stream_id_accepts_url_encoded_value() -> None:
    encoded = "https%3A%2F%2Fexample.com%2Fwatch%3Fid%3D" + ACE_ID

    assert player.extract_ace_stream_id(encoded) == ACE_ID


def test_start_player_rejects_invalid_id(monkeypatch) -> None:
    messages: list[str] = []

    monkeypatch.setattr(player, "stop_existing_vlc", lambda: None)
    monkeypatch.setattr(player, "log_warning", messages.append)
    monkeypatch.setattr(player, "log_info", messages.append)

    assert player.start_player("not-a-valid-id", prompt_if_missing=False) is False
    assert any("ID de Ace Stream invalido" in message for message in messages)


def test_start_player_launches_vlc_with_stream_url(monkeypatch) -> None:
    calls: dict[str, object] = {}
    vlc_path = Path("C:/Program Files/VideoLAN/VLC/vlc.exe")

    def fake_start_detached_process(executable, args):
        calls["executable"] = executable
        calls["args"] = args
        return True

    monkeypatch.setattr(player, "stop_existing_vlc", lambda: None)
    monkeypatch.setattr(player, "get_vlc_path", lambda: vlc_path)
    monkeypatch.setattr(player, "start_detached_process", fake_start_detached_process)
    monkeypatch.setattr(player, "log_success", lambda message: None)

    assert player.start_player(ACE_ID, prompt_if_missing=False) is True
    assert calls == {
        "executable": vlc_path,
        "args": [player.build_stream_url(ACE_ID)],
    }
