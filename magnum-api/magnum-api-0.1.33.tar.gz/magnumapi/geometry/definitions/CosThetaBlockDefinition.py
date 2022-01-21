from dataclasses import dataclass

from magnumapi.geometry.definitions.BlockDefinition import BlockDefinition


@dataclass
class CosThetaBlockDefinition(BlockDefinition):
    """Class for cos-theta block definition.

    Attributes:
       radius (float): The radius in millimeter.
    """
    radius: float
