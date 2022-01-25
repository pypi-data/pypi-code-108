"""
This module defines the Building class, which represents buildings containing different units and their data
"""
import re
from typing import Dict, List, Optional, Union

import pandas as pd

from . import unit_graph
from .api import AccessDeniedError, api_get
from .building_unit import BaseBuildingUnit, populate_units
from .data import load_model_data
from .helpers import convenience_result_list_shortener, sanitise_datetime_input
from .price import SupplyPoint
from .weather import Weather
from .zone import Zone, populate_zones


class Building(object):
    """Building defines a building in the PreHEAT sense"""

    def __init__(self, location_id: int):
        self.location_id = location_id

        # Dict containing the details of the location
        self.location = {}
        # List of zones within the building (of class PreHEAT_API.Zone)
        self.zones = []
        # Dict w.units within the building (of class PreHEAT_API.Unit)
        self.units = {}
        # Dict w. weather information for the location (PreHEAT_API.Weather)
        self.weather = None  # type: Weather
        # Area of the building
        self.area = None
        # All characteristics get summarised in this dictionary
        # (duplicate with some attributes do to backwards-compatibility requirement)
        self.characteristics = {}

        # Supply points (for pricing)
        self.__supply_points = []

        # Load from API
        self.__populate()

        # Construct graph
        self.G = unit_graph.generate_unit_graph(self)

        # Traverse and map sub-unit references
        for node, data in self.G.nodes.data():
            # Add sub-units as new nodes
            if hasattr(data["unit"], "_related_sub_units_refs"):
                for ref in data["unit"]._related_sub_units_refs:
                    data["unit"].add_sub_unit(self.G.nodes[ref]["unit"])
            if hasattr(data["unit"], "_related_meters_refs"):
                for ref in data["unit"]._related_meters_refs:
                    data["unit"]._meters.append(self.G.nodes[ref]["unit"])

    def get_unit_graph(self):
        """

        :return:
        :rtype:
        """
        return self.G

    def load_data(
        self,
        start_date,
        end_date,
        time_resolution: str = "hour",
        components: Optional[Dict] = {},
    ) -> None:
        """

        :param start_date:
        :type start_date:
        :param end_date:
        :type end_date:
        :param time_resolution:
        :type time_resolution:
        :param components:
        :type components:
        :return:
        :rtype:
        """
        start_date = sanitise_datetime_input(start_date)
        end_date = sanitise_datetime_input(end_date)
        if components is None:
            components = {}

        if len(components) == 0:
            # Load all data on building, if nothing is specified
            self.weather.load_data(
                start_date, end_date, time_resolution, components.get("weather")
            )
            for node, data in self.G.nodes.data():
                u_i = data["unit"]
                c_i = components.get(u_i.unit_type)
                u_i.load_data(start_date, end_date, time_resolution, components=c_i)

        else:
            # Otherwise, just load specific components
            for i in components.keys():
                c_i = components.get(i)
                if i == "weather":
                    self.weather.load_data(
                        start_date, end_date, time_resolution, components=c_i
                    )
                else:
                    for u_i in self.query_units(unit_type=i):
                        u_i.load_data(
                            start_date, end_date, time_resolution, components=c_i
                        )

    def load_dataset(
        self,
        component_map,
        start_date,
        end_date,
        time_resolution: str = "hour",
        load_weather: bool = True,
    ) -> pd.DataFrame:
        """

        :param component_map:
        :type component_map:
        :param start_date:
        :type start_date:
        :param end_date:
        :type end_date:
        :param time_resolution:
        :type time_resolution:
        :param load_weather:
        :type load_weather:
        :return:
        :rtype:
        """

        df = load_model_data(component_map, start_date, end_date, time_resolution)

        if load_weather is True:
            self.weather.load_data(start_date, end_date, time_resolution)
            df_weather = self.weather.data
            df_weather.columns = "weather." + df_weather.columns
            df = pd.concat((df_weather, df), axis=1)

        return df

    def clear_data(self) -> None:
        """

        :return:
        :rtype:
        """
        self.weather.clear_data()

        for node, data in self.G.nodes.data():
            data["unit"].clear_data()

    def get_all_component_ids(self):
        """

        :return:
        :rtype:
        """
        return {
            k: v
            for node, data in self.G.nodes.data()
            for k, v in data["unit"].get_all_component_ids(True).items()
        }

    def get_all_component_details(self):
        """

        :return:
        :rtype:
        """
        all_comps = []
        for node, data in self.G.nodes.data():
            all_comps += data["unit"].get_all_component_details(prefix=True)

        return all_comps

    def query_units(
        self, unit_type: str = None, name: str = None, unit_id: int = None
    ) -> List[BaseBuildingUnit]:
        """

        :param unit_type:
        :type unit_type:
        :param name:
        :type name:
        :param unit_id:
        :type unit_id:
        :return:
        :rtype:
        """
        # If we pass a unit ID, find specific unit
        if unit_id:
            if unit_id in self.G.nodes.keys():
                return [self.G.nodes[unit_id]["unit"]]
            else:
                return []

        # If we pass a unit_type, check if we do regex search or strict search
        if unit_type:
            if unit_type[0] == "?":
                r_type = re.compile(unit_type[1:])
                type_match = lambda t: r_type.search(t)
            else:
                type_match = lambda t: t == unit_type

        # If we pass name, check if we do regex search or strict search
        if name:
            # Check if we do strict search or search by regex:
            if name[0] == "?":
                r_name = re.compile(name[1:])
                name_match = lambda n: r_name.search(n)
            else:
                name_match = lambda n: n == name

        try:
            # If we pass unit_type and name
            if unit_type and name:
                result = [
                    data["unit"]
                    for node, data in self.G.nodes.data()
                    if name_match(data["unit"].name)
                    and type_match(data["unit"].unit_type)
                ]

            elif name:
                result = [
                    data["unit"]
                    for node, data in self.G.nodes.data()
                    if name_match(data["unit"].name)
                ]

            elif unit_type:
                result = [
                    data["unit"]
                    for node, data in self.G.nodes.data()
                    if type_match(data["unit"].unit_type)
                ]

            return result

        except:
            return []

    def qu(self, *args, **kwargs) -> Union[BaseBuildingUnit, List[BaseBuildingUnit]]:
        """

        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        result = self.query_units(*args, **kwargs)
        return convenience_result_list_shortener(result)

    def __populate(self) -> None:
        # Request PreHEAT API for location
        resp = api_get(f"locations/{self.location_id}", out="json")

        # Check if we have building data and if we do, extract and populate
        if "building" in resp:
            data = resp["building"]

            self.location = data["location"]
            self.area = data["buildingArea"]
            self.type = data["buildingType"]
            self.characteristics = {
                "area": self.area,
                "type": self.type,
                "apartments": data["apartments"],
            }

            self.weather = Weather(self.location_id, data["weatherForecast"])

            self.zones = populate_zones(data["zones"])

            # Order is important for dependency
            unit_types = [
                "main",
                "coldWater",
                "heating",
                "hotWater",
                "cooling",
                "electricity",
                "ventilation",
                "heatPumps",
                "indoorClimate",
                "custom",
            ]

            for unit_type in unit_types:
                self.units[unit_type] = populate_units(unit_type, data[unit_type], self)

            for sp_i in data["supplyPoints"]:
                self.__supply_points.append(SupplyPoint(sp_i))

        else:
            raise AccessDeniedError("Access denied for given building")

    def get_supply_points(self):
        """

        :return:
        :rtype:
        """
        return self.__supply_points

    def __repr__(self):
        return f"""{type(self).__name__}({self.location_id}): {self.location["address"]} - {self.type}"""

    def get_zones(self, zone_ids) -> List[Zone]:
        """

        :param zone_ids:
        :type zone_ids:
        :return:
        :rtype:
        """
        res = []
        for z_i in self.zones:
            if z_i.id in zone_ids:
                res.append(z_i)
            res += z_i.get_sub_zones(zone_ids=zone_ids)
        return res

    def get_zone(self, id: int) -> Zone:
        """

        :param id:
        :type id:
        :return:
        :rtype:
        """
        zs = self.get_zones([id])
        n_zs = len(zs)
        if n_zs < 1:
            raise Exception(f"Zone not found (id={id})")
        elif n_zs > 1:
            raise Exception(f"Too many zones found for id (id={id} / {n_zs} found)")
        return zs[0]


def available_buildings() -> pd.DataFrame:
    """
    Lists available buildings

    :return: dataframe of buildings available
    :rtype:
    """
    out = api_get("locations")
    return pd.DataFrame(out["locations"])
