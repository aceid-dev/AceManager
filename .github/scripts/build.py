#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import uuid
import zipfile
from datetime import datetime
from pathlib import Path

try:
    import PyInstaller.__main__ as pyinstaller
except ImportError:  # pragma: no cover - dependency check path
    pyinstaller = None


REPO_ROOT = Path(__file__).resolve().parents[2]
PYI_ROOT = REPO_ROOT / ".pyinstaller"

TARGETS_ALL = {"AceManager", "ListaAceStream", "Installer", "FixConfig"}

DEFAULT_CONFIG = """# Configuracion de AceManager
# Puedes poner el dominio de tu servidor aqui
dominio = https://aceid.short.gy

# Puedes poner el nombre de la lista (ej: lista_acestream)
# o una URL completa (ej: https://otro-sitio.com/lista.m3u)
lista = lista_acestream
"""


def log(message: str) -> None:
    print(message)


def parse_version(version: str) -> tuple[int, int, int, int]:
    parts = version.split(".")
    if len(parts) != 4:
        raise ValueError("La version debe tener formato A.B.C.D")

    numbers = tuple(int(part) for part in parts)
    if any(number < 0 for number in numbers):
        raise ValueError("La version no puede tener valores negativos")

    return numbers  # type: ignore[return-value]


def normalize_targets(values: list[str]) -> set[str]:
    exploded: list[str] = []
    for value in values:
        exploded.extend(part.strip() for part in value.split(",") if part.strip())

    if not exploded:
        return set(TARGETS_ALL)

    normalized: set[str] = set()
    for target in exploded:
        if target == "All":
            normalized.update(TARGETS_ALL)
            continue

        if target not in TARGETS_ALL:
            raise ValueError(f"Target invalido: {target}")

        normalized.add(target)

    return normalized


def build_version_file(app_version: str, product_name: str) -> Path:
    file_version = parse_version(app_version)
    version_tuple = f"({file_version[0]}, {file_version[1]}, {file_version[2]}, {file_version[3]})"

    PYI_ROOT.mkdir(parents=True, exist_ok=True)
    file_name = product_name.lower().replace(" ", "_") + "_version.txt"
    version_path = PYI_ROOT / file_name

    content = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={version_tuple},
    prodvers={version_tuple},
    mask=0x3F,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'AceManager'),
        StringStruct(u'FileDescription', u'{product_name}'),
        StringStruct(u'FileVersion', u'{app_version}'),
        StringStruct(u'InternalName', u'{product_name}'),
        StringStruct(u'OriginalFilename', u'{product_name}.exe'),
        StringStruct(u'ProductName', u'AceManager'),
        StringStruct(u'ProductVersion', u'{app_version}')]
      )
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

    version_path.write_text(content, encoding="utf-8")
    return version_path


def run_pyinstaller(
    *,
    entry_script: Path,
    output_name: str,
    icon_path: Path,
    product_title: str,
    app_version: str,
    windowed: bool = False,
) -> None:
    if pyinstaller is None:
        raise RuntimeError(
            "PyInstaller no esta instalado. Ejecuta: python -m pip install -r requirements-build.txt"
        )

    if not entry_script.exists():
        raise FileNotFoundError(f"No se encontro el entrypoint: {entry_script}")

    log(f"\n>> Preparando: {output_name}.exe")
    version_file = build_version_file(app_version, product_title)

    work_path = PYI_ROOT / "build" / output_name
    spec_path = PYI_ROOT / "spec" / output_name
    work_path.mkdir(parents=True, exist_ok=True)
    spec_path.mkdir(parents=True, exist_ok=True)

    args = [
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name",
        output_name,
        "--distpath",
        str(REPO_ROOT),
        "--workpath",
        str(work_path),
        "--specpath",
        str(spec_path),
        "--version-file",
        str(version_file),
    ]

    if icon_path.exists():
        args.extend(["--icon", str(icon_path)])

    if windowed:
        args.append("--windowed")

    args.append(str(entry_script))

    pyinstaller.run(args)

    output_exe = REPO_ROOT / f"{output_name}.exe"
    if not output_exe.exists():
        raise RuntimeError(f"No se genero {output_name}.exe")

    log(f"   [OK] {output_name}.exe creado con exito")


def ensure_config_ini() -> Path:
    config_path = REPO_ROOT / "config.ini"
    if not config_path.exists():
        log("   [WARN] config.ini no encontrado. Se genera uno por defecto")
        config_path.write_text(DEFAULT_CONFIG, encoding="ascii")
    return config_path


def package_release(app_version: str) -> Path:
    log("\n>> Iniciando empaquetado ZIP...")

    package_dir = REPO_ROOT / f"AceManager_v{app_version}"
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True, exist_ok=True)

    config_path = ensure_config_ini()

    for file_name in ("AceManager.exe", "ListaAceStream.exe", "Installer.exe", "FixConfig.exe"):
        source = REPO_ROOT / file_name
        if not source.exists():
            raise FileNotFoundError(f"No se encontro {file_name} para empaquetar")
        shutil.copy2(source, package_dir / file_name)

    shutil.copy2(config_path, package_dir / "config.ini")

    zip_path = REPO_ROOT / "AceManager.zip"
    temp_zip = REPO_ROOT / f"AceManager_{uuid.uuid4().hex}.tmp.zip"

    if zip_path.exists():
        try:
            zip_path.unlink()
        except PermissionError:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_path = REPO_ROOT / f"AceManager_{timestamp}.zip"
            log(f"   [WARN] AceManager.zip en uso. Se generara: {zip_path.name}")

    with zipfile.ZipFile(temp_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in package_dir.iterdir():
            archive.write(item, arcname=item.name)

    temp_zip.replace(zip_path)
    shutil.rmtree(package_dir)

    log(f"   [OK] Paquete ZIP generado: {zip_path.name}")
    return zip_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compila ejecutables autocontenidos de AceManager, Launcher, Installer y Fix (PyInstaller)."
    )
    parser.add_argument(
        "--app-version",
        default="1.0.0.0",
        help="Version de archivo para los EXE en formato A.B.C.D",
    )
    parser.add_argument(
        "--targets",
        nargs="+",
        default=["All"],
        help="Objetivos: All, AceManager, ListaAceStream, Installer, FixConfig",
    )
    parser.add_argument(
        "--skip-package",
        action="store_true",
        help="Omite la generacion del ZIP",
    )
    return parser.parse_args()


def main() -> int:
    if os.name != "nt":
        log("[ERROR] La generacion de .exe con este proyecto requiere Windows.")
        log("[INFO] Ejecuta el build en windows-latest o en un equipo Windows.")
        return 1

    args = parse_args()

    try:
        parse_version(args.app_version)
    except ValueError as error:
        log(f"[ERROR] {error}")
        return 1

    try:
        selected_targets = normalize_targets(args.targets)
    except ValueError as error:
        log(f"[ERROR] {error}")
        return 1

    should_package = (not args.skip_package) and selected_targets == TARGETS_ALL

    log("\n[BUILD] Iniciando proceso de compilacion")
    log(f"[INFO] Raiz detectada: {REPO_ROOT}")
    log(f"[INFO] Version de destino: {args.app_version}")
    log(f"[INFO] Objetivos: {', '.join(sorted(selected_targets))}")
    log(f"[INFO] Empaquetado ZIP: {'habilitado' if should_package else 'omitido'}")

    try:
        if "AceManager" in selected_targets:
            run_pyinstaller(
                entry_script=REPO_ROOT / "src" / "main.py",
                output_name="AceManager",
                icon_path=REPO_ROOT / "icons" / "launcher.ico",
                product_title="Ace Manager",
                app_version=args.app_version,
                windowed=False,
            )

        if "ListaAceStream" in selected_targets:
            run_pyinstaller(
                entry_script=REPO_ROOT / "utils" / "lista_acestream.py",
                output_name="ListaAceStream",
                icon_path=REPO_ROOT / "icons" / "icon.ico",
                product_title="Lista AceStream Launcher",
                app_version=args.app_version,
                windowed=True,
            )

        if "Installer" in selected_targets:
            run_pyinstaller(
                entry_script=REPO_ROOT / "scripts" / "installer" / "install.py",
                output_name="Installer",
                icon_path=REPO_ROOT / "icons" / "launcher.ico",
                product_title="AceManager Installer",
                app_version=args.app_version,
                windowed=False,
            )

        if "FixConfig" in selected_targets:
            run_pyinstaller(
                entry_script=REPO_ROOT / "scripts" / "fix.py",
                output_name="FixConfig",
                icon_path=REPO_ROOT / "icons" / "icon.ico",
                product_title="AceManager Fix Config",
                app_version=args.app_version,
                windowed=False,
            )

        if should_package:
            package_release(args.app_version)
        else:
            log("\n[INFO] Empaquetado ZIP omitido por seleccion de objetivos")

        log("\n[OK] PROCESO FINALIZADO: Todo esta listo para el release")
        return 0
    except Exception as error:
        log("\n[ERROR] ERROR CRITICO durante el proceso de build")
        log(f"[DETALLE] {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
