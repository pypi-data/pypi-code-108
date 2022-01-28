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

"""@Beamparameters docstring

This class represents parameters associated with a given beam segment.
"""

# Project
import obplib.OBP_pb2 as OBP


class Beamparameters:
    def __init__(self, spot_size, power):
        """
        Constructor for the Beamparameters class

        Args:
            spotSize (Int): Desired spot size in µm
            power (Int): Desired beam power in W
        """
        self.spot_size = spot_size
        self.power = power

    def get_pb(self):
        """
        Returns a protobuf packet containing the specified beam paramters

        Returns:
           Beamparameters packet (binary): A packet containing beam parameter information
        """
        pkt = OBP.BeamParameters()
        pkt.beam_power = self.power
        pkt.spot_size = self.spot_size
        return pkt
