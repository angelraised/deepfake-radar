from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import torch
from torch import nn

from ml.common import save_json, set_seed
from ml.datasets.report import make_report
from ml.evaluation.metrics import evaluate_loader
from ml.training.data import labels_to_real_ai, loader
from ml.training.model import build_model


def train(args: argparse.Namespace) -> dict:
    set_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_loader, _ = loader(args.data, "train", args.batch_size, args.workers, True)
    val_loader, _ = loader(args.data, "val", args.batch_size, args.workers, False)
    test_loader, _ = loader(args.fixed_test, "test", args.batch_size, args.workers, False)
    model = build_model(pretrained=not args.no_pretrained).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    best_loss = float("inf"); best_state = None; history = []; started = time.perf_counter()
    for epoch in range(args.epochs):
        model.train(); running, seen = 0.0, 0
        for images, labels in train_loader:
            images, labels = images.to(device), labels_to_real_ai(labels).to(device)
            optimizer.zero_grad(set_to_none=True); logits = model(images); loss = criterion(logits, labels); loss.backward(); optimizer.step()
            running += loss.item() * len(images); seen += len(images)
        model.eval(); val_loss, val_seen = 0.0, 0
        with torch.inference_mode():
            for images, labels in val_loader:
                images, labels = images.to(device), labels_to_real_ai(labels).to(device); loss = criterion(model(images), labels)
                val_loss += loss.item() * len(images); val_seen += len(images)
        epoch_row = {"epoch": epoch + 1, "train_loss": running / max(seen, 1), "val_loss": val_loss / max(val_seen, 1)}; history.append(epoch_row); print(epoch_row)
        if epoch_row["val_loss"] < best_loss:
            best_loss = epoch_row["val_loss"]; best_state = {k: value.detach().cpu().clone() for k, value in model.state_dict().items()}
    duration = time.perf_counter() - started
    if best_state is None: raise RuntimeError("Training produced no checkpoint.")
    model.load_state_dict(best_state); metrics = evaluate_loader(model, test_loader, device); metrics["training_time_seconds"] = duration
    args.output.mkdir(parents=True, exist_ok=True)
    checkpoint = Path("models/checkpoints") / f"{args.stage}.pt"; checkpoint.parent.mkdir(parents=True, exist_ok=True)
    config = {"stage": args.stage, "architecture": "efficientnet_b0", "pretrained": not args.no_pretrained, "seed": args.seed, "epochs": args.epochs, "batch_size": args.batch_size, "lr": args.lr, "weight_decay": args.weight_decay, "image_size": 224, "fixed_test": str(args.fixed_test), "device": str(device)}
    torch.save({"model_state_dict": best_state, "metadata": {"version": f"{args.stage}-seed{args.seed}", "config": config}}, checkpoint)
    save_json(config, args.output / "config.json"); save_json(metrics, args.output / "metrics.json"); save_json(make_report(args.data), args.output / "dataset_report.json")
    with (args.output / "history.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=history[0]); writer.writeheader(); writer.writerows(history)
    return metrics


def parser():
    p = argparse.ArgumentParser()
    p.add_argument("--stage", choices=["original", "expanded", "improved"], required=True); p.add_argument("--data", type=Path, required=True); p.add_argument("--fixed-test", type=Path, required=True); p.add_argument("--output", type=Path, required=True)
    p.add_argument("--epochs", type=int, default=10); p.add_argument("--batch-size", type=int, default=32); p.add_argument("--workers", type=int, default=0); p.add_argument("--lr", type=float, default=3e-4); p.add_argument("--weight-decay", type=float, default=1e-4); p.add_argument("--seed", type=int, default=42); p.add_argument("--no-pretrained", action="store_true")
    return p


if __name__ == "__main__": print(train(parser().parse_args()))

