"""Deprecated import of structure_generator.
Module has been moved to clease.structgen, so
use clease.structgen.structure_generator instead"""

from warnings import warn
from deprecated import deprecated
import numpy as np
from clease.structgen import structure_generator

MSG = 'Import {} from clease.structgen.structure_generator instead'
DEP_VERSION = '0.10.2'  # Deprecation version

MODULE_DEP_MSG = f"""
The clease.new_struct module has been moved as of version {DEP_VERSION}.
Please use the clease.structgen.structure_generator module instead"""

# Print the message on import
warn(MODULE_DEP_MSG, np.VisibleDeprecationWarning)


@deprecated(version=DEP_VERSION, reason=MSG.format('StructureGenerator'))
class StructureGenerator(structure_generator.StructureGenerator):
    pass


@deprecated(version=DEP_VERSION, reason=MSG.format('GSStructure'))
class GSStructure(structure_generator.GSStructure):
    pass


@deprecated(version=DEP_VERSION, reason=MSG.format('MetropolisTrajectory'))
class MetropolisTrajectory(structure_generator.MetropolisTrajectory):
    pass


@deprecated(version=DEP_VERSION, reason=MSG.format('ProbeStructure'))
class ProbeStructure(structure_generator.ProbeStructure):
    pass
