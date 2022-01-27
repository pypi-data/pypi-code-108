"""
API Contracts for DW Operation Sets
"""
from datetime import datetime

from pydantic import BaseModel, Field
from typing import List, Optional, Any

from pyrasgo.schemas import dw_operation as op_contracts
from pyrasgo.schemas import dataset as datasets_contracts


class OperationSetCreate(BaseModel):
    """
    Contract to create an operation set
    """
    operation_type: str = Field(default="udt", alias="operationType")
    operations: Optional[List[op_contracts.OperationCreate]]
    dataset_dependency_ids: Optional[List[int]] = Field(alias="datasetDependencyIds") # Dataset Ids

    class Config:
        allow_population_by_field_name = True


class OperationSetUpdate(BaseModel):
    """
    Contract to update an operation set
    """
    operation_type: str = Field(default="udt", alias="operationType")
    operations: Optional[List[op_contracts.OperationUpdate]]
    dataset_dependency_ids: Optional[List[int]] = Field(alias="datasetDependencyIds") # Dataset Ids

    class Config:
        allow_population_by_field_name = True


class OperationSet(BaseModel):
    """
    Contract to return from get endpoints
    """
    id: int
    operation_type: str = Field(default="udt", alias="operationType")
    operations: Optional[List[op_contracts.Operation]]
    dataset_dependencies: Optional[List[datasets_contracts.Dataset]] = Field(alias="datasetDependencies")
    organization_id: int = Field(alias="organizationId")

    class Config:
        allow_population_by_field_name = True


class OperationSetAsyncEvent(BaseModel):
    """
    Represents a single event that happened while executing an async OperationSetCreate task
    """
    id: int
    create_timestamp: datetime = Field(alias='createTimestamp')
    event_type: str = Field(alias='eventType')
    message: Optional[Any]


class OperationSetAsyncTask(BaseModel):
    """
    Response model for when a caller asks to create a task or polls for that task's status
    """
    id: int = Field()
    request: OperationSetCreate = Field()
    create_author: Optional[int] = Field(alias='createAuthor')
    organization_id: int = Field(alias='organizationId')
    events: List[OperationSetAsyncEvent]


class OperationSetOfflineAsyncEvent(BaseModel):
    """
    Represents a single event that happened while executing an async OperationSetCreate offline task
    """
    id: int
    create_timestamp: datetime = Field(alias='createTimestamp')
    event_type: str = Field(alias='eventType')


class OperationSetOfflineAsyncTask(BaseModel):
    """
    Response model for when a caller asks to create a task or polls for that task's status
    """
    id: int = Field()
    request: Any = Field()
    create_author: Optional[int] = Field(alias='createAuthor')
    organization_id: int = Field(alias='organizationId')
    events: List[OperationSetAsyncEvent]
