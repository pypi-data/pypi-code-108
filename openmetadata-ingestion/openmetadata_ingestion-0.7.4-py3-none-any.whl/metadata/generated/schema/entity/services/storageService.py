# generated by datamodel-codegen:
#   filename:  schema/entity/services/storageService.json
#   timestamp: 2022-01-19T12:42:55+00:00

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Extra, Field, constr

from ...type import basic, entityHistory, storage


class StorageService(BaseModel):
    class Config:
        extra = Extra.forbid

    id: basic.Uuid = Field(
        ..., description='Unique identifier of this storage service instance.'
    )
    name: constr(min_length=1, max_length=128) = Field(
        ..., description='Name that identifies this storage service.'
    )
    displayName: Optional[str] = Field(
        None, description='Display Name that identifies this storage service.'
    )
    serviceType: storage.StorageServiceType = Field(
        ..., description='Type of storage service such as S3, GCS, HDFS...'
    )
    description: Optional[str] = Field(
        None, description='Description of a storage service instance.'
    )
    version: Optional[entityHistory.EntityVersion] = Field(
        None, description='Metadata version of the entity.'
    )
    updatedAt: Optional[basic.DateTime] = Field(
        None,
        description='Last update time corresponding to the new version of the entity.',
    )
    updatedBy: Optional[str] = Field(None, description='User who made the update.')
    href: basic.Href = Field(
        ..., description='Link to the resource corresponding to this storage service.'
    )
    changeDescription: Optional[entityHistory.ChangeDescription] = Field(
        None, description='Change that lead to this version of the entity.'
    )
