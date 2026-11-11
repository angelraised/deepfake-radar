from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results"
CHECKPOINT_DIR = ROOT / "models" / "checkpoints"
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", 10 * 1024 * 1024))
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
ENABLE_TRAIN_API = os.getenv("ENABLE_TRAIN_API", "false").lower() == "true"

