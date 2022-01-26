import math


class Telescope:
    def __init__(self, d_primary: float, d_secondary: float = 0.):
        """
        Constructor for telescope

        Args:
            d_primary: diameter of primary mirror [m]
            d_secondary: diameter of secondary mirror [m]
        """
        self.d_primary = d_primary
        self.d_secondary = d_secondary

    @property
    def area(self) -> float:
        """ Effective collecting area

        Returns: effective collecting area of the telescope [m^2]

        """
        return (self.d_primary ** 2 - self.d_secondary ** 2) / 4. * math.pi
