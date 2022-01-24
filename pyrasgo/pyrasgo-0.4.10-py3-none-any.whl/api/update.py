from typing import List, Optional

from .error import APIError
from pyrasgo import schemas
from pyrasgo import primitives


class Update():

    def __init__(self):
        from . import Get
        from .connection import Connection
        from pyrasgo.config import get_session_api_key

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)
        self.get = Get()

    def collection_attributes(self,
                              id: int,
                              attributes: List[dict]):
        """
        Create or update attributes on a Rasgo Collection

        param attributes: dict [{"key": "value"}, {"key": "value"}]
        """
        msg = 'attributes parameter must be passed in as a list of k:v pairs. Example: [{"key": "value"}, {"key": "value"}]'
        if not isinstance(attributes, list):
            raise APIError(msg)
        attr = []
        for kv in attributes:
            if not isinstance(kv, dict):
                raise APIError(msg)
            for k, v in kv.items():
                attr.append(schemas.Attribute(key=k, value=v))
        attr_in = schemas.CollectionAttributeBulkCreate(collectionId = id, attributes=attr)
        return self.api._put(f"/models/{id}/attributes", attr_in.dict(exclude_unset=True), api_version=1).json()

    def data_source(self,
                    id: int,
                    name: Optional[str] = None,
                    domain: Optional[str] = None,
                    source_type: Optional[str] = None,
                    table: Optional[str] = None,
                    database: Optional[str] = None,
                    schema: Optional[str] = None,
                    source_code: Optional[str] = None,
                    table_status: Optional[str] = None,
                    parent_source_id: Optional[int] = None) -> primitives.DataSource:
        data_source = schemas.DataSourceUpdate(id=id,
                                           name=name,
                                           domain=domain,
                                           table=table,
                                           tableDatabase=database,
                                           tableSchema=schema,
                                           sourceCode=source_code,
                                           tableStatus=table_status,
                                           sourceType=source_type,
                                           parentId=parent_source_id)
        response = self.api._patch(f"/data-source/{id}", data_source.dict(exclude_unset=True, exclude_none=True), api_version=1).json()
        return primitives.DataSource(api_object=response)

    def dataframe(self,
                  unique_id: str,
                  name: Optional[str] = None,
                  shared_status: str = None,
                  column_hash: str = None,
                  update_date: str = None) -> schemas.Dataframe:
        if shared_status not in [None, 'private', 'organization', 'public']:
            raise APIError("Valid values for shared_status are ['private', 'organization', 'public']")
        dataframe = schemas.DataframeUpdate(name=name,
                                        uniqueId=unique_id,
                                        sharedStatus=shared_status,
                                        columnHash=column_hash,
                                        updatedDate = update_date)
        response = self.api._patch(f"/dataframes/{unique_id}", dataframe.dict(exclude_unset=True, exclude_none=True), api_version=1).json()
        return schemas.Dataframe(**response)

    def feature(self,
                id: int,
                display_name: Optional[str] = None,
                column_name: Optional[str] = None,
                description: Optional[str] = None,
                status: Optional[str] = None,
                tags: Optional[List[str]] = None,
                git_repo: Optional[str] = None) -> primitives.Feature:
        feature = schemas.FeatureUpdate(id=id,
                                    name=display_name,
                                    code=column_name,
                                    description=description,
                                    orchestrationStatus=status,
                                    tags=tags,
                                    gitRepo=git_repo)
        response = self.api._patch(f"/features/{id}", feature.dict(exclude_unset=True, exclude_none=True), api_version=1).json()
        return primitives.Feature(api_object=response)

    def feature_attributes(self,
                           id: int,
                           attributes: List[dict]):
        """
        Create or update attributes on a feature

        param attributes: dict [{"key": "value"}, {"key": "value"}]
        """
        msg = 'attributes parameter must be passed in as a list of k:v pairs. Example: [{"key": "value"}, {"key": "value"}]'
        if not isinstance(attributes, list):
            raise APIError(msg)
        attr = []
        for kv in attributes:
            if not isinstance(kv, dict):
                raise APIError(msg)
            for k, v in kv.items():
                attr.append(schemas.Attribute(key=k, value=v))
        attr_in = schemas.FeatureAttributeBulkCreate(
            featureId = id,
            attributes=attr
        )
        return self.api._put(f"/features/{id}/attributes", attr_in.dict(exclude_unset=True), api_version=1).json()

    def transform(
            self,
            transform_id: int,
            name: Optional[str] = None,
            source_code: Optional[str] = None,
            type: Optional[str] = None,
            arguments: Optional[List[dict]] = None,
            description: Optional[str] = None,
    ) -> schemas.Transform:
        """
        Updates a transform in Rasgo
        """
        transform_update = schemas.TransformUpdate(
            name=name,
            type=type,
            description=description,
            sourceCode=source_code,
            arguments=arguments
        )
        response = self.api._put(
            f"/transform/{transform_id}",
            transform_update.dict(exclude_unset=True, exclude_none=True),
            api_version=1
        ).json()
        return schemas.Transform(**response)

    def dataset(
            self,
            dataset: primitives.Dataset,
            *,
            name: Optional[str] = None,
            description: Optional[str] = None,
    ) -> primitives.Dataset:
        """
        Update a dataset name and/or description in Rasgo
        """
        # Raise error if trying to update a dataset in offline mode
        if not dataset._api_dataset:
            raise APIError("Can not update dataset. Needs to be saved first with `rasgo.save.dataset()`")

        dataset_update = schemas.DatasetUpdate(
            # Possible Changed Fields
            name=name,
            description=description,
            # Persist other fields in update contract so no fields set to None in update
            status=dataset._api_dataset.status,
            owner_id=dataset._api_dataset.owner_id,
            dw_table_id=dataset._api_dataset.dw_table_id,
        )
        response = self.api._put(
            f"/datasets/{dataset._api_dataset.id}",
            dataset_update.dict(exclude_unset=True, exclude_none=True),
            api_version=2
        ).json()
        dataset_schema = schemas.Dataset(**response)
        return primitives.Dataset(
            api_dataset=dataset_schema
        )
