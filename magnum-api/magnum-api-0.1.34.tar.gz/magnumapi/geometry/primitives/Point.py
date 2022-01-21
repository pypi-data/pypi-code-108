import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    """A Point class implementing basic operations of a cartesian point in 2D.

   Attributes:
       x (float): x coordinate
       y (float): y coordinate
    """
    x: float
    y: float

    # ToDo add examples to documentation and test them

    @staticmethod
    def of_cartesian(x: float, y: float) -> "Point":
        """ Static method creating a new Point object with cartesian x and y coordinates

        :param x: x coordinate
        :param y: y coordinate
        :return: a new Point object with x,y coordinates
        """
        return Point(x=x, y=y)

    @staticmethod
    def of_polar(r: float, phi: float) -> "Point":
        """ Static method creating a new Point object with polar r and phi coordinates.

        :param r: point radius
        :param phi: point angle (in degrees)
        :return: a new Point object with r, phi coordinates
        """
        phi_in_rad = math.radians(phi)
        x = r * math.cos(phi_in_rad)
        y = r * math.sin(phi_in_rad)
        return Point(x=x, y=y)

    def copy(self) -> "Point":
        """ Method returning a copy of a current Point instance

        :return: a copy of the Point instance
        """
        return Point.of_cartesian(x=self.x, y=self.y)

    def get_phi(self) -> float:
        """ Method returning point angle in degrees

        :return: point angle in polar coordinate expressed in degrees
        """
        return math.degrees(math.atan2(self.y, self.x))

    def get_phi_in_rad(self) -> float:
        """ Method returning point angle in radians

        :return: point angle in polar coordinate expressed in radians
        """
        return math.atan2(self.y, self.x)

    def get_r(self) -> float:
        """ Method returning point radius

        :return: point radius in polar coordinates
        """
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def rotate(self, alpha: float) -> "Point":
        """ Method rotating a Point instance by a given angle w.r.t. the center of the coordinate system (0,0)

        :param alpha: rotation angle in degrees
        :return: a new rotated Point instance
        """
        alpha_in_rad = math.radians(alpha)
        x = math.cos(alpha_in_rad) * self.x - math.sin(alpha_in_rad) * self.y
        y = math.sin(alpha_in_rad) * self.x + math.cos(alpha_in_rad) * self.y
        return Point.of_cartesian(x=x, y=y)

    def translate(self, point: "Point") -> "Point":
        """ Method translating a Point instance by an input point

        :param point: input point by which a Point instance is translated
        :return: a new translated Point instance
        """
        # ToDo this method can profit from add method
        return Point.of_cartesian(x=self.x + point.x, y=self.y + point.y)

    def plot(self, ax, marker='o', markersize=3, color="black") -> None:
        """ Method plotting point on an input axis.

        :param ax: axis on which a point is plotted
        :param marker: point marker, circle by default
        :param markersize: point marker size, 3 by default
        :param color: point marker color, black by default
        :return: None
        """
        ax.plot([self.x], [self.y], marker=marker, markersize=markersize, color=color)

    def __neg__(self) -> "Point":
        """ Method negating point coordinates

        :return: a new a Point instance with negative x and y coordinates
        """
        return Point.of_cartesian(-self.x, -self.y)

    def __sub__(self, p: "Point") -> "Point":
        """ Method subtracting a Point p from a Point instance

        :param p: Point object subtracted from a Point instance
        :return: a new Point instance equal to a difference between a Point instance and input point
        """
        return Point.of_cartesian(self.x - p.x, self.y - p.y)

    def __add__(self, p: "Point") -> "Point":
        """ Method adding a Point p to a Point instance

        :param p: Point object added to a Point instance
        :return: a new Point instance equal to a sum of a Point instance and input point
        """
        return Point.of_cartesian(self.x + p.x, self.y + p.y)

    def __mul__(self, scalar: float) -> "Point":
        """ Method multiplying a Point p by a Point instance

        :param p: Point object multiplied by a Point instance
        :return: a new Point instance equal to a multiplication of a Point instance and input point
        """
        # ToDo lmul, rmul missing
        return Point.of_cartesian(self.x * scalar, self.y * scalar)

    def __str__(self) -> str:
        """ Method returning a string representation of a Point for a user

        :return: string representation of a Point instance
        """
        if isinstance(self.x, int) and isinstance(self.y, int):
            return "(%d, %d)" % (self.x, self.y)
        elif isinstance(self.x, int):
            return "(%d, %f)" % (self.x, self.y)
        elif isinstance(self.y, int):
            return "(%f, %d)" % (self.x, self.y)
        else:
            return "(%f, %f)" % (self.x, self.y)

    def __repr__(self) -> str:
        """ Method returning a string representation of a Point for a developer

        :return: string representation of a Point instance as for a constructor call
        """
        return "Point(%f, %f)" % (self.x, self.y)

    def __eq__(self, p: "Point") -> bool:
        """ Method checking equality between two points

        :param p: a Point instance with which equality is checked
        :return: True if points are exactly equal (no tolerance is used), False otherwise
        """
        return self.x == p.x and \
               self.y == p.y

    def det(self) -> float:
        """ Method calculating length of a vector constructed from the origin of the cartesian coordinate system (0, 0)
        and a Point instance coordinates. This method is an alias for Point().get_r() method.

        :return: length of a vector constructed from the coordinate system origin and the point itself
        """
        return self.get_r()

    def dot(self, p: "Point") -> float:
        """ Method calculating the dot product of a Point instance with input Point p

        :param p: input Point with which the dot product is calculated
        :return: scalar value of the dot product
        """
        return self.x * p.x + self.y * p.y

    def unit(self) -> "Point":
        """ Method calculating a unit vector of a vector constructed from the origin of the cartesian coordinate system
        (0, 0) and a Point instance coordinates.

        :return: a Point instance with coordinates scaled with the length of the length in order to obtain a unit length
        """
        det = self.det()
        if det == 0:
            return Point.of_cartesian(0.0, 0.0)
        else:
            return Point.of_cartesian(self.x / det, self.y / det)
