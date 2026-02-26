from __future__ import annotations

import os
import shutil
import subprocess
import time
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

from src.functions import log_error, log_info, log_step, log_success, log_warning
from installer_discovery import ace_engine_installed, discover_installation, vlc_installed
from installer_shortcuts import create_shortcut
from installer_system import ask_yes_no, wait_keypress
from installer_types import InstallerDiscovery, InstallerPaths


def build_paths(base_dir: Path) -> InstallerPaths:
    appdata = Path(os.environ.get("APPDATA", ""))
    ace_dest = appdata / "ACEStream"
    acemanager_dest = ace_dest / "AceManager.exe"
    lista_dest = ace_dest / "ListaAceStream.exe"
    fix_dest = ace_dest / "Fix.exe"
    config_dest = ace_dest / "config.ini"
    start_menu = appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "AceManager"
    desktop = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"

    return InstallerPaths(
        base_dir=base_dir,
        appdata=appdata,
        ace_dest=ace_dest,
        acemanager_dest=acemanager_dest,
        lista_dest=lista_dest,
        fix_dest=fix_dest,
        config_dest=config_dest,
        start_menu=start_menu,
        desktop=desktop,
        link_start=start_menu / "AceManager.lnk",
        link_desktop=desktop / "AceManager.lnk",
        link_start_lista=start_menu / "ListaAceStream.lnk",
        link_desktop_lista=desktop / "ListaAceStream.lnk",
        link_start_fix=start_menu / "Fix.lnk",
        link_desktop_fix=desktop / "Fix.lnk",
    )


def _extract_acemanager_zip(base_dir: Path) -> bool:
    zip_path = base_dir / "AceManager.zip"
    if not zip_path.exists():
        log_info("No se encontro AceManager.zip. Se buscara contenido extraido manualmente.")
        return False

    log_info("Detectado AceManager.zip. Extrayendo contenido en carpeta actual...")
    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            extracted_files = 0
            for member in archive.infolist():
                if member.is_dir():
                    continue

                file_name = Path(member.filename).name
                if not file_name:
                    continue

                destination = base_dir / file_name
                with archive.open(member, "r") as source, destination.open("wb") as target:
                    shutil.copyfileobj(source, target)
                extracted_files += 1

        log_success(
            f"AceManager.zip extraido correctamente ({extracted_files} archivos, sin crear carpeta)."
        )
        return True
    except Exception as error:
        log_error(f"No se pudo extraer AceManager.zip: {error}")
        raise


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

    if not discovery.fix_src:
        missing.append("Fix.exe")
    else:
        log_success(f"Encontrado: {discovery.fix_src.name}")

    if not discovery.config_src:
        missing.append("config.ini")
    else:
        log_success(f"Encontrado: {discovery.config_src.name}")

    return missing


def _install_prerequisites(discovery: InstallerDiscovery, appdata: Path) -> bool:
    has_errors = False

    log_step("[3/5] Verificando instalaciones...")
    if discovery.ace_already_installed:
        log_info("Ace Stream ya esta instalado")
    if discovery.vlc_already_installed:
        log_info("VLC ya esta instalado")

    if not discovery.ace_already_installed or not discovery.vlc_already_installed:
        log_step("[4/5] Instalando software necesario...")
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
        log_info("[4/5] Software ya instalado, se omite este paso")

    return has_errors


def _install_executables(discovery: InstallerDiscovery, paths: InstallerPaths) -> bool:
    has_errors = False

    log_step("[5/5] Instalando/actualizando ejecutables...")
    paths.ace_dest.mkdir(parents=True, exist_ok=True)

    if (
        discovery.acemanager_src is None
        or discovery.lista_src is None
        or discovery.fix_src is None
        or discovery.config_src is None
    ):
        raise RuntimeError("Faltan archivos requeridos para copiar")

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

    if paths.fix_dest.exists():
        should_update_fix = ask_yes_no(
            log_warning,
            "Fix.exe ya existe. Deseas actualizarlo?",
            default=True,
        )
        if should_update_fix:
            shutil.copy2(discovery.fix_src, paths.fix_dest)
            log_success(f"Fix.exe actualizado en: {paths.ace_dest}")
        else:
            log_info("Se conserva la version existente de Fix.exe")
    else:
        shutil.copy2(discovery.fix_src, paths.fix_dest)
        log_success(f"Fix.exe instalado en: {paths.ace_dest}")

    if paths.config_dest.exists():
        should_update_config = ask_yes_no(
            log_warning,
            "config.ini ya existe. Deseas actualizarlo?",
            default=True,
        )
        if should_update_config:
            shutil.copy2(discovery.config_src, paths.config_dest)
            log_success(f"config.ini actualizado en: {paths.ace_dest}")
        else:
            log_info("Se conserva la version existente de config.ini")
    else:
        shutil.copy2(discovery.config_src, paths.config_dest)
        log_success(f"config.ini instalado en: {paths.ace_dest}")

    _cleanup_start_menu_shortcuts(paths)

    log_info("Creando accesos directos...")
    shortcuts = [
        (
            paths.link_start,
            paths.acemanager_dest,
            "AceManager - Gestor de enlaces Ace Stream",
            "Menu Inicio (AceManager)",
        ),
        (
            paths.link_desktop,
            paths.acemanager_dest,
            "AceManager - Gestor de enlaces Ace Stream",
            "Escritorio (AceManager)",
        ),
        (
            paths.link_start_lista,
            paths.lista_dest,
            "ListaAceStream - Reproductor de lista Ace Stream",
            "Menu Inicio (ListaAceStream)",
        ),
        (
            paths.link_desktop_lista,
            paths.lista_dest,
            "ListaAceStream - Reproductor de lista Ace Stream",
            "Escritorio (ListaAceStream)",
        ),
        (
            paths.link_start_fix,
            paths.fix_dest,
            "Fix - Configuracion de dominio y lista",
            "Menu Inicio (Fix)",
        ),
        (
            paths.link_desktop_fix,
            paths.fix_dest,
            "Fix - Configuracion de dominio y lista",
            "Escritorio (Fix)",
        ),
    ]

    success = 0
    for shortcut_path, target_path, description, label in shortcuts:
        try:
            shortcut_path.parent.mkdir(parents=True, exist_ok=True)
            if shortcut_path.exists():
                shortcut_path.unlink()
            create_shortcut(
                shortcut_path,
                target_path,
                paths.ace_dest,
                description,
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


def _cleanup_start_menu_shortcuts(paths: InstallerPaths) -> None:
    start_menu_root = paths.start_menu.parent
    if not start_menu_root.exists():
        return

    managed_names = {
        paths.link_start.name,
        paths.link_start_lista.name,
        paths.link_start_fix.name,
    }

    removed_count = 0
    for candidate in start_menu_root.rglob("*.lnk"):
        if candidate.name not in managed_names:
            continue
        if candidate.parent == paths.start_menu:
            continue

        try:
            candidate.unlink()
            removed_count += 1
            log_info(f"Acceso directo antiguo eliminado: {candidate}")
        except OSError as error:
            log_warning(f"No se pudo eliminar acceso directo antiguo ({candidate}): {error}")

    if removed_count > 0:
        log_success(
            f"Limpieza de Menu Inicio completada: {removed_count} acceso(s) antiguo(s) eliminado(s)"
        )


def run_installation(paths: InstallerPaths) -> bool:
    has_errors = False

    log_step("[1/5] Preparando archivos del instalador...")
    extracted_from_zip = _extract_acemanager_zip(paths.base_dir)

    log_step("[2/5] Buscando archivos necesarios...")
    discovery = discover_installation(paths.base_dir, paths.appdata)

    missing = _validate_required_files(discovery)
    if missing:
        log_error("Faltan archivos necesarios:")
        for item in missing:
            log_error(f"- {item}")
        if not extracted_from_zip:
            log_error(
                "No se encontro AceManager.zip ni los archivos extraidos en la misma carpeta del instalador."
            )
            log_error(
                "Coloca AceManager.zip junto a Installer.exe o extrae su contenido en esa misma carpeta."
            )
        raise RuntimeError("Archivos faltantes")

    log_success("Todos los archivos se encontraron correctamente")

    if _install_prerequisites(discovery, paths.appdata):
        has_errors = True

    if _install_executables(discovery, paths):
        has_errors = True

    return has_errors
