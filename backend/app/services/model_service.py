from __future__ import annotations

import io
import time
from functools import lru_cache
from pathlib import Path

from PIL import Image

try:
    import torch
    from torchvision.models import efficientnet_b0
    from torchvision.transforms import v2
except (ImportError, OSError):  # Research API remains inspectable before ML dependencies are installed.
    torch = None
    efficientnet_b0 = None
    v2 = None

from backend.app.config import CHECKPOINT_DIR

MODEL_FILES = {
    "baseline": CHECKPOINT_DIR / "original.pt",
    "expanded": CHECKPOINT_DIR / "expanded.pt",
    "improved": CHECKPOINT_DIR / "improved.pt",
}


def _build_model() -> torch.nn.Module:
    if torch is None or efficientnet_b0 is None:
        raise RuntimeError("PyTorch and torchvision are not installed in this Python environment.")
    model = efficientnet_b0(weights=None)
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, 2)
    return model


@lru_cache(maxsize=3)
def load_model(model_id: str, modified_ns: int) -> tuple[torch.nn.Module, dict]:
    del modified_ns
    path = MODEL_FILES[model_id]
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    model = _build_model()
    state = checkpoint.get("model_state_dict", checkpoint)
    model.load_state_dict(state)
    model.eval()
    metadata = checkpoint.get("metadata", {}) if isinstance(checkpoint, dict) else {}
    return model, metadata


def model_status(model_id: str) -> dict:
    path = MODEL_FILES[model_id]
    return {
        "id": model_id,
        "name": f"EfficientNet-B0 {model_id.title()}",
        "version": "trained" if path.is_file() else "not-trained",
        "architecture": "efficientnet_b0",
        "available": path.is_file() and torch is not None,
        "checkpoint": str(path) if path.is_file() else None,
    }


def predict(image_bytes: bytes, model_id: str) -> dict:
    if torch is None or v2 is None:
        raise RuntimeError("PyTorch and torchvision are required for inference.")
    path = MODEL_FILES[model_id]
    if not path.is_file():
        raise FileNotFoundError(f"Checkpoint for '{model_id}' has not been trained yet.")
    model, metadata = load_model(model_id, path.stat().st_mtime_ns)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    transform = v2.Compose([
        v2.Resize((224, 224)),
        v2.ToImage(),
        v2.ToDtype(torch.float32, scale=True),
        v2.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ])
    tensor = transform(image).unsqueeze(0)
    started = time.perf_counter()
    with torch.inference_mode():
        probabilities = torch.softmax(model(tensor), dim=1)[0]
    elapsed = (time.perf_counter() - started) * 1000
    real, ai = (float(probabilities[0]), float(probabilities[1]))
    prediction = "AI_GENERATED" if ai >= real else "REAL"
    return {
        "prediction": prediction,
        "confidence": max(real, ai),
        "probabilities": {"real": real, "ai_generated": ai},
        "model": f"efficientnet_b0_{model_id}",
        "version": str(metadata.get("version", "trained")),
        "inference_time_ms": elapsed,
    }

