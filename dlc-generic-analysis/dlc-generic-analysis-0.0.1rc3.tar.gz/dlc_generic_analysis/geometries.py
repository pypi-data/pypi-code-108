from typing import Tuple


class Line:
    """A line between two points. Used to measure scarring or other deformation
    in vocal cords.
    end1: point
        first point to calc line Endpoint with smaller x value if x1 \neq x2
    end2: point
        second point to calc line. Endpoint with greater x if x1 \neq x2
    slope: float
        slope of the line
    yint: float
        y intercept of line
    """

    def __init__(
        self,
        end1: Tuple[float, float] = None,
        end2: Tuple[float, float] = None,
        slope: float = None,
        intercept: float = None,
    ):
        """
        creates a Line either between 2 points or a slope and intercept
        :param end1: The first point for the line.
        :param end2: The second point for the line.
        :param slope: The slope of the line.
        :param intercept: the Y intercept of the line
        """
        if end1 is not None and end2 is not None:
            if end1[0] > end2[0]:
                self._end1 = end2
                self._end2 = end1
            else:
                self._end1 = end1
                self._end2 = end2
            self._slope = None
            self._intercept = None
            self._calc_slope_intercept()
        elif slope is not None and intercept is not None:
            self._intercept = intercept
            self._slope = slope
            self._end1 = (0, self._intercept)
            self._end2 = (1, int(self._intercept + self._slope))
        else:
            raise AttributeError

    def _calc_slope_intercept(self):
        if not self._end2[0] == self._end1[0]:
            self._slope = (self._end2[1] - self._end1[1]) / (self._end2[0] - self._end1[0])
        else:
            self._slope = 999999999999999
        self._intercept = self._end1[1] - self.slope * self._end1[0]

    @property
    def end1(self):
        return self._end1

    @property
    def end2(self):
        return self._end2

    @end1.setter
    def end1(self, end1: (float, float)):
        self._end1 = end1
        self._calc_slope_intercept()

    @end2.setter
    def end2(self, end2: (float, float)):
        self._end2 = end2
        self._calc_slope_intercept()

    @property
    def slope(self):
        return self._slope

    @property
    def intercept(self):
        return self._intercept
