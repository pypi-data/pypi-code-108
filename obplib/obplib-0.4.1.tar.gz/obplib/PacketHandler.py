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

"""@file
pktHandler docstring

A collection of methods used when handling protocol buffer pkts
"""

# Project
from obplib.Line import Line
from obplib.Point import Point
from obplib.TimedPoints import TimedPoints
from obplib.Beamparameters import Beamparameters
from obplib.Curve import Curve
from obplib.AcceleratingLine import AcceleratingLine
from obplib.AcceleratingCurve import AcceleratingCurve
from obplib.SyncPoint import SyncPoint


def handle_line(pkt):
    """
    Handles pkts containing line objects

    Args:
        pkt (protobuf): A protobuf pkt
    Returns:
        l (Line): A OBP line object
    """
    p1 = Point(pkt.line.x0, pkt.line.y0)
    p2 = Point(pkt.line.x1, pkt.line.y1)
    bp = pkt.line.params
    bp1 = Beamparameters(bp.spot_size, bp.beam_power)
    speed = pkt.line.speed
    l = Line(p1, p2, speed, bp1)
    return l


def handle_timed_points(pkt):
    """
    Handles pkts containing Timed Points objects

    Args:
        pkt (protobuf): A protobuf pkt
    Returns:
        tp (TimedPoints): A OBP TimedPoints object
    """
    points = pkt.timed_points.points
    dwellTimes = []

    for i in range(len(points)):
        dwellTimes.append(points[i].t)

    bp = pkt.timed_points.params
    bp1 = Beamparameters(bp.spot_size, bp.beam_power)
    tp = TimedPoints(points, dwellTimes, bp1)
    return tp


def handle_curve(pkt):
    """
    Handles pkts containing Curve objects

    Args:
        pkt (protobuf): A protobuf pkt
    Returns:
        c (Curve): A OBP Curve object
    """
    p0 = Point(pkt.curve.p0.x, pkt.curve.p0.y)
    p1 = Point(pkt.curve.p1.x, pkt.curve.p1.y)
    p2 = Point(pkt.curve.p2.x, pkt.curve.p2.y)
    p3 = Point(pkt.curve.p3.x, pkt.curve.p3.y)
    speed = pkt.curve.speed
    bp = pkt.curve.params
    bp1 = Beamparameters(bp.spot_size, bp.beam_power)

    
    return Curve(p0, p1, p2, p3, speed, bp1)


def handle_accelerating_line(pkt):
    """
    Handles pkts containing Accelerating Line objects

    Args:
        pkt (protobuf): A protobuf pkt
    Returns:
        AcceleratingLine (Accelerating line): An accelerating line
    """
    p1 = Point(pkt.accelerating_line.x0, pkt.accelerating_line.y0)
    p2 = Point(pkt.accelerating_line.x1, pkt.accelerating_line.y1)
    v0 = pkt.accelerating_line.si
    v1 = pkt.accelerating_line.sf
    bp = Beamparameters(
        pkt.accelerating_line.params.spot_size,
        pkt.accelerating_line.params.beam_power,
    )
    return AcceleratingLine(p1, p2, v0, v1, bp)

def handle_sync_point(pkt):
    """
    Handles pkts containing sync point information

    Args:
        pkt (protobuf): A protobuf pkt
    Returns:
        SyncPoint (Sync point): A SyncPoint object
    """
    endpoint = pkt.sync_point.endpoint
    value = pkt.sync_point.value
    duration = pkt.sync_point.duration

    return SyncPoint(endpoint, value, duration)

def handle_accelerating_curve(pkt):
    """
    Handles pkts containing accelerating curves

    Args:
        pkt (protobuf): A protobuf pkt
    Returns:
        AcceleratingCurve (accelerating curve): A AcceleratingCurve object
    """
    p1 = Point(pkt.accelerating_curve.p0.x, pkt.accelerating_curve.p0.y)
    p2 = Point(pkt.accelerating_curve.p1.x, pkt.accelerating_curve.p1.y)
    p3 = Point(pkt.accelerating_curve.p2.x, pkt.accelerating_curve.p2.y)
    p4 = Point(pkt.accelerating_curve.p3.x, pkt.accelerating_curve.p3.y)

    si = pkt.accelerating_curve.si
    sf = pkt.accelerating_curve.sf
    
    bp = Beamparameters(pkt.accelerating_curve.params.spotSize, pkt.accelerating_curve.params.power)

    return AcceleratingCurve(p1, p2, p3, p4, si, sf, bp)

def handle_pkt(pkt):
    """
    This methods is responsible for the delegation of pkt handling
    dependent upon the contents of said pkt

    Args:
        pkt (protobuf): A protobuf pkt

    Returns:
        A pkt handler: Delegated pkt handler
    """
    if pkt.HasField("line"):
        return handle_line(pkt)
    elif pkt.HasField("timed_points"):
        return handle_timed_points(pkt)
    elif pkt.HasField("curve"):
        return handle_curve(pkt)
    elif pkt.HasField("accelerating_line"):
        return handle_accelerating_line(pkt)
    elif pkt.HasField("accelerating_curve"):
        return handle_accelerating_curve(pkt)
    elif pkt.HasField("sync_point"):
        return handle_sync_point(pkt)
    else:
        print(pkt)
        raise Exception("Unknown pkt recieved")
