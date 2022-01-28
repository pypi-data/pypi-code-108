# SPDX-FileCopyrightText: 2019,2020 Freemelt AB
#
# SPDX-License-Identifier: Apache-2.0

# Built-in
import math
import logging

# Freemelt
from ..Line import Line
from ..Curve import Curve
from ..TimedPoints import TimedPoints
from ..Point import Point
from ..Beamparameters import Beamparameters



log = logging.getLogger(__name__)

def create_segment(t, element, width, height):

    xscale = 100000/width
    yscale = 100000/height
    xoffset = -width/2
    yoffset = -height/2

    def conv_x(x):
        return float((x + xoffset)*xscale)

    def conv_y(y):
        return float((y + yoffset)*yscale)

    if t == 'Line':
        p1 = Point(conv_x(element.start.real), conv_y(element.start.imag))
        p2 = Point(conv_x(element.end.real), conv_y(element.end.imag))
        l = Line(p1,p2, 100000, Beamparameters(100,100))
    elif t == 'Curve':
        p1 = Point(conv_x(element.start.real), conv_y(element.start.imag))
        p2 = Point(conv_x(element.control1.real), conv_y(element.control1.imag))
        p3 = Point(conv_x(element.control2.real), conv_y(element.control2.imag))
        p4 = Point(conv_x(element.end.real), conv_y(element.end.imag))
        l = Curve(p1,p2,p3,p4, 100000, Beamparameters(100,100))
    return l

#Work in progress
def validate_segment(seg):
    if isinstance(seg, Line):
        length = math.sqrt(math.pow(seg.P2.X - seg.P1.X, 2) + math.pow(seg.P2.Y - seg.P1.Y, 2))
        if length > 100000:
            log.warning("Max length of line exceeded")
        elif seg.Speed == 0:
            log.warning("One or more lines has a speed of 0")
    if isinstance(seg, Curve):
        length = math.sqrt(math.pow(seg.P4.X - seg.P1.X, 2) + math.pow(seg.P4.Y - seg.P1.Y, 2))
        if length > 100000:
            log.warning("Curve segment longer than 10cm")
        elif seg.speed == 0:
            log.warning("One or more curves has a speed of 0")
    if isinstance(seg, TimedPoints):
        for point in seg.points:
            if point.X or point.Y > 100000:
                log.warning("A point is located outside of the build area")

