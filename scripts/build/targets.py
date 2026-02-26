from __future__ import annotations

from build.config import TARGETS_ALL


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
