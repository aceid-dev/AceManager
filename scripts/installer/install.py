from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

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


def wait_keypress(message: str = "Presione cualquier tecla para continuar...") -> None:
    print()
    print(message)
    print()
    input()


def find_first(base_dir: Path, pattern: str) -> Path | None:
    matches = sorted(base_dir.glob(pattern))
    for match in matches:
        if match.is_file():
            return match
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
        print("Este instalador solo es compatible con Windows.")
        return 1

    if not is_admin():
        try:
            elevate()
            return 0
        except Exception as error:
            print("ERROR: No se pudo elevar privilegios")
            print(error)
            wait_keypress()
            return 1

    print("==========================================")
    print("  INSTALADOR ACEMANAGER")
    print("==========================================")

    base_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    if not base_dir.exists() or any(token in str(base_dir) for token in ("System32", "Temp")):
        base_dir = Path.home() / "Downloads"

    print(f"Buscando archivos en: {base_dir}")
    print()

    appdata = Path(os.environ.get("APPDATA", ""))
    ace_dest = appdata / "ACEStream"
    acemanager_dest = ace_dest / "AceManager.exe"
    start_menu = appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    desktop = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"

    link_start = start_menu / "AceManager.lnk"
    link_desktop = desktop / "AceManager.lnk"

    has_errors = False

    try:
        print("[1/4] Buscando archivos necesarios...")

        ace_installer = find_first(base_dir, "*Ace*Stream*.exe")
        vlc_installer = find_first(base_dir, "vlc*.exe")
        acemanager_src = find_first(base_dir, "AceManager.exe")

        missing = []
        if not ace_installer:
            missing.append("Ace Stream installer (Ace_Stream*.exe)")
        else:
            print(f"  Encontrado: {ace_installer.name}")

        if not vlc_installer:
            missing.append("VLC installer (vlc*.exe)")
        else:
            print(f"  Encontrado: {vlc_installer.name}")

        if not acemanager_src:
            missing.append("AceManager.exe")
        else:
            print(f"  Encontrado: {acemanager_src.name}")

        if missing:
            print("\nERROR: Faltan archivos necesarios:")
            for item in missing:
                print(f"  - {item}")
            raise RuntimeError("Archivos faltantes")

        print("\n  Todos los archivos encontrados correctamente!")

        print("\n[2/4] Verificando instalaciones...")
        ace_installed = ace_dest.exists()
        vlc_already_installed = vlc_installed()

        if ace_installed:
            print("  Ace Stream ya esta instalado")
        if vlc_already_installed:
            print("  VLC ya esta instalado")

        if not ace_installed or not vlc_already_installed:
            print("\n[3/4] Instalando software necesario...")
            if not ace_installed and ace_installer:
                print("  Iniciando instalacion de Ace Stream...")
                subprocess.Popen([str(ace_installer)])

            if not vlc_already_installed and vlc_installer:
                print("  Iniciando instalacion de VLC (modo silencioso)...")
                subprocess.Popen([str(vlc_installer), "/S"])

            timeout_seconds = 300
            elapsed = 0
            check_interval = 3
            ace_complete = ace_installed
            vlc_complete = vlc_already_installed

            while (not ace_complete or not vlc_complete) and elapsed < timeout_seconds:
                time.sleep(check_interval)
                elapsed += check_interval

                if not ace_complete and ace_dest.exists():
                    ace_complete = True
                    print("  [OK] Ace Stream instalado correctamente")

                if not vlc_complete and vlc_installed():
                    vlc_complete = True
                    print("  [OK] VLC instalado correctamente")

                if (not ace_complete or not vlc_complete) and elapsed % 15 == 0:
                    waiting = []
                    if not ace_complete:
                        waiting.append("Ace Stream")
                    if not vlc_complete:
                        waiting.append("VLC")
                    print(f"  Esperando: {', '.join(waiting)}... ({elapsed} seg)")

            if not ace_complete:
                print("\nATENCION: Ace Stream requiere atencion manual")
                wait_keypress("Complete la instalacion y pulse Enter cuando termine...")
                if not ace_dest.exists():
                    print("ERROR: Ace Stream no se instalo correctamente")
                    has_errors = True

            if not vlc_complete:
                print("Advertencia: VLC puede no estar completamente instalado")
        else:
            print("\n[3/4] Software ya instalado, saltando...")

        print("\n[4/4] Instalando AceManager...")
        ace_dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(acemanager_src, acemanager_dest)
        print(f"  AceManager.exe copiado a: {ace_dest}")

        print("  Creando accesos directos...")
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
                print(f"    [OK] {label}")
                success += 1
            except Exception as error:
                print(f"    [X] {label}: {error}")

        if success == 0:
            print("  No se pudieron crear accesos directos automaticamente")
        elif success < len(shortcuts):
            print("  Algunos accesos directos se crearon correctamente")

    except Exception as error:
        print("\n==========================================")
        print("  ERROR CRITICO DURANTE LA INSTALACION")
        print("==========================================")
        print(error)
        has_errors = True

    print("\n==========================================")
    if has_errors:
        print("Revise los mensajes anteriores")
    else:
        print("Instalacion completa")
    print("==========================================")

    wait_keypress("Presione cualquier tecla para cerrar...")
    return 0 if not has_errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
