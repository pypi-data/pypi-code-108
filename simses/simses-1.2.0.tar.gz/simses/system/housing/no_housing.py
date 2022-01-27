import numpy
from simses.system.housing.abstract_housing import Housing


class NoHousing(Housing):
    LARGE_NUMBER = numpy.finfo(numpy.float64).max * 1e-100

    def __init__(self):
        super().__init__()

    @property
    def internal_volume(self) -> float:
        return self.LARGE_NUMBER

    @property
    def azimuth(self) -> float:
        return 0.0

    @property
    def albedo(self) -> float:
        return 0.0

