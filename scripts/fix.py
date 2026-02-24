from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.common import clear_screen, log_error, log_info, log_step, log_success, log_warning


def write_log_error(message: str) -> None:
    log_error(message)


def write_log_warning(message: str) -> None:
    log_warning(message)


def write_log_info(message: str) -> None:
    log_info(message)


def write_log_success(message: str) -> None:
    log_success(message)


LISTS = ["lista_acestream", "lista_Icastresana", "lista_ramses"]


def resolve_script_base() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    if "__file__" in globals():
        return Path(__file__).resolve().parent

    return Path.cwd()


def resolve_config_file() -> Path:
    script_base = resolve_script_base()
    appdata = os.environ.get("APPDATA", "")

    candidates = [
        script_base / "config.ini",
        Path(appdata) / "ACEStream" / "config.ini",
        Path(appdata) / "ACEStream" / "manager" / "config.ini",
        REPO_ROOT / "config.ini",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0]


CONFIG_FILE = resolve_config_file()


def read_config_text() -> str:
    return CONFIG_FILE.read_text(encoding="utf-8", errors="ignore")


def show_current_config() -> None:
    if not CONFIG_FILE.exists():
        write_log_error(f"Archivo NO ENCONTRADO: {CONFIG_FILE}")
        return

    content = read_config_text()
    dominio_match = re.search(r"^\s*dominio\s*=\s*(.+)", content, flags=re.MULTILINE)
    lista_match = re.search(r"^\s*lista\s*=\s*(.+)", content, flags=re.MULTILINE)

    if dominio_match:
        write_log_info(f"Dominio actual: {dominio_match.group(1).strip()}")
    else:
        write_log_warning("No se encontro clave 'dominio'.")

    if lista_match:
        write_log_info(f"Lista actual:   {lista_match.group(1).strip()}")
    else:
        write_log_warning("No se encontro clave 'lista'.")


def update_ini_key(key: str, value: str) -> None:
    content = read_config_text()
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*=\s*.+", flags=re.MULTILINE)

    if pattern.search(content):
        new_content = pattern.sub(f"{key} = {value}", content, count=1)
    else:
        new_content = content.rstrip() + f"\n{key} = {value}\n"
        write_log_warning(f"Clave '{key}' no existia. Se ha anadido al final.")

    if content != new_content:
        CONFIG_FILE.write_text(new_content, encoding="ascii", errors="ignore")
        write_log_success(f"Actualizado: {key} = {value}")


def set_list_change(choice: int) -> None:
    idx = (choice - 1) // 2
    others = [item for item in LISTS if item != LISTS[idx]]
    destination = others[(choice - 1) % 2]
    update_ini_key("lista", destination)
    input("\nPulsa Enter para continuar...")


def set_replacement_automatic() -> None:
    while True:
        raw_value = input(
            "\nIntroduce la URL completa de la lista (ej: https://servidor.com/ruta/lista.m3u): "
        ).strip()

        if not raw_value:
            write_log_error("No puedes dejarlo vacio.")
            continue

        if not re.match(r"^https?://", raw_value, flags=re.IGNORECASE):
            write_log_error("La URL debe empezar por http:// o https://")
            continue

        parsed = urlparse(raw_value)
        if not parsed.scheme or not parsed.netloc:
            write_log_error("URL invalida.")
            continue

        base_url = f"{parsed.scheme}://{parsed.netloc}"

        normalized_path = parsed.path or ""
        if normalized_path.endswith("/"):
            write_log_error("La URL no termina con un nombre de archivo valido.")
            continue

        file_name = normalized_path.split("/")[-1].strip()
        if not file_name:
            write_log_error("La URL no termina con un nombre de archivo valido.")
            continue

        directory = "/".join(part for part in normalized_path.split("/")[:-1] if part)
        if directory:
            base_url = f"{base_url}/{directory}"

        update_ini_key("dominio", base_url)
        update_ini_key("lista", file_name)

        print()
        write_log_success("URL aplicada correctamente.")
        write_log_info(f"   dominio = {base_url}")
        write_log_info(f"   lista   = {file_name}")
        input("\nPulsa Enter para continuar...")
        return


def show_menu() -> None:
    clear_screen()
    show_current_config()
    print()
    log_step("Cambiar lista de canales")
    print("-----------------------------------")

    for index, source in enumerate(LISTS):
        others = [item for item in LISTS if item != source]
        print(f"{index * 2 + 1}. '{source}' -> '{others[0]}'")
        print(f"{index * 2 + 2}. '{source}' -> '{others[1]}'")

    print()
    print("7. Introducir nueva URL completa")
    print("0. Salir")
    print("-----------------------------------")


def invoke_choice_handler(choice: str) -> bool:
    if choice in {"1", "2", "3", "4", "5", "6"}:
        set_list_change(int(choice))
        return True

    if choice == "7":
        set_replacement_automatic()
        return True

    if choice == "0":
        write_log_info("Saliendo...")
        return False

    write_log_warning("Opcion invalida.")
    input("Pulsa Enter para continuar...")
    return True


def main() -> int:
    if not CONFIG_FILE.exists():
        write_log_error(f"El archivo '{CONFIG_FILE}' no existe.")
        input("Pulsa Enter para salir...")
        return 1

    keep_running = True
    while keep_running:
        show_menu()
        choice = input("\nElige una opcion: ").strip()
        keep_running = invoke_choice_handler(choice)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
