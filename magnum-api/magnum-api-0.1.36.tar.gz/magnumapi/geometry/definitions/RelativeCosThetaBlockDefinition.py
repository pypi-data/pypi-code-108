from dataclasses import dataclass

from magnumapi.geometry.definitions.CosThetaBlockDefinition import CosThetaBlockDefinition


@dataclass
class RelativeCosThetaBlockDefinition(CosThetaBlockDefinition):
    """Class for relative cos-theta block definition.

    Attributes:
       phi_r (float): The positioning angle in degrees.
       alpha_r (float): The inclination angle in degrees.
    """
    phi_r: float
    alpha_r: float
