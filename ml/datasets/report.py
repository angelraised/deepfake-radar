from __future__ import annotations

import argparse
import csv
import hashlib
import statistics
from collections import Counter
from pathlib import Path

from PIL import Image

from ml.common import CLASSES, save_json
from ml.datasets.prepare import EXTENSIONS


def make_report(root: Path) -> dict:
    rows = []
    hashes = Counter()
    provenance = {}
    manifest = root / "manifest.csv"
    if manifest.is_file():
        with manifest.open("r", encoding="utf-8", newline="") as stream:
            provenance = {row.get("prepared_path", ""): row for row in csv.DictReader(stream)}
    for split in ("train", "val", "test"):
        for label in CLASSES:
            folder = root / split / label
            if not folder.is_dir():
                continue
            for path in folder.rglob("*"):
                if path.suffix.lower() not in EXTENSIONS:
                    continue
                with Image.open(path) as image:
                    width, height = image.size
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                hashes[digest] += 1
                relative = path.relative_to(root).as_posix()
                meta = provenance.get(relative, {})
                rows.append({"split": split, "label": label, "width": width, "height": height, "source": meta.get("source", "unrecorded")})
    widths, heights = [r["width"] for r in rows], [r["height"] for r in rows]
    return {
        "total_images": len(rows),
        "class_distribution": dict(Counter(r["label"] for r in rows)),
        "split_distribution": dict(Counter(r["split"] for r in rows)),
        "source_distribution": dict(Counter(r["source"] for r in rows)),
        "dimensions": {"width_min": min(widths, default=0), "width_median": statistics.median(widths) if widths else 0, "width_max": max(widths, default=0), "height_min": min(heights, default=0), "height_median": statistics.median(heights) if heights else 0, "height_max": max(heights, default=0)},
        "exact_duplicate_files": sum(count - 1 for count in hashes.values() if count > 1),
        "unrecorded_provenance": sum(r["source"] == "unrecorded" for r in rows),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = make_report(args.root)
    save_json(report, args.output)
    print(report)

