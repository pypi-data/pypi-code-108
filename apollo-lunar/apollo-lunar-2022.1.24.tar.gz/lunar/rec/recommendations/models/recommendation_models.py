from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator


class RecommendationIn(BaseModel):
    id: str = Field(..., title="Unique identifier of a recommendation target")
    channel_id: str = Field(..., title="Unique identifier of a channel")
    params: Optional[Dict[str, Any]] = Field(dict(), title="Additional parameters for recommendation")


class RecommendationOut(BaseModel):
    items: List[Dict[str, Any]] = Field(
        ..., title="Recommended items for the target", description="Each item map(dict) in this must have `id` field."
    )

    @validator("items")
    def check_ids(cls, items):
        for item in items:
            if "id" not in item:
                raise ValueError("'id' is a required field in an item")
        return items
