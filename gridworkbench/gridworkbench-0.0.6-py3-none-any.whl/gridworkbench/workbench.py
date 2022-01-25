# GridWorkbench: A Python structure for power system data
#
# Adam Birchfield, Texas A&M University
# 
# Log:
# 9/29/2021 Initial version, rearranged from prior draft so that most object fields
#   are only listed in one place, the PW_Fields table. Now to add a field you just
#   need to add it in that list.
# 11/2/2021 Renamed this file to core and added fuel type object
# 1/22/22 Split out all device types
#
print("Importing local copy")

import esa
from typing import OrderedDict
import pandas as pd
import json
from .containers import Region, Area, Sub, Bus, Node
from .devices import Gen, Load, Shunt, Branch

class GridWorkbench:

    from .pwb_analysis import setup_pwb_fields
    from .pwb_analysis import open_pwb
    from .pwb_analysis import close_pwb
    from .pwb_analysis import pwb_read_all
    from .pwb_analysis import pwb_write_all
    from .pwb_analysis import pwb_write_data
    from .pwb_analysis import json_save

    def __init__(self):
        self.clear()
        self.setup_pwb_fields()

    def clear(self):
        self._region_map = OrderedDict()
        self._area_map = OrderedDict()
        self._sub_map = OrderedDict()
        self._bus_map = OrderedDict()
        self._node_map = OrderedDict()
        self.esa = None

    def region(self, number):
        if number in self._region_map:
            return self._region_map[number]

    def area(self, number):
        if number in self._area_map:
            return self._area_map[number]

    def sub(self, number):
        if number in self._sub_map:
            return self._sub_map[number]

    def bus(self, number):
        if number in self._bus_map:
            return self._bus_map[number]

    def node(self, number):
        if number in self._node_map:
            return self._node_map[number]

    def gen(self, node_number, id):
        node = self.node(node_number)
        if node is not None:
            return node.gen(id)

    def load(self, node_number, id):
        node = self.node(node_number)
        if node is not None:
            return node.load(id)

    def shunt(self, node_number, id):
        node = self.node(node_number)
        if node is not None:
            return node.shunt(id)
            
    def branch(self, from_node_number, to_node_number, id):
        from_node = self.node(from_node_number)
        if from_node is not None:
            return from_node.branch_from(to_node_number, id)
    
    @property
    def regions(self):
        return (region for region in self._region_map.values())

    @property
    def areas(self):
        return (area for area in self._area_map.values())

    @property
    def subs(self):
        return (sub for sub in self._sub_map.values())

    @property
    def buses(self):
        return (bus for bus in self._bus_map.values())

    @property
    def nodes(self):
        return (bus for bus in self._node_map.values())

    @property
    def gens(self):
        return (gen for node in self.nodes for gen in node.gens)

    @property
    def branches(self):
        return (branch for node in self.nodes for branch in node.branches_from)

    @property
    def loads(self):
        return (load for node in self.nodes for load in node.loads)

    @property
    def shunts(self):
        return (shunt for node in self.nodes for shunt in node.shunts)
