from pydantic import BaseModel


class TrainingEvalEventData(BaseModel):
    model_id: str
