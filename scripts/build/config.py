from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYI_ROOT = REPO_ROOT / ".pyinstaller"
BUILD_VENV = REPO_ROOT / ".venv-build"
REQUIREMENTS_BUILD = REPO_ROOT / "requirements-build.txt"

TARGETS_ALL = {"AceManager", "ListaAceStream", "Installer", "Fix"}
RELEASE_STANDALONE_ASSETS = ("Installer.exe",)
ACE_MANAGER_ZIP_ASSET = "AceManager.zip"

TARGET_SPECS = {
    "AceManager": {
        "entry_script": REPO_ROOT / "src" / "main.py",
        "output_name": "AceManager",
        "icon_path": REPO_ROOT / "icons" / "launcher.ico",
        "product_title": "Ace Manager",
        "windowed": False,
    },
    "ListaAceStream": {
        "entry_script": REPO_ROOT / "src" / "functions" / "lista_acestream.py",
        "output_name": "ListaAceStream",
        "icon_path": REPO_ROOT / "icons" / "icon.ico",
        "product_title": "Lista AceStream Launcher",
        "windowed": True,
    },
    "Installer": {
        "entry_script": REPO_ROOT / "scripts" / "installer" / "install.py",
        "output_name": "Installer",
        "icon_path": REPO_ROOT / "icons" / "software.ico",
        "product_title": "AceManager Installer",
        "windowed": False,
    },
    "Fix": {
        "entry_script": REPO_ROOT / "scripts" / "fix.py",
        "output_name": "Fix",
        "icon_path": REPO_ROOT / "icons" / "icon.ico",
        "product_title": "AceManager Fix",
        "windowed": False,
    },
}

DEFAULT_CONFIG = """# Configuracion de AceManager
# Puedes poner el dominio de tu servidor aqui
dominio = https://aceid.short.gy

# Puedes poner el nombre de la lista (ej: lista_acestream)
# o una URL completa (ej: https://otro-sitio.com/lista.m3u)
lista = lista_acestream
"""
