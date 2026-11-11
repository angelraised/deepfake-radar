# Training handoff - Deepfake Radar

This file is for the teammate who will run the experiments. Do not commit datasets, virtual environments, or model checkpoints to GitHub.

## 1. Clone and create the environment

Use Python 3.11 or 3.12.

```powershell
git clone https://github.com/OWNER/deepfake-radar.git
cd deepfake-radar
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu121
python -m pip install -r backend\requirements.txt
```

For a computer without an NVIDIA GPU, replace `cu121` with `cpu`.

## 2. Download CIFAKE

Use the public CIFAKE dataset by Bird and Lotfi. It contains 60,000 real CIFAR-10 images and 60,000 Stable Diffusion 1.4 images. Download it from the official author's repository/Kaggle link, review its terms, and extract it outside this Git repository.

Expected downloaded structure:

```text
CIFAKE/
  train/
    REAL/
    FAKE/
  test/
    REAL/
    FAKE/
```

Rename or copy the class folders used by our preparation pipeline:

```powershell
New-Item -ItemType Directory -Force incoming\original\real,incoming\original\ai_generated
Copy-Item "D:\datasets\CIFAKE\train\REAL\*" incoming\original\real
Copy-Item "D:\datasets\CIFAKE\train\FAKE\*" incoming\original\ai_generated

New-Item -ItemType Directory -Force incoming\fixed_test\real,incoming\fixed_test\ai_generated
Copy-Item "D:\datasets\CIFAKE\test\REAL\*" incoming\fixed_test\real
Copy-Item "D:\datasets\CIFAKE\test\FAKE\*" incoming\fixed_test\ai_generated
```

`incoming/` is local-only and must not be pushed.

## 3. Prepare the fixed test set first

Never regenerate it between experiments.

```powershell
python -m ml.datasets.prepare --source incoming\fixed_test --output data\fixed_test --stage fixed_test --test-only --seed 42
```

## 4. Prepare the three dataset stages

Baseline/original:

```powershell
python -m ml.datasets.prepare --source incoming\original --output data\original --stage original --seed 42
```

Expanded: add additional licensed source folders under `incoming\expanded\real` and `incoming\expanded\ai_generated`, record them in `provenance.csv`, then run:

```powershell
python -m ml.datasets.prepare --source incoming\expanded --output data\expanded --stage expanded --seed 42
```

Improved: use the same collected sources after duplicate removal, provenance completion, balancing, and quality checks. JPEG and lighting variants are created only for train images:

```powershell
python -m ml.datasets.prepare --source incoming\improved --output data\improved --stage improved --seed 42 --quality-control --train-variants
```

If there is no time to obtain a genuinely new generator source, state this limitation honestly during the presentation. Do not claim that JPEG/brightness variants are new generator diversity.

## 5. Train all stages with exactly the same settings

Recommended first run on a GPU:

```powershell
python -m ml.training.train --stage original --data data\original --fixed-test data\fixed_test --output results\baseline --epochs 5 --batch-size 64
python -m ml.training.train --stage expanded --data data\expanded --fixed-test data\fixed_test --output results\expanded --epochs 5 --batch-size 64
python -m ml.training.train --stage improved --data data\improved --fixed-test data\fixed_test --output results\improved --epochs 5 --batch-size 64
```

If GPU memory is insufficient, use batch size 32 for every stage. Do not change settings for only one stage.

## 6. OOD evaluation

Create `incoming\ood` from real and AI sources not used in training, prepare it with `--test-only`, then run:

```powershell
python -m ml.datasets.prepare --source incoming\ood --output data\ood --stage ood --test-only --seed 42
python -m ml.evaluation.evaluate --checkpoint models\checkpoints\original.pt --data data\ood --output results\baseline\ood_metrics.json
python -m ml.evaluation.evaluate --checkpoint models\checkpoints\expanded.pt --data data\ood --output results\expanded\ood_metrics.json
python -m ml.evaluation.evaluate --checkpoint models\checkpoints\improved.pt --data data\ood --output results\improved\ood_metrics.json
python -m ml.evaluation.compare --results results --output results\comparison
```

## 7. Verify and return the artifacts

Run:

```powershell
python -m pytest
cd frontend
npm install
npm run build
```

Return these files to the project owner:

- `models/checkpoints/original.pt`
- `models/checkpoints/expanded.pt`
- `models/checkpoints/improved.pt`
- `results/baseline/`
- `results/expanded/`
- `results/improved/`
- `results/comparison/`

The checkpoints can be shared through Google Drive or GitHub Releases if they exceed GitHub's normal file-size limit. Metrics/configuration files should be committed to the repository.

## Rules that protect the experiment

- Keep the test and OOD sets out of training and validation.
- Keep related originals and derived variants in one split through `group_id`.
- Use identical architecture and training parameters for all three stages.
- Save terminal logs and hardware information.
- Never type presentation metrics manually; the website reads JSON results.
- Never report a number from an interrupted or failed run.

