# Deepfake Radar

**See beyond what looks real.**

Deepfake Radar is a full-stack Computer Vision research project for Assignment #2 (Option B: improve the dataset and compare results). It compares one unchanged EfficientNet-B0 classifier across three dataset stages: original, expanded, and improved. A separate fixed test set and an out-of-distribution (OOD) set measure generalization.

The application is intentionally honest: it never returns a synthetic prediction or invented metric. When checkpoints or result files are absent, the API and UI explain what must be run.

## Research question

Does enriching an image dataset with diverse AI-generated sources, compression variations, and realistic image conditions improve a detector's generalization to unseen sources and conditions?

## Experimental controls

- Same EfficientNet-B0 architecture, optimizer, seed, image size, training loop, and evaluation protocol in all stages.
- Dataset stage is the primary experimental variable.
- `data/fixed_test` and `data/ood` are never used for training or validation.
- Group-aware manifests keep an original image and all derived variants in one split.
- Metrics are written only after inference on actual files.

## Structure

```text
frontend/              React + TypeScript + Vite + Tailwind + Recharts
backend/               FastAPI inference and research API
ml/                    dataset, training, and evaluation pipeline
data/                  local datasets (ignored by Git)
models/checkpoints/    trained weights (ignored by Git)
results/               real configs, metrics, plots, and reports
docs/                  methodology, dataset notes, and presentation material
```

## Quick start (Windows PowerShell)

Use Python 3.11 or 3.12 for the pinned PyTorch environment. Python 3.14 is not supported by the pinned PyTorch build in this project.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
cd frontend
npm install
npm run build
cd ..
uvicorn backend.app.main:app --reload --port 8000
```

In a second terminal:

```powershell
cd frontend
npm run dev
```

Open `http://localhost:5173`. The Vite server proxies `/api` to FastAPI.

## Quick start (macOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
(cd frontend && npm install && npm run build)
uvicorn backend.app.main:app --reload --port 8000
```

In a second terminal: `cd frontend && npm run dev`.

## Dataset setup

Do not download a large dataset until you have checked its license and free disk space. CIFAKE is a practical starting point, but it must be obtained from its official/current source under its terms. Place class folders under a source directory:

```text
incoming/original/real/
incoming/original/ai_generated/
incoming/extra_real/real/
incoming/extra_ai/ai_generated/
incoming/ood/real/
incoming/ood/ai_generated/
```

Index and split the original source:

```powershell
python -m ml.datasets.prepare --source incoming\original --output data\original --stage original --seed 42
```

Build the fixed test set once, then keep it unchanged for all experiments:

```powershell
python -m ml.datasets.prepare --source incoming\original --output data\fixed_test --stage fixed_test --test-only --seed 42
python -m ml.datasets.prepare --source incoming\ood --output data\ood --stage ood --test-only --seed 42
```

For the expanded and improved stages, merge licensed sources using a CSV provenance manifest. See `docs/dataset_documentation.md`. Derived JPEG/lighting variants are created only in train folders and retain their `group_id`.

```powershell
python -m ml.datasets.prepare --source incoming\expanded --output data\expanded --stage expanded --seed 42
python -m ml.datasets.prepare --source incoming\improved --output data\improved --stage improved --seed 42 --quality-control --train-variants
python -m ml.datasets.report --root data\improved --output results\improved\dataset_report.json
```

## Train and evaluate

If another teammate will run training, send them [`docs/TRAINING_HANDOFF.md`](docs/TRAINING_HANDOFF.md). It contains the full environment, dataset, training, OOD, and artifact-return checklist.

The same configuration should be used for every stage:

```powershell
python -m ml.training.train --stage original --data data\original --fixed-test data\fixed_test --output results\baseline
python -m ml.training.train --stage expanded --data data\expanded --fixed-test data\fixed_test --output results\expanded
python -m ml.training.train --stage improved --data data\improved --fixed-test data\fixed_test --output results\improved
```

Evaluate each checkpoint on the independent OOD set:

```powershell
python -m ml.evaluation.evaluate --checkpoint models\checkpoints\original.pt --data data\ood --output results\baseline\ood_metrics.json
python -m ml.evaluation.evaluate --checkpoint models\checkpoints\expanded.pt --data data\ood --output results\expanded\ood_metrics.json
python -m ml.evaluation.evaluate --checkpoint models\checkpoints\improved.pt --data data\ood --output results\improved\ood_metrics.json
python -m ml.evaluation.compare --results results --output results\comparison
```

GPU training was not executed while generating this repository. Until you provide datasets and train, the dashboard correctly shows empty states and prediction endpoints return HTTP 503.

## API

- `GET /api/health` - service and checkpoint status
- `GET /api/models` - available model metadata
- `POST /api/predict?model=improved` - inference on one PNG/JPEG/WEBP image
- `POST /api/compare` - baseline/improved inference on the same image
- `GET /api/research/results` - saved real experiment files
- `GET /api/research/dataset-stats` - dataset reports
- `GET /api/research/comparison` - comparison artifact
- `POST /api/research/train` - local opt-in subprocess training (disabled unless `ENABLE_TRAIN_API=true`)

Interactive API docs: `http://localhost:8000/docs`.

## Testing

```powershell
python -m pytest
cd frontend
npm run typecheck
npm run build
```

## Limitations and responsible use

This is an image classifier, not a forensic proof system. Results depend on training sources, preprocessing, post-processing, and distribution shift. A high confidence score does not establish authenticity, authorship, or malicious intent. Do not use predictions alone for moderation, legal, employment, or disciplinary decisions.

