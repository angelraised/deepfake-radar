import argparse
import csv
import json
from pathlib import Path

from ml.common import save_json


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--results", type=Path, required=True); p.add_argument("--output", type=Path, required=True); args = p.parse_args()
    experiments = {}; rows = []
    for stage in ("baseline", "expanded", "improved"):
        metric_path = args.results / stage / "metrics.json"; ood_path = args.results / stage / "ood_metrics.json"
        if not metric_path.is_file(): continue
        metrics = json.loads(metric_path.read_text(encoding="utf-8")); ood = json.loads(ood_path.read_text(encoding="utf-8")) if ood_path.is_file() else None
        experiments[stage] = {"metrics": metrics, "ood_metrics": ood}; rows.append({"stage": stage, **{k: metrics.get(k) for k in ("accuracy", "precision", "recall", "f1", "roc_auc")}, "ood_f1": ood.get("f1") if ood else None})
    comparison = {"status": "evaluated" if len(experiments) == 3 else "partial", "experiments": experiments, "note": "Dataset stage is the primary experimental variable; inspect configs before attributing differences."}
    args.output.mkdir(parents=True, exist_ok=True); save_json(comparison, args.output / "comparison.json")
    with (args.output / "comparison.csv").open("w", newline="", encoding="utf-8") as stream:
        if rows: writer = csv.DictWriter(stream, fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
    print(comparison["status"])

