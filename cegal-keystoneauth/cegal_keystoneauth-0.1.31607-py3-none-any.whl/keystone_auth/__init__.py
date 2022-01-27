# Copyright 2021 Cegal AS
# All rights reserved

import logging
from os import getenv


logger = logging.getLogger(__name__)
verify_tls = True
if getenv("PYVAR_ALLOW_NON_HTTPS") == "true":
    verify_tls = False


from .client import OidcClient
from .options import OidcOptions, OidcFlow
