# SPDX-FileCopyrightText: 2019,2020 Freemelt AB
#
# SPDX-License-Identifier: Apache-2.0

"""
Copyright 2019,2020 Freemelt AB

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


"""@Point docstring

A class representing a point on a 2D grid with coordinates (x,y)
"""


# Built-in
import math

class Point:
    def __init__(self, x, y):
        """
        Contructor for the point class

        Args:
            x (Int): The x-coordinate for the point
            y (Int): The y-coordinate for the point
        """
        self.x = x
        self.y = y

    def get_x(self):
        """
        Coordinate getter method

        Returns:
            x (Int): the x-coordinate of the specific point instance
        """
        return self.x

    def get_y(self):
        """
        Coordinate getter method

        Returns:
            y (Int): the y-coordinate of the specific point instance
        """
        return self.y

    def translate(self, V):
        """
        Returns a new point that has been translated according to the coordinates in the given vector V

        Args:
            V (Vector): A translation vector

        Returns:
            Point: A point that has been translated according to V
        """
        x1 = self.get_x() + V.get_x()
        y1 = self.get_y() + V.get_y()
        return Point(x1, y1)

    def rotate(self, theta):
        """
        Returns a new Point that has been rotated theta radians relative to the origin

        Args:
            theta (Int): Number of radians to rotate

        Returns:
            Point: A point that has been rotated theta degrees around the origin
        """
        x1 = self.get_x() * math.cos(theta) - self.get_y() * math.sin(theta)
        y1 = self.get_x() * math.sin(theta) + self.get_y() * math.cos(theta)
        return Point(x1, y1)

    def scale(self, c):
        """
        Returns a new point that has been scaled according to the constant scaling factor c

        Args:
            c (float): The scaling factor

        Returns:
            Point: A point which coordinates have been scaled by the given factor
        """
        x1 = self.get_x() * c
        y1 = self.get_y() * c
        return Point(x1, y1)

    def dist(self, p):
        """
        Returns the distance between two points in the 2D-space. Calculated using the Euclidean norm.

        Args:
            p (Point): A Point object

        Returns:
            float: The distance between two points
        """
        d = math.pow((p.get_x() - self.get_x()), 2) + math.pow((p.get_y() - self.get_y()), 2)
        return math.sqrt(d)