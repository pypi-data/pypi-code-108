# Devices: Device objects for GridWorkbench
#
# Adam Birchfield, Texas A&M University
# 
# Log:
# 9/29/2021 Initial version, rearranged from prior draft so that most object fields
#   are only listed in one place, the PW_Fields table. Now to add a field you just
#   need to add it in that list.
# 11/2/2021 Renamed this file to core and added fuel type object
# 1/22/22 Separated from gridworkbench to contain Gen, Load, Shunt, Branch, (later ThreeWinder and Converter)
#
from .containers import Region, Area, Sub, Bus, Node

class Gen:

    def __init__(self, node, id):
        self._node = node
        if not isinstance(node, Node):
            raise Exception(f"Invalid node provided to create gen {id}")
        self.id = id
        for f in self.bus.wb.gen_pw_fields:
            setattr(self, f[0], f[2])
    
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if hasattr(self, "_id"):
            del self.node._gen_map[self._id]
        if not isinstance(value, str):
            raise Exception(f"Gen id must be string")
        if len(value) < 1 or len(value) > 2:
            raise Exception(f"Gen ID '{value}' must be 1 or 2 characters")
        if value in self.node._gen_map:
            raise Exception(f"Gen ID '{value}' already exists!")
        self._id = value
        self.node._gen_map[self._id] = self

    def __str__(self):
        return f"Gen {self.node.number} {self.id} " \
            + f"{self.node.name if hasattr(self.node, 'name') else ''}"

    def __repr__(self):
        return str(self) + f" {hex(id(self))}"

    @property
    def node(self):
        return self._node

    @property
    def bus(self):
        return self.node.bus


class Load:

    def __init__(self, node, id):
        self._node = node
        if not isinstance(node, Node):
            raise Exception(f"Invalid node provided to create load {id}")
        self.id = id
        for f in self.bus.wb.load_pw_fields:
            setattr(self, f[0], f[2])

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if hasattr(self, "_id"):
            del self.node._load_map[self._id]
        if not isinstance(value, str):
            raise Exception(f"Load id must be string")
        if len(value) < 1 or len(value) > 2:
            raise Exception(f"Load ID '{value}' must be 1 or 2 characters")
        if value in self.node._load_map:
            raise Exception(f"Load ID '{value}' already exists!")
        self._id = value
        self.node._load_map[self._id] = self

    def __str__(self):
        return f"Load {self.node.number} {self.id} " \
            + f"{self.node.name if hasattr(self.node, 'name') else ''}"

    def __repr__(self):
        return str(self) + f" {hex(id(self))}"

    @property
    def node(self):
        return self._node

    @property
    def bus(self):
        return self.node.bus


class Shunt:

    def __init__(self, node, id):
        self._node = node
        if not isinstance(node, Node):
            raise Exception(f"Invalid node provided to create shunt {id}")
        self.id = id
        node._shunt_map[id] = self
        for f in self.bus.wb.shunt_pw_fields:
            setattr(self, f[0], f[2])

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if hasattr(self, "_id"):
            del self.node._shunt_map[self._id]
        if not isinstance(value, str):
            raise Exception(f"Shunt id must be string")
        if len(value) < 1 or len(value) > 2:
            raise Exception(f"Shunt ID '{value}' must be 1 or 2 characters")
        if value in self.node._shunt_map:
            raise Exception(f"Shunt ID '{value}' already exists!")
        self._id = value
        self.node._shunt_map[self._id] = self

    def __str__(self):
        return f"Shunt {self.node.number} {self.id} " \
            + f"{self.node.name if hasattr(self.node, 'name') else ''}"

    def __repr__(self):
        return str(self) + f" {hex(id(self))}"

    @property
    def node(self):
        return self._node

    @property
    def bus(self):
        return self.node.bus


class Branch:

    def __init__(self, from_node, to_node, id):
        self._from_node = from_node
        self._to_node = to_node
        if not isinstance(from_node, Node):
            raise Exception(f"Invalid node provided to create branch {id}")
        if not isinstance(to_node, Node):
            raise Exception(f"Invalid node provided to create branch {id}")
        self.id = id
        for f in self.from_bus.wb.branch_pw_fields:
            setattr(self, f[0], f[2])

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if hasattr(self, "_id"):
            del self.from_node._branch_from_map[(self.to_node.number, self._id)]
            del self.to_node._branch_to_map[(self.from_node.number, self._id)]
        if not isinstance(value, str):
            raise Exception(f"Branch id must be string")
        if len(value) < 1 or len(value) > 2:
            raise Exception(f"Branch ID '{value}' must be 1 or 2 characters")
        self._id = value
        if (self.to_node.number, self._id) in self.from_node._branch_from_map:
            raise Exception(f"Branch ID '{value}' already exists!")
        if (self.from_node.number, self._id) in self.to_node._branch_to_map:
            raise Exception(f"Branch ID '{value}' already exists!")
        self.from_node._branch_from_map[(self.to_node.number, self._id)] = self
        self.to_node._branch_to_map[(self.from_node.number, self._id)] = self

    def __str__(self):
        return f"Branch {self.from_node.number} {self.to_node.number} {self.id} " \
            + f"{self.from_node.name if hasattr(self.from_node, 'name') else ''} to " \
            + f"{self.to_node.name if hasattr(self.to_node, 'name') else ''}"

    def __repr__(self):
        return str(self) + f" {hex(id(self))}"

    @property
    def from_node(self):
        return self._from_node

    @property
    def to_node(self):
        return self._to_node

    @property
    def from_bus(self):
        return self.from_node.bus

    @property
    def to_bus(self):
        return self.to_node.bus

