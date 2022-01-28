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

"""@AcceleratingLine docstring
A class describing a straigh line drawn between points p1 and p2, with initial speed v0 and final speed v1.
"""

# PyPI
from google.protobuf.json_format import MessageToDict
import json

# Project
import obplib.OBP_pb2 as OBP
from obplib.Point import Point
from obplib.Beamparameters import Beamparameters


class AcceleratingLine:
    def __init__(self, p1, p2, si, sf, bp):
        """
        Constructor for the AcceleratingLine class

        Args:
            p1 (Point): The start point
            p2 (Point): The end point
            v0 (Int): Initial speed in µm/s
            v1 (Int): Final speed in µm/s
            bp (Beamparameters): Beam parameters
        """
        self.si = si
        self.sf = sf
        self.p1 = p1
        self.p2 = p2
        self.bp = bp

    @classmethod
    def from_dict(cls, kw):
        """
        Returns an instance of the AcceleratingLine class created using parameters specified in a dictionary

        Args:
            kw (dictionary): A dictionary representation of an AcceleratingLine object
        """
        v0 = kw["si"]
        v1 = kw["sf"]
        p0 = Point(kw["x0"], kw["y0"])
        p1 = Point(kw["x1"], kw["y1"])
        bp = Beamparameters(kw["params"]["spotSize"], kw["params"]["beamPower"])
        return cls(p0, p1, v0, v1, bp)

    def get_pb(self):
        """
        Returns a protobuf packet containing AcceleratingLine information

        Returns:
            Protobuf packet: A packet containing AccelerationLine info
        """
        pkt = OBP.Packet()
        acc_line = OBP.AcceleratingLine()

        acc_line.params.CopyFrom(self.bp.get_pb())

        acc_line.x0 = self.p1.get_x()
        acc_line.y0 = self.p1.get_y()
        acc_line.x1 = self.p2.get_x()
        acc_line.y1 = self.p2.get_y()

        acc_line.si = int(self.si)
        acc_line.sf = int(self.sf)

        pkt.accelerating_line.CopyFrom(acc_line)

        return pkt

    def get_packet(self, pkt):
        """
        Returns a serialized packet
        Args:
            pkt (binary): A packet

        Returns:
            A serialized packet (String): A serialized packet
        """
        return pkt.SerializeToString()

    def write_obp(self):
        return self.get_packet(self.get_pb())

    def get_obpj(self):
        """
        Overloaded writer method - is used by the FileHandler

        Returns:
            d (dictionary): A dictionary representation of a protobuf packet
        """
        return MessageToDict(self.get_pb())

    def __repr__(self):
        return json.dumps(self.get_obpj(), indent=2) 

    def translate(self, V):
        """
        Returns a new AcceleratomgLine object which has been translated according to the given vector V

        Args:
            V (Vector): A translation vector

        Returns:
            AcceleratingLine: An AcceleratingLine which has been traslated according to the given vector
        """
        return AcceleratingLine(
            self.p1.translate(V),
            self.p2.translate(V),
            self.si, self.sf, self.bp)

    def rotate(self, theta):
        """
        Returns a new AcceleratingLine which has been rotated theta radians around the origin

        Args:
            theta (radians): The amount of radians which the AccelerartingLine is to be rotated

        Returns:
            AcceleratingLine: An AcceleratingLine rotated theta radians relative to the origin
        """
        return AcceleratingLine(
            self.p1.rotate(theta),
            self.p2.rotate(theta),
            self.si, self.sf, self.bp
        )

    def scale(self, factor):
        """
        Returns a new AcceleratingLine scaled by the specified factor.

        Args:
            factor (float): The factor with which to scale the AcceleratingLine

        Returns:
            AcceleratingLine: An AcceleratingLine scaled using the specified factor
        """
        return AcceleratingLine(
            self.p1.scale(factor),
            self.p2.scale(factor),
            self.si, self.sf, self.bp
        )
