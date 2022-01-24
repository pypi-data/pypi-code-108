"""This package defines an API by which backbones should comply.

A backbone is the "workhorse" of a forecasting model, providing the majority of the model's capacity. Given that
backbones often consist of one or more cells, this package also includes the cell subpackage, which defines the cell
API.
"""

from .base import AbstractBackbone, AbstractBackboneConfig, MultilevelType  # noqa: F401
from .lstm import LSTMBackbone, LSTMBackboneConfig  # noqa: F401
from .repeated_cell import RepeatedCellBackbone, RepeatedCellBackboneConfig, RepeatMode  # noqa: F401
