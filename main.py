"""Entry program: place the front-page image at the grader's output path.

The repository ships entry.png, a JPEG of the 26 November 2026
world-news front page. This program copies it to the output location
the grader reads, then checks the copy landed whole.
Standard library only, no network, deterministic.
"""

import hashlib
import os
import shutil
from pathlib import Path

IMAGE_NAME = "entry.png"


def output_path() -> Path:
    base = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return Path(base) / IMAGE_NAME


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    source = Path(__file__).resolve().parent / IMAGE_NAME
    target = output_path()
    if not source.is_file():
        raise SystemExit(f"entry image not found: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    expected = source.stat().st_size
    expected_hash = sha256_of(source)
    shutil.copyfile(source, target)
    # A copy is deterministic by construction; the size and hash checks
    # just prove the whole file landed before the grader reads it.
    if target.stat().st_size != expected:
        raise SystemExit("output image size does not match the source")
    if sha256_of(target) != expected_hash:
        raise SystemExit("output image hash does not match the source")


if __name__ == "__main__":
    main()
