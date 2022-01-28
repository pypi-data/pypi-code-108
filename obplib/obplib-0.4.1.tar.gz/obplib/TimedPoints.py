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

"""@TimedPoints docstring
A class containing a list of coordinate points, each with its own associated dwell time
"""

# PyPI
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message

import json

# Project
import obplib.OBP_pb2 as OBP
from obplib.Point import Point
from obplib.Beamparameters import Beamparameters
from obplib.PathSegment import PathSegment


class TimedPoints(PathSegment):
    def __init__(self, points, dwellTimes, bp):
        """
        Constructor for the TimedPoints class

        Args:
            points (list): A list of coordinate points
            dwellTimes (list): A list of dwell times
            bp (Beamparamters): Beam parameters

        Raises:
            Exception: Raised if points and dwellTimes are not of the same length
        """
        super().__init__()
        self.points = points
        self.dwellTimes = dwellTimes
        self.bp = bp
        if len(points) != len(dwellTimes):
            raise Exception("points and dwellTimes must be of the same length")

    @classmethod
    def from_dict(cls, kw):
        """
        Returns an instance of the TimedPoints class created using parameters specified in a dictionary

        Args:
            kw (dictionary): A dictionary representation of a TimedPoints object
        """
        points = kw["points"]
        p = []
        t = []
        for d in points:
            p.append(Point(d["x"], d["y"]))
            t.append(d["t"])
        bp = Beamparameters(kw["params"]["spotSize"], kw["params"]["beamPower"])
        return cls(p, t, bp)

    def get_packet(self, packet) -> bytes:
        """
        Returns a serialized string representation of a packet

        Args:
            packet (binary): A protobuf packet
        Returns:
            A serizalied packet (String): A serialized packet
        """
        pkt = packet.SerializeToString()
        return pkt

    def get_pb(self) -> Message:
        """
        Returns a protobuf packet containing TimedPoint information

        Returns:
           pkt (binary): A protobuf packet
        """
        pkt = OBP.Packet()
        timedPoints = OBP.TimedPoints()
        t = []
        timedPoints.params.CopyFrom(self.bp.get_pb())

        lastDwell = 0
        for i in range(len(self.points)):
            timedPoint = OBP.TimedPoints.TimedPoint()
            if self.dwellTimes[i] != lastDwell:

                lastDwell = self.dwellTimes[i]
                timedPoint.t = self.dwellTimes[i]
            p = Point(self.points[i].x, self.points[i].y)
            timedPoint.x = p.x
            timedPoint.y = p.y
            t.append(timedPoint)
            timedPoints.points.extend(t)
            t.clear()

        pkt.timed_points.CopyFrom(timedPoints)

        return pkt

    def write_obp(self) -> bytes:
        return self.get_packet(self.get_pb())

    def get_obpj(self) -> dict:
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
        Returns a TimedPoints object containing a list of points translated according to the given vector V

        Args:
            V (Vector): A translation vector

        Returns:
            TimedPoints: A TimedPoints object with a list of points which have been translated according to the given vector
        """
        pointlist = []
        dwell = []

        for i in range(0, len(self.points)):
            pointlist.append(self.points[i].translate(V))
            dwell.append(self.dwellTimes[i])

        return TimedPoints(pointlist, dwell, self.bp)

    def rotate(self, theta):
        """
        Returns a new TimedPoints object containing a list of points which have been rotated theta radians relative to the origin

        Args:
            theta (radians): The amount of radians which the points are to be rotated

        Returns:
            TimedPoints: A TimedPoints object containing a list of points that have been rotated theta radians relative to the origin

        """
        pointlist = []
        dwell = []

        for i in range(0, len(self.points)):
            pointlist.append(self.points[i].rotate(theta))
            dwell.append(self.dwellTimes[i])

        return TimedPoints(pointlist, dwell, self.bp)

    def scale(self, factor):
        """
        Returns a new TimedPoints object containing a list of points that have been scaled by the specified factor.

        Args:
            factor (float): The factor with which to scale the list of points

        Returns:
            Curve: A TimedPoints object containing a list of points scaled using the specified factor
        """

        pointlist = []
        dwell = []

        for i in range(0, len(self.points)):
            pointlist.append(self.points[i].scale(factor))
            dwell.append(self.dwellTimes[i])

        return TimedPoints(pointlist, dwell, self.bp)

    def get_segment_length(self) -> float:
        return 0

    def get_segment_duration(self) -> float:
        return sum(self.dwellTimes)


