from __future__ import annotations

import asyncio
import io
import subprocess
import sys

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from PIL import Image, UnidentifiedImageError

from backend.app.config import ALLOWED_FORMATS, ENABLE_TRAIN_API, MAX_UPLOAD_BYTES, ROOT
from backend.app.schemas import CompareResponse, ModelInfo, PredictionResponse, TrainRequest
from backend.app.services.model_service import MODEL_FILES, model_status, predict
from backend.app.services.results import comparison, dataset_stats, experiment_results

router = APIRouter(prefix="/api")


async def validated_upload(file: UploadFile) -> bytes:
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    await file.close()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"Image exceeds the {MAX_UPLOAD_BYTES // 1024 // 1024} MB limit.")
    try:
        image = Image.open(io.BytesIO(data))
        image.verify()
        if image.format not in ALLOWED_FORMATS:
            raise HTTPException(415, "Supported formats: PNG, JPG, JPEG, WEBP.")
    except UnidentifiedImageError as exc:
        raise HTTPException(415, "The uploaded file is not a valid image.") from exc
    if not data:
        raise HTTPException(400, "The uploaded file is empty.")
    return data


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "models_available": [k for k, p in MODEL_FILES.items() if p.is_file()]}


@router.get("/models", response_model=list[ModelInfo])
def models() -> list[dict]:
    return [model_status(model_id) for model_id in MODEL_FILES]


@router.post("/predict", response_model=PredictionResponse)
async def predict_image(
    file: UploadFile = File(...),
    model: str = Query(default="improved", pattern="^(baseline|expanded|improved)$"),
) -> dict:
    data = await validated_upload(file)
    try:
        return await asyncio.to_thread(predict, data, model)
    except FileNotFoundError as exc:
        raise HTTPException(503, str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc


@router.post("/compare", response_model=CompareResponse)
async def compare_image(file: UploadFile = File(...)) -> dict:
    data = await validated_upload(file)
    missing = [name for name in ("baseline", "improved") if not MODEL_FILES[name].is_file()]
    if missing:
        raise HTTPException(503, f"Missing checkpoint(s): {', '.join(missing)}.")
    baseline, improved = await asyncio.gather(
        asyncio.to_thread(predict, data, "baseline"),
        asyncio.to_thread(predict, data, "improved"),
    )
    return {"baseline": baseline, "improved": improved}


@router.get("/research/results")
def research_results() -> dict:
    return experiment_results()


@router.get("/research/dataset-stats")
def research_dataset_stats() -> dict:
    return dataset_stats()


@router.get("/research/comparison")
def research_comparison() -> dict:
    return comparison()


@router.post("/research/train", status_code=202)
def train(request: TrainRequest) -> dict:
    if not ENABLE_TRAIN_API:
        raise HTTPException(403, "Training through the API is disabled. Set ENABLE_TRAIN_API=true locally.")
    stage_dir = "original" if request.stage == "original" else request.stage
    result_dir = "baseline" if request.stage == "original" else request.stage
    command = [
        sys.executable, "-m", "ml.training.train",
        "--stage", request.stage,
        "--data", str(ROOT / "data" / stage_dir),
        "--fixed-test", str(ROOT / "data" / "fixed_test"),
        "--output", str(ROOT / "results" / result_dir),
        "--epochs", str(request.epochs),
    ]
    subprocess.Popen(command, cwd=ROOT)  # noqa: S603 - fixed local command with validated inputs
    return {"status": "started", "stage": request.stage, "epochs": request.epochs}

