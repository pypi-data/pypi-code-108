from dataclasses import dataclass

from magnumapi.geometry.definitions.RectangularBlockDefinition import RectangularBlockDefinition


@dataclass
class HomogenizedRectangularBlockDefinition(RectangularBlockDefinition):
    """Class for a homogenized rectangular block definition.

    Attributes:
       x_up_r (float): The x-coordinate of upper right block corner (assuming alpha equal to 0).
       y_up_r (float): The y-coordinate of upper right block corner (assuming alpha equal to 0).
    """
    x_up_r: float
    y_up_r: float
