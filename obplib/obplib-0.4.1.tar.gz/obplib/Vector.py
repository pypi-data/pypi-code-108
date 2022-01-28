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


"""@Vector docstring

A class representing a 2 or 3-dimensional vector. The constructor default to 2D if not z-coordinate is given.
"""


class Vector:
    def __init__(self, x, y, z=None):
        """
        Constructor for the Vector class

        Args:
            x (Int): x-coordinate
            y (Int): y-coordinate
            z (Int, optional): z-coordinate. Defaults to None.
        """
        self.X = x
        self.Y = y
        self.Z = z

    def get_x(self):
        return self.X

    def get_y(self):
        return self.Y

    def get_z(self):
        return self.Z

    def add(self, V):
        """
        Adds two vectors and returns as new vector which elements are the element-wise sum of the two others

        Args:
            V (Vector): A 2 or 3-dimensional vector

        Returns:
            Vector: A vector which elements are the element-wise sum of the two others
        """
        return Vector(self.get_x() + V.get_x(), self.get_y() + V.get_y(), self.get_z() + V.get_Z())

    def subtract(self, V):
        """
        Subtracts two vectors and returns as new vector which elements are the element-wise difference of the two others

        Args:
            V (Vector): A 2 or 3-dimensional vector

        Returns:
            Vector: A vector which elements are the element-wise difference of the two others
        """
        return Vector(self.get_x() - V.get_x(), self.get_y() - V.get_y(), self.get_z() - V.get_z())

    def dot_prod(self, V):
        """
        Returns the dot product of two vectors

        Args:
            V (Vector): A 2 or 3-dimensional vector

        Returns:
            int: The dot product of two vectors
        """
        return self.get_x() * V.get_x() + self.get_y() * V.get_y() + self.get_z() * V.get_z()
