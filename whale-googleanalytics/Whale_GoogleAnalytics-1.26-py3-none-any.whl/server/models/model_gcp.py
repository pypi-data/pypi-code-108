from typing import List, Optional
from pydantic import BaseModel


class DataModel(BaseModel):
    id: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    metrics_list: list = []
    dimensions_list: list = []
    chartTitle: Optional[str] = None
    secondary_metrics: Optional[str] = None
    chart: bool
    to_csv: bool

    class Config:
        schema_extra = {
            "example": {
                "id": "13406065",
                "start_date": "2021-10-01",
                "end_date": "2021-10-31",
                "metrics_list": {"ga:users", "ga:sessions"},
                "dimensions_list": {"ga:deviceCategory"},
                "secondary_metrics": "ga:bounceRate",
                "chart": True,
                "to_csv": True,
            }
        }


class MCFModel(BaseModel):
    ids: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    metrics: list = []
    dimensions: str
    chart: bool
    to_csv: bool

    class Config:
        schema_extra = {
            "example": {
                "ids": "13406065",
                "start_date": "2021-10-01",
                "end_date": "2021-10-31",
                "metrics": {
                    "mcf:firstInteractionConversions",
                    "mcf:lastInteractionConversions",
                },
                "dimensions": "mcf:medium",
                "chart": True,
                "to_csv": True,
            }
        }


class TestingModel(BaseModel):
    id: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "id": "13406065",
            }
        }


def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}
