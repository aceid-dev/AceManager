from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class InstallerPaths:
    base_dir: Path
    appdata: Path
    ace_dest: Path
    acemanager_dest: Path
    lista_dest: Path
    fix_dest: Path
    config_dest: Path
    start_menu: Path
    desktop: Path
    link_start: Path
    link_desktop: Path
    link_start_lista: Path
    link_desktop_lista: Path
    link_start_fix: Path
    link_desktop_fix: Path


@dataclass(frozen=True)
class InstallerDiscovery:
    ace_already_installed: bool
    vlc_already_installed: bool
    ace_installer: Path | None
    vlc_installer: Path | None
    acemanager_src: Path | None
    lista_src: Path | None
    fix_src: Path | None
    config_src: Path | None
