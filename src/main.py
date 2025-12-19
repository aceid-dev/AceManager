from __future__ import annotations

import re
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.check_ace_engine import test_ace_engine
from src.common import clear_screen
from src.functions.pause import pause
from src.player import start_player
from src.start_ace_engine import start_ace_engine
from src.stop_ace_engine import stop_ace_engine


def _show_menu() -> None:
    print(" ***************************")
    print(" *           Menu          *")
    print(" ***************************")
    print()
    print(" 1.) Start Ace Stream Engine")
    print(" 2.) Stop Ace Stream Engine")
    print(" 3.) Check Ace Stream Engine")
    print(" 4.) Play Ace Stream ID")
    print(" 0.) Quit")
    print()


def run_menu() -> None:
    clear_screen()

    selection = ""
    while selection != "0":
        _show_menu()
        selection = input("Select an option and press Enter: ").strip()

        if not re.fullmatch(r"[0-4]", selection):
            input("Opcion invalida. Pulsa Enter para continuar...")
            clear_screen()
            continue

        if selection == "1":
            start_ace_engine()
            pause()
            clear_screen()
            continue

        if selection == "2":
            stop_ace_engine()
            pause()
            clear_screen()
            continue

        if selection == "3":
            test_ace_engine()
            pause()
            clear_screen()
            continue

        if selection == "4":
            test_ace_engine()
            start_player()
            pause()
            clear_screen()


if __name__ == "__main__":
    run_menu()
