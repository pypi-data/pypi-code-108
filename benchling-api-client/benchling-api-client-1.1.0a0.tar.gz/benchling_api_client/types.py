""" Contains some shared types for properties """
import warnings

import benchling_api_client.v2.types

Unset = benchling_api_client.v2.types.Unset
UNSET = benchling_api_client.v2.types.UNSET
FileJsonType = benchling_api_client.v2.types.FileJsonType
File = benchling_api_client.v2.types.File
Response = benchling_api_client.v2.types.Response

__all__ = ["File", "Response"]

warnings.warn("This package is deprecated: please use benchling_api_client.v2.types", DeprecationWarning)
