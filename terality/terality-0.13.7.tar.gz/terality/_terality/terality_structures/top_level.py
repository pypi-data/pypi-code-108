from functools import partial
from typing import Dict, Optional
import inspect

import pandas as pd

from common_client_scheduler import UploadRequest
from terality_serde import StructType

from . import call_pandas_function
from ..utils.azure import parse_azure_filesystem, test_for_azure_libs
from ...exceptions import TeralityClientError
from terality._terality.globals import global_client
from terality._terality.utils.config import TeralityConfig
from terality._terality.data_transfers import upload_local_files, upload_s3_files


def _make_upload(path: str, storage_options: Optional[Dict] = None) -> UploadRequest:
    config = TeralityConfig.load(fallback_to_defaults=True)
    if config.skip_transfers:
        transfer_id = ""
        aws_region = None
    else:
        if path.startswith("s3://"):
            parts = path[len("s3://") :].split("/", 1)
            if len(parts) != 2:
                raise ValueError(
                    f"Invalid S3 path, expected format: 's3://bucket/prefix' (prefix may be the empty string), got: '{path}'."
                )
            transfer_id = upload_s3_files(s3_bucket=parts[0], s3_key_prefix=parts[1])
            aws_region = global_client().data_transfer().get_upload_aws_region()
        elif path.startswith("abfs://") or path.startswith("az://"):
            test_for_azure_libs()
            from ..data_transfers.azure import upload_azure_storage_files

            storage_account_name, container, folder = parse_azure_filesystem(path, storage_options)
            transfer_id = upload_azure_storage_files(storage_account_name, container, folder)
            aws_region = global_client().data_transfer().get_upload_aws_region()
        elif path.startswith("gs://"):
            raise TeralityClientError(
                "Currently, Terality does not support GCP storage. Please use AWS S3 or Azure paths."
            )
        else:
            transfer_id = upload_local_files(
                path, global_client().get_aws_credentials(), global_client().cache_disabled()
            )
            aws_region = None
    return UploadRequest(path=path, transfer_id=transfer_id, aws_region=aws_region)


def _treat_read_job(method_name, *args, **kwargs):
    """Special job to intercept file arguments and upload them to Terality for pd.read_xxx() jobs"""
    storage_options = kwargs.get("storage_options")
    path_parameter_name = _read_top_level_functions_to_path_parameter[method_name]
    if path_parameter_name in kwargs:
        kwargs[path_parameter_name] = _make_upload(kwargs[path_parameter_name], storage_options)
    else:
        if len(args) == 0:
            raise TypeError(
                f"{method_name}() missing 1 required positional argument: '{path_parameter_name}'"
            )
        path, *others = args
        args = [_make_upload(path, storage_options)] + others
    return call_pandas_function(StructType.TOP_LEVEL, None, method_name, *args, **kwargs)


# pandas top level functions (e.g defined as pd.SomeFunc) that Terality reimplements
# we also need to specify each path parameter name as we handle it similarly for all read methods
_read_top_level_functions_to_path_parameter = {
    "read_parquet": "path",
    "read_csv": "filepath_or_buffer",
    "read_excel": "io",
    "read_fwf": "filepath_or_buffer",
    "read_json": "path_or_buf",
    "read_html": "io",
    "read_xml": "path_or_buffer",
    "read_hdf": "path_or_buf",
    "read_feather": "path",
    "read_orc": "path",
    "read_stata": "filepath_or_buffer",
    "read_sas": "filepath_or_buffer",
    "read_spss": "path",
}

# Even if for now the `read_xxx` function are the only one to be reimplemented by Terality,
# they have a very specific path in the code.
# Should we add any new top level function in the future, it can be implemented very differently
# than a "read_xxx" function.
# Make this clear by already having two concepts: generic "top level functions" whose only instances
# for now are the read functions.
top_level_functions = list(_read_top_level_functions_to_path_parameter)


def get_dynamic_top_level_attribute(attribute: str):
    """Return the Terality or pandas module attribute with the given name.

    This function is intended to be the implementation of `__getattr__` (not `__getattribute__`) for the
    Terality module.

    When a user tries to access an attribute on the `terality` module that's not exported through the usual means,
    such as:

    >>> import terality as pd
    >>> df = pd.Something()

    then we use `_get_top_level_attribute` to dynamically resolve the `pd.Something` name.

    Note that data structures such as `pd.DataFrame` are exported in the `__init__` file of the Terality module
    and as such are never resolved through this function. Python only calls `__getattr__` when it can't resolve
    a name otherwise.

    The name resolution logic we use is:
    0. check that the pandas module defines the name. If not, raise an AttributeError
    1. intercept functions that need special client processing (such as read_csv, read_parquet...)
    2. if it's a class in pandas (`pd.Timestamp`), then return the pandas class
    3. if it's a module in pandas (`pd.tseries`), then return the pandas module
    4. otherwise, assume that it's a function, and send it to the Terality API

    In the future, we may implement an allowlist of functions to be locally executed by pandas (it could
    be sent by the server at session creation for instance).
    """
    # Check if the attribute is defined by the pandas library. If not, this line will raise an AttributeError.
    pd_attr = getattr(pd, attribute)

    # Special cases for NaT and NA
    if attribute == "NaT":
        return pd.NaT
    if attribute == "NA":
        return pd.NA

    # Intercept functions that need special handling (for now, only the "read_xxx" family of functions).
    if attribute in _read_top_level_functions_to_path_parameter:
        return partial(_treat_read_job, attribute)

    # Send class and module calls to the pandas module
    if inspect.isclass(pd_attr) or inspect.ismodule(pd_attr):
        return pd_attr

    # Send anything else to the Terality API
    return partial(call_pandas_function, StructType.TOP_LEVEL, None, attribute)
