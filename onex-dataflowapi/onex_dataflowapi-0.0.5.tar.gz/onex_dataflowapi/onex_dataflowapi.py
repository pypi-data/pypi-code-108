# Distributed System Emulator Dataflow API and Data Models 0.0.1
# License: MIT

import importlib
import logging
import json
import yaml
import requests
import urllib3
import io
import sys
import time
import re

try:
    from typing import Union, Dict, List, Any, Literal
except ImportError:
    from typing_extensions import Literal

if sys.version_info[0] == 3:
    unicode = str


def api(location=None, verify=True, logger=None, loglevel=logging.INFO, ext=None):
    """Create an instance of an Api class

    generator.Generator outputs a base Api class with the following:
    - an abstract method for each OpenAPI path item object
    - a concrete properties for each unique OpenAPI path item parameter.

    generator.Generator also outputs an HttpApi class that inherits the base
    Api class, implements the abstract methods and uses the common HttpTransport
    class send_recv method to communicate with a REST based server.

    Args
    ----
    - location (str): The location of an Open Traffic Generator server.
    - verify (bool): Verify the server's TLS certificate, or a string, in which
      case it must be a path to a CA bundle to use. Defaults to `True`.
      When set to `False`, requests will accept any TLS certificate presented by
      the server, and will ignore hostname mismatches and/or expired
      certificates, which will make your application vulnerable to
      man-in-the-middle (MitM) attacks. Setting verify to `False`
      may be useful during local development or testing.
    - logger (logging.Logger): A user defined logging.logger, if none is provided
      then a default logger with a stdout handler will be provided
    - loglevel (logging.loglevel): The logging package log level.
      The default loglevel is logging.INFO
    - ext (str): Name of an extension package
    """
    params = locals()
    if ext is None:
        return HttpApi(**params)
    try:
        lib = importlib.import_module("sanity_{}.onex_dataflowapi_api".format(ext))
        return lib.Api(**params)
    except ImportError as err:
        msg = "Extension %s is not installed or invalid: %s"
        raise Exception(msg % (ext, err))


class HttpTransport(object):
    def __init__(self, **kwargs):
        """Use args from api() method to instantiate an HTTP transport"""
        self.location = (
            kwargs["location"]
            if "location" in kwargs and kwargs["location"] is not None
            else "https://localhost:443"
        )
        self.verify = kwargs["verify"] if "verify" in kwargs else False
        self.logger = kwargs["logger"] if "logger" in kwargs else None
        self.loglevel = kwargs["loglevel"] if "loglevel" in kwargs else logging.DEBUG
        if self.logger is None:
            stdout_handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(fmt="%(asctime)s [%(name)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            formatter.converter = time.gmtime
            stdout_handler.setFormatter(formatter)
            self.logger = logging.Logger(self.__module__, level=self.loglevel)
            self.logger.addHandler(stdout_handler)
        self.logger.debug("HttpTransport args: {}".format(", ".join(["{}={!r}".format(k, v) for k, v in kwargs.items()])))
        if self.verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            self.logger.warning("Certificate verification is disabled")
        self._session = requests.Session()

    def send_recv(self, method, relative_url, payload=None, return_object=None, headers=None):
        url = "%s%s" % (self.location, relative_url)
        data = None
        headers = headers or {"Content-Type": "application/json"}
        if payload is not None:
            if isinstance(payload, bytes):
                data = payload
                headers["Content-Type"] = "application/octet-stream"
            elif isinstance(payload, (str, unicode)):
                data = payload
            elif isinstance(payload, OpenApiBase):
                data = payload.serialize()
            else:
                raise Exception("Type of payload provided is unknown")
        response = self._session.request(
            method=method,
            url=url,
            data=data,
            verify=False,
            allow_redirects=True,
            # TODO: add a timeout here
            headers=headers,
        )
        if response.ok:
            if "application/json" in response.headers["content-type"]:
                # TODO: we might want to check for utf-8 charset and decode
                # accordingly, but current impl works for now
                response_dict = yaml.safe_load(response.text)
                if return_object is None:
                    # if response type is not provided, return dictionary
                    # instead of python object
                    return response_dict
                else:
                    return return_object.deserialize(response_dict)
            elif "application/octet-stream" in response.headers["content-type"]:
                return io.BytesIO(response.content)
            else:
                # TODO: for now, return bare response object for unknown
                # content types
                return response
        else:
            raise Exception(response.status_code, yaml.safe_load(response.text))


class OpenApiBase(object):
    """Base class for all generated classes"""

    JSON = "json"
    YAML = "yaml"
    DICT = "dict"

    __slots__ = ()

    def __init__(self):
        pass

    def serialize(self, encoding=JSON):
        """Serialize the current object according to a specified encoding.

        Args
        ----
        - encoding (str[json, yaml, dict]): The object will be recursively
            serialized according to the specified encoding.
            The supported encodings are json, yaml and python dict.

        Returns
        -------
        - obj(Union[str, dict]): A str or dict object depending on the specified
            encoding. The json and yaml encodings will return a str object and
            the dict encoding will return a python dict object.
        """
        if encoding == OpenApiBase.JSON:
            return json.dumps(self._encode(), indent=2, sort_keys=True)
        elif encoding == OpenApiBase.YAML:
            return yaml.safe_dump(self._encode())
        elif encoding == OpenApiBase.DICT:
            return self._encode()
        else:
            raise NotImplementedError("Encoding %s not supported" % encoding)

    def _encode(self):
        raise NotImplementedError()

    def deserialize(self, serialized_object):
        """Deserialize a python object into the current object.

        If the input `serialized_object` does not match the current
        openapi object an exception will be raised.

        Args
        ----
        - serialized_object (Union[str, dict]): The object to deserialize.
            If the serialized_object is of type str then the internal encoding
            of the serialized_object must be json or yaml.

        Returns
        -------
        - obj(OpenApiObject): This object with all the
            serialized_object deserialized within.
        """
        if isinstance(serialized_object, (str, unicode)):
            serialized_object = yaml.safe_load(serialized_object)
        self._decode(serialized_object)
        return self

    def _decode(self, dict_object):
        raise NotImplementedError()


class OpenApiValidator(object):

    __slots__ = ()

    def __init__(self):
        pass

    def validate_mac(self, mac):
        if mac is None or not isinstance(mac, (str, unicode)) or mac.count(" ") != 0:
            return False
        try:
            if len(mac) != 17:
                return False
            return all([0 <= int(oct, 16) <= 255 for oct in mac.split(":")])
        except Exception:
            return False

    def validate_ipv4(self, ip):
        if ip is None or not isinstance(ip, (str, unicode)) or ip.count(" ") != 0:
            return False
        if len(ip.split(".")) != 4:
            return False
        try:
            return all([0 <= int(oct) <= 255 for oct in ip.split(".", 3)])
        except Exception:
            return False

    def validate_ipv6(self, ip):
        if ip is None or not isinstance(ip, (str, unicode)):
            return False
        ip = ip.strip()
        if ip.count(" ") > 0 or ip.count(":") > 7 or ip.count("::") > 1 or ip.count(":::") > 0:
            return False
        if (ip[0] == ":" and ip[:2] != "::") or (ip[-1] == ":" and ip[-2:] != "::"):
            return False
        if ip.count("::") == 0 and ip.count(":") != 7:
            return False
        if ip == "::":
            return True
        if ip[:2] == "::":
            ip = ip.replace("::", "0:")
        elif ip[-2:] == "::":
            ip = ip.replace("::", ":0")
        else:
            ip = ip.replace("::", ":0:")
        try:
            return all([True if (0 <= int(oct, 16) <= 65535) and (1 <= len(oct) <= 4) else False for oct in ip.split(":")])
        except Exception:
            return False

    def validate_hex(self, hex):
        if hex is None or not isinstance(hex, (str, unicode)):
            return False
        try:
            int(hex, 16)
            return True
        except Exception:
            return False

    def validate_integer(self, value, min, max):
        if value is None or not isinstance(value, int):
            return False
        if value < 0:
            return False
        if min is not None and value < min:
            return False
        if max is not None and value > max:
            return False
        return True

    def validate_float(self, value):
        return isinstance(value, (int, float))

    def validate_string(self, value, min_length, max_length):
        if value is None or not isinstance(value, (str, unicode)):
            return False
        if min_length is not None and len(value) < min_length:
            return False
        if max_length is not None and len(value) > max_length:
            return False
        return True

    def validate_bool(self, value):
        return isinstance(value, bool)

    def validate_list(self, value, itemtype, min, max, min_length, max_length):
        if value is None or not isinstance(value, list):
            return False
        v_obj = getattr(self, "validate_{}".format(itemtype), None)
        if v_obj is None:
            raise AttributeError("{} is not a valid attribute".format(itemtype))
        v_obj_lst = []
        for item in value:
            if itemtype == "integer":
                v_obj_lst.append(v_obj(item, min, max))
            elif itemtype == "string":
                v_obj_lst.append(v_obj(item, min_length, max_length))
            else:
                v_obj_lst.append(v_obj(item))
        return v_obj_lst

    def validate_binary(self, value):
        if value is None or not isinstance(value, (str, unicode)):
            return False
        return all([True if int(bin) == 0 or int(bin) == 1 else False for bin in value])

    def types_validation(self, value, type_, err_msg, itemtype=None, min=None, max=None, min_length=None, max_length=None):
        type_map = {int: "integer", str: "string", float: "float", bool: "bool", list: "list", "int64": "integer", "int32": "integer", "double": "float"}
        if type_ in type_map:
            type_ = type_map[type_]
        if itemtype is not None and itemtype in type_map:
            itemtype = type_map[itemtype]
        v_obj = getattr(self, "validate_{}".format(type_), None)
        if v_obj is None:
            msg = "{} is not a valid or unsupported format".format(type_)
            raise TypeError(msg)
        if type_ == "list":
            verdict = v_obj(value, itemtype, min, max, min_length, max_length)
            if all(verdict) is True:
                return
            err_msg = "{} \n {} are not valid".format(err_msg, [value[index] for index, item in enumerate(verdict) if item is False])
            verdict = False
        elif type_ == "integer":
            verdict = v_obj(value, min, max)
            if verdict is True:
                return
            min_max = ""
            if min is not None:
                min_max = ", expected min {}".format(min)
            if max is not None:
                min_max = min_max + ", expected max {}".format(max)
            err_msg = "{} \n got {} of type {} {}".format(err_msg, value, type(value), min_max)
        elif type_ == "string":
            verdict = v_obj(value, min_length, max_length)
            if verdict is True:
                return
            msg = ""
            if min_length is not None:
                msg = ", expected min {}".format(min_length)
            if max_length is not None:
                msg = msg + ", expected max {}".format(max_length)
            err_msg = "{} \n got {} of type {} {}".format(err_msg, value, type(value), msg)
        else:
            verdict = v_obj(value)
        if verdict is False:
            raise TypeError(err_msg)


class OpenApiObject(OpenApiBase, OpenApiValidator):
    """Base class for any /components/schemas object

    Every OpenApiObject is reuseable within the schema so it can
    exist in multiple locations within the hierarchy.
    That means it can exist in multiple locations as a
    leaf, parent/choice or parent.
    """

    __slots__ = ("_properties", "_parent", "_choice")
    _DEFAULTS = {}
    _TYPES = {}
    _REQUIRED = []

    def __init__(self, parent=None, choice=None):
        super(OpenApiObject, self).__init__()
        self._parent = parent
        self._choice = choice
        self._properties = {}

    @property
    def parent(self):
        return self._parent

    def _set_choice(self, name):
        if self._has_choice(name):
            for enum in self._TYPES["choice"]["enum"]:
                if enum in self._properties and name != enum:
                    self._properties.pop(enum)
            self._properties["choice"] = name

    def _has_choice(self, name):
        if "choice" in dir(self) and "_TYPES" in dir(self) and "choice" in self._TYPES and name in self._TYPES["choice"]["enum"]:
            return True
        else:
            return False

    def _get_property(self, name, default_value=None, parent=None, choice=None):
        if name in self._properties and self._properties[name] is not None:
            return self._properties[name]
        if isinstance(default_value, type) is True:
            self._set_choice(name)
            if "_choice" in default_value.__slots__:
                self._properties[name] = default_value(parent=parent, choice=choice)
            else:
                self._properties[name] = default_value(parent=parent)
            if "_DEFAULTS" in dir(self._properties[name]) and "choice" in self._properties[name]._DEFAULTS:
                getattr(self._properties[name], self._properties[name]._DEFAULTS["choice"])
        else:
            if default_value is None and name in self._DEFAULTS:
                self._set_choice(name)
                self._properties[name] = self._DEFAULTS[name]
            else:
                self._properties[name] = default_value
        return self._properties[name]

    def _set_property(self, name, value, choice=None):
        if name in self._DEFAULTS and value is None:
            self._set_choice(name)
            self._properties[name] = self._DEFAULTS[name]
        else:
            self._set_choice(name)
            self._properties[name] = value
        if self._parent is not None and self._choice is not None and value is not None:
            self._parent._set_property("choice", self._choice)

    def _encode(self):
        """Helper method for serialization"""
        output = {}
        self._validate_required()
        for key, value in self._properties.items():
            self._validate_types(key, value)
            if isinstance(value, (OpenApiObject, OpenApiIter)):
                output[key] = value._encode()
            elif value is not None:
                if key in self._TYPES and "format" in self._TYPES[key] and self._TYPES[key]["format"] == "int64":
                    value = str(value)
                output[key] = value
        return output

    def _decode(self, obj):
        dtypes = [list, str, int, float, bool]
        for property_name, property_value in obj.items():
            if property_name in self._TYPES:
                if isinstance(property_value, dict):
                    child = self._get_child_class(property_name)
                    if "choice" in child[1]._TYPES and "_parent" in child[1].__slots__:
                        property_value = child[1](self, property_name)._decode(property_value)
                    elif "_parent" in child[1].__slots__:
                        property_value = child[1](self)._decode(property_value)
                    else:
                        property_value = child[1]()._decode(property_value)
                elif isinstance(property_value, list) and property_name in self._TYPES and self._TYPES[property_name]["type"] not in dtypes:
                    child = self._get_child_class(property_name, True)
                    openapi_list = child[0]()
                    for item in property_value:
                        item = child[1]()._decode(item)
                        openapi_list._items.append(item)
                    property_value = openapi_list
                elif property_name in self._DEFAULTS and property_value is None:
                    if isinstance(self._DEFAULTS[property_name], tuple(dtypes)):
                        property_value = self._DEFAULTS[property_name]
                self._set_choice(property_name)
                if "format" in self._TYPES[property_name] and self._TYPES[property_name]["format"] == "int64":
                    property_value = int(property_value)
                self._properties[property_name] = property_value
            self._validate_types(property_name, property_value)
        self._validate_required()
        return self

    def _get_child_class(self, property_name, is_property_list=False):
        list_class = None
        class_name = self._TYPES[property_name]["type"]
        module = importlib.import_module(self.__module__)
        object_class = getattr(module, class_name)
        if is_property_list is True:
            list_class = object_class
            object_class = getattr(module, class_name[0:-4])
        return (list_class, object_class)

    def __str__(self):
        return self.serialize(encoding=self.YAML)

    def __deepcopy__(self, memo):
        """Creates a deep copy of the current object"""
        return self.__class__().deserialize(self.serialize())

    def __copy__(self):
        """Creates a deep copy of the current object"""
        return self.__deepcopy__(None)

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def clone(self):
        """Creates a deep copy of the current object"""
        return self.__deepcopy__(None)

    def _validate_required(self):
        """Validates the required properties are set
        Use getattr as it will set any defaults prior to validating
        """
        if getattr(self, "_REQUIRED", None) is None:
            return
        for name in self._REQUIRED:
            if getattr(self, name, None) is None:
                msg = "{} is a mandatory property of {}" " and should not be set to None".format(
                    name,
                    self.__class__,
                )
                raise ValueError(msg)

    def _validate_types(self, property_name, property_value):
        common_data_types = [list, str, int, float, bool]
        if property_name not in self._TYPES:
            # raise ValueError("Invalid Property {}".format(property_name))
            return
        details = self._TYPES[property_name]
        if property_value is None and property_name not in self._DEFAULTS and property_name not in self._REQUIRED:
            return
        if "enum" in details and property_value not in details["enum"]:
            msg = "property {} shall be one of these" " {} enum, but got {} at {}"
            raise TypeError(msg.format(property_name, details["enum"], property_value, self.__class__))
        if details["type"] in common_data_types and "format" not in details:
            msg = "property {} shall be of type {} at {}".format(property_name, details["type"], self.__class__)
            self.types_validation(property_value, details["type"], msg, details.get("itemtype"), details.get("minimum"), details.get("maximum"),
                                  details.get("minLength"), details.get("maxLength"))

        if details["type"] not in common_data_types:
            class_name = details["type"]
            # TODO Need to revisit importlib
            module = importlib.import_module(self.__module__)
            object_class = getattr(module, class_name)
            if not isinstance(property_value, object_class):
                msg = "property {} shall be of type {}," " but got {} at {}"
                raise TypeError(msg.format(property_name, class_name, type(property_value), self.__class__))
        if "format" in details:
            msg = "Invalid {} format, expected {} at {}".format(property_value, details["format"], self.__class__)
            _type = details["type"] if details["type"] is list else details["format"]
            self.types_validation(property_value, _type, msg, details["format"], details.get("minimum"), details.get("maximum"),
                                  details.get("minLength"), details.get("maxLength"))

    def validate(self):
        self._validate_required()
        for key, value in self._properties.items():
            self._validate_types(key, value)

    def get(self, name, with_default=False):
        """
        getattr for openapi object
        """
        if self._properties.get(name) is not None:
            return self._properties[name]
        elif with_default:
            # TODO need to find a way to avoid getattr
            choice = self._properties.get("choice") if "choice" in dir(self) else None
            getattr(self, name)
            if "choice" in dir(self):
                if choice is None and "choice" in self._properties:
                    self._properties.pop("choice")
                else:
                    self._properties["choice"] = choice
            return self._properties.pop(name)
        return None


class OpenApiIter(OpenApiBase):
    """Container class for OpenApiObject

    Inheriting classes contain 0..n instances of an OpenAPI components/schemas
    object.
    - config.flows.flow(name="1").flow(name="2").flow(name="3")

    The __getitem__ method allows getting an instance using ordinal.
    - config.flows[0]
    - config.flows[1:]
    - config.flows[0:1]
    - f1, f2, f3 = config.flows

    The __iter__ method allows for iterating across the encapsulated contents
    - for flow in config.flows:
    """

    __slots__ = ("_index", "_items")
    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self):
        super(OpenApiIter, self).__init__()
        self._index = -1
        self._items = []

    def __len__(self):
        return len(self._items)

    def _getitem(self, key):
        found = None
        if isinstance(key, int):
            found = self._items[key]
        elif isinstance(key, slice) is True:
            start, stop, step = key.indices(len(self))
            sliced = self.__class__()
            for i in range(start, stop, step):
                sliced._items.append(self._items[i])
            return sliced
        elif isinstance(key, str):
            for item in self._items:
                if item.name == key:
                    found = item
        if found is None:
            raise IndexError()
        if self._GETITEM_RETURNS_CHOICE_OBJECT is True and found._properties.get("choice") is not None:
            return found._properties[found._properties["choice"]]
        return found

    def _iter(self):
        self._index = -1
        return self

    def _next(self):
        if self._index + 1 >= len(self._items):
            raise StopIteration
        else:
            self._index += 1
        return self.__getitem__(self._index)

    def __getitem__(self, key):
        raise NotImplementedError("This should be overridden by the generator")

    def _add(self, item):
        self._items.append(item)
        self._index = len(self._items) - 1

    def remove(self, index):
        del self._items[index]
        self._index = len(self._items) - 1

    def append(self, item):
        """Append an item to the end of OpenApiIter
        TBD: type check, raise error on mismatch
        """
        if isinstance(item, OpenApiObject) is False:
            raise Exception("Item is not an instance of OpenApiObject")
        self._add(item)
        return self

    def clear(self):
        del self._items[:]
        self._index = -1

    def _encode(self):
        return [item._encode() for item in self._items]

    def _decode(self, encoded_list):
        item_class_name = self.__class__.__name__.replace("Iter", "")
        module = importlib.import_module(self.__module__)
        object_class = getattr(module, item_class_name)
        self.clear()
        for item in encoded_list:
            self._add(object_class()._decode(item))

    def __copy__(self):
        raise NotImplementedError("Shallow copy of OpenApiIter objects is not supported")

    def __deepcopy__(self, memo):
        raise NotImplementedError("Deep copy of OpenApiIter objects is not supported")

    def __str__(self):
        return yaml.safe_dump(self._encode())

    def __eq__(self, other):
        return self.__str__() == other.__str__()


class Config(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'hosts': {'type': 'HostIter'},
        'dataflow': {'type': 'Dataflow'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(Config, self).__init__()
        self._parent = parent

    @property
    def hosts(self):
        # type: () -> HostIter
        """hosts getter

        TBD

        Returns: HostIter
        """
        return self._get_property('hosts', HostIter, self._parent, self._choice)

    @property
    def dataflow(self):
        # type: () -> Dataflow
        """dataflow getter

        

        Returns: Dataflow
        """
        return self._get_property('dataflow', Dataflow)


class Host(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'name': {'type': str},
        'address': {'type': str},
        'prefix': {'type': int},
    } # type: Dict[str, str]

    _REQUIRED = ('address', 'name') # type: tuple(str)

    _DEFAULTS = {
        'prefix': 24,
    } # type: Dict[str, Union(type)]

    def __init__(self, parent=None, name=None, address=None, prefix=24):
        super(Host, self).__init__()
        self._parent = parent
        self._set_property('name', name)
        self._set_property('address', address)
        self._set_property('prefix', prefix)

    @property
    def name(self):
        # type: () -> str
        """name getter

        The name, uniquely identifying the host

        Returns: str
        """
        return self._get_property('name')

    @name.setter
    def name(self, value):
        """name setter

        The name, uniquely identifying the host

        value: str
        """
        self._set_property('name', value)

    @property
    def address(self):
        # type: () -> str
        """address getter

        The test address of the host

        Returns: str
        """
        return self._get_property('address')

    @address.setter
    def address(self, value):
        """address setter

        The test address of the host

        value: str
        """
        self._set_property('address', value)

    @property
    def prefix(self):
        # type: () -> int
        """prefix getter

        The prefix of the host

        Returns: int
        """
        return self._get_property('prefix')

    @prefix.setter
    def prefix(self, value):
        """prefix setter

        The prefix of the host

        value: int
        """
        self._set_property('prefix', value)


class HostIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(HostIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[Host]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> HostIter
        return self._iter()

    def __next__(self):
        # type: () -> Host
        return self._next()

    def next(self):
        # type: () -> Host
        return self._next()

    def host(self, name=None, address=None, prefix=24):
        # type: (str,str,int) -> HostIter
        """Factory method that creates an instance of the Host class

        TBD

        Returns: HostIter
        """
        item = Host(parent=self._parent, name=name, address=address, prefix=prefix)
        self._add(item)
        return self

    def add(self, name=None, address=None, prefix=24):
        # type: (str,str,int) -> Host
        """Add method that creates and returns an instance of the Host class

        TBD

        Returns: Host
        """
        item = Host(parent=self._parent, name=name, address=address, prefix=prefix)
        self._add(item)
        return item


class Dataflow(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'host_management': {'type': 'DataflowHostManagementIter'},
        'workload': {'type': 'DataflowWorkloadItemIter'},
        'flow_profiles': {'type': 'DataflowFlowProfileIter'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(Dataflow, self).__init__()
        self._parent = parent

    @property
    def host_management(self):
        # type: () -> DataflowHostManagementIter
        """host_management getter

        TBD

        Returns: DataflowHostManagementIter
        """
        return self._get_property('host_management', DataflowHostManagementIter, self._parent, self._choice)

    @property
    def workload(self):
        # type: () -> DataflowWorkloadItemIter
        """workload getter

        The workload items making up the dataflow

        Returns: DataflowWorkloadItemIter
        """
        return self._get_property('workload', DataflowWorkloadItemIter, self._parent, self._choice)

    @property
    def flow_profiles(self):
        # type: () -> DataflowFlowProfileIter
        """flow_profiles getter

        foo

        Returns: DataflowFlowProfileIter
        """
        return self._get_property('flow_profiles', DataflowFlowProfileIter, self._parent, self._choice)


class DataflowHostManagement(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'host_name': {'type': str},
        'management_address': {'type': str},
        'nic_name': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED = ('host_name', 'management_address', 'nic_name') # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, host_name=None, management_address=None, nic_name=None):
        super(DataflowHostManagement, self).__init__()
        self._parent = parent
        self._set_property('host_name', host_name)
        self._set_property('management_address', management_address)
        self._set_property('nic_name', nic_name)

    @property
    def host_name(self):
        # type: () -> str
        """host_name getter

        TBD. . x-constraint:. - #components/schemas/Host/properties/name. 

        Returns: str
        """
        return self._get_property('host_name')

    @host_name.setter
    def host_name(self, value):
        """host_name setter

        TBD. . x-constraint:. - #components/schemas/Host/properties/name. 

        value: str
        """
        self._set_property('host_name', value)

    @property
    def management_address(self):
        # type: () -> str
        """management_address getter

        Hostname or address of management interface of a server running dataflow traffic

        Returns: str
        """
        return self._get_property('management_address')

    @management_address.setter
    def management_address(self, value):
        """management_address setter

        Hostname or address of management interface of a server running dataflow traffic

        value: str
        """
        self._set_property('management_address', value)

    @property
    def nic_name(self):
        # type: () -> str
        """nic_name getter

        unique idenfier for the network interface card (nic), e.g. "eth1"

        Returns: str
        """
        return self._get_property('nic_name')

    @nic_name.setter
    def nic_name(self, value):
        """nic_name setter

        unique idenfier for the network interface card (nic), e.g. "eth1"

        value: str
        """
        self._set_property('nic_name', value)


class DataflowHostManagementIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(DataflowHostManagementIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[DataflowHostManagement]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> DataflowHostManagementIter
        return self._iter()

    def __next__(self):
        # type: () -> DataflowHostManagement
        return self._next()

    def next(self):
        # type: () -> DataflowHostManagement
        return self._next()

    def hostmanagement(self, host_name=None, management_address=None, nic_name=None):
        # type: (str,str,str) -> DataflowHostManagementIter
        """Factory method that creates an instance of the DataflowHostManagement class

        auxillary host information needed to run dataflow experiments

        Returns: DataflowHostManagementIter
        """
        item = DataflowHostManagement(parent=self._parent, host_name=host_name, management_address=management_address, nic_name=nic_name)
        self._add(item)
        return self

    def add(self, host_name=None, management_address=None, nic_name=None):
        # type: (str,str,str) -> DataflowHostManagement
        """Add method that creates and returns an instance of the DataflowHostManagement class

        auxillary host information needed to run dataflow experiments

        Returns: DataflowHostManagement
        """
        item = DataflowHostManagement(parent=self._parent, host_name=host_name, management_address=management_address, nic_name=nic_name)
        self._add(item)
        return item


class DataflowWorkloadItem(OpenApiObject):
    __slots__ = ('_parent','_choice')

    _TYPES = {
        'name': {'type': str},
        'choice': {
            'type': str,
            'enum': [
                'scatter',
                'gather',
                'all_reduce',
                'loop',
                'compute',
                'broadcast',
            ],
        },
        'scatter': {'type': 'DataflowScatterWorkload'},
        'gather': {'type': 'DataflowGatherWorkload'},
        'loop': {'type': 'DataflowLoopWorkload'},
        'compute': {'type': 'DataflowComputeWorkload'},
        'all_reduce': {'type': 'DataflowAllReduceWorkload'},
        'broadcast': {'type': 'DataflowBroadcastWorkload'},
    } # type: Dict[str, str]

    _REQUIRED = ('name', 'choice') # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    SCATTER = 'scatter' # type: str
    GATHER = 'gather' # type: str
    ALL_REDUCE = 'all_reduce' # type: str
    LOOP = 'loop' # type: str
    COMPUTE = 'compute' # type: str
    BROADCAST = 'broadcast' # type: str

    def __init__(self, parent=None, choice=None, name=None):
        super(DataflowWorkloadItem, self).__init__()
        self._parent = parent
        self._set_property('name', name)
        if 'choice' in self._DEFAULTS and choice is None:
            getattr(self, self._DEFAULTS['choice'])
        else:
            self.choice = choice

    @property
    def scatter(self):
        # type: () -> DataflowScatterWorkload
        """Factory property that returns an instance of the DataflowScatterWorkload class

        TBD

        Returns: DataflowScatterWorkload
        """
        return self._get_property('scatter', DataflowScatterWorkload, self, 'scatter')

    @property
    def gather(self):
        # type: () -> DataflowGatherWorkload
        """Factory property that returns an instance of the DataflowGatherWorkload class

        TBD

        Returns: DataflowGatherWorkload
        """
        return self._get_property('gather', DataflowGatherWorkload, self, 'gather')

    @property
    def all_reduce(self):
        # type: () -> DataflowAllReduceWorkload
        """Factory property that returns an instance of the DataflowAllReduceWorkload class

        TBD

        Returns: DataflowAllReduceWorkload
        """
        return self._get_property('all_reduce', DataflowAllReduceWorkload, self, 'all_reduce')

    @property
    def loop(self):
        # type: () -> DataflowLoopWorkload
        """Factory property that returns an instance of the DataflowLoopWorkload class

        TBD

        Returns: DataflowLoopWorkload
        """
        return self._get_property('loop', DataflowLoopWorkload, self, 'loop')

    @property
    def compute(self):
        # type: () -> DataflowComputeWorkload
        """Factory property that returns an instance of the DataflowComputeWorkload class

        TBD

        Returns: DataflowComputeWorkload
        """
        return self._get_property('compute', DataflowComputeWorkload, self, 'compute')

    @property
    def broadcast(self):
        # type: () -> DataflowBroadcastWorkload
        """Factory property that returns an instance of the DataflowBroadcastWorkload class

        TBD

        Returns: DataflowBroadcastWorkload
        """
        return self._get_property('broadcast', DataflowBroadcastWorkload, self, 'broadcast')

    @property
    def name(self):
        # type: () -> str
        """name getter

        uniquely identifies the workload item

        Returns: str
        """
        return self._get_property('name')

    @name.setter
    def name(self, value):
        """name setter

        uniquely identifies the workload item

        value: str
        """
        self._set_property('name', value)

    @property
    def choice(self):
        # type: () -> Union[Literal["all_reduce"], Literal["broadcast"], Literal["compute"], Literal["gather"], Literal["loop"], Literal["scatter"]]
        """choice getter

        The type of workflow item

        Returns: Union[Literal["all_reduce"], Literal["broadcast"], Literal["compute"], Literal["gather"], Literal["loop"], Literal["scatter"]]
        """
        return self._get_property('choice')

    @choice.setter
    def choice(self, value):
        """choice setter

        The type of workflow item

        value: Union[Literal["all_reduce"], Literal["broadcast"], Literal["compute"], Literal["gather"], Literal["loop"], Literal["scatter"]]
        """
        self._set_property('choice', value)


class DataflowScatterWorkload(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'sources': {
            'type': list,
            'itemtype': str,
        },
        'destinations': {
            'type': list,
            'itemtype': str,
        },
        'flow_profile_name': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, sources=None, destinations=None, flow_profile_name=None):
        super(DataflowScatterWorkload, self).__init__()
        self._parent = parent
        self._set_property('sources', sources)
        self._set_property('destinations', destinations)
        self._set_property('flow_profile_name', flow_profile_name)

    @property
    def sources(self):
        # type: () -> List[str]
        """sources getter

        list of host names, indicating the originator of the data

        Returns: List[str]
        """
        return self._get_property('sources')

    @sources.setter
    def sources(self, value):
        """sources setter

        list of host names, indicating the originator of the data

        value: List[str]
        """
        self._set_property('sources', value)

    @property
    def destinations(self):
        # type: () -> List[str]
        """destinations getter

        list of host names, indicating the destination of the data

        Returns: List[str]
        """
        return self._get_property('destinations')

    @destinations.setter
    def destinations(self, value):
        """destinations setter

        list of host names, indicating the destination of the data

        value: List[str]
        """
        self._set_property('destinations', value)

    @property
    def flow_profile_name(self):
        # type: () -> str
        """flow_profile_name getter

        flow profile reference

        Returns: str
        """
        return self._get_property('flow_profile_name')

    @flow_profile_name.setter
    def flow_profile_name(self, value):
        """flow_profile_name setter

        flow profile reference

        value: str
        """
        self._set_property('flow_profile_name', value)


class DataflowGatherWorkload(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'sources': {
            'type': list,
            'itemtype': str,
        },
        'destinations': {
            'type': list,
            'itemtype': str,
        },
        'flow_profile_name': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, sources=None, destinations=None, flow_profile_name=None):
        super(DataflowGatherWorkload, self).__init__()
        self._parent = parent
        self._set_property('sources', sources)
        self._set_property('destinations', destinations)
        self._set_property('flow_profile_name', flow_profile_name)

    @property
    def sources(self):
        # type: () -> List[str]
        """sources getter

        list of host names, indicating the originator of the data

        Returns: List[str]
        """
        return self._get_property('sources')

    @sources.setter
    def sources(self, value):
        """sources setter

        list of host names, indicating the originator of the data

        value: List[str]
        """
        self._set_property('sources', value)

    @property
    def destinations(self):
        # type: () -> List[str]
        """destinations getter

        list of host names, indicating the destination of the data

        Returns: List[str]
        """
        return self._get_property('destinations')

    @destinations.setter
    def destinations(self, value):
        """destinations setter

        list of host names, indicating the destination of the data

        value: List[str]
        """
        self._set_property('destinations', value)

    @property
    def flow_profile_name(self):
        # type: () -> str
        """flow_profile_name getter

        flow profile reference

        Returns: str
        """
        return self._get_property('flow_profile_name')

    @flow_profile_name.setter
    def flow_profile_name(self, value):
        """flow_profile_name setter

        flow profile reference

        value: str
        """
        self._set_property('flow_profile_name', value)


class DataflowLoopWorkload(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'iterations': {'type': int},
        'children': {'type': 'DataflowWorkloadItemIter'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, iterations=None):
        super(DataflowLoopWorkload, self).__init__()
        self._parent = parent
        self._set_property('iterations', iterations)

    @property
    def iterations(self):
        # type: () -> int
        """iterations getter

        number of iterations in the loop

        Returns: int
        """
        return self._get_property('iterations')

    @iterations.setter
    def iterations(self, value):
        """iterations setter

        number of iterations in the loop

        value: int
        """
        self._set_property('iterations', value)

    @property
    def children(self):
        # type: () -> DataflowWorkloadItemIter
        """children getter

        list of workload items that are executed in this loop

        Returns: DataflowWorkloadItemIter
        """
        return self._get_property('children', DataflowWorkloadItemIter, self._parent, self._choice)


class DataflowWorkloadItemIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(DataflowWorkloadItemIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[DataflowAllReduceWorkload, DataflowBroadcastWorkload, DataflowComputeWorkload, DataflowGatherWorkload, DataflowLoopWorkload, DataflowScatterWorkload, DataflowWorkloadItem]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> DataflowWorkloadItemIter
        return self._iter()

    def __next__(self):
        # type: () -> DataflowWorkloadItem
        return self._next()

    def next(self):
        # type: () -> DataflowWorkloadItem
        return self._next()

    def workloaditem(self, name=None):
        # type: (str) -> DataflowWorkloadItemIter
        """Factory method that creates an instance of the DataflowWorkloadItem class

        TBD

        Returns: DataflowWorkloadItemIter
        """
        item = DataflowWorkloadItem(parent=self._parent, choice=self._choice, name=name)
        self._add(item)
        return self

    def add(self, name=None):
        # type: (str) -> DataflowWorkloadItem
        """Add method that creates and returns an instance of the DataflowWorkloadItem class

        TBD

        Returns: DataflowWorkloadItem
        """
        item = DataflowWorkloadItem(parent=self._parent, choice=self._choice, name=name)
        self._add(item)
        return item


class DataflowComputeWorkload(OpenApiObject):
    __slots__ = ('_parent','_choice')

    _TYPES = {
        'nodes': {
            'type': list,
            'itemtype': str,
        },
        'choice': {
            'type': str,
            'enum': [
                'simulated',
            ],
        },
        'simulated': {'type': 'DataflowSimulatedComputeWorkload'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    SIMULATED = 'simulated' # type: str

    def __init__(self, parent=None, choice=None, nodes=None):
        super(DataflowComputeWorkload, self).__init__()
        self._parent = parent
        self._set_property('nodes', nodes)
        if 'choice' in self._DEFAULTS and choice is None:
            getattr(self, self._DEFAULTS['choice'])
        else:
            self.choice = choice

    @property
    def simulated(self):
        # type: () -> DataflowSimulatedComputeWorkload
        """Factory property that returns an instance of the DataflowSimulatedComputeWorkload class

        TBD

        Returns: DataflowSimulatedComputeWorkload
        """
        return self._get_property('simulated', DataflowSimulatedComputeWorkload, self, 'simulated')

    @property
    def nodes(self):
        # type: () -> List[str]
        """nodes getter

        TBD

        Returns: List[str]
        """
        return self._get_property('nodes')

    @nodes.setter
    def nodes(self, value):
        """nodes setter

        TBD

        value: List[str]
        """
        self._set_property('nodes', value)

    @property
    def choice(self):
        # type: () -> Union[Literal["simulated"]]
        """choice getter

        type of compute

        Returns: Union[Literal["simulated"]]
        """
        return self._get_property('choice')

    @choice.setter
    def choice(self, value):
        """choice setter

        type of compute

        value: Union[Literal["simulated"]]
        """
        self._set_property('choice', value)


class DataflowSimulatedComputeWorkload(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'duration': {'type': float},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, duration=None):
        super(DataflowSimulatedComputeWorkload, self).__init__()
        self._parent = parent
        self._set_property('duration', duration)

    @property
    def duration(self):
        # type: () -> float
        """duration getter

        duration of the simulated compute workload in seconds

        Returns: float
        """
        return self._get_property('duration')

    @duration.setter
    def duration(self, value):
        """duration setter

        duration of the simulated compute workload in seconds

        value: float
        """
        self._set_property('duration', value)


class DataflowAllReduceWorkload(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'nodes': {
            'type': list,
            'itemtype': str,
        },
        'flow_profile_name': {'type': str},
        'type': {
            'type': str,
            'enum': [
                'butterfly',
                'ring',
                'tree',
            ],
        },
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'type': 'ring',
    } # type: Dict[str, Union(type)]

    BUTTERFLY = 'butterfly' # type: str
    RING = 'ring' # type: str
    TREE = 'tree' # type: str

    def __init__(self, parent=None, nodes=None, flow_profile_name=None, type='ring'):
        super(DataflowAllReduceWorkload, self).__init__()
        self._parent = parent
        self._set_property('nodes', nodes)
        self._set_property('flow_profile_name', flow_profile_name)
        self._set_property('type', type)

    @property
    def nodes(self):
        # type: () -> List[str]
        """nodes getter

        TBD

        Returns: List[str]
        """
        return self._get_property('nodes')

    @nodes.setter
    def nodes(self, value):
        """nodes setter

        TBD

        value: List[str]
        """
        self._set_property('nodes', value)

    @property
    def flow_profile_name(self):
        # type: () -> str
        """flow_profile_name getter

        flow profile reference

        Returns: str
        """
        return self._get_property('flow_profile_name')

    @flow_profile_name.setter
    def flow_profile_name(self, value):
        """flow_profile_name setter

        flow profile reference

        value: str
        """
        self._set_property('flow_profile_name', value)

    @property
    def type(self):
        # type: () -> Union[Literal["butterfly"], Literal["ring"], Literal["tree"]]
        """type getter

        type of all reduce

        Returns: Union[Literal["butterfly"], Literal["ring"], Literal["tree"]]
        """
        return self._get_property('type')

    @type.setter
    def type(self, value):
        """type setter

        type of all reduce

        value: Union[Literal["butterfly"], Literal["ring"], Literal["tree"]]
        """
        self._set_property('type', value)


class DataflowBroadcastWorkload(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'sources': {
            'type': list,
            'itemtype': str,
        },
        'destinations': {
            'type': list,
            'itemtype': str,
        },
        'flow_profile_name': {'type': str},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, sources=None, destinations=None, flow_profile_name=None):
        super(DataflowBroadcastWorkload, self).__init__()
        self._parent = parent
        self._set_property('sources', sources)
        self._set_property('destinations', destinations)
        self._set_property('flow_profile_name', flow_profile_name)

    @property
    def sources(self):
        # type: () -> List[str]
        """sources getter

        list of host names, indicating the originator of the data

        Returns: List[str]
        """
        return self._get_property('sources')

    @sources.setter
    def sources(self, value):
        """sources setter

        list of host names, indicating the originator of the data

        value: List[str]
        """
        self._set_property('sources', value)

    @property
    def destinations(self):
        # type: () -> List[str]
        """destinations getter

        list of host names, indicating the destination of the data

        Returns: List[str]
        """
        return self._get_property('destinations')

    @destinations.setter
    def destinations(self, value):
        """destinations setter

        list of host names, indicating the destination of the data

        value: List[str]
        """
        self._set_property('destinations', value)

    @property
    def flow_profile_name(self):
        # type: () -> str
        """flow_profile_name getter

        flow profile reference

        Returns: str
        """
        return self._get_property('flow_profile_name')

    @flow_profile_name.setter
    def flow_profile_name(self, value):
        """flow_profile_name setter

        flow profile reference

        value: str
        """
        self._set_property('flow_profile_name', value)


class DataflowFlowProfile(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'name': {'type': str},
        'data_size': {'type': int},
        'l2_protocol_choice': {
            'type': str,
            'enum': [
                'ethernet',
            ],
        },
        'ethernet': {'type': 'DataflowFlowProfileEthernet'},
        'l4_protocol_choice': {
            'type': str,
            'enum': [
                'tcp',
                'udp',
            ],
        },
        'tcp': {'type': 'DataflowFlowProfileTcp'},
        'udp': {'type': 'DataflowFlowProfileUdp'},
    } # type: Dict[str, str]

    _REQUIRED = ('name', 'data_size') # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    ETHERNET = 'ethernet' # type: str

    TCP = 'tcp' # type: str
    UDP = 'udp' # type: str

    def __init__(self, parent=None, name=None, data_size=None, l2_protocol_choice=None, l4_protocol_choice=None):
        super(DataflowFlowProfile, self).__init__()
        self._parent = parent
        self._set_property('name', name)
        self._set_property('data_size', data_size)
        self._set_property('l2_protocol_choice', l2_protocol_choice)
        self._set_property('l4_protocol_choice', l4_protocol_choice)

    @property
    def name(self):
        # type: () -> str
        """name getter

        TBD

        Returns: str
        """
        return self._get_property('name')

    @name.setter
    def name(self, value):
        """name setter

        TBD

        value: str
        """
        self._set_property('name', value)

    @property
    def data_size(self):
        # type: () -> int
        """data_size getter

        TBD

        Returns: int
        """
        return self._get_property('data_size')

    @data_size.setter
    def data_size(self, value):
        """data_size setter

        TBD

        value: int
        """
        self._set_property('data_size', value)

    @property
    def l2_protocol_choice(self):
        # type: () -> Union[Literal["ethernet"]]
        """l2_protocol_choice getter

        layer2 protocol selection

        Returns: Union[Literal["ethernet"]]
        """
        return self._get_property('l2_protocol_choice')

    @l2_protocol_choice.setter
    def l2_protocol_choice(self, value):
        """l2_protocol_choice setter

        layer2 protocol selection

        value: Union[Literal["ethernet"]]
        """
        self._set_property('l2_protocol_choice', value)

    @property
    def ethernet(self):
        # type: () -> DataflowFlowProfileEthernet
        """ethernet getter

        

        Returns: DataflowFlowProfileEthernet
        """
        return self._get_property('ethernet', DataflowFlowProfileEthernet)

    @property
    def l4_protocol_choice(self):
        # type: () -> Union[Literal["tcp"], Literal["udp"]]
        """l4_protocol_choice getter

        layer4 protocol selection

        Returns: Union[Literal["tcp"], Literal["udp"]]
        """
        return self._get_property('l4_protocol_choice')

    @l4_protocol_choice.setter
    def l4_protocol_choice(self, value):
        """l4_protocol_choice setter

        layer4 protocol selection

        value: Union[Literal["tcp"], Literal["udp"]]
        """
        self._set_property('l4_protocol_choice', value)

    @property
    def tcp(self):
        # type: () -> DataflowFlowProfileTcp
        """tcp getter

        

        Returns: DataflowFlowProfileTcp
        """
        return self._get_property('tcp', DataflowFlowProfileTcp)

    @property
    def udp(self):
        # type: () -> DataflowFlowProfileUdp
        """udp getter

        

        Returns: DataflowFlowProfileUdp
        """
        return self._get_property('udp', DataflowFlowProfileUdp)


class DataflowFlowProfileEthernet(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'mtu': {'type': int},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'mtu': 1500,
    } # type: Dict[str, Union(type)]

    def __init__(self, parent=None, mtu=1500):
        super(DataflowFlowProfileEthernet, self).__init__()
        self._parent = parent
        self._set_property('mtu', mtu)

    @property
    def mtu(self):
        # type: () -> int
        """mtu getter

        Maximum Transmission Unit

        Returns: int
        """
        return self._get_property('mtu')

    @mtu.setter
    def mtu(self, value):
        """mtu setter

        Maximum Transmission Unit

        value: int
        """
        self._set_property('mtu', value)


class DataflowFlowProfileTcp(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'congestion_algorithm': {
            'type': str,
            'enum': [
                'bbr',
                'dctcp',
                'cubic',
                'reno',
            ],
        },
        'initcwnd': {'type': int},
        'send_buf': {'type': int},
        'receive_buf': {'type': int},
        'destination_port': {'type': 'L4PortRange'},
        'source_port': {'type': 'L4PortRange'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'congestion_algorithm': 'cubic',
    } # type: Dict[str, Union(type)]

    BBR = 'bbr' # type: str
    DCTCP = 'dctcp' # type: str
    CUBIC = 'cubic' # type: str
    RENO = 'reno' # type: str

    def __init__(self, parent=None, congestion_algorithm='cubic', initcwnd=None, send_buf=None, receive_buf=None):
        super(DataflowFlowProfileTcp, self).__init__()
        self._parent = parent
        self._set_property('congestion_algorithm', congestion_algorithm)
        self._set_property('initcwnd', initcwnd)
        self._set_property('send_buf', send_buf)
        self._set_property('receive_buf', receive_buf)

    @property
    def congestion_algorithm(self):
        # type: () -> Union[Literal["bbr"], Literal["cubic"], Literal["dctcp"], Literal["reno"]]
        """congestion_algorithm getter

        The TCP congestion algorithm:. bbr - Bottleneck Bandwidth and Round-trip propagation time. dctcp - Data center TCP. cubic - cubic window increase function. reno - TCP New Reno

        Returns: Union[Literal["bbr"], Literal["cubic"], Literal["dctcp"], Literal["reno"]]
        """
        return self._get_property('congestion_algorithm')

    @congestion_algorithm.setter
    def congestion_algorithm(self, value):
        """congestion_algorithm setter

        The TCP congestion algorithm:. bbr - Bottleneck Bandwidth and Round-trip propagation time. dctcp - Data center TCP. cubic - cubic window increase function. reno - TCP New Reno

        value: Union[Literal["bbr"], Literal["cubic"], Literal["dctcp"], Literal["reno"]]
        """
        self._set_property('congestion_algorithm', value)

    @property
    def initcwnd(self):
        # type: () -> int
        """initcwnd getter

        initial congestion window

        Returns: int
        """
        return self._get_property('initcwnd')

    @initcwnd.setter
    def initcwnd(self, value):
        """initcwnd setter

        initial congestion window

        value: int
        """
        self._set_property('initcwnd', value)

    @property
    def send_buf(self):
        # type: () -> int
        """send_buf getter

        send buffer size

        Returns: int
        """
        return self._get_property('send_buf')

    @send_buf.setter
    def send_buf(self, value):
        """send_buf setter

        send buffer size

        value: int
        """
        self._set_property('send_buf', value)

    @property
    def receive_buf(self):
        # type: () -> int
        """receive_buf getter

        receive buffer size

        Returns: int
        """
        return self._get_property('receive_buf')

    @receive_buf.setter
    def receive_buf(self, value):
        """receive_buf setter

        receive buffer size

        value: int
        """
        self._set_property('receive_buf', value)

    @property
    def destination_port(self):
        # type: () -> L4PortRange
        """destination_port getter

        Layer4 protocol source or destination port valuesLayer4 protocol source or destination port values

        Returns: L4PortRange
        """
        return self._get_property('destination_port', L4PortRange)

    @property
    def source_port(self):
        # type: () -> L4PortRange
        """source_port getter

        Layer4 protocol source or destination port valuesLayer4 protocol source or destination port values

        Returns: L4PortRange
        """
        return self._get_property('source_port', L4PortRange)


class L4PortRange(OpenApiObject):
    __slots__ = ('_parent','_choice')

    _TYPES = {
        'choice': {
            'type': str,
            'enum': [
                'single_value',
                'range',
            ],
        },
        'single_value': {'type': 'L4PortRangeSingleValue'},
        'range': {'type': 'L4PortRangeRange'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    SINGLE_VALUE = 'single_value' # type: str
    RANGE = 'range' # type: str

    def __init__(self, parent=None, choice=None):
        super(L4PortRange, self).__init__()
        self._parent = parent
        if 'choice' in self._DEFAULTS and choice is None:
            getattr(self, self._DEFAULTS['choice'])
        else:
            self.choice = choice

    @property
    def single_value(self):
        # type: () -> L4PortRangeSingleValue
        """Factory property that returns an instance of the L4PortRangeSingleValue class

        TBD

        Returns: L4PortRangeSingleValue
        """
        return self._get_property('single_value', L4PortRangeSingleValue, self, 'single_value')

    @property
    def range(self):
        # type: () -> L4PortRangeRange
        """Factory property that returns an instance of the L4PortRangeRange class

        TBD

        Returns: L4PortRangeRange
        """
        return self._get_property('range', L4PortRangeRange, self, 'range')

    @property
    def choice(self):
        # type: () -> Union[Literal["range"], Literal["single_value"]]
        """choice getter

        None

        Returns: Union[Literal["range"], Literal["single_value"]]
        """
        return self._get_property('choice')

    @choice.setter
    def choice(self, value):
        """choice setter

        None

        value: Union[Literal["range"], Literal["single_value"]]
        """
        self._set_property('choice', value)


class L4PortRangeSingleValue(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'value': {'type': int},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'value': 1,
    } # type: Dict[str, Union(type)]

    def __init__(self, parent=None, value=1):
        super(L4PortRangeSingleValue, self).__init__()
        self._parent = parent
        self._set_property('value', value)

    @property
    def value(self):
        # type: () -> int
        """value getter

        TBD

        Returns: int
        """
        return self._get_property('value')

    @value.setter
    def value(self, value):
        """value setter

        TBD

        value: int
        """
        self._set_property('value', value)


class L4PortRangeRange(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'start_value': {'type': int},
        'increment': {
            'type': int,
            'minimum': 1,
        },
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS = {
        'start_value': 1,
        'increment': 1,
    } # type: Dict[str, Union(type)]

    def __init__(self, parent=None, start_value=1, increment=1):
        super(L4PortRangeRange, self).__init__()
        self._parent = parent
        self._set_property('start_value', start_value)
        self._set_property('increment', increment)

    @property
    def start_value(self):
        # type: () -> int
        """start_value getter

        TBD

        Returns: int
        """
        return self._get_property('start_value')

    @start_value.setter
    def start_value(self, value):
        """start_value setter

        TBD

        value: int
        """
        self._set_property('start_value', value)

    @property
    def increment(self):
        # type: () -> int
        """increment getter

        TBD

        Returns: int
        """
        return self._get_property('increment')

    @increment.setter
    def increment(self, value):
        """increment setter

        TBD

        value: int
        """
        self._set_property('increment', value)


class DataflowFlowProfileUdp(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {} # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(DataflowFlowProfileUdp, self).__init__()
        self._parent = parent


class DataflowFlowProfileIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(DataflowFlowProfileIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[DataflowFlowProfile]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> DataflowFlowProfileIter
        return self._iter()

    def __next__(self):
        # type: () -> DataflowFlowProfile
        return self._next()

    def next(self):
        # type: () -> DataflowFlowProfile
        return self._next()

    def flowprofile(self, name=None, data_size=None, l2_protocol_choice=None, l4_protocol_choice=None):
        # type: (str,int,Union[Literal["ethernet"]],Union[Literal["tcp"], Literal["udp"]]) -> DataflowFlowProfileIter
        """Factory method that creates an instance of the DataflowFlowProfile class

        TBD

        Returns: DataflowFlowProfileIter
        """
        item = DataflowFlowProfile(parent=self._parent, name=name, data_size=data_size, l2_protocol_choice=l2_protocol_choice, l4_protocol_choice=l4_protocol_choice)
        self._add(item)
        return self

    def add(self, name=None, data_size=None, l2_protocol_choice=None, l4_protocol_choice=None):
        # type: (str,int,Union[Literal["ethernet"]],Union[Literal["tcp"], Literal["udp"]]) -> DataflowFlowProfile
        """Add method that creates and returns an instance of the DataflowFlowProfile class

        TBD

        Returns: DataflowFlowProfile
        """
        item = DataflowFlowProfile(parent=self._parent, name=name, data_size=data_size, l2_protocol_choice=l2_protocol_choice, l4_protocol_choice=l4_protocol_choice)
        self._add(item)
        return item


class GetConfigDetails(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {} # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(GetConfigDetails, self).__init__()
        self._parent = parent


class ExperimentRequest(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {} # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(ExperimentRequest, self).__init__()
        self._parent = parent


class ErrorDetails(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'errors': {
            'type': list,
            'itemtype': str,
        },
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, errors=None):
        super(ErrorDetails, self).__init__()
        self._parent = parent
        self._set_property('errors', errors)

    @property
    def errors(self):
        # type: () -> List[str]
        """errors getter

        TBD

        Returns: List[str]
        """
        return self._get_property('errors')

    @errors.setter
    def errors(self, value):
        """errors setter

        TBD

        value: List[str]
        """
        self._set_property('errors', value)


class MetricsRequest(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {} # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None):
        super(MetricsRequest, self).__init__()
        self._parent = parent


class MetricsResponse(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'jct': {
            'type': int,
            'format': 'int64',
        },
        'flow_results': {'type': 'MetricsResponseFlowResultIter'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, jct=None):
        super(MetricsResponse, self).__init__()
        self._parent = parent
        self._set_property('jct', jct)

    @property
    def jct(self):
        # type: () -> int
        """jct getter

        job completion time in micro seconds

        Returns: int
        """
        return self._get_property('jct')

    @jct.setter
    def jct(self, value):
        """jct setter

        job completion time in micro seconds

        value: int
        """
        self._set_property('jct', value)

    @property
    def flow_results(self):
        # type: () -> MetricsResponseFlowResultIter
        """flow_results getter

        TBD

        Returns: MetricsResponseFlowResultIter
        """
        return self._get_property('flow_results', MetricsResponseFlowResultIter, self._parent, self._choice)


class MetricsResponseFlowResult(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'workload_name': {'type': str},
        'flow_number': {
            'type': int,
            'format': 'int64',
        },
        'from_host_name': {'type': str},
        'to_host_name': {'type': str},
        'fct': {
            'type': int,
            'format': 'int64',
        },
        'first_timestamp': {
            'type': int,
            'format': 'int64',
        },
        'last_timestamp': {
            'type': int,
            'format': 'int64',
        },
        'bytes_tx': {
            'type': int,
            'format': 'int64',
        },
        'bytes_rx': {
            'type': int,
            'format': 'int64',
        },
        'tcp_info': {'type': 'MetricsResponseFlowResultTcpInfo'},
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, workload_name=None, flow_number=None, from_host_name=None, to_host_name=None, fct=None, first_timestamp=None, last_timestamp=None, bytes_tx=None, bytes_rx=None):
        super(MetricsResponseFlowResult, self).__init__()
        self._parent = parent
        self._set_property('workload_name', workload_name)
        self._set_property('flow_number', flow_number)
        self._set_property('from_host_name', from_host_name)
        self._set_property('to_host_name', to_host_name)
        self._set_property('fct', fct)
        self._set_property('first_timestamp', first_timestamp)
        self._set_property('last_timestamp', last_timestamp)
        self._set_property('bytes_tx', bytes_tx)
        self._set_property('bytes_rx', bytes_rx)

    @property
    def workload_name(self):
        # type: () -> str
        """workload_name getter

        TBD

        Returns: str
        """
        return self._get_property('workload_name')

    @workload_name.setter
    def workload_name(self, value):
        """workload_name setter

        TBD

        value: str
        """
        self._set_property('workload_name', value)

    @property
    def flow_number(self):
        # type: () -> int
        """flow_number getter

        TBD

        Returns: int
        """
        return self._get_property('flow_number')

    @flow_number.setter
    def flow_number(self, value):
        """flow_number setter

        TBD

        value: int
        """
        self._set_property('flow_number', value)

    @property
    def from_host_name(self):
        # type: () -> str
        """from_host_name getter

        TBD

        Returns: str
        """
        return self._get_property('from_host_name')

    @from_host_name.setter
    def from_host_name(self, value):
        """from_host_name setter

        TBD

        value: str
        """
        self._set_property('from_host_name', value)

    @property
    def to_host_name(self):
        # type: () -> str
        """to_host_name getter

        TBD

        Returns: str
        """
        return self._get_property('to_host_name')

    @to_host_name.setter
    def to_host_name(self, value):
        """to_host_name setter

        TBD

        value: str
        """
        self._set_property('to_host_name', value)

    @property
    def fct(self):
        # type: () -> int
        """fct getter

        flow completion time in micro seconds

        Returns: int
        """
        return self._get_property('fct')

    @fct.setter
    def fct(self, value):
        """fct setter

        flow completion time in micro seconds

        value: int
        """
        self._set_property('fct', value)

    @property
    def first_timestamp(self):
        # type: () -> int
        """first_timestamp getter

        first timestamp in micro seconds

        Returns: int
        """
        return self._get_property('first_timestamp')

    @first_timestamp.setter
    def first_timestamp(self, value):
        """first_timestamp setter

        first timestamp in micro seconds

        value: int
        """
        self._set_property('first_timestamp', value)

    @property
    def last_timestamp(self):
        # type: () -> int
        """last_timestamp getter

        last timestamp in micro seconds

        Returns: int
        """
        return self._get_property('last_timestamp')

    @last_timestamp.setter
    def last_timestamp(self, value):
        """last_timestamp setter

        last timestamp in micro seconds

        value: int
        """
        self._set_property('last_timestamp', value)

    @property
    def bytes_tx(self):
        # type: () -> int
        """bytes_tx getter

        bytes transmitted from src to dst

        Returns: int
        """
        return self._get_property('bytes_tx')

    @bytes_tx.setter
    def bytes_tx(self, value):
        """bytes_tx setter

        bytes transmitted from src to dst

        value: int
        """
        self._set_property('bytes_tx', value)

    @property
    def bytes_rx(self):
        # type: () -> int
        """bytes_rx getter

        bytes received by src from dst

        Returns: int
        """
        return self._get_property('bytes_rx')

    @bytes_rx.setter
    def bytes_rx(self, value):
        """bytes_rx setter

        bytes received by src from dst

        value: int
        """
        self._set_property('bytes_rx', value)

    @property
    def tcp_info(self):
        # type: () -> MetricsResponseFlowResultTcpInfo
        """tcp_info getter

        TCP information for this flowTCP information for this flow

        Returns: MetricsResponseFlowResultTcpInfo
        """
        return self._get_property('tcp_info', MetricsResponseFlowResultTcpInfo)


class MetricsResponseFlowResultTcpInfo(OpenApiObject):
    __slots__ = ('_parent')

    _TYPES = {
        'rtt': {
            'type': int,
            'format': 'int64',
        },
        'rtt_variance': {
            'type': int,
            'format': 'int64',
        },
        'retransmissions': {
            'type': int,
            'format': 'int64',
        },
    } # type: Dict[str, str]

    _REQUIRED= () # type: tuple(str)

    _DEFAULTS= {} # type: Dict[str, Union(type)]

    def __init__(self, parent=None, rtt=None, rtt_variance=None, retransmissions=None):
        super(MetricsResponseFlowResultTcpInfo, self).__init__()
        self._parent = parent
        self._set_property('rtt', rtt)
        self._set_property('rtt_variance', rtt_variance)
        self._set_property('retransmissions', retransmissions)

    @property
    def rtt(self):
        # type: () -> int
        """rtt getter

        round trip time in microseconds

        Returns: int
        """
        return self._get_property('rtt')

    @rtt.setter
    def rtt(self, value):
        """rtt setter

        round trip time in microseconds

        value: int
        """
        self._set_property('rtt', value)

    @property
    def rtt_variance(self):
        # type: () -> int
        """rtt_variance getter

        round trip time variance in microseconds, larger values indicate less stable performance

        Returns: int
        """
        return self._get_property('rtt_variance')

    @rtt_variance.setter
    def rtt_variance(self, value):
        """rtt_variance setter

        round trip time variance in microseconds, larger values indicate less stable performance

        value: int
        """
        self._set_property('rtt_variance', value)

    @property
    def retransmissions(self):
        # type: () -> int
        """retransmissions getter

        total number of TCP retransmissions

        Returns: int
        """
        return self._get_property('retransmissions')

    @retransmissions.setter
    def retransmissions(self, value):
        """retransmissions setter

        total number of TCP retransmissions

        value: int
        """
        self._set_property('retransmissions', value)


class MetricsResponseFlowResultIter(OpenApiIter):
    __slots__ = ('_parent', '_choice')

    _GETITEM_RETURNS_CHOICE_OBJECT = False

    def __init__(self, parent=None, choice=None):
        super(MetricsResponseFlowResultIter, self).__init__()
        self._parent = parent
        self._choice = choice

    def __getitem__(self, key):
        # type: (str) -> Union[MetricsResponseFlowResult]
        return self._getitem(key)

    def __iter__(self):
        # type: () -> MetricsResponseFlowResultIter
        return self._iter()

    def __next__(self):
        # type: () -> MetricsResponseFlowResult
        return self._next()

    def next(self):
        # type: () -> MetricsResponseFlowResult
        return self._next()

    def flowresult(self, workload_name=None, flow_number=None, from_host_name=None, to_host_name=None, fct=None, first_timestamp=None, last_timestamp=None, bytes_tx=None, bytes_rx=None):
        # type: (str,int,str,str,int,int,int,int,int) -> MetricsResponseFlowResultIter
        """Factory method that creates an instance of the MetricsResponseFlowResult class

        result for a single data flow

        Returns: MetricsResponseFlowResultIter
        """
        item = MetricsResponseFlowResult(parent=self._parent, workload_name=workload_name, flow_number=flow_number, from_host_name=from_host_name, to_host_name=to_host_name, fct=fct, first_timestamp=first_timestamp, last_timestamp=last_timestamp, bytes_tx=bytes_tx, bytes_rx=bytes_rx)
        self._add(item)
        return self

    def add(self, workload_name=None, flow_number=None, from_host_name=None, to_host_name=None, fct=None, first_timestamp=None, last_timestamp=None, bytes_tx=None, bytes_rx=None):
        # type: (str,int,str,str,int,int,int,int,int) -> MetricsResponseFlowResult
        """Add method that creates and returns an instance of the MetricsResponseFlowResult class

        result for a single data flow

        Returns: MetricsResponseFlowResult
        """
        item = MetricsResponseFlowResult(parent=self._parent, workload_name=workload_name, flow_number=flow_number, from_host_name=from_host_name, to_host_name=to_host_name, fct=fct, first_timestamp=first_timestamp, last_timestamp=last_timestamp, bytes_tx=bytes_tx, bytes_rx=bytes_rx)
        self._add(item)
        return item


class Api(object):
    """OpenApi Abstract API
    """

    def __init__(self, **kwargs):
        pass

    def set_config(self, payload):
        """POST /config

        Sets the ONEx dataflow config

        Return: config
        """
        raise NotImplementedError("set_config")

    def get_config(self, payload):
        """GET /config

        Gets the ONEx dataflow config from the server, as currently configured

        Return: config
        """
        raise NotImplementedError("get_config")

    def run_experiment(self, payload):
        """POST /control/experiment

        Runs the currently configured experiment

        Return: error_details
        """
        raise NotImplementedError("run_experiment")

    def get_metrics(self, payload):
        """POST /results/metrics

        TBD

        Return: metrics_response
        """
        raise NotImplementedError("get_metrics")

    def config(self):
        """Factory method that creates an instance of Config

        Return: Config
        """
        return Config()

    def getconfigdetails(self):
        """Factory method that creates an instance of GetConfigDetails

        Return: GetConfigDetails
        """
        return GetConfigDetails()

    def experiment_request(self):
        """Factory method that creates an instance of ExperimentRequest

        Return: ExperimentRequest
        """
        return ExperimentRequest()

    def error_details(self):
        """Factory method that creates an instance of ErrorDetails

        Return: ErrorDetails
        """
        return ErrorDetails()

    def metrics_request(self):
        """Factory method that creates an instance of MetricsRequest

        Return: MetricsRequest
        """
        return MetricsRequest()

    def metrics_response(self):
        """Factory method that creates an instance of MetricsResponse

        Return: MetricsResponse
        """
        return MetricsResponse()


class HttpApi(Api):
    """OpenAPI HTTP Api
    """
    def __init__(self, **kwargs):
        super(HttpApi, self).__init__(**kwargs)
        self._transport = HttpTransport(**kwargs)

    def set_config(self, payload):
        """POST /config

        Sets the ONEx dataflow config

        Return: config
        """
        return self._transport.send_recv(
            "post",
            "/config",
            payload=payload,
            return_object=self.config(),
        )

    def get_config(self, payload):
        """GET /config

        Gets the ONEx dataflow config from the server, as currently configured

        Return: config
        """
        return self._transport.send_recv(
            "get",
            "/config",
            payload=payload,
            return_object=self.config(),
        )

    def run_experiment(self, payload):
        """POST /control/experiment

        Runs the currently configured experiment

        Return: error_details
        """
        return self._transport.send_recv(
            "post",
            "/control/experiment",
            payload=payload,
            return_object=self.error_details(),
        )

    def get_metrics(self, payload):
        """POST /results/metrics

        TBD

        Return: metrics_response
        """
        return self._transport.send_recv(
            "post",
            "/results/metrics",
            payload=payload,
            return_object=self.metrics_response(),
        )
