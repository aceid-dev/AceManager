from __future__ import annotations

import shutil
import uuid
import zipfile
from datetime import datetime
from pathlib import Path

from build_modules.config import (
    DEFAULT_CONFIG,
    FIX_ZIP_ASSET,
    RELEASE_STANDALONE_ASSETS,
    REPO_ROOT,
    ZIP_EXECUTABLES,
)
from build_modules.logging_utils import log


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

    for file_name in ZIP_EXECUTABLES:
        source = REPO_ROOT / file_name
        if not source.exists():
            raise FileNotFoundError(f"No se encontro {file_name} para empaquetar")
        shutil.copy2(source, package_dir / file_name)

    shutil.copy2(config_path, package_dir / "config.ini")

    for file_name in RELEASE_STANDALONE_ASSETS:
        source = REPO_ROOT / file_name
        if not source.exists():
            raise FileNotFoundError(f"No se encontro {file_name} para release")

    fix_exe = REPO_ROOT / "FixConfig.exe"
    if not fix_exe.exists():
        raise FileNotFoundError("No se encontro FixConfig.exe para generar FixConfig.zip")

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

    fix_zip_path = REPO_ROOT / FIX_ZIP_ASSET
    fix_temp_zip = REPO_ROOT / f"FixConfig_{uuid.uuid4().hex}.tmp.zip"

    if fix_zip_path.exists():
        try:
            fix_zip_path.unlink()
        except PermissionError:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fix_zip_path = REPO_ROOT / f"FixConfig_{timestamp}.zip"
            log(f"   [WARN] {FIX_ZIP_ASSET} en uso. Se generara: {fix_zip_path.name}")

    with zipfile.ZipFile(fix_temp_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(fix_exe, arcname="FixConfig.exe")

    fix_temp_zip.replace(fix_zip_path)

    log(f"   [OK] Paquete ZIP generado: {zip_path.name}")
    log(f"   [OK] Paquete ZIP generado: {fix_zip_path.name}")
    log(
        "   [OK] Assets fuera del ZIP listos: "
        + ", ".join(RELEASE_STANDALONE_ASSETS)
    )
    return zip_path
