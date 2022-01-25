# Containers: Container types for GridWorkbench
#
# Adam Birchfield, Texas A&M University
# 
# Log:
# 9/29/2021 Initial version, rearranged from prior draft so that most object fields
#   are only listed in one place, the PW_Fields table. Now to add a field you just
#   need to add it in that list.
# 11/2/2021 Renamed this file to core and added fuel type object
# 1/22/22 Separated this from main gridworkbench
#
# 
from typing import OrderedDict

class Region:

    def __init__(self, wb, number):
        self._wb = wb
        self.number = number
        self._area_map = OrderedDict()
    
    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        if hasattr(self, "_number"):
            del self.wb._region_map[self._number]
        if not isinstance(value, int):
            raise Exception(f"Region number must be integer")
        if value < 1:
            raise Exception(f"Region number {value} must be positive")
        if value in self.wb._region_map:
            raise Exception(f"Region number {value} already exists!")
        self._number = value
        self.wb._region_map[self._number] = self

    def __str__(self):
        return f"Region {self.number} {self.name if hasattr(self, 'name') else ''}"

    def __repr__(self):
        return str(self) + f" {hex(id(self))}"

    @property
    def wb(self):
        return self._wb
    
    def area(self, number):
        if number in self._area_map:
            return self._area_map[number]

    @property
    def areas(self):
        return (area for area in self._area_map.values())

    @property
    def subs(self):
        return (sub for area in self.areas for sub in area.subs)

    @property
    def buses(self):
        return (bus for area in self.areas for bus in area.buses)

    @property
    def gens(self):
        return (gen for area in self.areas for gen in area.gens)

    @property
    def loads(self):
        return (load for area in self.areas for load in area.loads)

    @property
    def shunts(self):
        return (shunt for area in self.areas for shunt in area.shunts)
    
    @property
    def branches(self):
        return (branch for area in self.areas for branch in area.branches)
    

class Area:
    
    def __init__(self, region, number):
        if not isinstance(region, Region):
            raise Exception(f"Invalid region provided to create area {number}")
        self._region = region
        self.number = number
        self._sub_map = OrderedDict()

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        if hasattr(self, "_number"):
            del self.wb._area_map[self._number]
            del self.region._area_map[self._number]
        if not isinstance(value, int):
            raise Exception(f"Area number must be integer")
        if value < 1:
            raise Exception(f"Area number {value} must be positive")
        if value in self.region.wb._area_map:
            raise Exception(f"Area number {value} already exists!")
        self._number = value
        self.wb._area_map[self._number] = self
        self.region._area_map[self._number] = self

    def __str__(self):
        return f"Area {self.number} {self.name if hasattr(self, 'name') else ''}"

    def __repr__(self):
        return str(self) + f" {hex(id(self))}"

    @property
    def region(self):
        return self._region

    @property
    def wb(self):
        return self._region._wb
    
    def sub(self, number):
        if number in self._sub_map:
            return self._sub_map[number]

    @property
    def subs(self):
        return (sub for sub in self._sub_map.values())

    @property
    def buses(self):
        return (bus for sub in self.subs for bus in sub.buses)

    @property
    def gens(self):
        return (gen for sub in self.subs for gen in sub.gens)

    @property
    def loads(self):
        return (load for sub in self.subs for load in sub.loads)

    @property
    def shunts(self):
        return (shunt for sub in self.subs for shunt in sub.shunts)
    
    @property
    def branches(self):
        return (branch for sub in self.subs for branch in sub.branches)
    

class Sub:

    def __init__(self, area, number):
        if not isinstance(area, Area):
            raise Exception(f"Invalid area provided to create sub {number}")
        self._area = area
        self.number = number
        self._bus_map = OrderedDict()

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        if hasattr(self, "_number"):
            del self.area.wb._sub_map[self._number]
            del self.area._sub_map[self._number]
        if not isinstance(value, int):
            raise Exception(f"Sub number must be integer")
        if value < 1:
            raise Exception(f"Sub number {value} must be positive")
        if value in self.wb._sub_map:
            raise Exception(f"Sub number {value} already exists!")
        self._number = value
        self.wb._sub_map[self._number] = self
        self.area._sub_map[self._number] = self

    def __str__(self):
        return f"Sub {self.number} {self.name if hasattr(self, 'name') else ''}"

    def __repr__(self):
        return str(self) + f" {hex(id(self))}"

    @property
    def area(self):
        return self._area

    @property
    def region(self):
        return self.area.region

    @property
    def wb(self):
        return self.area.wb
    
    def bus(self, number):
        if number in self._bus_map:
            return self._bus_map[number]

    @property
    def buses(self):
        return (bus for bus in self._bus_map.values())

    @property
    def gens(self):
        return (gen for bus in self.buses for gen in bus.gens)

    @property
    def loads(self):
        return (load for bus in self.buses for load in bus.loads)

    @property
    def shunts(self):
        return (shunt for bus in self.buses for shunt in bus.shunts)
    
    @property
    def branches(self):
        return (branch for bus in self.buses for branch in bus.branches)
    

class Bus:

    def __init__(self, sub, number):
        if not isinstance(sub, Sub):
            raise Exception(f"Invalid sub provided to create bus {number}")
        self._sub = sub
        self.number = number
        self._node_map = OrderedDict()
        for f in self.wb.bus_pw_fields:
            setattr(self, f[0], f[2])

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        if hasattr(self, "_number"):
            del self.wb._bus_map[self._number]
            del self.sub._bus_map[self._number]
        if not isinstance(value, int):
            raise Exception(f"Bus number must be integer")
        if value < 1:
            raise Exception(f"Bus number {value} must be positive")
        if value in self.wb._bus_map:
            raise Exception(f"Bus number {value} already exists!")
        self._number = value
        self.wb._bus_map[self._number] = self
        self.sub._bus_map[self._number] = self

    def __str__(self):
        return f"Bus {self.number} {self.name if hasattr(self, 'name') else ''}"

    def __repr__(self):
        return str(self) + f" {hex(id(self))}"

    @property
    def sub(self):
        return self._sub

    @property
    def area(self):
        return self.sub.area

    @property
    def region(self):
        return self.sub.region

    @property
    def wb(self):
        return self.sub.wb

    def node(self, number):
        if number in self._node_map:
            return self._node_map[number]

    @property
    def nodes(self):
        return (node for node in self._node_map.values())

    def gen(self, id):
        for node in self.nodes:
            if id in node._gen_map:
                return node._gen_map[id]

    @property
    def gens(self):
        return (gen for node in self.nodes for gen in node.gens)

    def load(self, id):
        for node in self.nodes:
            if id in node._load_map:
                return node._load_map[id]

    @property
    def loads(self):
        return (load for node in self.nodes for load in node.loads)

    def shunt(self, id):
        for node in self.nodes:
            if id in node._shunt_map:
                return node._shunt_map[id]

    @property
    def shunts(self):
        return (shunt for node in self.nodes for shunt in node.shunts)

    def branch_from(self, to_node_number, id):
        for node in self.nodes:
            if (to_node_number, id) in node._branch_from_map:
                return node._branch_from_map[(to_node_number, id)]

    @property
    def branches_from(self):
        return (branch for node in self.nodes for branch in node.branches_from)

    def branch_to(self, from_node_number, id):
        for node in self.nodes:
            if (from_node_number, id) in node._branch_to_map:
                return node._branch_to_map[(from_node_number, id)]

    @property
    def branches_to(self):
        return (branch for node in self.nodes for branch in node.branches_to)

    @property
    def branches(self):
        return (branch for branchset in (self.branches_to, self.branches_from) for branch in branchset)


class Node:

    def __init__(self, bus, number):
        self._bus = bus
        if not isinstance(bus, Bus):
            raise Exception(f"Invalid bus provided to create node {number}")
        self.number = number
        self._gen_map = OrderedDict()
        self._load_map = OrderedDict()
        self._shunt_map = OrderedDict()
        self._branch_from_map = OrderedDict()
        self._branch_to_map = OrderedDict()

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        if hasattr(self, "_number"):
            del self.wb._node_map[self._number]
            del self.bus._node_map[self._number]
        if not isinstance(value, int):
            raise Exception(f"Node number must be integer")
        if value < 1:
            raise Exception(f"Node number {value} must be positive")
        if value in self.wb._node_map:
            raise Exception(f"Node number {value} already exists!")
        self._number = value
        self.wb._node_map[self._number] = self
        self.bus._node_map[self._number] = self

    def __str__(self):
        return f"Node {self.number} {self.name if hasattr(self, 'name') else ''}"

    def __repr__(self):
        return str(self) + f" {hex(id(self))}"

    @property
    def bus(self):
        return self._bus

    @property
    def sub(self):
        return self.bus.sub

    @property
    def area(self):
        return self.bus.area

    @property
    def region(self):
        return self.bus.region

    @property
    def wb(self):
        return self.bus.wb
    
    def gen(self, id):
        if id in self._gen_map:
            return self._gen_map[id]

    def load(self, id):
        if id in self._load_map:
            return self._load_map[id]

    def shunt(self, id):
        if id in self._shunt_map:
            return self._shunt_map[id]

    def branch_from(self, to_node_number, id):
        if (to_node_number, id) in self._branch_from_map:
            return self._branch_from_map[(to_node_number, id)]

    def branch_to(self, from_node_number, id):
        if (from_node_number, id) in self._branch_to_map:
            return self._branch_to_map[(from_node_number, id)]

    @property
    def gens(self):
        return (gen for gen in self._gen_map.values())

    @property
    def loads(self):
        return (load for load in self._load_map.values())

    @property
    def shunts(self):
        return (shunt for shunt in self._shunt_map.values())

    @property
    def branches_from(self):
        return (branch for branch in self._branch_from_map.values())

    @property
    def branches_to(self):
        return (branch for branch in self._branch_to_map.values())
    
    @property
    def branches(self):
        return (branch for branchset in (self.branches_to(), self.branches_from()) for branch in branchset)

