from __future__ import annotations

from pathlib import Path

from build.config import PYI_ROOT


def parse_version(version: str) -> tuple[int, int, int, int]:
    parts = version.split(".")
    if len(parts) != 4:
        raise ValueError("La version debe tener formato A.B.C.D")

    numbers = tuple(int(part) for part in parts)
    if any(number < 0 for number in numbers):
        raise ValueError("La version no puede tener valores negativos")

    return numbers  # type: ignore[return-value]


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
