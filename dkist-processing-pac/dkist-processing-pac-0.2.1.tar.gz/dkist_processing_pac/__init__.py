# Licensed under a 3-clause BSD style license - see LICENSE.rst
from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    __version__ = "unknown"

from dkist_processing_pac import Data, CUModel, TelescopeModel, FittingFramework, FitCUParams, GenerateDemodMatrices, \
     FitM36Params, generic

