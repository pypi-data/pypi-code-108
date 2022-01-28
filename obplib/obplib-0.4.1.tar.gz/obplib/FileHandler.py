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
FileHandler docstring

A collection of methods that can be used to write serialized protobuf packets to the binary version of the OBP-format.
"""

# Built-in
import json

# PyPI
from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32

# Project
import obplib.PacketHandler as PacketHandler
import obplib.OBP_pb2 as OBP
from obplib.Line import Line
from obplib.Curve import Curve
from obplib.TimedPoints import TimedPoints
from obplib.AcceleratingCurve import AcceleratingCurve
from obplib.AcceleratingLine import AcceleratingLine
from obplib.SyncPoint import SyncPoint


def write(obpdata, filename):
    """
        Writes the given data to a file.

        Args:
            obpdata (list): A list of OBP objects such as Line, TimedPoints and Curve
            filename (stream): The file to be written to
    """
    for i in range(0, len(obpdata)):
        data = obpdata[i].write_obp()
        filename.write(_VarintBytes(len(data)))
        filename.write(data)


def write_obp(obpdata, filename):
    """
        Writes obpData to a OBP-file with the given file name by calling Write(obpData, stream), if it exists. Creates a file and with the given name if it does not exist.

        Args:
            obpData (list): A list of OBP objects such as Line, TimedPoints and Curve
            filename (String): The name of the file to be written to
    """
    with open(filename, "wb+") as out:
        write(obpdata, out)
        out.flush()


def write_obpj(obpdata, filename):
    """
        Writes obpData to a OBPJ-file with the specified file name, if it exists. Creates a file with the given name if it does not exist.
        Args:
            obpData (list): A list OBP objects such as Line, TimedPoints and Curve
            filename (String): Name of the file to be written to
    """
    with open(filename, "w+") as out:
        out.write('{\n"OBP":[\n')
        lastind = len(obpdata) - 1

        for i in range(len(obpdata)):
            data = obpdata[i].get_obpj()
            check_keys(data)
            json.dump(data, out, indent=4)
            if i < lastind:
                out.write(",\n")
        out.write("\n]\n}\n")
        out.flush()


def read_obp(filename):
    """
        Reads a OBP-file with the specified file name and returns a list containing all OBP objects found wihin the file.

        Args:
            filename (String): Name of the file to be read from
        Returns:
                l (list): A list of OBP objects
    """
    l = []
    with open(filename, "rb") as f:
        data = f.read()
        next_pos, pos = 0, 0
        while pos < len(data):
            p = OBP.Packet()
            next_pos, pos = _DecodeVarint32(data, pos)
            p.ParseFromString(data[pos : pos + next_pos])
            pos = pos + next_pos
            temp = PacketHandler.handle_pkt(p)
            l.append(temp)
    f.close()
    return l


def read_obpj(filename):
    """
        Reads a OBPJ-file with the specified file name and returns a dictionary representation of the file in question

        Args:
            filename (String): obpj-file to be read
    """
    with open(filename, "r") as f:
        data = json.load(f)
        return data


def get_segment_from_dict(filename):  
    """ 
        Method used by the compiler when reading obpj files. Reads a obpj file and returns a list of its constituent objects.

        Args:
            filename (String): obpj-file to be read
        Returns:
            l (list): A list of obp objects
    """
    l = []
    with open(filename, "r") as f:
        data = json.load(f)
        dicts = data["OBP"]
        for i in range(len(dicts)):
            k = dicts[i].keys()
            for key in k:
                if key == "line":
                    l.append(Line.from_dict(dicts[i][key]))
                if key == "curve":
                    l.append(Curve.from_dict(dicts[i][key]))
                if key == "timedPoints":
                    l.append(TimedPoints.from_dict(dicts[i][key]))
                if key == "acceleratingLine":
                    l.append(AcceleratingLine.from_dict(dicts[i][key]))
                if key == "acceleratingCurve":
                    l.append(AcceleratingCurve.from_dict(dicts[i][key]))
                if key == "syncPoint":
                    l.append(SyncPoint.from_dict(dicts[i][key]))
    f.close()
    return l


def check_keys(
    blob
):  
    """
        Checks that all keys are present before writing to obpj, used by both the compiler and the writer. Has to be done or else we won't be able
        to compile obpj files with default values. Checks each subdict in the file for missing keys and adds the key:value pair [key]:0 or [key]:False if it is not present.
        
        Needs refinement.

        Args:
            blob (dictionary): A dictionary
    """
    keys = ["x0", "y0", "x1", "y1"]
    for item in blob.keys():
        if item == "line" or item == "acceleratingLine":
            for key in keys:
                if key not in blob[item]:
                    blob[item][key] = 0

            if "beamPower" not in blob[item]["params"]:
                blob[item]["params"]["beamPower"] = 0
            if "spotSize" not in blob[item]["params"]:
                blob[item]["params"]["spotSize"] = 0

        if item == "timedPoints":  
            if "beamPower" not in blob[item]["params"]:
                blob[item]["params"]["beamPower"] = 0
            if "spotSize" not in blob[item]["params"]:
                blob[item]["params"]["spotSize"] = 0

            current = blob[item]["points"][0]["t"]
            for i in range(len(blob[item]["points"])):
                if "t" in blob[item]["points"][i]:
                    current = blob[item]["points"][i]["t"]
                elif "t" not in blob[item]["points"][i]:
                    blob[item]["points"][i]["t"] = current
                

        if item == "curve":
            points = ["p0", "p1", "p2", "p3"]
            for point in points:
                if "x" not in blob[item][point]:
                    blob[item][point]["x"] = 0
                if "y" not in blob[item][point]:
                    blob[item][point]["y"] = 0
            
            if "beamPower" not in blob[item]["params"]:
                blob[item]["params"]["beamPower"] = 0
            if "spotSize" not in blob[item]["params"]:
                blob[item]["params"]["spotSize"] = 0

