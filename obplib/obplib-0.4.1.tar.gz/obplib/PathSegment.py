# SPDX-FileCopyrightText: 2019,2020 Freemelt AB
#
# SPDX-License-Identifier: Apache-2.0

"""@PathSegment docstring
An abstract base class containing all methods that are common among the different path segments. Line, Curve, etc.
"""
#PyPI
from google.protobuf.message import Message

class PathSegment:

    def __init__(self):
        pass

    def get_segment_length(self) -> float:
        pass

    def get_segment_duration(self) -> float:
        pass

    def get_pb(self) -> Message:
        pass

    def get_packet(self) -> bytes:
        pass

    def write_obp(self) -> bytes:
        pass

    def get_obpj(self) -> dict:
        pass

