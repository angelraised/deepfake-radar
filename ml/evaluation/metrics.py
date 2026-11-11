from __future__ import annotations

import time

import numpy as np
import torch
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score, roc_curve

from ml.training.data import labels_to_real_ai


def evaluate_loader(model, data_loader, device) -> dict:
    model.eval(); labels_all, probs_all = [], []; started = time.perf_counter(); count = 0
    with torch.inference_mode():
        for images, labels in data_loader:
            images = images.to(device); labels = labels_to_real_ai(labels).to(device)
            probabilities = torch.softmax(model(images), dim=1)[:, 1]
            labels_all.extend(labels.cpu().numpy().tolist()); probs_all.extend(probabilities.cpu().numpy().tolist()); count += len(images)
    elapsed = time.perf_counter() - started
    y_true = np.asarray(labels_all); y_prob = np.asarray(probs_all); y_pred = (y_prob >= 0.5).astype(int)
    if len(np.unique(y_true)) > 1:
        auc = float(roc_auc_score(y_true, y_prob)); fpr, tpr, _ = roc_curve(y_true, y_prob); curve = {"fpr": fpr.tolist(), "tpr": tpr.tolist()}
    else:
        auc, curve = None, None
    return {"accuracy": float(accuracy_score(y_true, y_pred)), "precision": float(precision_score(y_true, y_pred, zero_division=0)), "recall": float(recall_score(y_true, y_pred, zero_division=0)), "f1": float(f1_score(y_true, y_pred, zero_division=0)), "roc_auc": auc, "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist(), "roc_curve": curve, "inference_time_ms": elapsed * 1000 / max(count, 1), "sample_count": count}

