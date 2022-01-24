from shyft.time_series import DoubleVector,time,ModelInfo,ModelInfoVector
from os import path

# The absolute import here is PyCharm specific. Please consider removing this when PyCharm improves!
from ._core import *
from .model_repository import ModelRepository
import functools
from typing import Callable, Any, List, Generator, Union

from ...utilities.environ_util import add_lib_path
add_lib_path()


class EnergyMarketCorePropertyError(Exception):
    """Error type for when a C++ object's property fails, but
    it shouldn't attempt __getattr__ afterwards."""
    pass


def no_getattr_if_exception(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """
    Decorator for energy_market.core properties that might throw AttributeErrors,
    but that we don't want to continue into __getattr__.
    Instead we want it to throw the error received from the first attempt.
    """
    @functools.wraps(func)
    def wrapped_func(self: Any) -> Any:
        try:
            return func(self)
        except AttributeError as err:
            raise EnergyMarketCorePropertyError(f"Error in {self.__class__}.{func.__name__}: {err}")
    return wrapped_func


class requires_data_object:
    """
    Decorator class for functions for lazy evaluations of Energy Market Core object attributes.
    The decorator checks whether "obj"-attribute has been set, and if not, applies a user-defined function
    to construct obj, before making the function call.
    """
    def __init__(self, construct_func):
        """
        :param construct_func: Function that's assumed to take one positional argument and return anything.
            Intended usage is that construct_func takes em.core.<Python wrapped C++ object> and construct
            an instance of some Python object that will help in mimicking the interfaces found in statkraft.ltm classes.
        """
        self.construct_func = construct_func

    def __call__(self, func):
        """
        Decorator function.
        :param func: Function to be decorated.
            Intended usage is that func should be a class method, and so the first argument should be "self".
        :return:  Decorated function that first constructs Python object, if necessary.
        """
        @functools.wraps(func)
        def wrapped_func(cppobj, *args, **kwargs):
            if cppobj.obj is None:
                wrapped_func.counter += 1
                cppobj.obj = self.construct_func(cppobj)
            return func(cppobj, *args, **kwargs)
        wrapped_func.counter = 0
        return wrapped_func


def get_dir(self) -> List:
    """
    Appends the content of __dir__ from the Python object to "self"
    :param self: A python-wrapped C++ object
    :return: [List] The updated self.__dir__()
    """
    return sorted(set(super(self.__class__, self).__dir__() + self.obj.__dir__()))


def get_object_attribute(self, attr):
    """
    Exposes the attributes of self's object to self (Self is a Python-wrapped C++ object and self's object is a
    Python object). Should be decorated with get_attribute_for_core_objects together with a suitable function to
    construct self.obj from self.
    """
    return getattr(self.obj, attr)


def get_item_from_name(self, key: Union[str, int]):
    """
    Returns the element in the self (a C++ std::vector object) having key as index or element name.

    :param self: A C++ std::vector object
    :param key: An integer, slice or string (element name)
    :return: The element with the corresponding key
    """
    if isinstance(key, str):
        item = None
        for obj in self:
            if key == obj.name:
                item = obj
                break
        if item is None:
            raise RuntimeError("Object not found in the list.")
        return item
    else:
        return self.get_item_old(key)


def get_item_from_id(self, key: Union[str, int]):
    """
    Returns the element in the self (C++ std::vector object) having key as index or element id.
    :param self: A C++ std::vector object
    :param key: An integer, slice or string (element id)
    :return: The element with the corresponding key
    """
    if isinstance(key, str):
        item = None
        ikey = int(key)
        for obj in self:
            if ikey == obj.id:
                item = obj
                break
        if item is None:
            raise RuntimeError("Object not found in the list.")
        return item
    else:
        return self.get_item_old(key)


def get_name_based_items(self) -> Generator:
    """
    Creates a generator of elements contained in self (a C++ std::vector). Solely implemented to imitate the items()
    method of a python dictionary.
    :param self: A C++ std::vector object
    :return: A generator containing a tuple of elements and the corresponding element ids
    """
    return ((item.name, item) for item in self)


def get_id_based_items(self) -> Generator:
    """
    Creates a generator of elements contained in self (a C++ std::vector). Solely implemented to imitate the items()
    method of a python dictionary.
    :param self: A C++ std::vector object
    :return: A generator containing a tuple of elements and the corresponding element ids
    """
    return ((str(item.id), item) for item in self)


def get_values(self) -> Generator:
    """
    Creates a generator for the elements contained in self, which is a C++ std::vector object. The purpose of this
    method is to imitate the values() method of a Python dictionary.
    :param self: A C++ std::vector object
    :return: A generator containing a tuple of elements
    """
    return (item for item in self)


def get_name_based_keys(self) -> Generator:
    """
    Creates a generator for the element names contained in self, which is a C++ std::vector object. The purpose of this
    method is to imitate the keys() method of a Python dictionary.
    :param self: A C++ std::vector object
    :return: A generator containing a tuple of element names
    """
    return (item.name for item in self)


def get_id_based_keys(self) -> Generator:
    """
    Creates a generator for the element ids contained in self, which is a C++ std::vector object. The purpose of this
    method is to imitate the keys() method of a Python dictionary.
    :param self: A C++ std::vector object
    :return: A generator containing a tuple of element ids
    """
    return (str(item.id) for item in self)


def add_hydro_connection_lists(self, x: HydroConnectionList) -> HydroConnectionList:
    """
    Overloads the addition operator (+) for HydroConnectionList
    :param self: A HydroConnectionList
    :param x: Another HydroConnectionList
    :return: self
    """
    self.extend(x)
    return self


def list_class_str(self) -> str:
    """
    String representation for the C++ List classes.
    """
    objects = ", ".join([f"{k}: {str(v)}" for k, v in self.items()])
    return f"{self.__class__.__name__}[{objects}]"


def dict_class_str(self) -> str:
    """
    String representation for the Python-wrapped C++ Dict class.
    """
    elements = ", ".join([str(item.data()) for item in self])
    return f"{self.__class__.__name__}[{elements}]"


def hydro_connection_list_str(self) -> str:
    """
    String representation for the Python-wrapped C++ HydroConnectionList class.
    """
    objects = ", ".join([f"(target:{str(v.target)}, role={v.role})" for v in self])
    return f"{self.__class__.__name__}[{objects}]"


def add_methods_to_id_based_interface(cls):
    """
    Adds Python-Dict methods to C++ std::vector (used for id-based dicts, e.g., std::vector<hydro_component_>)
    :param cls: A Python-wrapped C++ std::vector object
    :return: cls with methods items(), values(), and keys()
    """
    cls.items = get_id_based_items
    cls.values = get_values
    cls.keys = get_id_based_keys
    cls.get_item_old = cls.__getitem__
    cls.__getitem__ = get_item_from_id
    cls.__contains__ = lambda self, key: key in self.keys()
    cls.__str__ = list_class_str
    return cls


def add_methods_to_name_based_interface(cls):
    """
    Adds Python-Dict methods to C++ vector (used for name-based dicts, e.g., std::vector<hydro_power_system_>)
    :param cls: A Python-wrapped C++ vector object
    :return: cls with methods items(), values(), and keys()
    """
    cls.items = get_name_based_items
    cls.values = get_values
    cls.keys = get_name_based_keys
    cls.get_item_old = cls.__getitem__
    cls.__getitem__ = get_item_from_name
    cls.__contains__ = lambda self, key: key in self.keys()
    cls.__str__ = list_class_str
    return cls


# **********************************************************************************************************************
#                   Backward compatibility
# **********************************************************************************************************************
Aggregate = Unit
AggregateList = UnitList
PowerStation = PowerPlant
PowerStationList = PowerPlantList
WaterRoute = Waterway
WaterRouteList = WaterwayList

HydroPowerSystem.create_river = lambda self, uid, name, json="": HydroPowerSystemBuilder(self).create_river(uid, name, json)
HydroPowerSystem.create_tunnel = lambda self, uid, name, json="": HydroPowerSystemBuilder(self).create_tunnel(uid, name, json)
HydroPowerSystem.create_aggregate = lambda self, uid, name, json="": HydroPowerSystemBuilder(self).create_unit(uid, name, json)
HydroPowerSystem.create_unit = lambda self, uid, name, json="": HydroPowerSystemBuilder(self).create_unit(uid, name, json)
HydroPowerSystem.create_gate = lambda self, uid, name, json="": HydroPowerSystemBuilder(self).create_gate(uid, name, json)

HydroPowerSystem.create_power_station = lambda self, uid, name, json="": HydroPowerSystemBuilder(self).create_power_plant(uid, name, json)
HydroPowerSystem.create_power_plant = lambda self, uid, name, json="": HydroPowerSystemBuilder(self).create_power_plant(uid, name, json)
HydroPowerSystem.create_reservoir = lambda self, uid, name, json="": HydroPowerSystemBuilder(self).create_reservoir(uid, name, json)
HydroPowerSystem.create_catchment = lambda self, uid, name, json="": HydroPowerSystemBuilder(self).create_catchment(uid, name, json)
HydroPowerSystem.to_blob = lambda self: HydroPowerSystem.to_blob_ref(self)

# fixup building Model, ModelArea
Model.create_model_area = lambda self, uid, name, json="": ModelBuilder(self).create_model_area(uid, name, json)
Model.create_power_module = lambda self, area, uid, name, json="": ModelBuilder(self).create_power_module( uid, name, json, area)
Model.create_power_line = lambda self, a, b, uid, name, json="": ModelBuilder(self).create_power_line(uid, name, json, a, b)
ModelArea.create_power_module = lambda self, uid, name, json="": ModelBuilder(self.model).create_power_module(uid, name, json,self)


# **********************************************************************************************************************
#                       Add Python Dictionary/List properties to C++ vectors/maps
# **********************************************************************************************************************
ReservoirList = add_methods_to_id_based_interface(ReservoirList)
WaterRouteList = add_methods_to_id_based_interface(WaterRouteList)
AggregateList = add_methods_to_id_based_interface(AggregateList)
GateList = add_methods_to_id_based_interface(GateList)
CatchmentList = add_methods_to_id_based_interface(CatchmentList)
PowerStationList = add_methods_to_id_based_interface(PowerStationList)
HydroComponentList = add_methods_to_id_based_interface(HydroComponentList)
HydroPowerSystemList = add_methods_to_name_based_interface(HydroPowerSystemList)

HydroConnectionList.__add__ = add_hydro_connection_lists
HydroConnectionList.__str__ = hydro_connection_list_str

ModelList = add_methods_to_id_based_interface(ModelList)
ModelAreaDict.__str__ = dict_class_str
PowerLineList = add_methods_to_name_based_interface(PowerLineList)
PowerModuleDict = add_methods_to_id_based_interface(PowerModuleDict)
HydroPowerSystemDict.items = lambda self: ((item.data().name, item.data()) for item in self)
HydroPowerSystemDict.keys = lambda self: (item.data().name for item in self)


def create_model_service(model_directory:str , storage_type: str ='blob'):
    """
    Create and return the client for the Ltm model service

    Parameters
    ----------
    model_directory:
        specifies the network host name, ip, name
    storage_type:
        specifies type of api-service, ('blob')
        default = 'blob'

    """
    if storage_type == 'blob':
        if not path.exists(model_directory):
            raise RuntimeError("Model directory does not exists:'{0}'".format(model_directory))

        if not path.isdir(model_directory):
            raise RuntimeError("Specified model directory is not a directory:'{0}'".format(model_directory))

        return ModelRepository(model_directory)

    raise RuntimeError("unknown service storage type specified, please support 'db' or 'blob'")

# need to create the `__all__` attribute for documentation.
# if you want sphinx-apidoc to autodoc a module/class it should be
# included below.
# generate using ipython: from `shyft.energy_market.core._core *` and `dir()`, then clean
# concatenate several lists from this file and from the list you create:
__all__ = [
 'Catchment',
 'CatchmentList',
 'Client',
 'ConnectionRole',
 'Gate',
 'GateList',
 'HydroComponent',
 'HydroComponentList',
 'HydroConnection',
 'HydroConnectionList',
 'HydroGraphTraversal',
 'HydroPowerSystem',
 'HydroPowerSystemBuilder',
 'HydroPowerSystemDict',
 'HydroPowerSystemList',
 'In',
 'IntStringDict',
 'Model',
 'ModelArea',
 'ModelAreaDict',
 'ModelBuilder',
 'ModelInfo',
 'ModelInfoVector',
 'ModelList',
 'Out',
 'Point',
 'PointList',
 'PowerLine',
 'PowerLineList',
 'PowerModule',
 'PowerModuleDict',
 'PowerPlant',
 'PowerPlantList',
 'R_CREATED',
 'R_FAILED',
 'R_FINISHED_RUN',
 'R_FROZEN',
 'R_PREP_INPUT',
 'R_READ_RESULT',
 'R_RUNNING',
 'Reservoir',
 'ReservoirList',
 'Run',
 'RunClient',
 'RunServer',
 'RunVector',
 'Server',
 'TurbineDescription',
 'TurbineEfficiency',
 'TurbineEfficiencyList',
 'Unit',
 'UnitList',
 'Waterway',
 'WaterwayList',
 'XyPointCurve',
 'XyPointCurveList',
 'XyPointCurveWithZ',
 'XyPointCurveWithZList',
 'bypass',
 'compressed_size',
 'flood',
 'input',
 'main',
 'points_from_x_y',
 'run_state'
]
