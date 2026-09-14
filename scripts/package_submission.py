"""Create the under-10-MB reviewer archive without local or secret files."""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIMIT_BYTES = 10 * 1024 * 1024
EXCLUDED_PARTS = {
    ".git",
    ".venv",
    ".vs",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
}
EXCLUDED_NAMES = {".env", ".DS_Store"}


def included_files() -> list[Path]:
    files: list[Path] = []
    for candidate in ROOT.rglob("*"):
        relative = candidate.relative_to(ROOT)
        if not candidate.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if candidate.name in EXCLUDED_NAMES or candidate.suffix.lower() == ".zip":
            continue
        if candidate.suffix.lower() in {".bin", ".gguf", ".safetensors"}:
            raise SystemExit(f"Refusing to package possible model weights: {relative}")
        files.append(candidate)
    return sorted(files)


def package(folder_name: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+", folder_name):
        raise SystemExit("Folder name must look like lastname-firstname.")
    destination_dir = ROOT / "dist"
    destination_dir.mkdir(exist_ok=True)
    destination = destination_dir / f"{folder_name}.zip"
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source in included_files():
            relative = source.relative_to(ROOT)
            archive.write(source, (Path(folder_name) / relative).as_posix())
    size = destination.stat().st_size
    if size >= LIMIT_BYTES:
        destination.unlink()
        raise SystemExit(f"Archive was {size / 1024 / 1024:.2f} MB; limit is under 10 MB.")
    print(f"Created {destination.relative_to(ROOT)} ({size / 1024:.1f} KiB)")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder_name", help="Required top-level zip folder, e.g. lovelace-ada")
    args = parser.parse_args()
    package(args.folder_name)


if __name__ == "__main__":
    main()
