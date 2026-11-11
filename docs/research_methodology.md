# Research methodology

## Objective

Test whether dataset diversity and quality improve generalization in binary real-versus-AI image classification.

## Independent variable

The training dataset stage:

1. **Original** - one documented public baseline dataset.
2. **Expanded** - additional licensed real and AI-generated source families.
3. **Improved** - the expanded data after provenance completion, exact-duplicate removal, class balancing, source balancing, low-quality image filtering, resolution diversity, and train-only condition variations.

## Controlled variables

- EfficientNet-B0 with a two-class head.
- Image size 224 x 224.
- ImageNet normalization.
- AdamW, learning rate 0.0003, weight decay 0.0001.
- Seed 42, same epoch count and batch size.
- Best validation-loss checkpoint.
- Fixed decision threshold 0.5.
- Same independent test and OOD sets.

Record deviations before training. If a stage requires a smaller batch because of hardware, rerun every stage with that batch size.

## Leakage prevention

- Give every original image family a stable `group_id`.
- Put original, resized, compressed, relit, and other related versions in the same split.
- Create condition variants only after splitting and only inside training.
- Compute exact hashes before splitting and after preparation.
- Keep the fixed test and OOD roots read-only during training.
- Never tune hyperparameters against OOD results.

## Evaluation

Report accuracy, precision, recall, F1, ROC-AUC, confusion matrix, training time, mean inference time, sample count, and source-wise results when provenance permits. Compare both the fixed in-distribution test set and the unseen-source OOD set.

## Interpretation protocol

Do not claim that dataset improvement caused a gain until all experiment configs match and source leakage checks pass. Inspect class-wise errors, per-source performance, confidence distributions, and failures. A lower in-distribution score with a higher OOD score may still support improved generalization, but it does not prove universal robustness.

