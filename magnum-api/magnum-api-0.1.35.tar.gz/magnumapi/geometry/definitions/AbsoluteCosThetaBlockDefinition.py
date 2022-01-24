from dataclasses import dataclass

from magnumapi.geometry.definitions.CosThetaBlockDefinition import CosThetaBlockDefinition


@dataclass
class AbsoluteCosThetaBlockDefinition(CosThetaBlockDefinition):
    """Class for absolute cos-theta block definition.

    Attributes:
       phi (float): The positioning angle in degrees.
       alpha (float): The inclination angle in degrees.
    """
    phi: float
    alpha: float
