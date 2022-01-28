import warnings

import benchling_api_client.v2.benchling_client

AuthorizationMethod = benchling_api_client.v2.benchling_client.AuthorizationMethod
BenchlingApiClient = benchling_api_client.v2.benchling_client.BenchlingApiClient

warnings.warn(
    "This package is deprecated: please use benchling_api_client.v2.benchling_client", DeprecationWarning
)
