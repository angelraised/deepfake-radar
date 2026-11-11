import json
from pathlib import Path
from typing import Any

from backend.app.config import RESULTS_DIR


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def experiment_results() -> dict[str, Any]:
    output: dict[str, Any] = {}
    for stage in ("baseline", "expanded", "improved"):
        metrics = read_json(RESULTS_DIR / stage / "metrics.json")
        ood = read_json(RESULTS_DIR / stage / "ood_metrics.json")
        output[stage] = {
            "status": "evaluated" if metrics else "not_evaluated",
            "metrics": metrics,
            "ood_metrics": ood,
        }
    return output


def dataset_stats() -> dict[str, Any]:
    return {
        stage: read_json(RESULTS_DIR / stage / "dataset_report.json")
        for stage in ("baseline", "expanded", "improved")
    }


def comparison() -> dict[str, Any]:
    saved = read_json(RESULTS_DIR / "comparison" / "comparison.json")
    return saved or {
        "status": "not_evaluated",
        "message": "Run all experiments and the comparison script to populate this view.",
        "experiments": experiment_results(),
    }

