#!/usr/bin/env python3

from .Lines import *

class Station(object):
    _Station__stations = []

    @classmethod
    def registerStation(cls, station):
        if station not in cls.__stations:
            cls.__stations.append(station)

    @classmethod
    def getAllStations(cls):
        return cls.__stations

    @classmethod
    def getStationByName(cls, name):
        for s in cls.__stations:
            if s.name == name:
                return s
        raise ValueError(f"No station with name '{name}'.")

    def __init__(self, name, id, physical_ids, lines):
        self.name = name
        self.id = id
        self.physical_ids = physical_ids
        self.lines = lines
        Station.registerStation(self)

    def getPhysicalId(self, direction, line):
        if direction not in [1, 2]:
            raise ValueError(f"Expected direction to be either 1 or 2, got '{direction}'.")
        if line not in self.lines:
            raise ValueError(f"Line '{line.name}' does not have this station.")
        index = self.lines.index(line)
        return self.physical_ids[index][direction - 1]

    def __repr__(self):
        return f"<Station: {self.name}>"

# TODO: Add all missing stations with the right lines mapping 
EUROPE = Station("europe", 209, ((100769, 100770), (100771, 100772)), (METRO, _6))
