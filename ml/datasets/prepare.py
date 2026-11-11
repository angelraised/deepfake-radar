from __future__ import annotations

import argparse
import csv
import hashlib
import io
import random
import shutil
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageEnhance, UnidentifiedImageError

from ml.common import CLASSES, save_json

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def validate(path: Path) -> tuple[bool, dict]:
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
            if width < 32 or height < 32:
                return False, {"reason": "too_small"}
            return True, {"width": width, "height": height, "format": image.format}
    except (UnidentifiedImageError, OSError, ValueError):
        return False, {"reason": "invalid_image"}


def source_manifest(source: Path) -> dict[str, dict[str, str]]:
    manifest = source / "provenance.csv"
    if not manifest.is_file():
        return {}
    with manifest.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = csv.DictReader(stream)
        return {row["relative_path"].replace("\\", "/"): row for row in rows}


def collect(source: Path) -> tuple[list[dict], list[dict]]:
    provenance = source_manifest(source)
    valid, rejected = [], []
    hashes: dict[str, str] = {}
    for label in CLASSES:
        folder = source / label
        if not folder.is_dir():
            continue
        for path in sorted(p for p in folder.rglob("*") if p.suffix.lower() in EXTENSIONS):
            ok, metadata = validate(path)
            relative = path.relative_to(source).as_posix()
            if not ok:
                rejected.append({"path": relative, **metadata})
                continue
            file_hash = digest(path)
            duplicate_of = hashes.get(file_hash)
            if duplicate_of:
                rejected.append({"path": relative, "reason": "exact_duplicate", "duplicate_of": duplicate_of})
                continue
            hashes[file_hash] = relative
            row = provenance.get(relative, {})
            # group_id must identify the underlying image family. It prevents derived variants leaking.
            group_id = row.get("group_id") or file_hash
            valid.append({
                "path": path,
                "relative_path": relative,
                "label": label,
                "sha256": file_hash,
                "group_id": group_id,
                "source": row.get("source", "unrecorded"),
                "license": row.get("license", "unrecorded"),
                **metadata,
            })
    return valid, rejected


def group_split(records: list[dict], seed: int, test_only: bool) -> dict[str, list[dict]]:
    if test_only:
        return {"test": records}
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for record in records:
        groups[(record["label"], record["group_id"])].append(record)
    rng = random.Random(seed)
    output = {"train": [], "val": [], "test": []}
    by_label: dict[str, list[list[dict]]] = defaultdict(list)
    for (label, _), group in groups.items():
        by_label[label].append(group)
    for label_groups in by_label.values():
        rng.shuffle(label_groups)
        total = len(label_groups)
        n_test = max(1, round(total * 0.15)) if total >= 3 else 0
        n_val = max(1, round(total * 0.15)) if total >= 3 else 0
        for index, group in enumerate(label_groups):
            split = "test" if index < n_test else "val" if index < n_test + n_val else "train"
            output[split].extend(group)
    return output


def jpeg_variant(source: Path, target: Path, quality: int, brightness: float) -> None:
    with Image.open(source) as image:
        rgb = image.convert("RGB")
        adjusted = ImageEnhance.Brightness(rgb).enhance(brightness)
        target.parent.mkdir(parents=True, exist_ok=True)
        adjusted.save(target, "JPEG", quality=quality, optimize=True)


def prepare(args: argparse.Namespace) -> dict:
    records, rejected = collect(args.source)
    if not records:
        raise SystemExit(f"No valid class images found under {args.source}")
    splits = group_split(records, args.seed, args.test_only)
    manifest_rows = []
    for split, split_records in splits.items():
        for index, record in enumerate(split_records):
            suffix = record["path"].suffix.lower()
            destination = args.output / split / record["label"] / f"{index:07d}_{record['sha256'][:10]}{suffix}"
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(record["path"], destination)
            manifest_rows.append({k: str(v) for k, v in record.items() if k != "path"} | {"split": split, "prepared_path": destination.relative_to(args.output).as_posix()})
            if args.train_variants and split == "train":
                for quality, brightness in ((55, 0.85), (82, 1.15)):
                    variant = destination.with_name(f"{destination.stem}_q{quality}_b{int(brightness*100)}.jpg")
                    jpeg_variant(record["path"], variant, quality, brightness)
                    manifest_rows.append({k: str(v) for k, v in record.items() if k != "path"} | {"split": split, "prepared_path": variant.relative_to(args.output).as_posix(), "derived": "true"})
    args.output.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in manifest_rows for key in row})
    with (args.output / "manifest.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader(); writer.writerows(manifest_rows)
    report = {"stage": args.stage, "seed": args.seed, "valid_source_images": len(records), "rejected": rejected, "split_counts": {k: len(v) for k, v in splits.items()}, "train_variants": args.train_variants, "quality_control": args.quality_control}
    save_json(report, args.output / "preparation_report.json")
    return report


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Validate, deduplicate, group-split, and prepare a dataset.")
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--stage", required=True)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--test-only", action="store_true")
    p.add_argument("--quality-control", action="store_true")
    p.add_argument("--train-variants", action="store_true")
    return p


if __name__ == "__main__":
    print(prepare(parser().parse_args()))

