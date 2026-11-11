# Deepfake Radar experiment

## Research question

Does training on CIFAKE plus a more diverse collection improve detection on a generator held out from both training sets?

## Data

| Role | Original | Enriched |
| --- | --- | --- |
| Training | 69,092 CIFAKE images | Same CIFAKE images plus 8,000 Tiny-GenImage images |
| Validation | 14,805 CIFAKE images | Identical membership |
| Fixed test | 19,962 CIFAKE images | Identical membership |
| Held-out test | 500 real and 500 Midjourney images | Identical membership |

The additions consist of 4,000 real images and 1,000 from each of ADM, BigGAN, GLIDE and Wukong. The holdout uses the published Tiny-GenImage validation split. The additions use the published training split. The selected revision is `89c4fe9efd0ebc7ce5c7641ef57d578ccd639c69`. The public dataset card labels Tiny-GenImage CC BY-NC-SA 4.0. The published manifests record provenance for the sampled images.

CIFAKE uses real CIFAR-10 photos and Stable Diffusion 1.4 images. The official test split was prepared first. The baseline preparation excluded 378 exact test matches from the training source. The added examples and holdout were checked against exact raw and standardized byte hashes.

Sources: [CIFAKE](https://github.com/jordan-bird/CIFAKE-Real-and-AI-Generated-Synthetic-Images), [Tiny-GenImage](https://huggingface.co/datasets/TheKernel01/Tiny-GenImage), [GenImage benchmark](https://github.com/GenImage-Dataset/GenImage).

## Training controls

Both runs use ImageNet-initialized EfficientNet-B0 with a two-class head, 224 × 224 input, AdamW, learning rate 0.0003, weight decay 0.0001, five epochs, batch size 64 and seed 42. Checkpoint selection uses the lowest CIFAKE validation loss. The inference threshold for the AI class is 0.5.

## Measured results

| Test | Images | Original accuracy | Enriched accuracy | Original F1 | Enriched F1 | Original AUROC | Enriched AUROC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CIFAKE | 19,962 | 98.16% | 98.07% | 98.16% | 98.08% | 0.998 | 0.998 |
| Midjourney holdout | 1,000 | 51.70% | 65.30% | 63.33% | 62.41% | 0.478 | 0.717 |

Accuracy changed by **-0.10 percentage points on CIFAKE** and **+13.60 percentage points on the Midjourney holdout**. The number of real holdout photos classified as AI changed from **400 to 135 out of 500**. F1 uses AI-generated as the positive class.

Across the same 1,000 holdout images, the enriched model corrected 331 baseline errors and introduced 195 new errors. The 95% paired bootstrap interval for the accuracy change is +9.90 to +17.30 percentage points. The interval reflects image sampling on this holdout and leaves training-seed variability outside its scope.

The selected example has the recorded label **real** and source **Real**. The Analyzer gave AI scores above **99.99%** and below **0.01%**. The paired CSV contains the scores for the full holdout.

## Limits

One seed and one held-out generator. Both arms used the same epoch count, so the enriched arm received more optimizer steps. Exact hashes leave perceptual duplicates outside the audit. This experiment combines an increase in data volume with a change in source mix. The reported scores apply to the stated test samples and preprocessing.

## Local inference

Follow the setup instructions in the README and place the trained checkpoints at `models/checkpoints/original.pt` and `models/checkpoints/improved.pt`. In Analyzer, select Compare and use a local image you have permission to use. Open Research to view the held-out results. The saved API verification response is in `results/assignment2/api_verification.json`.
