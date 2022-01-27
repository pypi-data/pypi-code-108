from pydantic import BaseModel, Field

from rosetta_dispatcher.model.dispatch_types import DispatchRequestType


class DispatchRequestModel(BaseModel):
    content_type: DispatchRequestType = Field(DispatchRequestType.JSON)
    reply_to: str = Field(None)
    correlation_id: str = Field(None)
    timeout: int = Field(None)
    data: str = Field(None)