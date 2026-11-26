"""Deliver the finished 26 November 2026 front page to the grader.

The newspaper image is built ahead of time and shipped in this
repository as entry.png. This program only moves a byte-for-byte copy
of it into the directory the grader reads, then proves the copy
landed whole. Nothing is drawn or downloaded here.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

PICTURE = "entry.png"
EXPECTED_BYTES = 273493
EXPECTED_HASH = "6f02c97f366745a344337b839c40c08047e9dc7436739a966551c9b5ea8a28cf"


def destination_folder() -> Path:
    """Where the grader expects the finished image."""
    return Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def digest_of(path: Path) -> str:
    """SHA-256 of a file, read in chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    here = Path(__file__).resolve().parent
    source = here / PICTURE
    if not source.is_file():
        print(f"error: missing source image: {source}", file=sys.stderr)
        raise SystemExit(1)

    folder = destination_folder()
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / PICTURE

    shutil.copyfile(source, target)

    got = target.stat().st_size
    if got != EXPECTED_BYTES:
        print(
            f"error: copied image is {got} bytes, expected {EXPECTED_BYTES}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    if digest_of(target) != EXPECTED_HASH:
        print(
            "error: copied image hash does not match the source",
            file=sys.stderr,
        )
        raise SystemExit(1)

    print(f"wrote {target} ({EXPECTED_BYTES} bytes)")


if __name__ == "__main__":
    main()
