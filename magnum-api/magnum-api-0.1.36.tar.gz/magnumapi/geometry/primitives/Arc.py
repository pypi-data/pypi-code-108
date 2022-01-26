import math
from dataclasses import dataclass

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from magnumapi.geometry.primitives.Point import Point


@dataclass(frozen=True)
class Arc:
    """ An Arc class implementing a 2D line made of two end points and center along with basic geometric transformations

   Attributes:
       p_start (Point): start point of an arc
       p_center (Point): arc center
       theta (float): angle of an arc instance expressed in degrees
    """
    p_start: Point
    p_center: Point
    theta: float

    @staticmethod
    def of_end_points_center(p_start: Point, p_end: Point, p_center=Point.of_cartesian(0.0, 0.0)) -> "Arc":
        """ Method constructing an arc from two end points and a center

        :param p_start: start point
        :param p_end: end point
        :param p_center: center point
        :return: an Arc object with initialized start point, end point and theta
        """
        theta = Arc.calculate_theta(p_start.translate(-p_center),
                                    p_end.translate(-p_center))
        return Arc(p_start, p_center, theta)

    @staticmethod
    def calculate_theta_in_rad(p_start: Point, p_end: Point) -> float:
        """ Static method calculating theta angle (in radians) of an arc from two end points

        :param p_start: start point
        :param p_end: end point
        :return: theta angle of an arc instance expressed in radians
        """
        theta = p_end.get_phi_in_rad() - p_start.get_phi_in_rad()
        return theta

    @staticmethod
    def calculate_theta(p_start: Point, p_end: Point) -> float:
        """ Static method calculating theta angle (in degrees) of an arc from two end points

        :param p_start: start point
        :param p_end: end point
        :return: theta angle of an arc instance expressed in degrees
        """
        theta = p_end.get_phi() - p_start.get_phi()
        return theta

    def plot(self, ax: plt.Axes) -> None:
        """ Method plotting an arc on a matplotlib axis

        :param ax: input matplotlib axis
        """
        start_angle_deg = self.get_start_angle()
        end_angle_deg = self.get_end_angle()
        radius = self.get_radius()
        center = (self.p_center.x, self.p_center.y)
        if start_angle_deg > end_angle_deg:
            arc = patches.Arc(center, 2 * radius, 2 * radius, 0, end_angle_deg, start_angle_deg)
        else:
            arc = patches.Arc(center, 2 * radius, 2 * radius, 0, start_angle_deg, end_angle_deg)
        ax.add_patch(arc)

    def get_radius(self) -> float:
        """ Method calculating and returning an Arc instance radius

        :return: the radius of an arc instance
        """
        return (self.p_start - self.p_center).det()

    def get_start_angle_in_rad(self) -> float:
        """ Method returning a start angle of an arc instance in radians

        :return: start angle of an arc in radians
        """
        return (self.p_start - self.p_center).get_phi_in_rad()

    def get_start_angle(self) -> float:
        """ Method returning a start angle of an arc instance in degrees

        :return: start angle of an arc in degrees
        """
        return (self.p_start - self.p_center).get_phi()

    def get_end_angle_in_rad(self) -> float:
        """ Method returning an end angle of an arc instance in radians

        :return: end angle of an arc in radians
        """
        return self.get_start_angle_in_rad() + math.radians(self.theta)

    def get_end_angle(self) -> float:
        """ Method returning an end angle of an arc instance in degrees

        :return: end angle of an arc in degrees
        """
        return self.get_start_angle() + self.theta

    def copy(self) -> "Arc":
        """ Method returning a copy of a current Arc instance

        :return: a copy of a Arc instance
        """
        return Arc(self.p_start, self.p_center, self.theta)

    @staticmethod
    def describe_ellipse_arc(x_center=0.0, y_center=0.0, a=1.0, b=1.0, start_angle=0.0, end_angle=2 * np.pi, N=100,
                             closed=False):
        """ Function creating a string description of an arc for plotly library.

        :param x_center: x-coordinate of a center of an arc
        :param y_center: y-coordinate of a center of an arc
        :param a: semi-major axes
        :param b: semi-minor axes
        :param start_angle: start angle
        :param end_angle: stop angle
        :param N: number of segments
        :param closed: True if an arc is closed, False otherwise
        :return: string representation of an arc composed of a given number of segments
        """
        t = np.linspace(start_angle, end_angle, num=N)
        x = x_center + a * np.cos(t)
        y = y_center + b * np.sin(t)
        path = f'M {x[0]}, {y[0]}'
        for k in range(1, len(t)):
            path += f'L{x[k]}, {y[k]}'
        if closed:
            path += ' Z'
        return path
