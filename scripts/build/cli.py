from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compila ejecutables autocontenidos de AceManager, ListaAcestream, Installer y Fix (PyInstaller)."
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
        help="Objetivos: All, AceManager, ListaAceStream, Installer, Fix",
    )
    parser.add_argument(
        "--skip-package",
        action="store_true",
        help="Omite la generacion del ZIP",
    )
    return parser.parse_args()
