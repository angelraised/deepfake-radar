from ml.datasets.prepare import group_split


def test_group_ids_never_cross_splits() -> None:
    records = [{"label": label, "group_id": f"{label}-{group}", "variant": variant} for label in ("real", "ai_generated") for group in range(10) for variant in range(2)]
    splits = group_split(records, seed=42, test_only=False)
    locations = {}
    for split, split_records in splits.items():
        for record in split_records:
            locations.setdefault(record["group_id"], set()).add(split)
    assert all(len(value) == 1 for value in locations.values())

