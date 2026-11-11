import torch
from torchvision.models import EfficientNet_B0_Weights, efficientnet_b0


def build_model(pretrained: bool = True) -> torch.nn.Module:
    weights = EfficientNet_B0_Weights.DEFAULT if pretrained else None
    model = efficientnet_b0(weights=weights)
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, 2)
    return model

