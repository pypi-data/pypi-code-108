from abc import ABC

import overpy

from pyridy.osm.utils import OSMRelation
from pyridy.utils.tools import generate_random_color


class OSMRailwayElement(ABC):
    def __init__(self, n: overpy.Node):
        """ Abstract Base Class for railway elements retrieved from OpenStreetMap

        Parameters
        ----------
        n: overpy.Node
            OpenStreetMap node queried by Overpy
        """
        self.n = n
        self.attributes = n.attributes
        self.tags = n.tags
        self.lat = float(n.lat)
        self.lon = float(n.lon)
        self.id = n.id

        if hasattr(n, "ways"):
            self.ways = n.ways
        else:
            self.ways = None

        self.__dict__.update(n.tags)  # Different elements contain different tags


class OSMLevelCrossing(OSMRailwayElement):
    def __init__(self, n: overpy.Node):
        """ Class representing railway level crossings

        See https://wiki.openstreetmap.org/wiki/Tag:railway%3Dlevel_crossing for more information on available tags

        Parameters
        ----------
        n: overpy.Node
            OpenStreetMap Node retrieved using Overpy
        """
        super(OSMLevelCrossing, self).__init__(n)

    def __repr__(self):
        return "Level Crossing at (%s, %s)" % (self.lon, self.lat)


class OSMRailwayMilestone(OSMRailwayElement):
    def __init__(self, n: overpy.Node):
        """ Class representing railway milestones (turnouts)

        Parameters
        ----------
        n: overpy.Node
            OpenStreetMap node retrieved using Overpy
        """
        super(OSMRailwayMilestone, self).__init__(n)
        self.position = float(n.tags.get("railway:position", "-1").replace(",", "."))

    def __repr__(self):
        return "Milestone at (%s, %s): %.3f" % (self.lon, self.lat, self.position)


class OSMRailwaySignal(OSMRailwayElement):
    def __init__(self, n: overpy.Node):
        """ Class representing railway signals

        See https://wiki.openstreetmap.org/wiki/Tag:railway%3Dsignal for more information on available tags

        Parameters
        ----------
        n: overpy.Node
            OpenStreetMap node retrieved using Overpy
        """
        super(OSMRailwaySignal, self).__init__(n)

    def __repr__(self):
        return "Signal at (%s, %s)" % (self.lon, self.lat)


class OSMRailwaySwitch(OSMRailwayElement):
    def __init__(self, n: overpy.Node):
        """ Class representing railway switches (turnouts)

        Parameters
        ----------
        n: overpy.Node
            OpenStreetMap node retrieved using Overpy
        """
        super(OSMRailwaySwitch, self).__init__(n)
        self.allowed_transits = []  # List of triples in form of (neighbor 1, switch id, neighbor 2)

    def __repr__(self):
        return "Switch at (%s, %s)" % (self.lon, self.lat)


class OSMRailwayLine(OSMRelation):
    def __init__(self, id: int, ways: list, tags: dict, members: list):
        """ Class representing a railway line

        See https://wiki.openstreetmap.org/wiki/Tag:railway%3Drail

        Parameters
        ----------
        id: int
            ID of the railway line
        ways: list
            List of ways of the railway line
        tags: dict
            Tags associated with the railway line
        members: list
            list of nodes and ways associated with the railway line
        """
        super().__init__(id=id, ways=ways, name=tags.get("name", ""),
                         color=tags.get("colour", generate_random_color("HEX")))
        self.__dict__.update(tags)
        self.members = members

    def __repr__(self):
        return self.__dict__.get("name", "")
