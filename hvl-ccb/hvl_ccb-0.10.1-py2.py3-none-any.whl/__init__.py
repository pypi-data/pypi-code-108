#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""Top-level package for HVL Common Code Base."""

__author__ = (
    "Mikołaj Rybiński, David Graber, Henrik Menne, Alise Chachereau, Henning Janssen, "
    "David Taylor"
)
__email__ = (
    "mikolaj.rybinski@id.ethz.ch, dev@davidgraber.ch, henrik.menne@eeh.ee.ethz.ch, "
    "chachereau@eeh.ee.ethz.ch, janssen@eeh.ee.ethz.ch, dtaylor@ethz.ch"
)
__version__ = '0.10.1'

from . import comm  # noqa: F401
from . import dev  # noqa: F401
from .configuration import ConfigurationMixin, configdataclass  # noqa: F401
from .experiment_manager import (  # noqa: F401
    ExperimentManager,
    ExperimentStatus,
    ExperimentError
)
