from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.common import log_error, log_info, log_step, log_success, log_warning

if os.name == "nt":
    import winreg
else:  # pragma: no cover - only executed outside Windows
    winreg = None


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except OSError:
        return False


def elevate() -> None:
    params = " ".join(f'"{arg}"' for arg in sys.argv)
    result = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    if result <= 32:
        raise RuntimeError("No se pudo elevar privilegios")


def wait_keypress(message: str = "Presiona Enter para continuar...") -> None:
    print()
    log_info(message)
    input()


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


def ask_yes_no(question: str, *, default: bool = True) -> bool:
    suffix = "[S/n]" if default else "[s/N]"
    while True:
        answer = input(f"{question} {suffix}: ").strip().lower()
        if not answer:
            return default
        if answer in {"s", "si", "y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        log_warning("Respuesta invalida. Escribe 's' o 'n'.")


def escape_ps(value: str) -> str:
    return value.replace("'", "''")


def create_shortcut(path: Path, target: Path, working_dir: Path, description: str) -> None:
    ps_script = (
        "$shell=New-Object -ComObject WScript.Shell;"
        f"$shortcut=$shell.CreateShortcut('{escape_ps(str(path))}');"
        f"$shortcut.TargetPath='{escape_ps(str(target))}';"
        f"$shortcut.WorkingDirectory='{escape_ps(str(working_dir))}';"
        f"$shortcut.IconLocation='{escape_ps(str(target))},0';"
        f"$shortcut.Description='{escape_ps(description)}';"
        "$shortcut.Save();"
    )

    subprocess.run(
        ["powershell", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        check=True,
    )

    # Activa el flag "Run as administrator" en el acceso directo.
    data = bytearray(path.read_bytes())
    if len(data) > 0x15:
        data[0x15] = data[0x15] | 0x20
        path.write_bytes(data)


def main() -> int:
    if os.name != "nt":
        log_error("Este instalador solo es compatible con Windows.")
        return 1

    if not is_admin():
        try:
            log_step("Elevando privilegios de administrador...")
            elevate()
            return 0
        except Exception as error:
            log_error("No se pudo elevar privilegios")
            log_error(str(error))
            wait_keypress()
            return 1

    log_step("==========================================")
    log_step("INSTALADOR ACEMANAGER")
    log_step("==========================================")

    base_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    if not base_dir.exists() or any(token in str(base_dir) for token in ("System32", "Temp")):
        base_dir = Path.home() / "Downloads"

    log_info(f"Buscando archivos en: {base_dir}")

    appdata = Path(os.environ.get("APPDATA", ""))
    ace_dest = appdata / "ACEStream"
    acemanager_dest = ace_dest / "AceManager.exe"
    lista_dest = ace_dest / "ListaAceStream.exe"
    start_menu = appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    desktop = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"

    link_start = start_menu / "AceManager.lnk"
    link_desktop = desktop / "AceManager.lnk"

    has_errors = False

    try:
        log_step("[1/4] Buscando archivos necesarios...")

        ace_already_installed = ace_engine_installed(appdata)
        vlc_already_installed = vlc_installed()

        ace_installer = find_ace_installer(base_dir)
        vlc_installer = find_first(base_dir, "vlc*.exe")
        acemanager_src = find_first(base_dir, "AceManager.exe")
        lista_src = find_first(base_dir, "ListaAceStream.exe")

        missing = []
        if ace_already_installed:
            log_info("Ace Stream ya esta instalado; se omite requisito del instalador")
        elif not ace_installer:
            missing.append("Instalador de Ace Stream (Ace_Stream*.exe) [requerido]")
        else:
            log_success(f"Encontrado: {ace_installer.name}")

        if vlc_already_installed:
            log_info("VLC ya esta instalado; se omite requisito del instalador")
        elif not vlc_installer:
            missing.append("Instalador de VLC (vlc*.exe) [requerido]")
        else:
            log_success(f"Encontrado: {vlc_installer.name}")

        if not acemanager_src:
            missing.append("AceManager.exe")
        else:
            log_success(f"Encontrado: {acemanager_src.name}")

        if not lista_src:
            missing.append("ListaAceStream.exe")
        else:
            log_success(f"Encontrado: {lista_src.name}")

        if missing:
            log_error("Faltan archivos necesarios:")
            for item in missing:
                log_error(f"- {item}")
            raise RuntimeError("Archivos faltantes")

        log_success("Todos los archivos se encontraron correctamente")

        log_step("[2/4] Verificando instalaciones...")
        if ace_already_installed:
            log_info("Ace Stream ya esta instalado")
        if vlc_already_installed:
            log_info("VLC ya esta instalado")

        if not ace_already_installed or not vlc_already_installed:
            log_step("[3/4] Instalando software necesario...")
            if not ace_already_installed and ace_installer:
                log_info("Iniciando instalacion de Ace Stream...")
                subprocess.Popen([str(ace_installer)])

            if not vlc_already_installed and vlc_installer:
                log_info("Iniciando instalacion de VLC (modo silencioso)...")
                subprocess.Popen([str(vlc_installer), "/S"])

            timeout_seconds = 300
            elapsed = 0
            check_interval = 3
            ace_complete = ace_already_installed
            vlc_complete = vlc_already_installed

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
                wait_keypress("Completa la instalacion y pulsa Enter cuando termines...")
                if not ace_engine_installed(appdata):
                    log_error("Ace Stream no se instalo correctamente")
                    has_errors = True

            if not vlc_complete:
                log_warning("VLC puede no estar completamente instalado")
        else:
            log_info("[3/4] Software ya instalado, se omite este paso")

        log_step("[4/4] Instalando/actualizando ejecutables...")
        ace_dest.mkdir(parents=True, exist_ok=True)

        if acemanager_dest.exists():
            should_update_acemanager = ask_yes_no(
                "AceManager.exe ya existe. Deseas actualizarlo?",
                default=True,
            )
            if should_update_acemanager:
                shutil.copy2(acemanager_src, acemanager_dest)
                log_success(f"AceManager.exe actualizado en: {ace_dest}")
            else:
                log_info("Se conserva la version existente de AceManager.exe")
        else:
            shutil.copy2(acemanager_src, acemanager_dest)
            log_success(f"AceManager.exe instalado en: {ace_dest}")

        if lista_dest.exists():
            should_update_lista = ask_yes_no(
                "ListaAceStream.exe ya existe. Deseas actualizarlo?",
                default=True,
            )
            if should_update_lista:
                shutil.copy2(lista_src, lista_dest)
                log_success(f"ListaAceStream.exe actualizado en: {ace_dest}")
            else:
                log_info("Se conserva la version existente de ListaAceStream.exe")
        else:
            shutil.copy2(lista_src, lista_dest)
            log_success(f"ListaAceStream.exe instalado en: {ace_dest}")

        log_info("Creando accesos directos...")
        shortcuts = [
            (link_start, "Menu Inicio"),
            (link_desktop, "Escritorio"),
        ]

        success = 0
        for shortcut_path, label in shortcuts:
            try:
                shortcut_path.parent.mkdir(parents=True, exist_ok=True)
                create_shortcut(
                    shortcut_path,
                    acemanager_dest,
                    ace_dest,
                    "AceManager - Gestor de enlaces Ace Stream",
                )
                log_success(f"Acceso directo creado: {label}")
                success += 1
            except Exception as error:
                log_warning(f"No se pudo crear acceso directo ({label}): {error}")

        if success == 0:
            log_warning("No se pudieron crear accesos directos automaticamente")
        elif success < len(shortcuts):
            log_warning("Solo algunos accesos directos se crearon correctamente")

    except Exception as error:
        log_error("ERROR CRITICO DURANTE LA INSTALACION")
        log_error(str(error))
        has_errors = True

    if has_errors:
        log_warning("Instalacion finalizada con advertencias")
    else:
        log_success("Instalacion finalizada correctamente")

    wait_keypress("Pulsa Enter para cerrar...")
    return 0 if not has_errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
