"""Deprecated import of new_struct.
Module has been moved to clease.structgen, so
use clease.structgen.new_struct instead """

from warnings import warn
from deprecated import deprecated
import numpy as np
from clease.structgen import new_struct

MSG = 'Import {} from clease.structgen.new_struct instead'
DEP_VERSION = '0.10.2'  # Deprecation version

MODULE_DEP_MSG = f"""
The clease.new_struct module has been moved as of version {DEP_VERSION}.
Please use the clease.structgen.new_struct module instead"""

# Print the message on import
warn(MODULE_DEP_MSG, np.VisibleDeprecationWarning)


@deprecated(version=DEP_VERSION, reason=MSG.format('NewStructures'))
class NewStructures(new_struct.NewStructures):
    pass


@deprecated(version=DEP_VERSION, reason=MSG.format('MaxAttemptReachedError'))
class MaxAttemptReachedError(new_struct.MaxAttemptReachedError):
    pass
