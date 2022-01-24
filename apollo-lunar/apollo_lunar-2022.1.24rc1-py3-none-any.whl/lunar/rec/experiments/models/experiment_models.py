from typing import List, Optional

from pydantic import BaseModel, Field, validator


class Bucket(BaseModel):
    name: str = Field(..., title="Name of a bucket")
    ratio: int = Field(..., ge=0, le=100, title="Ratio for bucketing", description="The ratio must be 0 ~ 100.")
    model_name: Optional[str] = Field(None, title="Name of an ML model")
    model_version: Optional[str] = Field(None, title="Version of an ML model")


class ExperimentBase(BaseModel):
    buckets: List[Bucket]
    bucketing_seed: Optional[str] = ""

    class Config:
        fields = {
            "id": {"title": "Unique identifier of an experiment"},
            "buckets": {
                "min_items": 1,
                "title": "Bucket list",
                "description": "Experiment must have at least one bucket.",
            },
            "bucketing_seed": {"title": "Random seed for bucketing"},
        }

    @validator("buckets")
    def check_sum_ratio(cls, buckets):
        if buckets is None:
            return buckets
        sum_ratio = 0
        for bucket in buckets:
            sum_ratio += bucket.ratio
        if sum_ratio != 100:
            raise ValueError("Sum of bucket ratios must be 100")
        return buckets

    @validator("buckets")
    def check_bucket_names(cls, buckets):
        if buckets is None:
            return buckets
        bucket_names = {bucket.name for bucket in buckets}
        if len(bucket_names) != len(buckets):
            raise ValueError("Bucket names are duplicated")
        return buckets


class Experiment(ExperimentBase):
    id: str


class ExperimentPutIn(ExperimentBase):
    pass


class ExperimentPatchIn(ExperimentBase):
    buckets: Optional[List[Bucket]] = None
    bucketing_seed: Optional[str] = None
