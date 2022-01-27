"""
Module for all things Source Transforms
"""
from typing import Dict, List, Optional, Union

import pandas as pd

from pyrasgo.api.connection import Connection
from pyrasgo.api.error import APIError
from pyrasgo.primitives.source import DataSource
from pyrasgo.schemas import transform as schemas


class TransformChain(Connection):
    """
    Class for implementing executing, previewing, and source creation of one
    or more transforms
    """

    def __init__(self,
                 source: DataSource,
                 transform_steps: Optional[List[schemas.TransformArgs]] = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        from pyrasgo.api import Get
        from pyrasgo.storage import DataWarehouse, SnowflakeDataWarehouse

        self.transform_steps = transform_steps if transform_steps else []
        self.source = source
        self._get_api = Get()
        self._data_warehouse: SnowflakeDataWarehouse = DataWarehouse.connect()

    @property
    def has_any_non_db_transforms(self) -> bool:
        """
        Return True if any of the supplied transform steps in the Chain
        are not from the db, but from source code.
        """
        return any([
            not bool(transform_step.transformId)
            for transform_step in self.transform_steps
        ])

    def transform(self,
                  *,
                  transform_id: Optional[int] = None,
                  transform_name: Optional[str] = None,
                  transform: Optional[schemas.Transform] = None,
                  source_code: Optional[str] = None,
                  arguments: Optional[Dict[str, str]] = None,
                  **kwargs: Union[str, int, List, Dict]) -> 'TransformChain':
        """
        Add/chain another transform step on this source, and return self/TransformerChain obj

        Returned obj can chain more transformers together by calling .transform() again if needed.

        Preview the transformed dataset as a df or SQL as a df with .preview() and .preview_sql()

        Create a source from the chained transforms by then calling .to_source(). You can ONLY do this
        when supplying a transform id, name, or obj and not source_code

        Args:
            transform_id: Transform id to add as step to chain. Can input Transform name or Transform schema instead
            transform_name: Transform name to add as step to chain. Can add Transform id or Transform schema instead
            transform: Transform schema to add as step to chain. Can be Transform id or name instead
            source_code: If not entering a transform id, name, or obj, test source_code with the transform
            arguments: Arguments to apply to this transform

        Returns:
            A TransformChain() obj with a newly added transform step
        """
        arguments = arguments if arguments else {}

        # Get and validate transform obj input
        self._validate_transform_inputs(
            transform_id, transform_name, transform, source_code
        )
        transform = self._get_transform_model(
            transform_id, transform_name, transform, source_code
        )

        # Update the Transform arguments with any supplied kwargs
        arguments.update(kwargs)

        # Create a new instance of a TransformChain
        # class with same source and steps
        new_transform_chain = self.__class__(
            source=self.source,
            transform_steps=self.transform_steps
        )

        # Append Transform Args as new step in new Chain Obj
        # and return new TransformChain
        transform_step = schemas.TransformArgs(
            transformId=transform.id if hasattr(transform, 'id') else None,
            sourceCode=transform.sourceCode,
            arguments=arguments,
        )
        new_transform_chain.transform_steps.append(transform_step)
        return new_transform_chain

    def preview_sql(self) -> str:
        """
        Preview the generated SQL for this Transform Chain
        """
        self._raise_error_if_no_transform_steps()

        transform_execute = schemas.TransformExecute(
            dataSourceId=self.source.id,
            transformArgs=self.transform_steps,
        )
        transform_sql = self._post(resource="/transform/sql",
                                   _json=transform_execute.dict(exclude_unset=True),
                                   api_version=1).json()
        return transform_sql

    def preview(self, limit: int = 10) -> Union[pd.DataFrame, str]:
        """
        Preview the dataset from this chain of transforms

        Returns a pandas DataFrame

        Args:
            limit: Number of rows to return; default 10

        Returns:
            DataFrame of the Transform Chained source if no errors
        """
        self._raise_error_if_no_transform_steps()

        # Get the transform SQL and set limit
        transform_sql = self.preview_sql()
        if limit:
            transform_sql = f"{transform_sql} LIMIT {limit}"

        # Execute the Transform Chain SQL query. Show error message if any
        try:
            df = self._data_warehouse.query_into_dataframe(transform_sql)
            return df
        except Exception as e:
            raise APIError(f"Error Executing transform SQL\n\nerror\n-----\n{e} "
                           f"{e}\n\ngenerated_sql\n--------------\n{transform_sql}")

    def to_source(self, new_table_name: Optional[str] = None) -> DataSource:
        """
        Create a new DataSource for this Chain of Transforms
        """
        self._raise_error_if_no_transform_steps()

        # Don't allow creating source if any transform steps
        # are from source_code and not DB
        if self.has_any_non_db_transforms:
            raise APIError("One or more of your transforms were created "
                           "from Jinja source_code and not the db. To call the .to_source() "
                           "method, all transforms need to be created already.\n\nCall "
                           "rasgo.get.transforms() and use any of those available. "
                           "Create a new Transform with rasgo.create.transform()")

        # If new source name entered make sure no spaces in name
        if new_table_name and " " in new_table_name:
            raise ValueError(f"The new source is going to be a table. "
                             f"Please pass a name without whitespace")

        # Execute the transforms on this source to create a new one
        transform_execute = schemas.TransformExecute(
            dataSourceId=self.source.id,
            transformArgs=self.transform_steps,
            newTableName=new_table_name
        )
        response = self._post(resource="/transform/execute",
                              _json=transform_execute.dict(exclude_unset=True),
                              api_version=1).json()
        return DataSource(api_object=response)

    @staticmethod
    def _validate_transform_inputs(transform_id: Optional[int] = None,
                                   transform_name: Optional[str] = None,
                                   transform: Optional[schemas.Transform] = None,
                                   source_code: Optional[str] = None) -> None:
        """
        Validate the user only inputted one transform (id, name, or obj)

        Also validate that a transform with id or name exists if one of those were entered
        """
        # Make sure source_code and not transform identifier supplied
        if source_code and (transform_id or transform_name or transform):
            raise APIError("You cannot execute a transform by supplying a Transform "
                           "identifier(id, name, or obj) and 'source_code'. "
                           "Please supply one or the other.")

        # Make sure only one transform identifier entered or source code not entered
        if not source_code and not transform_id and not transform and not transform_name:
            raise APIError("To execute a Transform supply the param "
                           "'transform_id' (id of transform), 'transform_name' "
                           "(name of transform), 'transform' (Transform obj), "
                           "or 'source_code' (Transform Jinja source code to apply)"
                           "from rasgo.get.transforms()")

        elif transform_id and (transform_name or transform) \
                or transform_name and (transform_id or transform) \
                or transform and (transform_id or transform_name):
            raise APIError("Please supply ONLY one of 'transform_id', 'transform_name' or 'transform' obj "
                           "as input params to identify the transform to use")

    def _get_transform_model(self,
                             transform_id: Optional[int] = None,
                             transform_name: Optional[str] = None,
                             transform: Optional[schemas.Transform] = None,
                             source_code: Optional[str] = None) -> schemas.Transform:
        """
        Get and return the transform model by id, name, or source code
        """
        # Validate transform with id or name exists if entered
        if transform_id:
            transform = self._get_api.transform(transform_id)
            if not transform:
                raise ValueError(f"No Transform found with id {transform_id}")
        elif transform_name:
            transform = self._get_transform_by_name(transform_name)
            if not transform:
                raise ValueError(f"No Transform found with name {transform_name}")

        # If source code provided init model with source code
        # We aren't adding arguments as their only used here for validation,
        # we don't have have jinja installed on the SDK to parse it,
        # and on the API side an error will be raised if any missing during execution
        elif source_code:
            transform = schemas.Transform(sourceCode=source_code,
                                          arguments=[])
        return transform

    def _get_transform_by_name(self, transform_name: str) -> Optional[schemas.Transform]:
        """
        Get and return a transform obj by name
        """
        available_transforms = self._get_api.transforms()
        for transform in available_transforms:
            if transform_name == transform.name:
                return transform

    def _raise_error_if_no_transform_steps(self) -> None:
        if not self.transform_steps:
            raise APIError(
                "No transform steps have been added to this chain yet. call .transform(**kwargs) "
                "first to preview the transform chain or create a source from it."
            )
