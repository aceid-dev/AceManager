# Repository Guidelines

## Project Structure & Module Organization

- `src/` contains the runtime application entrypoints: `main.py`, `player.py`, `start_ace_engine.py`, `stop_ace_engine.py`, and `check_ace_engine.py`.
- `src/functions/` holds shared helpers for logging, process control, VLC discovery, UI, and Ace Stream utilities.
- `scripts/build/` contains the PyInstaller-based build pipeline; `scripts/installer/` contains the Windows installer flow.
- `tests/` contains the `pytest` suite. Keep new tests near the behavior they validate, for example `tests/test_player.py`.
- `docs/` stores user and build documentation. `icons/` contains release assets and executable icons.

## Build, Test, and Development Commands

- `python src/main.py` runs the app from source.
- `python scripts/build/build.py` builds `AceManager.exe`, `ListaAceStream.exe`, `Installer.exe`, `Fix.exe`, and `AceManager.zip`.
- `python -m pip install -r requirements-build.txt -r requirements-test.txt` installs build and test dependencies.
- `python -m pytest -q` runs the test suite.

## Coding Style & Naming Conventions

- Use Python 3.10+ syntax, 4-space indentation, and UTF-8 text files.
- Follow the existing style: small functions, type hints, `pathlib.Path`, and `from __future__ import annotations` in Python modules.
- Use `snake_case` for functions and variables, `UPPER_CASE` for constants, and `PascalCase` for dataclasses such as `InstallerPaths`.
- No formatter or linter is currently configured; keep changes consistent with the existing codebase and avoid unnecessary dependencies.

## Testing Guidelines

- The project uses `pytest`.
- Name test files `test_*.py` and test functions `test_*`.
- Prefer unit tests with `monkeypatch` or mocks for Windows-specific side effects such as `subprocess.Popen`, `tasklist`, `taskkill`, registry lookups, and `%APPDATA%` paths.
- Add tests for new CLI flows, installer logic, and path/process handling before changing release behavior.

## Commit & Pull Request Guidelines

- Follow the existing Conventional Commit style seen in history: `fix(installer): ...`, `refactor(scripts): ...`, `fix(ci): ...`.
- Keep commit scopes specific to the module you changed.
- Pull requests should include a short summary, affected paths, test results, and any Windows-specific manual verification.
- Include screenshots only when menu output, installer UX, or generated assets visibly change.

## Configuration & Release Notes

- `config.ini` is part of the shipped package; preserve backward compatibility when changing its keys.
- CI on `.github/workflows/build-exe.yml` runs on Windows and drives release automation, so build and test changes should be validated together.
