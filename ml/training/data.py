from pathlib import Path

from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import v2

MEAN = (0.485, 0.456, 0.406)
STD = (0.229, 0.224, 0.225)


def transforms(training: bool):
    operations = [v2.ToImage()]
    if training:
        operations += [v2.RandomResizedCrop((224, 224), scale=(0.8, 1.0)), v2.RandomHorizontalFlip(), v2.ColorJitter(brightness=0.15, contrast=0.15)]
    else:
        operations += [v2.Resize((224, 224))]
    operations += [v2.ToDtype(__import__("torch").float32, scale=True), v2.Normalize(MEAN, STD)]
    return v2.Compose(operations)


def loader(root: Path, split: str | None, batch_size: int, workers: int, shuffle: bool):
    folder = root / split if split and (root / split).is_dir() else root
    dataset = datasets.ImageFolder(folder, transform=transforms(shuffle))
    if dataset.classes != ["ai_generated", "real"]:
        # ImageFolder sorts alphabetically. Remapping is explicit in training/evaluation.
        pass
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=workers, pin_memory=True), dataset


def labels_to_real_ai(labels):
    # ImageFolder: ai_generated=0, real=1. Model contract: real=0, ai_generated=1.
    return 1 - labels

