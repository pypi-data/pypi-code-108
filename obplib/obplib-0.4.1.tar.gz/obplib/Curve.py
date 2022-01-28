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

"""@Curve docstring
A class which describes a cubic bezier curve corresponding to a given speed and given parameters.
The curve starts at P1, aims at P2 and ends at P4, via P3.
"""

# PyPI
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message
import math


import json


# Project
import obplib.OBP_pb2 as OBP
from obplib.Beamparameters import Beamparameters
from obplib.Point import Point
from obplib.PathSegment import PathSegment


class Curve(PathSegment):
    def __init__(self, P1, P2, P3, P4, speed, bp):
        """

        Constructor for the Curve class

        Args:
           P1 (Point): The starting point
           P2 (Point): First control point
           P3 (Point): Second control point
           P4 (Point): End point
           speed (Int): Scan speed in µm/s
           bp (Beamparamters): Desired beam parameters
        """
        super().__init__()
        self.P1 = P1
        self.P2 = P2
        self.P3 = P3
        self.P4 = P4
        self.speed = speed
        self.bp = bp

    @classmethod
    def from_dict(cls, kw):
        """
        Returns an instance of the Curve class created using parameters specified in a dictionary

        Args:
            kw (dictionary): A dictionary representation of a Curve object
        """
        P1 = Point(kw["p0"]["x"], kw["p0"]["y"])
        P2 = Point(kw["p1"]["x"], kw["p1"]["y"])
        P3 = Point(kw["p2"]["x"], kw["p2"]["y"])
        P4 = Point(kw["p3"]["x"], kw["p3"]["y"])
        bp = Beamparameters(kw["params"]["spotSize"], kw["params"]["beamPower"])
        speed = int(kw["speed"])
        return cls(P1, P2, P3, P4, speed, bp)

    def get_pb(self) -> Message:
        """
        Returns a protobuf packet containing curve information

        Returns:
            pkt (binary): A protobuf packet containing curve information
        """
        pkt = OBP.Packet()
        curve = OBP.Curve()

        curve.speed = self.speed
        curve.params.CopyFrom(self.bp.get_pb())

        cp0 = OBP.Curve.Point()
        cp1 = OBP.Curve.Point()
        cp2 = OBP.Curve.Point()
        cp3 = OBP.Curve.Point()

        cp0.x = self.P1.get_x()
        cp0.y = self.P1.get_y()

        cp1.x = self.P2.get_x()
        cp1.y = self.P2.get_y()

        cp2.x = self.P3.get_x()
        cp2.y = self.P3.get_y()

        cp3.x = self.P4.get_x()
        cp3.y = self.P4.get_y()

        curve.p0.CopyFrom(cp0)
        curve.p1.CopyFrom(cp1)
        curve.p2.CopyFrom(cp2)
        curve.p3.CopyFrom(cp3)

        pkt.curve.CopyFrom(curve)

        return pkt

    def get_packet(self, packet) -> bytes:
        """
        Returns a serialized packet
        Args:
            packet (binary): A packet

        Returns:
            A serialized packet (String): A serialized packet
        """
        pkt = packet.SerializeToString()
        return pkt

    def write_obp(self) -> bytes:
        return self.get_packet(self.get_pb())

    def get_obpj(self) -> dict:
        """
        Overloaded writer method - is used by the FileHandler

        Returns:
             (dictionary): A dictionary representation of a protobuf packet
        """
        return MessageToDict(self.get_pb())

    def __repr__(self):
        return json.dumps(self.get_obpj(), indent=2) 

    def translate(self, V):
        """
        Returns a new curve that has been translated using the translation vector V

        Args:
            V (Vector): A translation vector

        Returns:
            Curve: A curve that has been translate according to the given vector
        """
        return Curve(
            self.P1.translate(V),
            self.P2.translate(V),
            self.P3.translate(V),
            self.P4.translate(V),
            self.speed,
            self.bp
        )

    def rotate(self, theta):
        """
        Returns a new Curve which has been rotated theta radians around the origin

        Args:
            theta (radians): The amount of radians which the curve is to be rotated

        Returns:
            Curve: A curve rotated theta radians relative to the origin
        """
        return Curve(
            self.P1.rotate(theta),
            self.P2.rotate(theta),
            self.P3.rotate(theta),
            self.P4.rotate(theta),
            self.speed,
            self.bp
        )

    def scale(self, factor):
        """
        Returns a new Curve scaled by the specified factor.

        Args:
            factor (float): The factor with which to scale the Curve

        Returns:
            Curve: A curve scaled using the specified factor
        """
        return Curve(
            self.P1.scale(factor),
            self.P2.scale(factor),
            self.P3.scale(factor),
            self.P4.scale(factor),
            self.speed,
            self.bp
        )
    
    def _bez(self, p0, p1, p2, p3, tc):
        t2 = tc * tc
        t3 = t2 * tc
        
        mt = 1-tc
        mt2 = mt * mt
        mt3 = mt2 * mt

        return p0*mt3 + 3*p1*mt2*tc + 3*p2*mt*t2 + p3*t3

    def arc_length_approximation(self):
        dist = 0
        curr_x = self.P1.get_x()
        curr_y = self.P1.get_y()
        approximation_steps = 32
        for i in range(approximation_steps):
            x = self._bez(self.P1.get_x(), self.P2.get_x(), self.P3.get_x(), self.P4.get_x(), i/approximation_steps)
            y = self._bez(self.P1.get_y(), self.P2.get_y(), self.P3.get_y(), self.P4.get_y(), i/approximation_steps)

            part_dist = math.sqrt(math.pow(curr_x - x, 2) + math.pow(curr_y - y, 2))

            dist = part_dist + dist
            curr_x = x
            curr_y = y

        return dist

    def get_segment_length(self) -> float:
        return self.arc_length_approximation()

    def get_segment_duration(self) -> float:
        return self.get_segment_length()/self.speed

