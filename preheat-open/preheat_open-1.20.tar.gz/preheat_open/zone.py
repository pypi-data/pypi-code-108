from __future__ import annotations

from typing import List, Tuple

from .building_unit import BaseBuildingUnit


def populate_zones(zones_data, parent_zone=None):
    zones = []
    # Loop over zones; create and populate Zone instances
    for zone_i in zones_data:
        zones.append(Zone(zone_i, parent_zone=parent_zone))

    return zones


class Zone(object):
    """Defines a building zone in the PreHEAT sense"""

    def __init__(self, zone_data, parent_zone=None):
        # Identifier of the zone
        self.id = zone_data.pop("id")
        # Name of the zone
        self.name = zone_data.pop("name", str(self.id))
        # Floor area of the zone
        self.area = zone_data.pop("zoneArea", None)
        # Whether zone has an external wall (boolean)
        self.has_external_wall = zone_data.pop("hasExternalWall", None)
        # Sub-zones of the zone (list of PreHEAT_API.Zones)
        self.sub_zones = populate_zones(zone_data.pop("subZones", []), parent_zone=self)
        # Adjacency
        self.adjacent_zones = [
            z["zoneId"] for z in zone_data.pop("adjacentZones", None)
        ]
        # Type of the zone
        self._type = zone_data.pop("type")

        # Parent zone
        self.__parent = parent_zone

        # Adding coupled units
        self.__coupled_units = dict()

    def get_sub_zones(self, zone_ids=None) -> List[Zone]:
        if zone_ids is None:
            res = self.sub_zones
        else:
            res = []
            for z_i in self.sub_zones:
                if z_i.id in zone_ids:
                    res.append(z_i)
                res += z_i.get_sub_zones(zone_ids=zone_ids)
        return res

    def get_parent_zone(self) -> Zone:
        return self.__parent

    def get_type(self) -> Tuple[str, str]:
        """
        Returns the type of the zone ('room', 'stairway', 'corridor', 'bathroom', 'kitchen')
        and its 'dryness' ('dry', 'wet', '?')

        :return: zone_type, wet_or_dry
        """
        zone_type = self._type.lower()
        if zone_type in ["room", "stairway", "corridor"]:
            wet_or_dry = "dry"
        elif zone_type in ["bathroom", "kitchen"]:
            wet_or_dry = "wet"
        else:
            wet_or_dry = "?"
        return zone_type, wet_or_dry

    def __repr__(self):
        return "{0}({1})".format(type(self).__name__, self.name)

    def add_coupled_unit(self, unit) -> None:
        unit_type = unit.unit_type
        if unit_type in self.__coupled_units.keys():
            if unit.id in [u_i.id for u_i in self.__coupled_units[unit_type]]:
                pass  # Skip addition of already existing units
            else:
                self.__coupled_units[unit_type].append(unit)
        else:
            self.__coupled_units[unit_type] = [unit]

    def get_units(self, unit_type, sub_zones=True) -> List[BaseBuildingUnit]:
        """
        Returns the coupled units of a given type

        :param unit_type: str
        :param sub_zones: bool (True)
        :return: list(BuildingUnit) or None
        """
        us = self.__coupled_units.get(unit_type)
        if sub_zones is True:
            for z_i in self.sub_zones:
                us_i = z_i.get_units(unit_type, sub_zones=True)
                if us_i is not None:
                    if us is None:
                        us = us_i
                    else:
                        us += us_i
        return us
