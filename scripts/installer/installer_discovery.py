from __future__ import annotations

import os
from pathlib import Path

from installer_types import InstallerDiscovery

if os.name == "nt":
    import winreg
else:  # pragma: no cover - only executed outside Windows
    winreg = None


def find_first(base_dir: Path, pattern: str) -> Path | None:
    matches = sorted(base_dir.glob(pattern))
    for match in matches:
        if match.is_file():
            return match
    return None


def find_ace_installer(base_dir: Path) -> Path | None:
    ignored_names = {
        "acemanager.exe",
        "listaacestream.exe",
        "installer.exe",
        "fixconfig.exe",
        "fix.exe",
    }
    for candidate in sorted(base_dir.glob("*Ace*Stream*.exe")):
        if not candidate.is_file():
            continue
        if candidate.name.lower() in ignored_names:
            continue
        return candidate
    return None


def vlc_installed() -> bool:
    if winreg is None:
        return False

    keys = (
        r"SOFTWARE\VideoLAN\VLC",
        r"SOFTWARE\WOW6432Node\VideoLAN\VLC",
    )

    for key_path in keys:
        for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                with winreg.OpenKey(root, key_path):
                    return True
            except OSError:
                continue

    return False


def ace_engine_installed(appdata: Path) -> bool:
    engine_path = appdata / "ACEStream" / "engine" / "ace_engine.exe"
    return engine_path.exists()


def discover_installation(base_dir: Path, appdata: Path) -> InstallerDiscovery:
    return InstallerDiscovery(
        ace_already_installed=ace_engine_installed(appdata),
        vlc_already_installed=vlc_installed(),
        ace_installer=find_ace_installer(base_dir),
        vlc_installer=find_first(base_dir, "vlc*.exe"),
        acemanager_src=find_first(base_dir, "AceManager.exe"),
        lista_src=find_first(base_dir, "ListaAceStream.exe"),
        fix_src=find_first(base_dir, "Fix.exe"),
        config_src=find_first(base_dir, "config.ini"),
    )
