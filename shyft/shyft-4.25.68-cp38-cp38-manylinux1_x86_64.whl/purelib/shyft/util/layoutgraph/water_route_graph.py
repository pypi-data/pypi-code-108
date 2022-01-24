import collections
from abc import ABC, abstractmethod
import os
import yaml

from . import ghost_object_factory, LayoutGraph


def load_default_config_yaml(filename=None):
    """

    Parameters
    ----------
    filename

    Returns
    -------

    """
    # TODO: try except
    if not filename:
        curr_dir = os.path.dirname(__file__)
        filename = os.path.join(curr_dir, 'layout_configuration.yml')
    with open(filename, 'r') as f:
        layout_config = yaml.load(f, Loader=yaml.SafeLoader)
    if not isinstance(layout_config, dict):
        raise RuntimeError(f'loaded yaml config should be a dict')
    return layout_config


# ---------------------------------------------------------------------------------------------------------------------#
# Main class for water route graph creation
class WaterRouteGraph(ABC, LayoutGraph):
    def __init__(self, default_config_file: str = None):

        # load default configuration
        layout_config = load_default_config_yaml(filename=default_config_file)
        graph_obj = ghost_object_factory('Graph', 'Graph_01')
        # init super class
        super().__init__(graph_obj, layout_config, 'Graph')
        # dict containg collections.OrderedDict() with tag: obj
        self.dh_tag_obj = self.get_clean_dh_tag_obj()

    @staticmethod
    def get_clean_dh_tag_obj():
        clean_dh_tag_obj = {"reservoirs": {},
                            "power_stations": {},
                            "pump_stations": {},
                            "pure_pumps": {},
                            "spill_routes": {},
                            "bypass_routes": {},
                            "main_water_routes": {},
                            "oceans": collections.OrderedDict(),
                            "oceans_flood": collections.OrderedDict(),
                            "oceans_bypass": collections.OrderedDict(),
                            "water_route_connector": collections.OrderedDict()}
        return clean_dh_tag_obj

    @abstractmethod
    def generate_graph(self, water_route):
        """

        Parameters
        ----------
        water_route: water route object model

        Returns
        -------

        """

        pass

    # graph data getter
    @property
    def main_water_route_beziers(self):
        # add tag update here if different run
        data_dict = self.get_connection_beziers(self.dh_tag_obj['main_water_routes'].keys())
        return data_dict

    @property
    def spill_routes_beziers(self):
        # add tag update here if different run
        data_dict = self.get_connection_beziers(self.dh_tag_obj['spill_routes'].keys())
        return data_dict

    @property
    def bypass_routes_beziers(self):
        # add tag update here if different run
        data_dict = self.get_connection_beziers(self.dh_tag_obj['bypass_routes'].keys())
        return data_dict

    @property
    def reservoir_coordinates(self):
        # add tag update here if different run
        data_dict = self.get_container_coordinates(self.dh_tag_obj['reservoirs'].keys())
        return data_dict

    @property
    def all_power_stations_coordinates(self):
        # add tag update here if different run
        data_dict = self.get_container_coordinates(list(self.dh_tag_obj['power_stations'].keys()) +
                                                   list(self.dh_tag_obj['pump_stations'].keys()) +
                                                   list(self.dh_tag_obj['pure_pumps'].keys()))
        return data_dict

    @property
    def power_stations_coordinates(self):
        # add tag update here if different run
        data_dict = self.get_container_coordinates(self.dh_tag_obj['power_stations'].keys())
        return data_dict

    @property
    def pump_stations_coordinates(self):
        # add tag update here if different run
        data_dict = self.get_container_coordinates(self.dh_tag_obj['pump_stations'].keys())
        return data_dict

    @property
    def pure_pumps_coordinates(self):
        # add tag update here if different run
        data_dict = self.get_container_coordinates(self.dh_tag_obj['pure_pumps'].keys())
        return data_dict

    @property
    def oceans_coordinates(self):
        # add tag update here if different run
        return self.get_container_coordinates(self.dh_tag_obj['oceans'].keys())

    @property
    def oceans_spillage_coordinates(self):
        # add tag update here if different run
        return self.get_container_coordinates(self.dh_tag_obj['oceans_flood'].keys())

    @property
    def oceans_bypass_coordinates(self):
        # add tag update here if different run
        return self.get_container_coordinates(self.dh_tag_obj['oceans_bypass'].keys())

    @property
    def water_route_connector_coordinates(self):
        # add tag update here if different run
        return self.get_container_coordinates(self.dh_tag_obj['water_route_connector'].keys())
