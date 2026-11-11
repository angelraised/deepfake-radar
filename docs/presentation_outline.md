# Deepfake Radar - 7 to 10 minute presentation

## 1. Problem and motivation (45 seconds)

- AI-generated images are increasingly convincing.
- Detection is probabilistic and changes as generators and post-processing evolve.
- Our project asks a narrow research question: can better training data improve generalization?

## 2. Research question and hypothesis (45 seconds)

- State the research question exactly.
- Hypothesis: broader, cleaner, source-balanced data should perform better on unseen sources and conditions.
- Emphasize Option B: the model remains the same; the dataset changes.

## 3. Data stages (75 seconds)

- Original: [insert actual source and count].
- Expanded: [insert newly added sources and counts].
- Improved: explain provenance, group-aware splitting, duplicate removal, class/source balance, and train-only condition variants.
- Show the actual dataset report, not estimates.

## 4. Experimental design (60 seconds)

- Same EfficientNet-B0, optimizer, seed, image size, epochs, and threshold.
- Same fixed test set for every experiment.
- Separate OOD set contains sources unseen in training.
- Related image families cannot cross splits.

## 5. Results (90 seconds)

- Show actual accuracy, precision, recall, F1, ROC-AUC, confusion matrices, time, and OOD scores.
- Discuss the most important source-wise failure.
- If experiments are incomplete, say so; never replace missing numbers with example values.

## 6. Live MVP demo (60 seconds)

- Upload one known test image.
- Explain probabilities and compare baseline versus improved.
- Point out the uncertainty disclaimer and missing-checkpoint behavior.

## 7. Limitations and conclusion (45 seconds)

- Dataset artifacts and generator drift.
- A prediction is not forensic proof.
- State whether the actual OOD results support or reject the hypothesis.

## Possible instructor Q&A

**Why did you keep the model identical?**  
To isolate dataset changes as the primary variable. Changing the model at the same time would confound the comparison.

**How did you prevent leakage?**  
We split by image-family `group_id`, then generate variants only in training. The fixed test and OOD sets are separate roots and duplicates are checked by hash.

**Why is OOD evaluation important?**  
A detector can score highly by learning source-specific artifacts. Unseen sources test whether it generalizes beyond those shortcuts.

**Why EfficientNet-B0?**  
It is a practical pretrained architecture with a good accuracy/compute tradeoff, suitable for a reproducible student project and CPU inference.

**Does a 90% confidence mean the image is definitely fake?**  
No. It is the model's probability under its learned distribution and can be miscalibrated under distribution shift.

**What counts as dataset improvement?**  
Source diversity, quality control, provenance, group-aware splitting, balanced composition, and realistic train-only condition variation - not merely duplicating images.

**What would you do next?**  
Add newer held-out generators, calibration analysis, source-wise error analysis, and repeated-seed confidence intervals.

