# PWB Analysis: The functions for sending PowerWorld data to and from the GridWorkbench using Easy SimAuto
#
# Adam Birchfield, Texas A&M University
# 
# Log:
# 9/29/2021 Initial version, rearranged from prior draft so that most object fields
#   are only listed in one place, the PW_Fields table. Now to add a field you just
#   need to add it in that list.
# 11/2/2021 Renamed this file to core and added fuel type object
# 1/22/22 Split out all device types
# 1/25/22 Split out this PWB file
#
import esa
from typing import OrderedDict
import pandas as pd
import json
from .containers import Region, Area, Sub, Bus, Node
from .devices import Gen, Load, Shunt, Branch


def setup_pwb_fields(self):

    # Converter functions from PowerWorld data. If unknown use pw2py_default
    pw2py_default = lambda x:x
    pw2py_connected = lambda x:x.lower() == "connected"
    pw2py_closed = lambda x:x.lower() == "closed"
    pw2py_yes = lambda x:x.lower() == "yes"

    # For each field in these lists, there are four items
    # [0] Name of field of the Python object
    # [1] Name of the field in PowerWorld
    # [2] Default value of the field (not currently implemented)
    # [3] Function to convert data from PowerWorld (see examples above)

    self.sa_pw_fields = [
        ("name", "SAName", "Default", pw2py_default)
    ]

    self.area_pw_fields = [
        ("name", "AreaName", "Default", pw2py_default)
    ]

    self.sub_pw_fields = [
        ("name", "SubName", "Default", pw2py_default),
        ("latitude", "Latitude", 0, pw2py_default),
        ("longitude", "Longitude", 0, pw2py_default)
    ]

    self.bus_pw_fields = [
        ("name", "BusName", "Default", pw2py_default),
        ("nominal_kv", "BusNomVolt", 138, pw2py_default),
        ("vpu", "BusPUVolt", 1.0, pw2py_default),
        ("vang", "BusAngle", 0.0, pw2py_default),
        ("status", "BusStatus", True, pw2py_connected),
        ("zone_number", "ZoneNum", 0, pw2py_default)
    ]

    self.gen_pw_fields = [
        ("status", "GenStatus", True, pw2py_closed),
        ("p", "GenMW", 0, pw2py_default),
        ("q", "GenMVR", 0, pw2py_default),
        ("pset", "GenMWSetPoint", 0, pw2py_default),
        ("qset", "GenMvrSetPoint", 0, pw2py_default),
        ("pmax", "GenMWMax", 9999, pw2py_default),
        ("pmin", "GenMWMin", 0, pw2py_default),
        ("qmax", "GenMVRMax", 9999, pw2py_default),
        ("qmin", "GenMVRMin", -9999, pw2py_default),
        ("reg_bus_num", "GenRegNum", 0, pw2py_default),
        ("reg_pu_v", "GenVoltSet", 1.0, pw2py_default),
        ("p_auto_status", "GenAGCAble", True, pw2py_yes),
        ("q_auto_status", "GenAVRAble", True, pw2py_yes),
        ("ramp_rate", "GenMWRampLimit", 0.0, pw2py_default),
        ("crank_p", "CustomFloat", 0.0, pw2py_default),
        ("crank_t", "CustomFloat:1", 0.0, pw2py_default),
        ("availability", "CustomFloat:2", 0.0, pw2py_default),
        ("fuel_type", "GenFuelType", "Unknown", pw2py_default)
    ]

    self.load_pw_fields = [
        ("status", "LoadStatus", True, pw2py_closed),
        ("p", "LoadMW", 0, pw2py_default),
        ("q", "LoadMVR", 0, pw2py_default),
        ("ps", "LoadSMW", 0, pw2py_default),
        ("qs", "LoadSMVR", 0, pw2py_default),
        ("benefit", "GenBidMWHR", 0, pw2py_default)
    ]

    self.shunt_pw_fields = [
        ("status","SSStatus", True, pw2py_closed),
        ("qnom", "SSNMVR", 0, pw2py_default),
        ("q", "SSAMVR", 0, pw2py_default),
        ("availability", "CustomInteger", 0, pw2py_default)
    ]

    self.branch_pw_fields = [
        ("status", "LineStatus", True, pw2py_closed),
        ("R", "LineR", 0, pw2py_default),
        ("X", "LineX", 0.1, pw2py_default),
        ("B", "LineC", 0, pw2py_default),
        ("G", "LineG", 0, pw2py_default),
        ("MVA_Limit_A", "LineAMVA", 0, pw2py_default),
        ("MVA_Limit_B", "LineAMVA:1", 0, pw2py_default),
        ("MVA_Limit_C", "LineAMVA:2", 0, pw2py_default),
        ("p1", "LineMW", 0, pw2py_default),
        ("q1", "LineMVR", 0, pw2py_default),
        ("p2", "LineMW:1", 0, pw2py_default),
        ("q2", "LineMVR:1", 0, pw2py_default),
        ("length", "GICLineDistance", 0, pw2py_default),
        ("availability", "CustomInteger", 0, pw2py_default)
    ]

def open_pwb(self, fname):
    self.esa = esa.SAW(fname)
    
def close_pwb(self):
    self.esa.CloseCase()

def pwb_read_all(self, s=None):
    if s is None:
        s = self.esa

    # Read super areas into regions
    print("Reading Super Areas")
    df = s.GetParametersMultipleElement("superarea",
        [f[1] for f in self.sa_pw_fields])
    if df is not None:
        df = df.to_dict("records")
        for i in range(len(df)):
            sa_info = df[i]
            sa_name = sa_info["SAName"]
            for region in self.regions:
                if hasattr(region, "name") and region.name == sa_name:
                    break
            else:
                number = max([0] + [r.number for r in self.regions]) + 1
                region = Region(self, number)
            for f in self.sa_pw_fields:
                setattr(region, f[0], f[3](sa_info[f[1]]))
        
    # Read areas into areas
    print("Reading Areas")
    area_df = s.GetParametersMultipleElement("area",
        ["AreaNum", "SAName"] + [f[1] for f in self.area_pw_fields]).to_dict("records")
    for i in range(len(area_df)):
        area_info = area_df[i]
        area_num = int(area_info["AreaNum"])
        sa_name = str(area_info["SAName"])
        area = self.area(area_num)
        if area is None:
            if sa_name == "":
                if len(list(self.regions)) == 0:
                    region = Region(self, 1)
                else:
                    region = next(self.regions)
            else:
                for region in self.regions:
                    if hasattr(region, "name") and region.name == sa_name:
                        break
                else:
                    number = max([0] + [r.number for r in self.regions]) + 1
                    region = Region(self, number)
            area = Area(region, area_num)
        for f in self.area_pw_fields:
            setattr(area, f[0], f[3](area_info[f[1]]))
    
    # Read substations into sub
    print("Reading Substations")
    sub_df = s.GetParametersMultipleElement("substation",
        ["SubNum", "AreaNum"] + [f[1] for f in self.sub_pw_fields])
    if sub_df is not None:
        sub_df = sub_df.to_dict("records")
        for i in range(len(sub_df)):
            sub_info = sub_df[i]
            sub_num = int(sub_info["SubNum"])
            area_num = int(sub_info["AreaNum"])
            sub = self.sub(sub_num)
            if sub is None:
                area = self.area(area_num)
                if area is None:
                    region = Region(self, 1) if len(list(self.regions)) == 0 else next(self.regions)
                    area = Area(region, area_num)
                sub = Sub(area, sub_num)
            for f in self.sub_pw_fields:
                setattr(sub, f[0], f[3](sub_info[f[1]]))

    # Read buses into both buses and paired-up nodes
    print("Reading Buses")
    bus_df = s.GetParametersMultipleElement("bus", 
        ["BusNum", "SubNum", "AreaNum"] + [f[1] for f in self.bus_pw_fields]).to_dict("records")
    for i in range(len(bus_df)):
        bus_info = bus_df[i]
        bus_num = int(bus_info["BusNum"])
        sub_num = bus_num
        if type(bus_info["SubNum"]) == int or bus_info["SubNum"].is_integer():
            sub_num = int(bus_info["SubNum"])
        area_num = int(bus_info["AreaNum"])
        bus = self.bus(bus_num)
        if bus is None:
            sub = self.sub(sub_num)
            if sub is None:
                area = self.area(area_num)
                if area is None:
                    region = Region(self, 1) if len(list(self.regions)) == 0 else next(self.regions)
                    area = Area(region, area_num)
                sub = Sub(area, sub_num)
            bus = Bus(sub, bus_num)
        node = self.node(bus_num)
        if node is None:
            node = Node(bus, bus_num)
        for f in self.bus_pw_fields:
            setattr(bus, f[0], f[3](bus_info[f[1]]))
        if hasattr(bus, "name"):
            node.name = bus.name

    print("Reading Gens")
    gen_df = s.GetParametersMultipleElement("gen", 
        ["BusNum", "GenID"] + [f[1] for f in self.gen_pw_fields]).to_dict("records")
    for i in range(len(gen_df)):
        gen_info = gen_df[i]
        gen_bus_num = int(gen_info["BusNum"])
        gen_id = str(gen_info["GenID"])
        gen = self.gen(gen_bus_num, gen_id)
        if gen is None:
            node = self.node(gen_bus_num)
            gen = Gen(node, gen_id)
        for f in self.gen_pw_fields:
            setattr(gen, f[0], f[3](gen_info[f[1]]))

    print("Reading Loads")
    load_df = s.GetParametersMultipleElement("load", 
        ["BusNum", "LoadID"] + [f[1] for f in self.load_pw_fields]).to_dict("records")
    for i in range(len(load_df)):
        load_info = load_df[i]
        load_bus_num = int(load_info["BusNum"])
        load_id = str(load_info["LoadID"])
        load = self.load(load_bus_num, load_id)
        if load is None:
            node = self.node(load_bus_num)
            load = Load(node, load_id)
        for f in self.load_pw_fields:
            setattr(load, f[0], f[3](load_info[f[1]]))

    print("Reading Shunts")
    shunt_df = s.GetParametersMultipleElement("shunt", 
        ["BusNum", "ShuntID"] + [f[1] for f in self.shunt_pw_fields])
    if shunt_df is not None:
        shunt_df = shunt_df.to_dict("records")
        for i in range(len(shunt_df)):
            shunt_info = shunt_df[i]
            shunt_bus_num = int(shunt_info["BusNum"])
            shunt_id = str(shunt_info["ShuntID"])
            shunt = self.shunt(shunt_bus_num, shunt_id)
            if shunt is None:
                node = self.node(shunt_bus_num)
                shunt = Shunt(node, shunt_id)
            for f in self.shunt_pw_fields:
                setattr(shunt, f[0], f[3](shunt_info[f[1]]))

    print("Reading Branches")
    branch_df = s.GetParametersMultipleElement("branch", 
        ["BusNum", "BusNum:1", "LineCircuit"] 
        + [f[1] for f in self.branch_pw_fields]).to_dict("records")
    for i in range(len(branch_df)):
        branch_info = branch_df[i]
        from_bus_num = int(branch_info["BusNum"])
        to_bus_num = int(branch_info["BusNum:1"])
        branch_id = str(branch_info["LineCircuit"])
        branch = self.branch(from_bus_num, to_bus_num, branch_id)
        if branch is None:
            from_node = self.node(from_bus_num)
            to_node = self.node(to_bus_num)
            branch = Branch(from_node, to_node, branch_id)
        for f in self.branch_pw_fields:
            setattr(branch, f[0], f[3](branch_info[f[1]]))

def pwb_write_all(self, s=None):
    if s is None:
        s = self.esa
    self.pwb_write_data(s, regions=self.regions, areas=self.areas, subs=self.subs,
        buses=self.buses, loads=self.loads, gens=self.gens, shunts=self.shunts,
        branches=self.branches)

def pwb_write_data(self, s=None, regions=None, areas=None, subs=None, buses=None, loads=None, 
    gens=None, shunts=None, branches=None):
    if s is None:
        s = self.esa
    
    if regions is not None:
        regions = tuple(regions)
        sa_data = {
            f[1]:[getattr(region, f[0]) for region in regions]
            for f in self.sa_pw_fields
        }
        sa_data["SAName"] = [region.name for region in regions]
        sa_df = pd.DataFrame.from_dict(sa_data)
        s.change_parameters_multiple_element_df("superarea", sa_df)
    
    if areas is not None:
        areas = tuple(areas)
        area_data = {
            f[1]:[getattr(area, f[0]) for area in areas]
            for f in self.area_pw_fields
        }
        area_data["AreaNum"] = [area.number for area in areas]
        area_df = pd.DataFrame.from_dict(area_data)
        s.change_parameters_multiple_element_df("area", area_df)
            
    if subs is not None:
        subs = tuple(subs)
        sub_data = {
            f[1]:[getattr(sub, f[0]) for sub in subs]
            for f in self.sub_pw_fields
        }
        sub_data["SubNum"] = [sub.number for sub in subs]
        sub_df = pd.DataFrame.from_dict(sub_data)
        s.change_parameters_multiple_element_df("substation", sub_df)
            
    if buses is not None:
        buses = tuple(buses)
        bus_data = {
            f[1]:[getattr(bus, f[0]) for bus in buses]
            for f in self.bus_pw_fields
        }
        bus_data["BusNum"] = [bus.number for bus in buses]
        bus_df = pd.DataFrame.from_dict(bus_data)
        s.change_parameters_multiple_element_df("bus", bus_df)

    if gens is not None:
        gens = tuple(gens)
        gen_data = {
            f[1]:[getattr(gen, f[0]) for gen in gens]
            for f in self.gen_pw_fields
        }
        gen_data["BusNum"] = [gen.bus.number for gen in gens]
        gen_data["GenID"] = [gen.id for gen in gens]
        gen_df = pd.DataFrame.from_dict(gen_data)
        s.change_parameters_multiple_element_df("gen", gen_df)

    if loads is not None:
        loads = tuple(loads)
        load_data = {
            f[1]:[getattr(load, f[0]) for load in loads]
            for f in self.load_pw_fields
        }
        load_data["BusNum"] = [load.bus.number for load in loads]
        load_data["LoadID"] = [load.id for load in loads]
        load_df = pd.DataFrame.from_dict(load_data)
        s.change_parameters_multiple_element_df("load", load_df)

    if branches is not None:
        branches = tuple(branches)
        branch_data = {
            f[1]:[getattr(branch, f[0]) for branch in branches]
            for f in self.branch_pw_fields
        }
        branch_data["BusNum"] = [branch.from_bus.number for branch in branches]
        branch_data["BusNum:1"] = [branch.to_bus.number for branch in branches]
        branch_data["LineCircuit"] = [branch.id for branch in branches]
        branch_df = pd.DataFrame.from_dict(branch_data)
        s.change_parameters_multiple_element_df("branch", branch_df)

    if shunts is not None:
        shunts = tuple(shunts)
        shunt_data = {
            f[1]:[getattr(shunt, f[0]) for shunt in shunts]
            for f in self.shunt_pw_fields
        }
        shunt_data["BusNum"] = [shunt.bus.number for shunt in shunts]
        shunt_data["ShuntID"] = [shunt.id for shunt in shunts]
        shunt_df = pd.DataFrame.from_dict(shunt_data)
        s.change_parameters_multiple_element_df("shunt", shunt_df)

def json_save(self, fname):
    obj = {"regions":{}}
    with open(fname, "w") as f:
        f.write(json.dumps(obj))