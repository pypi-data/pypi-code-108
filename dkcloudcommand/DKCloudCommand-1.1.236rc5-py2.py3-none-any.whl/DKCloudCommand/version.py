__all__ = ["DK_VERSION"]

import pkg_resources
from pkg_resources import DistributionNotFound

try:
    DK_VERSION = pkg_resources.require("DKCloudCommand")[0].version
except DistributionNotFound:
    DK_VERSION = "1.0.0"
# For local testing:
# except pkg_resources.ContextualVersionConflict:
#    DK_VERSION = "1.0.0"
