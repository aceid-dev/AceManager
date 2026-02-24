from __future__ import annotations

import uuid
import zipfile
from datetime import datetime
from pathlib import Path

from build_modules.config import (
    ACE_MANAGER_ZIP_ASSET,
    DEFAULT_CONFIG,
    RELEASE_STANDALONE_ASSETS,
    REPO_ROOT,
)
from build_modules.logging_utils import log


def ensure_config_ini() -> Path:
    config_path = REPO_ROOT / "config.ini"
    if not config_path.exists():
        log("   [WARN] config.ini no encontrado. Se genera uno por defecto")
        config_path.write_text(DEFAULT_CONFIG, encoding="ascii")
    return config_path


def _resolve_zip_target(path: Path) -> Path:
    if path.exists():
        try:
            path.unlink()
        except PermissionError:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fallback = path.with_stem(f"{path.stem}_{timestamp}")
            log(f"   [WARN] {path.name} en uso. Se generara: {fallback.name}")
            return fallback
    return path


def _build_zip(zip_name: str, files: list[tuple[str, Path]]) -> Path:
    zip_path = _resolve_zip_target(REPO_ROOT / zip_name)
    temp_zip = REPO_ROOT / f"{Path(zip_name).stem}_{uuid.uuid4().hex}.tmp.zip"

    with zipfile.ZipFile(temp_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for arcname, source in files:
            archive.write(source, arcname=arcname)

    temp_zip.replace(zip_path)
    return zip_path


def package_release(app_version: str) -> Path:
    log(f"\n>> Iniciando empaquetado de release (version {app_version})...")

    config_path = ensure_config_ini()

    for file_name in (*RELEASE_STANDALONE_ASSETS, "AceManager.exe", "ListaAceStream.exe", "Fix.exe"):
        source = REPO_ROOT / file_name
        if not source.exists():
            raise FileNotFoundError(f"No se encontro {file_name} para release")

    ace_zip_path = _build_zip(
        ACE_MANAGER_ZIP_ASSET,
        [
            ("AceManager.exe", REPO_ROOT / "AceManager.exe"),
            ("ListaAceStream.exe", REPO_ROOT / "ListaAceStream.exe"),
            ("Fix.exe", REPO_ROOT / "Fix.exe"),
            ("config.ini", config_path),
        ],
    )

    legacy_artifacts = [REPO_ROOT / "FixConfig.zip", REPO_ROOT / "ListaAcestream.zip"]
    for legacy_artifact in legacy_artifacts:
        if not legacy_artifact.exists():
            continue

        try:
            legacy_artifact.unlink()
            log(f"   [INFO] Artefacto legado eliminado: {legacy_artifact.name}")
        except OSError:
            log(f"   [WARN] No se pudo eliminar artefacto legado: {legacy_artifact.name}")

    log(f"   [OK] Paquete ZIP generado: {ace_zip_path.name}")
    log("   [OK] Assets de release listos: " + ", ".join(RELEASE_STANDALONE_ASSETS))
    return ace_zip_path
