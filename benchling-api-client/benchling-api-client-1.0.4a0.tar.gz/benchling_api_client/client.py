import warnings

import benchling_api_client.v2.client

Client = benchling_api_client.v2.client.Client
AuthenticatedClient = benchling_api_client.v2.client.AuthenticatedClient

warnings.warn("This package is deprecated: please use benchling_api_client.v2.client", DeprecationWarning)
