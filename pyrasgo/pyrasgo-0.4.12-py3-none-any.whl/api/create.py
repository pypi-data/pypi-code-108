from typing import Dict, List, Optional, Union

from pyrasgo import primitives, schemas
from requests.exceptions import HTTPError

from .error import APIError


class Create():

    def __init__(self):
        from pyrasgo.config import get_session_api_key
        from .connection import Connection

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)

    def collection(self, name: str,
                   type: Union[str, schemas.ModelType],
                   granularity: Union[str, schemas.Granularity],
                   description: Optional[str] = None,
                   is_shared: Optional[bool] = False) -> primitives.Collection:
        try:
            # If not enum, convert to enum first.
            model_type = type.name
        except AttributeError:
            model_type = schemas.ModelType(type)

        try:
            # If not enum, convert to enum first.
            granularity = granularity.name
        except AttributeError:
            granularity = schemas.Granularity(granularity)

        content = {"name": name,
                   "type": model_type.value,
                   "granularities": [{"name": granularity.value}],
                   "isShared": is_shared
                   }
        if description:
            content["description"] = description
        response = self.api._post("/models", _json=content, api_version=1)
        return primitives.Collection(api_object=response.json())

    def data_source(self, table: str,
                    name: str,
                    source_type: str,
                    database: Optional[str] = None,
                    schema: Optional[str] = None,
                    source_code: Optional[str] = None,
                    domain: Optional[str] = None,
                    parent_source_id: Optional[int] = None) -> primitives.DataSource:
        data_source = schemas.DataSourceCreate(name=name,
                                               table=table,
                                               tableDatabase=database,
                                               tableSchema=schema,
                                               sourceCode=source_code,
                                               domain=domain,
                                               sourceType=source_type,
                                               parentId=parent_source_id)
        response = self.api._post("/data-source", data_source.dict(exclude_unset=True), api_version=1).json()
        return primitives.DataSource(api_object=response)

    def dataframe(self, unique_id: str,
                  name: str = None,
                  shared_status: str = 'organization',
                  column_hash: Optional[str] = None,
                  update_date: str = None) -> schemas.Dataframe:
        shared_status = 'organization' if shared_status not in ['public', 'private'] else shared_status
        dataframe = schemas.DataframeCreate(uniqueId=unique_id,
                                            name=name,
                                            sharedStatus=shared_status,
                                            columnHash=column_hash,
                                            updatedDate=update_date)
        try:
            response = self.api._post("/dataframes", dataframe.dict(exclude_unset=True), api_version=1).json()
        except HTTPError as e:
            error_message = f"Failed to create dataframe {unique_id}."
            if e.response.status_code == 409:
                error_message += f" This id is already in use in your organization. Dataframe IDs must be unique."
            raise APIError(error_message)
        return schemas.Dataframe(**response)

    def data_source_stats(self, data_source_id: int):
        """
        Sends an api request to build stats for a specified data source.
        """
        return self.api._post(f"/data-source/profile/{data_source_id}", api_version=1).json()

    def data_source_feature_stats(self, data_source_id: int):
        """
        Sends an api request to build stats for all features in a specified data source.
        """
        return self.api._post(f"/data-source/{data_source_id}/features/stats", api_version=1).json()

    def feature(self,
                data_source_id: int,
                display_name: str,
                column_name: str,
                description: str,
                # data_source_column_id: int,
                status: str,
                git_repo: str,
                tags: Optional[List[str]] = None) -> primitives.Feature:
        feature = schemas.FeatureCreate(name=display_name,
                                        code=column_name,
                                        description=description,
                                        dataSourceId=data_source_id,
                                        orchestrationStatus=status,
                                        tags=tags or [],
                                        gitRepo=git_repo)
        try:
            response = self.api._post("/features/", feature.dict(exclude_unset=True), api_version=1).json()
        except HTTPError as e:
            error_message = f"Failed to create Feature {display_name}."
            if e.response.status_code == 409:
                error_message += f" {column_name} already has a feature associated with it. Try running update feature instead."
            raise APIError(error_message)
        return primitives.Feature(api_object=response)

    def feature_stats(self, feature_id: int) -> Dict:
        """
        Sends an api request to build feature stats for a specified feature.
        """
        return self.api._post(f"/features/{feature_id}/stats", api_version=1).json()

    def feature_importance_stats(self, id: int, payload: schemas.FeatureImportanceStats) -> Dict:
        """
        Sends an api requrest to build feature importance stats for the specified model
        """
        return self.api._post(f"/models/{id}/stats/feature-importance", payload.dict(), api_version=1).json()

    def column_importance_stats(self, id: str, payload: schemas.FeatureImportanceStats) -> Dict:
        """
        Sends a json payload of importance from a dataFrame to the API so it can render in the WebApp
        """
        return self.api._post(f"/dataframes/{id}/feature-importance", payload.dict(), api_version=1).json()

    def dataframe_profile(self, id: str, payload: schemas.ColumnProfiles) -> Dict:
        """
        Send a json payload of a dataframe profile so it can render in the WebApp
        """
        return self.api._post(f"/dataframes/{id}/profile", payload.dict(), api_version=1).json()

    def transform(
        self,
        *,
        name: str,
        source_code: str,
        type: Optional[str] = None,
        arguments: Optional[List[dict]] = None,
        description: Optional[str] = None
    ) -> schemas.Transform:
        """
        Create and return a new Transform in Rasgo
        Args:
            name: Name of the Transform
            source_code: Source code of transform
            type: Type of transform it is. Used for categorization only
            arguments: A list of arguments to supply to the transform
                       so it can render them in the UI. Each argument
                       must be a dict with the keys: 'name', 'description', and 'type'
                       values all strings for their corresponding value
            description: Description of Transform

        Returns:
            Created Transform obj
        """
        arguments = arguments if arguments else []

        transform = schemas.TransformCreate(
            name=name,
            type=type,
            sourceCode=source_code,
            description=description
        )
        transform.arguments = [
            schemas.TransformArgumentCreate(**x) for x in arguments
        ]
        response = self.api._post("/transform", transform.dict(), api_version=1).json()
        return schemas.Transform(**response)

    # ----------------------------------
    #  Internal/Private Create Calls
    # ----------------------------------

    def _dataset(
            self,
            *,
            name: str,
            description: Optional[str] = None,
            status: Optional[str] = 'published',
            dw_table_id: Optional[int] = None,
            dw_operation_set_id: Optional[int] = None,
            fqtn: Optional[str] = None
    ) -> schemas.Dataset:
        """
        Create a Dataset in Rasgo.

        Args:
            name: Name of the dataset
            description: Description of the dataset
            status: Status of whether this datasets is published or not
            dw_table_id: DW table to associate with this Dataset
            dw_operation_set_id: Id of the Operation Set to associate with this Dataset
            fqtn: Fully qualified table name of the table to register this Dataset as.
        Returns:
            Created Dataset Obj
        """
        dataset_create = schemas.DatasetCreate(
            name=name,
            description=description,
            status=status,
            dw_table_id=dw_table_id,
            dw_operation_set_id=dw_operation_set_id
        )
        path = f"/datasets" + (f"?fqtn={fqtn}" if fqtn else '')
        response = self.api._post(
            path, dataset_create.dict(), api_version=2
        ).json()
        return schemas.Dataset(**response)

    def _operation_set(
            self,
            operations: List[schemas.OperationCreate],
            dataset_dependency_ids: List[int]
    ) -> schemas.OperationSet:
        """
        Create a operation set in Rasgo with specified operation
        and input dataset dependencies ids
        """
        operation_set_create = schemas.OperationSetCreate(
            operations=operations,
            dataset_dependency_ids=dataset_dependency_ids
        )
        response = self.api._post(
            "/operation-sets", operation_set_create.dict(), api_version=2
        ).json()
        return schemas.OperationSet(**response)

    def _operation_set_async(
            self,
            operations: List[schemas.OperationCreate],
            dataset_dependency_ids: List[int]
    ) -> schemas.OperationSetAsyncTask:
        """
        Create a operation set in Rasgo with specified operation
        and input dataset dependencies ids
        """
        operation_set_create = schemas.OperationSetCreate(
            operations=operations,
            dataset_dependency_ids=dataset_dependency_ids
        )
        response = self.api._post(
            "/operation-sets/async", operation_set_create.dict(), api_version=2
        ).json()
        return schemas.OperationSetAsyncTask(**response)

    def _operation_set_preview(
            self,
            operations: List[schemas.OperationCreate],
            dataset_dependency_ids: List[int]
    ) -> str:
        """
        Create a operation set in Rasgo with specified operation
        and input dataset dependencies ids
        """
        operation_set_create = schemas.OperationSetCreate(
            operations=operations,
            dataset_dependency_ids=dataset_dependency_ids
        )
        response = self.api._post(
            "/operation-sets/offline", operation_set_create.dict(), api_version=2
        ).json()
        return response

    def _operation_set_preview_async(
            self,
            operations: List[schemas.OperationCreate],
            dataset_dependency_ids: List[int]
    ) -> schemas.OperationSetOfflineAsyncTask:
        """
        Create a operation set in Rasgo with specified operation
        and input dataset dependencies ids in an async fashion
        """
        operation_set_create = schemas.OperationSetCreate(
            operations=operations,
            dataset_dependency_ids=dataset_dependency_ids
        )
        response = self.api._post(
            "/operation-sets/offline/async", operation_set_create.dict(), api_version=2
        ).json()
        return schemas.OperationSetOfflineAsyncTask(**response)
