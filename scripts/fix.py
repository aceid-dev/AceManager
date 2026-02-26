from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.functions import clear_screen, log_error, log_info, log_step, log_success, log_warning


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


def get_current_list_value() -> str | None:
    content = read_config_text()
    lista_match = re.search(r"^\s*lista\s*=\s*(.+)", content, flags=re.MULTILINE)
    if not lista_match:
        return None

    current_value = lista_match.group(1).strip()
    if not current_value:
        return None

    return current_value


def resolve_known_list(value: str | None) -> str | None:
    if not value:
        return None

    value_normalized = value.casefold()
    for known_list in LISTS:
        if known_list.casefold() == value_normalized:
            return known_list

    return None


def build_available_list_changes() -> tuple[str | None, dict[str, str]]:
    current_list = get_current_list_value()
    source = resolve_known_list(current_list)
    if not source:
        return current_list, {}

    destinations = [item for item in LISTS if item != source]
    options = {str(index): destination for index, destination in enumerate(destinations, start=1)}
    return source, options


def show_current_config() -> None:
    if not CONFIG_FILE.exists():
        write_log_error(f"Archivo NO ENCONTRADO: {CONFIG_FILE}")
        return

    content = read_config_text()
    dominio_match = re.search(r"^\s*dominio\s*=\s*(.+)", content, flags=re.MULTILINE)
    current_list = get_current_list_value()

    if dominio_match:
        write_log_info(f"Dominio actual: {dominio_match.group(1).strip()}")
    else:
        write_log_warning("No se encontro clave 'dominio'.")

    if current_list:
        write_log_info(f"Lista actual:   {current_list}")
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


def set_list_change(destination: str) -> None:
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


def show_menu() -> dict[str, str]:
    clear_screen()
    show_current_config()
    print()
    log_step("Cambiar lista de canales")
    print("-----------------------------------")

    source, available_changes = build_available_list_changes()
    if available_changes:
        for option, destination in available_changes.items():
            print(f"{option}. '{source}' -> '{destination}'")
    else:
        if source:
            write_log_warning(f"No hay cambios rapidos disponibles para '{source}'.")
        else:
            write_log_warning("No hay cambios rapidos disponibles para la lista actual.")
            write_log_info("Usa la opcion 7 para introducir una URL completa.")

    print()
    print("7. Introducir nueva URL completa")
    print("0. Salir")
    print("-----------------------------------")
    return available_changes


def invoke_choice_handler(choice: str, available_changes: dict[str, str]) -> bool:
    destination = available_changes.get(choice)
    if destination:
        set_list_change(destination)
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
        available_changes = show_menu()
        choice = input("\nElige una opcion: ").strip()
        keep_running = invoke_choice_handler(choice, available_changes)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
