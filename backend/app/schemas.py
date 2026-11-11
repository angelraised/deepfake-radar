from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    id: str
    name: str
    version: str = "not-trained"
    architecture: str = "efficientnet_b0"
    available: bool
    checkpoint: str | None = None


class PredictionResponse(BaseModel):
    prediction: str
    confidence: float = Field(ge=0, le=1)
    probabilities: dict[str, float]
    model: str
    version: str
    inference_time_ms: float
    warning: str = (
        "This prediction is probabilistic and is not proof of image authenticity."
    )


class CompareResponse(BaseModel):
    baseline: PredictionResponse
    improved: PredictionResponse


class TrainRequest(BaseModel):
    stage: str = Field(pattern="^(original|expanded|improved)$")
    epochs: int = Field(default=10, ge=1, le=100)

