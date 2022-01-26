# Copyright 2019 Cognite AS

from cognite.seismic._api_client import CogniteSeismicClient
from cognite.seismic._token import TokenGenerator, generate_oidc_token
from cognite.seismic.data_classes.api_types import *

from ._version import get_version

__version__ = get_version()

del get_version
