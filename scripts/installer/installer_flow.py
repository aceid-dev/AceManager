from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

from src.common import log_error, log_info, log_step, log_success, log_warning
from installer_discovery import ace_engine_installed, discover_installation, vlc_installed
from installer_shortcuts import create_shortcut
from installer_system import ask_yes_no, wait_keypress
from installer_types import InstallerDiscovery, InstallerPaths


def build_paths(base_dir: Path) -> InstallerPaths:
    appdata = Path(os.environ.get("APPDATA", ""))
    ace_dest = appdata / "ACEStream"
    acemanager_dest = ace_dest / "AceManager.exe"
    lista_dest = ace_dest / "ListaAceStream.exe"
    start_menu = appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    desktop = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"

    return InstallerPaths(
        base_dir=base_dir,
        appdata=appdata,
        ace_dest=ace_dest,
        acemanager_dest=acemanager_dest,
        lista_dest=lista_dest,
        start_menu=start_menu,
        desktop=desktop,
        link_start=start_menu / "AceManager.lnk",
        link_desktop=desktop / "AceManager.lnk",
    )


def _validate_required_files(discovery: InstallerDiscovery) -> list[str]:
    missing: list[str] = []

    if discovery.ace_already_installed:
        log_info("Ace Stream ya esta instalado; se omite requisito del instalador")
    elif not discovery.ace_installer:
        missing.append("Instalador de Ace Stream (Ace_Stream*.exe) [requerido]")
    else:
        log_success(f"Encontrado: {discovery.ace_installer.name}")

    if discovery.vlc_already_installed:
        log_info("VLC ya esta instalado; se omite requisito del instalador")
    elif not discovery.vlc_installer:
        missing.append("Instalador de VLC (vlc*.exe) [requerido]")
    else:
        log_success(f"Encontrado: {discovery.vlc_installer.name}")

    if not discovery.acemanager_src:
        missing.append("AceManager.exe")
    else:
        log_success(f"Encontrado: {discovery.acemanager_src.name}")

    if not discovery.lista_src:
        missing.append("ListaAceStream.exe")
    else:
        log_success(f"Encontrado: {discovery.lista_src.name}")

    return missing


def _install_prerequisites(discovery: InstallerDiscovery, appdata: Path) -> bool:
    has_errors = False

    log_step("[2/4] Verificando instalaciones...")
    if discovery.ace_already_installed:
        log_info("Ace Stream ya esta instalado")
    if discovery.vlc_already_installed:
        log_info("VLC ya esta instalado")

    if not discovery.ace_already_installed or not discovery.vlc_already_installed:
        log_step("[3/4] Instalando software necesario...")
        if not discovery.ace_already_installed and discovery.ace_installer:
            log_info("Iniciando instalacion de Ace Stream...")
            subprocess.Popen([str(discovery.ace_installer)])

        if not discovery.vlc_already_installed and discovery.vlc_installer:
            log_info("Iniciando instalacion de VLC (modo silencioso)...")
            subprocess.Popen([str(discovery.vlc_installer), "/S"])

        timeout_seconds = 300
        elapsed = 0
        check_interval = 3
        ace_complete = discovery.ace_already_installed
        vlc_complete = discovery.vlc_already_installed

        while (not ace_complete or not vlc_complete) and elapsed < timeout_seconds:
            time.sleep(check_interval)
            elapsed += check_interval

            if not ace_complete and ace_engine_installed(appdata):
                ace_complete = True
                log_success("Ace Stream instalado correctamente")

            if not vlc_complete and vlc_installed():
                vlc_complete = True
                log_success("VLC instalado correctamente")

            if (not ace_complete or not vlc_complete) and elapsed % 15 == 0:
                waiting = []
                if not ace_complete:
                    waiting.append("Ace Stream")
                if not vlc_complete:
                    waiting.append("VLC")
                log_info(f"Esperando: {', '.join(waiting)}... ({elapsed} seg)")

        if not ace_complete:
            log_warning("Ace Stream requiere atencion manual")
            wait_keypress(log_info, "Completa la instalacion y pulsa Enter cuando termines...")
            if not ace_engine_installed(appdata):
                log_error("Ace Stream no se instalo correctamente")
                has_errors = True

        if not vlc_complete:
            log_warning("VLC puede no estar completamente instalado")
    else:
        log_info("[3/4] Software ya instalado, se omite este paso")

    return has_errors


def _install_executables(discovery: InstallerDiscovery, paths: InstallerPaths) -> bool:
    has_errors = False

    log_step("[4/4] Instalando/actualizando ejecutables...")
    paths.ace_dest.mkdir(parents=True, exist_ok=True)

    if discovery.acemanager_src is None or discovery.lista_src is None:
        raise RuntimeError("Faltan ejecutables requeridos para copiar")

    if paths.acemanager_dest.exists():
        should_update_acemanager = ask_yes_no(
            log_warning,
            "AceManager.exe ya existe. Deseas actualizarlo?",
            default=True,
        )
        if should_update_acemanager:
            shutil.copy2(discovery.acemanager_src, paths.acemanager_dest)
            log_success(f"AceManager.exe actualizado en: {paths.ace_dest}")
        else:
            log_info("Se conserva la version existente de AceManager.exe")
    else:
        shutil.copy2(discovery.acemanager_src, paths.acemanager_dest)
        log_success(f"AceManager.exe instalado en: {paths.ace_dest}")

    if paths.lista_dest.exists():
        should_update_lista = ask_yes_no(
            log_warning,
            "ListaAceStream.exe ya existe. Deseas actualizarlo?",
            default=True,
        )
        if should_update_lista:
            shutil.copy2(discovery.lista_src, paths.lista_dest)
            log_success(f"ListaAceStream.exe actualizado en: {paths.ace_dest}")
        else:
            log_info("Se conserva la version existente de ListaAceStream.exe")
    else:
        shutil.copy2(discovery.lista_src, paths.lista_dest)
        log_success(f"ListaAceStream.exe instalado en: {paths.ace_dest}")

    log_info("Creando accesos directos...")
    shortcuts = [
        (paths.link_start, "Menu Inicio"),
        (paths.link_desktop, "Escritorio"),
    ]

    success = 0
    for shortcut_path, label in shortcuts:
        try:
            shortcut_path.parent.mkdir(parents=True, exist_ok=True)
            create_shortcut(
                shortcut_path,
                paths.acemanager_dest,
                paths.ace_dest,
                "AceManager - Gestor de enlaces Ace Stream",
            )
            log_success(f"Acceso directo creado: {label}")
            success += 1
        except Exception as error:
            log_warning(f"No se pudo crear acceso directo ({label}): {error}")

    if success == 0:
        log_warning("No se pudieron crear accesos directos automaticamente")
        has_errors = True
    elif success < len(shortcuts):
        log_warning("Solo algunos accesos directos se crearon correctamente")

    return has_errors


def run_installation(paths: InstallerPaths) -> bool:
    has_errors = False

    log_step("[1/4] Buscando archivos necesarios...")
    discovery = discover_installation(paths.base_dir, paths.appdata)

    missing = _validate_required_files(discovery)
    if missing:
        log_error("Faltan archivos necesarios:")
        for item in missing:
            log_error(f"- {item}")
        raise RuntimeError("Archivos faltantes")

    log_success("Todos los archivos se encontraron correctamente")

    if _install_prerequisites(discovery, paths.appdata):
        has_errors = True

    if _install_executables(discovery, paths):
        has_errors = True

    return has_errors
