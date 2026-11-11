import argparse
from pathlib import Path

import torch

from ml.common import save_json
from ml.evaluation.metrics import evaluate_loader
from ml.training.data import loader
from ml.training.model import build_model


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--checkpoint", type=Path, required=True); p.add_argument("--data", type=Path, required=True); p.add_argument("--output", type=Path, required=True); p.add_argument("--batch-size", type=int, default=32); args = p.parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False); model = build_model(pretrained=False).to(device); model.load_state_dict(checkpoint["model_state_dict"]); data_loader, _ = loader(args.data, "test", args.batch_size, 0, False)
    metrics = evaluate_loader(model, data_loader, device); save_json(metrics, args.output); print(metrics)

