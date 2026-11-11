"""Explicit, size-aware downloader for user-approved public dataset archives."""
from __future__ import annotations

import argparse
import shutil
import urllib.request
from pathlib import Path


def free_bytes(path: Path) -> int:
    path.mkdir(parents=True, exist_ok=True)
    return shutil.disk_usage(path).free


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a user-selected licensed dataset archive.")
    parser.add_argument("--url", required=True, help="Official direct download URL")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-bytes", type=int, required=True, help="Expected archive size from the source")
    parser.add_argument("--accept-license", action="store_true")
    args = parser.parse_args()
    if not args.accept_license:
        raise SystemExit("Review the source license, then rerun with --accept-license.")
    available = free_bytes(args.output.parent)
    required = args.expected_bytes * 2  # archive plus extracted data safety margin
    if available < required:
        raise SystemExit(f"Insufficient space: need about {required:,} bytes, have {available:,}.")
    request = urllib.request.Request(args.url, headers={"User-Agent": "Deepfake-Radar/0.1"})
    with urllib.request.urlopen(request) as response, args.output.open("wb") as target:
        shutil.copyfileobj(response, target)
    if args.output.stat().st_size < args.expected_bytes * 0.8:
        args.output.unlink(missing_ok=True)
        raise SystemExit("Downloaded file is much smaller than expected; removed possible error page.")
    print(f"Saved {args.output} ({args.output.stat().st_size:,} bytes)")

