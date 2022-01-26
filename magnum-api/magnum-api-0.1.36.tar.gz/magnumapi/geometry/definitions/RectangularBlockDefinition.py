from dataclasses import dataclass

from magnumapi.geometry.definitions.BlockDefinition import BlockDefinition


@dataclass
class RectangularBlockDefinition(BlockDefinition):
    """Class for a rectangular block definition.

    Attributes:
       x (float): The x-coordinate of lower left block corner (assuming alpha equal to 0).
       y (float): The y-coordinate of lower left block corner (assuming alpha equal to 0).
       alpha (float): The inclination angle in degrees.
    """
    x: float
    y: float
    alpha: float
