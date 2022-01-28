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

# From PyPI
from google.protobuf.json_format import MessageToDict
import json

# Project
import obplib.OBP_pb2 as OBP
from obplib.Point import Point
from obplib.Beamparameters import Beamparameters


class AcceleratingCurve:
    """
        Constructor for the accelerating curve class

        Args:
            P1 (Point): The starting point
            P2 (Point): First control point
            P3 (Point): Second control point
            P4 (Point): End point
            speed (Int): Scan speed in µm/s
            bp (Beamparamters): Desired beam parameters
    """
    def __init__(self, P1, P2, P3, P4, si, sf, bp):
        self.P1 = P1
        self.P2 = P2
        self.P3 = P3
        self.P4 = P4
        self.si = si
        self.sf = sf
        self.bp = bp

    @classmethod
    def from_dict(cls, kw):
        """
        Recrates an instance of the accelerating curve class using a dictionary representation of said class. Assumes that that the given dictionary is in standard JSON structure.

        Args:
            kw: A dictionary representation of an accelerating curve
        Returns:
            cls: An instance of AcceleratingCurve recreated using kw
        """
        P1 = Point(kw["p0"]["x"], kw["p0"]["y"])
        P2 = Point(kw["p1"]["x"], kw["p1"]["y"])
        P3 = Point(kw["p2"]["x"], kw["p2"]["y"])
        P4 = Point(kw["p3"]["x"], kw["p3"]["y"])
        si = kw["si"]
        sf = kw["sf"]
        bp = Beamparameters(kw["params"]["spotSize"], kw["params"]["beamPower"])
        return cls(P1, P2, P3, P4, si, sf, bp)

    def get_pb(self):
        """
        Returns a protobuf packet containing curve information

        Returns:
            packet (binary): A protobuf packet containing curve information
        """

        pkt = OBP.Packet()
        accCurve = OBP.AcceleratingCurve()

        accCurve.params.CopyFrom(self.bp.get_pb())
        
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

        accCurve.p0.CopyFrom(cp0)
        accCurve.p1.CopyFrom(cp1)
        accCurve.p2.CopyFrom(cp2)
        accCurve.p3.CopyFrom(cp3)

        accCurve.si = int(self.si)
        accCurve.sf = int(self.sf)

        pkt.accelerating_curve.CopyFrom(accCurve)

        return pkt

    def get_packet(self, pkt):
        """
        Returns a serialize packet

        Args:
            packet (binary): A packet

        Returns:
            A serialized packet (String): A serialized packet
        """

        return pkt.SerializeToString()

    def write_obp(self):
        """
        Overloaded writer method - is called by the FileHandler when writing to obp

        Returns:
            serialized (binary): A serialized protobuf packet
        """
        return self.get_packet(self.get_pb())

    def get_obpj(self):
        """
        Overloaded writer method - is called by the FileHandler when writing to obpj

        Returns:
            d (dictionary): A dictionary representation of a protobuf packet
        """
        return MessageToDict(self.get_pb())
    
    def __repr__(self):
        return json.dumps(self.get_obpj(), indent=2) 

    def translate(self, v):
        """
        Returns a new AcceleratingCurve object which has been translated according to the given vector V

        Args:
            V (Vector): A translation vector

        Returns:
            AcceleratingCurve: An AcceleratingCurve which has been traslated according to the given vector
        """
        return AcceleratingCurve(
            self.P1.translate(v), 
            self.P2.translate(v), 
            self.P3.translate(v), 
            self.P4.translate(v), 
            self.si, self.sf, self.bp)

    def rotate(self, theta):
        """
        Returns a new AcceleratingCurve which has been rotated theta radians around the origin

        Args:
            theta (radians): The amount of radians which the AcceleratingCurve is to be rotated

        Returns:
            AcceleratingCurve: An AcceleratingCurve rotated theta radians relative to the origin
        """
        return AcceleratingCurve(
            self.P1.rotate(theta), 
            self.P2.rotate(theta), 
            self.P3.rotate(theta), 
            self.P4.rotate(theta), 
            self.si, self.sf, self.bp)

    def scale(self, factor):
        """
        Returns a new AcceleratingCurve scaled by the specified factor.

        Args:
            factor (float): The factor with which to scale the AcceleratingCurve

        Returns:
            AcceleratingCurve: An AcceleratingCurve scaled using the specified factor
        """
        return AcceleratingCurve(
            self.P1.scale(factor),
            self.P2.scale(factor),
            self.P3.scale(factor),
            self.P4.scale(factor),
            self.si, self.sf, self.bp)

