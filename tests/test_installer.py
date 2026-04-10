from __future__ import annotations

from pathlib import Path

from installer_discovery import ace_engine_installed, find_ace_installer
from scripts.installer.installer_flow import build_paths


def test_build_paths_uses_appdata_and_userprofile(monkeypatch, tmp_path: Path) -> None:
    appdata = tmp_path / "AppData" / "Roaming"
    userprofile = tmp_path / "UserProfile"

    monkeypatch.setenv("APPDATA", str(appdata))
    monkeypatch.setenv("USERPROFILE", str(userprofile))

    paths = build_paths(tmp_path)

    assert paths.ace_dest == appdata / "ACEStream"
    assert paths.acemanager_dest == appdata / "ACEStream" / "AceManager.exe"
    assert paths.lista_dest == appdata / "ACEStream" / "ListaAceStream.exe"
    assert paths.fix_dest == appdata / "ACEStream" / "Fix.exe"
    assert paths.config_dest == appdata / "ACEStream" / "config.ini"
    assert paths.start_menu == appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "AceManager"
    assert paths.desktop == userprofile / "Desktop"


def test_find_ace_installer_ignores_project_executables(tmp_path: Path) -> None:
    installer = tmp_path / "Ace_Stream_3.2.8.exe"
    installer.write_bytes(b"")
    (tmp_path / "AceManager.exe").write_bytes(b"")
    (tmp_path / "ListaAceStream.exe").write_bytes(b"")
    (tmp_path / "Installer.exe").write_bytes(b"")
    (tmp_path / "Fix.exe").write_bytes(b"")

    assert find_ace_installer(tmp_path) == installer


def test_ace_engine_installed_checks_expected_location(tmp_path: Path) -> None:
    appdata = tmp_path / "AppData" / "Roaming"
    engine_path = appdata / "ACEStream" / "engine" / "ace_engine.exe"

    assert ace_engine_installed(appdata) is False

    engine_path.parent.mkdir(parents=True)
    engine_path.write_bytes(b"")

    assert ace_engine_installed(appdata) is True
