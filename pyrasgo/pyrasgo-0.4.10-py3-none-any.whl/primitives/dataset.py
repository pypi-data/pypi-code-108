"""
Dataset 'Primitive' In rasgo SDK
"""
import functools
import inspect
from inspect import Parameter
from datetime import datetime
from typing import Callable, Dict, List, Optional, Union

import pandas as pd
from pyrasgo import schemas
from pyrasgo.api.connection import Connection
from pyrasgo.api.error import APIError
from pyrasgo.utils import naming, polling

# Value of dataset.status if dataset is published
DS_PUBLISHED_STATUS = 'published'


def require_operation_set(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self: 'Dataset' = args[0]
        self._require_operation_set()
        return func(*args, **kwargs)
    return wrapper


class Dataset(Connection):
    """
    Representation of a Rasgo Dataset
    """
    def __init__(self,
                 # Args passed from Rasgo
                 api_dataset: Optional[schemas.Dataset] = None,
                 api_operation_set: Optional[schemas.OperationSet] = None,
                 # Args passed from transforming
                 operations: Optional[List[schemas.OperationCreate]] = None,
                 dataset_dependencies: Optional[List[int]] = None,
                 guid: Optional[str] = None,
                 transforms: Optional[List[schemas.Transform]] = None,
                 verbose=False,
                 experimental_async=False,
                 **kwargs: Dict):
        """
        Init functions in two modes:
            1. This Dataset retrieved from Rasgo. This object is for reference, and cannot
               be changed, but can be transformed to build new datasets
            2. This Dataset represents a new dataset under construction. It is not persisted in Rasgo
               and instead consists of some operations that will be used to generate a new dataset.
        """
        super().__init__(**kwargs)

        self._verbose = verbose
        self._api_dataset: schemas.Dataset = api_dataset
        self._api_operation_set: schemas.OperationSet = api_operation_set
        self._operations = operations if operations else []
        self._dataset_dependencies = dataset_dependencies if dataset_dependencies else []
        self._guid = guid
        self._source_code_preview = None
        if transforms:
            self._available_transforms = transforms
        else:
            self._available_transforms = _get_transforms()
        self._experimental_async = experimental_async

        #  alias .transform allowing direct referencing of named transforms
        for transform in self._available_transforms:
            f = self._create_udt_function(transform)
            setattr(self, transform.name, f)

    def __repr__(self) -> str:
        """
        Get string representation of this dataset
        """
        if self._api_dataset:
            return f"Dataset(id={self.id}, " \
                   f"name={self.name}, " \
                   f"status={self.status}, " \
                   f"description={self.description})"
        else:
            return f"Dataset()"

    # -------------------
    # Properties
    # -------------------

    @property
    def id(self) -> Optional[int]:
        """
        Return the id for this dataset

        Raise API error if one doesn't exist yet and is an offline dataset
        """
        if self._api_dataset:
            return self._api_dataset.id

    @property
    def name(self) -> Optional[str]:
        """
        Return dataset name if set/saved
        """
        if self._api_dataset:
            return self._api_dataset.name

    @property
    def description(self) -> Optional[str]:
        """
        Return dataset description if set/saved
        """
        if self._api_dataset:
            return self._api_dataset.description

    @property
    def status(self) -> Optional[str]:
        """
        Return dataset status
        """
        if self._api_dataset:
            return self._api_dataset.status

    @property
    @require_operation_set
    def fqtn(self) -> str:
        """
        Returns the Fully Qualified Table Name for this dataset
        """
        if self._api_dataset and self._api_dataset.dw_table:
            return self._api_dataset.dw_table.fqtn
        elif self._guid:
            dw_namespace = self._get_default_namespace()
            return f"{dw_namespace['database']}." \
                   f"{dw_namespace['schema']}." \
                   f"{self._guid}"
        else:
            raise AttributeError("No data warehouse fqtn exists for this Dataset")

    @property
    def columns(self) -> Optional[List[schemas.DatasetColumn]]:
        """
        Return the columns for this dataset if it is from the API
        """
        if self._api_dataset:
            return self._api_dataset.columns


    @property
    def created_date(self) -> Optional[datetime]:
        """
        Return date this dataset was created
        """
        if self._api_dataset:
            return self._api_dataset.create_timestamp

    @property
    def update_date(self) -> Optional[datetime]:
        """
        Return date this dataset was updated
        """
        if self._api_dataset:
            return self._api_dataset.update_timestamp

    @property
    def attributes(self) -> Optional[Dict]:
        """
        Return the attributes for this dataset if it is from the API
        """
        if self._api_dataset:
            return self._api_dataset.attributes

    @property
    def dependencies(self) -> List['Dataset']:
        """
        Return a list of dataset dependencies for this dataset
        """
        from pyrasgo.api import Get

        get = Get()
        dataset_deps = []
        self._cache_op_set_from_api()
        if self._api_operation_set:
            for ds in self._api_operation_set.dataset_dependencies:
                dataset_deps.append(get.dataset(ds.id))
        else:
            get = Get()
            for ds_id in self._dataset_dependencies:
                dataset_deps.append(get.dataset(ds_id))
        return dataset_deps


    @property
    @require_operation_set
    def sql(self) -> Optional[str]:
        """
        Return the source code SQL used to generate this dataset
        """
        # Raise error if no operations/source code for this dataset yet
        has_operations = (not hasattr(self._api_operation_set, "operations")
                          or (not self._api_operation_set.operations))
        if has_operations and not self._source_code_preview:
            return
        if self._api_dataset:
            return '\n\n'.join([x.operation_sql for x in self._api_operation_set.operations])
        else:
            return self._source_code_preview

    @property
    def snapshots(self) -> Optional[list]:
        return [(i+1, ss.timestamp) for i, ss in enumerate(self._api_dataset.snapshots)]

# --------
# Methods
# --------

    def transform(
            self,
            transform_name: str,
            arguments: Optional[Dict[str, Union[str, int, List, Dict, 'Dataset']]] = None,
            operation_name: Optional[str] = None,
            experimental_async = False,
            **kwargs: Union[str, int, List, Dict, 'Dataset']
    ) -> 'Dataset':
        """
        Transform a new dataset with the given transform and arguments.
        Created operation is added to the dataset's canvas/operations set

        Args:
            transform_name: Name of transform to Apply
            arguments: Optional transform arguments sin not supplied by **kwargs
            operation_name: Name to set for the operation/transform
            **kwargs:

        Returns:
             Returns an new dataset with the referenced transform
             added to this dataset's definition/operation set
        """
        arguments = arguments if arguments else {}

        # Update the Transform arguments with any supplied kwargs
        arguments.update(kwargs)

        # Add required reference to self in transform
        arguments['source_table'] = self

        dataset_dependencies = set(self._dataset_dependencies)
        operation_dependencies = []
        parent_operations = []

        for k, v in arguments.items():
            if isinstance(v, self.__class__):
                if v._api_dataset:
                    v._assert_can_transform()
                    dataset_dependencies.add(v._api_dataset.id)
                else:
                    # if parent (could be self) is another transformed dataset, grab it's operations too
                    parent_operations.extend(v._operations)
                arguments[k] = v.fqtn
                operation_dependencies.append(v.fqtn)

        # Init table name GUID for outputted dataset
        new_guid = naming.random_operation_table_name()
        transform = self._get_transform_by_name(transform_name)

        operation_create = schemas.OperationCreate(
            operation_name=operation_name if operation_name else transform.name,
            operation_args=arguments,
            transform_id=transform.id,
            table_name=new_guid,
            table_dependency_names=operation_dependencies
        )

        operations = parent_operations + [operation_create]

        return self.__class__(
            operations=operations,
            dataset_dependencies=list(dataset_dependencies),
            guid=new_guid,
            experimental_async=experimental_async
        )

    @require_operation_set
    def to_df(
            self,
            filters: Optional[List[str]] = None,
            order_by: Optional[List[str]] = None,
            columns: Optional[List[str]] = None,
            limit: Optional[int] = None,
            snapshot_index: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Reads and returns this dataset into a pandas dataframe

        You can supply SQL WHERE clause filters, order the dataset by columns, only
        return selected columns, and add a return limit as well

        Example:
            ```
            ds = rasgo.get.dataset(dataset_id=74)
            ds.to_df(
                filters=['SALESTERRITORYKEY = 1', 'TOTALPRODUCTCOST BETWEEN 1000 AND 2000'],
                order_by=['TOTALPRODUCTCOST'],
                columns=['PRODUCTKEY', 'TOTALPRODUCTCOST', 'SALESTERRITORYKEY'],
                limit=50
            )
            ```

        Args:
            filters: List of SQL WHERE filters strings to filter on returned df
            order_by: List of columns to order by in returned dataset
            columns: List of columns to return in the df
            limit: Only return this many rows in the df
            snapshot_index: the index of a snapshot from Dataset.snapshots to read
        """
        from pyrasgo.api import Read
        return Read().dataset(
            dataset=self,
            filters=filters,
            order_by=order_by,
            columns=columns,
            limit=limit,
            snapshot_index=snapshot_index-1
        )

    def preview(
            self,
            filters: Optional[List[str]] = None,
            order_by: Optional[List[str]] = None,
            columns: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Preview the first 10 rows of this dataset, returned as pandas dataframe

        You can supply SQL WHERE clause filters, order the dataset by columns, and
        only return selected columns

        Example:
            ```
            ds = rasgo.get.dataset(dataset_id=74)
            ds.preview(
                filters=['SALESTERRITORYKEY = 1', 'TOTALPRODUCTCOST BETWEEN 1000 AND 2000'],
                order_by=['TOTALPRODUCTCOST'],
                columns=['PRODUCTKEY', 'TOTALPRODUCTCOST', 'SALESTERRITORYKEY']
            )
            ```

        Args:
            filters: List of SQL WHERE filters strings to filter on returned df
            order_by: List of columns to order by in returned dataset
            columns: List of columns to return in the df
        """
        return self.to_df(filters, order_by, columns, limit=10)

# -----------------------------------------------------
# Methods requiring dataset to be registered with Rasgo
# -----------------------------------------------------

    def visualize(self) -> None:
        """
        Opens the visualization of this dataset in the Rasgo UI. Dataset must have been `saved` in Rasgo
        """
        raise NotImplementedError

    def profile(self) -> any:
        """
        Get stats for a dataset. Dataset must have been `saved` in Rasgo
        """
        raise NotImplementedError

# ---------------------------------
#  Private Helper Funcs for Class
# ---------------------------------

    def _get_transform_by_name(self, transform_name: str) -> schemas.Transform:
        """
        Get and return a transform obj by name

        Raise Error if no transform with that name found
        """
        for transform in self._available_transforms:
            if transform_name == transform.name:
                return transform
        raise ValueError(f"No Transform with name "
                         f"'{transform_name}' available to your organization")

    def _assert_can_transform(self) -> None:
        """
        Raise an API error if you can't transform this dataset
        """
        if self._api_dataset:
            if not self._api_dataset.dw_table_id or self.status != DS_PUBLISHED_STATUS:
                raise APIError(
                    f"Dataset({self._api_dataset.id}) has not been locked/published, "
                    f"and cannot be used as an arg for new dataset transformations"
                )

    def _require_operation_set(self) -> None:
        """
        This function used to ensure that an operation set exists for a given dataset before 
        attempting to do any operations that require the operations to exist in Rasgo (for example,
        previewing tables before they actually exist)

        If the operation set does not exist, AND the set of operations to be created does,
        create temp operations so the tables exists.

        NOTE: If this is a 'offline'/transformed dataset, the endpoint hit
        doesn't do everything to create a full working OP set for the UI for
        speed performance reason, just a temp one; Just enough so can preview
        datasets/source code. Call  `self._get_or_create_op_set()` or
        `rasgo.save.dataset()` to create the full working op set for UI and more
        """
        # If the dataset is from the API and it has a
        # op set, get and cache it if not done so yet
        if self._api_dataset:
            self._cache_op_set_from_api()

        # If this is a transformed/'offline' dataset create temp op set
        # and set source code preview
        if not self._source_code_preview and self._operations:
            from pyrasgo.api.create import Create
            if self._experimental_async:
                task = Create()._operation_set_preview_async(
                    operations=self._operations,
                    dataset_dependency_ids=self._dataset_dependencies
                )
                self._source_code_preview = polling.poll_operation_set_offline_async_status(task)
            else:
                self._source_code_preview = Create()._operation_set_preview(
                    operations=self._operations,
                    dataset_dependency_ids=self._dataset_dependencies
                )

    def _cache_op_set_from_api(self) -> None:
        """
        If this dataset is from the API, and it's op set is not cached
        yet do so
        """
        if self._api_dataset:
            if not self._api_operation_set and self._api_dataset.dw_operation_set_id:
                from pyrasgo.api import Get
                self._api_operation_set = Get()._operation_set(
                    self._api_dataset.dw_operation_set_id
                )

    def _get_or_create_op_set(self) -> schemas.OperationSet:
        """
        Get or create plus return the operation set for this dataset
        """
        # If the dataset is from the API and it has a
        # op set, get and cache it if not done so yet
        if self._api_dataset:
            self._cache_op_set_from_api()

        # If the dataset doesn't have a op set in the API, or
        # it is a 'offline' transformed dataset create the op
        # set if not done so on this dataset yet
        if not self._api_operation_set:
            from pyrasgo.api.create import Create
            if self._experimental_async:
                from pyrasgo.api.get import Get
                get = Get()

                # Submit the task request
                task_request = Create()._operation_set_async(
                    operations=self._operations,
                    dataset_dependency_ids=self._dataset_dependencies
                )
                operation_set_id = polling.poll_operation_set_async_status(task_request=task_request, verbose=self._verbose)
                self._api_operation_set = get._operation_set(operation_set_id)
            else:
                self._api_operation_set = Create()._operation_set(
                    operations=self._operations,
                    dataset_dependency_ids=self._dataset_dependencies
                )

        return self._api_operation_set

    def _create_udt_function(self, transform: schemas.Transform) -> Callable:
        """
        Creates and returns a new udt function to dynamically attached to the Dataset obj on init

        New funcs docstring, name, and signature (params shown when inspecting/doing . tab on func)
        as well to improve notebook experience of using UDTs for users

        Args:
            ds_transform_func: Function pointer of Dataset.transform()
            transform: Transform to read metadata and create new udt function for
        """

        # Create new function with 'transform_name` param set to this transform's name
        def f(*arg, **kwargs) -> 'Dataset':
            return self.transform(transform_name=transform.name, *arg, **kwargs)

        # Update func meta data for better inspection in notebook
        f.__name__ = transform.name
        f.__signature__ = _gen_udt_func_signature(f, transform)
        f.__doc__ = _gen_udt_func_docstring(transform)
        return f


# -----------------------------------------
#  Internal/private methods for this file
# -----------------------------------------


def _get_transforms() -> List[schemas.Transform]:
    """
    Get and set available transforms from the API to be used
    directly as functions of Dataset if not retrieved yet
    """
    # Get available transforms from the API to be used directly as functions of Dataset
    from pyrasgo.api import Get
    try:
        return Get().transforms()
    except:
        print('Unable to fetch available transforms from Rasgo.  '
              'Will not be able to transform this Dataset')
        return []


def _gen_udt_func_signature(udt_func: Callable, transform: schemas.Transform) -> inspect.Signature:
    """
    Creates and returns a UDT param signature.

    This is shown documentation for the parameters when hitting shift tab in a notebook
    """
    # Get current signature of function
    sig = inspect.signature(udt_func)

    # Create Signature Params for UDT Args
    udt_params = []
    for t_arg in transform.arguments:
        p = Parameter(name=t_arg.name, kind=Parameter.KEYWORD_ONLY)
        udt_params.append(p)

    # Add `operation_name` param as last in signature with type annotation
    op_name_param = Parameter(
        name='operation_name',
        kind=Parameter.KEYWORD_ONLY,
        annotation=Optional[str],
        default=None
    )
    udt_params.append(op_name_param)

    # Return new signature
    return sig.replace(parameters=udt_params)


def _gen_udt_func_docstring(transform: schemas.Transform) -> str:
    """
    Generate and return a docstring for a transform func
    with transform description, args, and return specified.
    """
    # Have start of docstring be transform description
    docstring = f"\n{transform.description}"

    # Add transform args to func docstring
    docstring = f"{docstring}\n  Args:"
    for t_arg in transform.arguments:
        docstring = f"{docstring}\n    {t_arg.name}: {t_arg.description}"
    docstring = f"{docstring}\n    operation_name: Name to set for the operation"

    # Add return to docstring
    docstring = f"{docstring}\n\n  Returns:\n    Returns an new dataset with the referenced " \
                f"{transform.name!r} added to this dataset's definition"
    return docstring
