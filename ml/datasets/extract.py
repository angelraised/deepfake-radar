from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


def safe_extract(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            target = (destination / member.filename).resolve()
            if root not in target.parents and target != root:
                raise ValueError(f"Unsafe archive path: {member.filename}")
        bundle.extractall(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--archive", type=Path, required=True); parser.add_argument("--output", type=Path, required=True); args = parser.parse_args()
    safe_extract(args.archive, args.output); print(f"Extracted to {args.output}")

