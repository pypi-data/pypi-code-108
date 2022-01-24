from dataclasses import dataclass

from magnumapi.geometry.definitions.BlockDefinition import BlockDefinition


@dataclass
class HomogenizedBlockDefinition(BlockDefinition):
    """Class for homogenized cos-theta block definition.
       The angle numbering is as follows:
            # 3 ----- 2
            # |       |
            # |       |
            # 0-------1

    Attributes:
       radius_inner (float): The inner radius in millimeter.
       radius_outer (float): The outer radius in millimeter.
       phi_0 (float): The first angle in degrees.
       phi_1 (float): The second angle in degrees.
       phi_2 (float): The third angle in degrees.
       phi_3 (float): The fourth angle in degrees.
    """
    radius_inner: float
    radius_outer: float
    phi_0: float
    phi_1: float
    phi_2: float
    phi_3: float
