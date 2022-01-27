from pydantic import BaseModel, Field

from rosetta_dispatcher.model.dispatch_types import DispatchRequestType, DispatchResponseStatus


class DispatchResponseModel(BaseModel):
    correlation_id: str = Field(None)
    status: DispatchResponseStatus = Field(DispatchResponseStatus.OK)
    data: str = Field(None)