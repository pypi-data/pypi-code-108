from pydantic import BaseModel, Field
from typing import Optional


class DatasetColumn(BaseModel):
    """
    Contract to return from get by id endpoints
    """
    id: int
    name: str = Field(alias='columnName')
    display_name: Optional[str] = Field(alias='displayName')
    data_type: str = Field(alias='dataType')
    description: Optional[str]
    is_feature: bool = Field(alias='isFeature')
    is_dimension: bool = Field(alias='isDimension')
    dw_column_id: int = Field(alias='dwColumnId')

    class Config:
        allow_population_by_field_name = True


class DatasetColumnCreate(BaseModel):
    """
    Contract to accept in post endpoints
    """
    name: str = Field(alias='columnName')
    display_name: Optional[str] = Field(alias='displayName')
    data_type: str = Field(alias='dataType')
    description: Optional[str]
    is_feature: bool = Field(alias='isFeature')
    is_dimension: bool = Field(alias='isDimension')
    dw_column_id: int = Field(alias='dwColumnId')

    class Config:
        allow_population_by_field_name = True


class DatasetColumnUpdate(BaseModel):
    """
    Contract to accept in put endpoints
    """
    name: Optional[str] = Field(alias='columnName')
    display_name: Optional[str] = Field(alias='displayName')
    data_type: Optional[str] = Field(alias='dataType')
    description: Optional[str]
    is_feature: Optional[bool] = Field(alias='isFeature')
    is_dimension: Optional[bool] = Field(alias='isDimension')
    dw_column_id: Optional[int] = Field(alias='dwColumnId')

    class Config:
        allow_population_by_field_name = True


class DatasetColumnUpdateById(DatasetColumnUpdate):
    """
    Contract to accept in put endpoints

    BMS:
    This is a bit of a dice-roll around our framework.
    The DatasetColumnUpdate contract is used in the PUT /v2/dataset-columns/{dataset_column_id} endpoint.
    Since the id is in the path, we don't need the id as part of the contract.

    This contract is used in the PUT /datasets/{dataset_id} endpoint. That endpoint accepts a DatasetUpdate contract,
    which in turn accepts a list of this contract. This contract is identical to its parent, except that we ask the user
    to provide the ids since we don't have them in the path parameter.

    This is a departure from our normal pattern of using match() to try to find the identity of an object in lieu of a
    user directly telling us.

    If this becomes a pain, we'll rip it out and revert back to using match().
    """
    id: int = Field()

    class Config:
        allow_population_by_field_name = True
