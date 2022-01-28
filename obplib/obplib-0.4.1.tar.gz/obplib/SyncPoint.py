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


"""@SyncPoint docstring

    This class represents a digital output signal with a given name, a value(True/False), and a duration(ms).

"""

# PyPI
from google.protobuf.json_format import MessageToDict
import json

# Project
import obplib.OBP_pb2 as OBP


class SyncPoint:
    def __init__(self, endpoint, value, duration):
        """
        SyncPoint constructor

        Args:
            endpoint (String): The name to be used for the signal
            value (bool): The value of the signal
            duration (int): duration of the signal in milliseconds, this is the time during which the syncpoint will keep its given value. 0 = keep until reset.
        """
        self.endpoint = endpoint
        self.value = value
        self.duration = duration

    @classmethod
    def from_dict(cls, kw):
        """
        Recrates an instance of the SyncPoint class using a dictionary representation of said class. Assumes that that the given dictionary is in standard JSON structure.

        Args:
            kw: A dictionary representation of a SyncPoint
        Returns:
            cls: An instance of SyncPoint recreated using kw
        """
        endpoint = kw["endpoint"]
        value = kw["value"]
        duration = kw["duration"]

        return cls(endpoint, value, duration)

    def get_pb(self):
        """
        Returns a protobuf packet containing SyncPoint information

        Returns:
            Protobuf packet: A packet containing SyncPoint information
        """
        pkt = OBP.Packet()
        sp = OBP.SyncPoint()

        sp.endpoint = self.endpoint
        sp.value = self.value
        sp.duration = self.duration

        pkt.sync_point.CopyFrom(sp)
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
        d = MessageToDict(self.get_pb())
        return d

    def __repr__(self):
        return json.dumps(self.get_obpj(), indent=2) 

    def translate(self, V):
        pass

    def rotate(self, theta):
        pass

    def scale(self, factor):
        pass
