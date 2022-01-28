import warnings

import benchling_api_client.v2.extensions

NotPresentError = benchling_api_client.v2.extensions.NotPresentError
UnknownType = benchling_api_client.v2.extensions.UnknownType
Enums = benchling_api_client.v2.extensions.Enums

warnings.warn("This package is deprecated: please use benchling_api_client.v2.extensions", DeprecationWarning)
