"""

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


    def transform(self,
                  transform_id: Optional[int] = None,
                  transform_name: Optional[str] = None,
                  transform: Optional[schemas.Transform] = None,
                  arguments: Optional[Dict[str, str]] = None,
                  utilities: Optional[List[Dict]] = None) -> 'TransformChain':
        """
        Add/chain another transform step on this source, and return self/TransformerChain obj

        Returned obj can chain more transformers together by calling .transform() again if needed.

        Create a source from the chained transforms by then calling .to_source() or preview the
        transformed datasets as a df with .preview()

        Args:
            transform_id: Transform id to add as step to chain. Can input Transform name or Transform schema instead
            transform_name: Transform name to add as step to chain. Can add Transform id or Transform schema instead
            transform: Transform schema to add as step to chain. Can be Transform id or name instead
            arguments: Arguments to apply to this transform
            utilities: Transform Utilities to apply to this Transform

        Returns:
            A TransformChain() obj with a newly added transform step
        """
        arguments = arguments if arguments else {}
        utilities = utilities if utilities else []

        # Get and validate transform obj input
        transform = self._validate_transform_inputs(transform_id, transform_name, transform)

        # Make sure all arguments entered for transform. Raise error if not.
        self._validate_transform_arguments(transform, arguments, utilities)

        # Create a new instance of a TransformChain
        # class with same source and steps
        new_transform_chain = self.__class__(
            source=self.source,
            transform_steps=self.transform_steps
        )

        # Append Transform Args as new step in new Chain Obj
        # and return new TransformChain
        transform_step = schemas.TransformArgs(
            transformId=transform.id,
            arguments=arguments,
            utilities=utilities,
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


    def _validate_transform_inputs(self,
                                   transform_id: Optional[int] = None,
                                   transform_name: Optional[str] = None,
                                   transform: Optional[schemas.Transform] = None) -> schemas.Transform:
        """
        Validate the user only inputted one transform (id, name, or obj)

        Also validate that a transform with id or name exists if one of those were entered

        Returns:
            Transform Obj if no errors and exists
        """
        # Make sure only one transform identifier entered. Raise APIError if so
        if not transform_id and not transform and not transform_name:
            raise APIError("To execute a Transform supply the param "
                           "'transform_id' (id of transform), 'transform_name' "
                           "(name of transform), or 'transform' (Transform obj) "
                           "from rasgo.get.transforms()")
        elif transform_id and (transform_name or transform) \
                or transform_name and (transform_id or transform) \
                or transform and (transform_id or transform_name):
            raise APIError("Please supply ONLY one of 'transform_id', 'transform_name' or 'transform' obj "
                           "as input params to identify the transform to use")

        # Validate transform with id or name exists if entered
        if transform_id:
            transform = self._get_api.transform(transform_id)
        elif transform_name:
            transform = self._get_transform_by_name(transform_name)
            if not transform:
                raise ValueError(f"No Transform found with name {transform_name}")

        return transform

    @staticmethod
    def _validate_transform_arguments(transform: schemas.Transform,
                                      arguments: Dict[str, str],
                                      utilities: List[Dict]) -> None:
        """
        Validate that all the arguments for the transform were entered
        """
        utility_arg_names = [x['resultArgumentName'] for x in utilities]
        all_inputted_args = list(arguments.keys()) + utility_arg_names
        for needed_arg in transform.arguments:
            if needed_arg not in all_inputted_args:
                raise APIError(f"Missing required argument '{needed_arg}' for transform '{transform.name}'. "
                               f"Add into the input arguments dict or as a transform utility result val")

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
