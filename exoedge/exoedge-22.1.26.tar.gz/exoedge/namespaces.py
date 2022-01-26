# pylint: disable=C0122,C0103
# -*- coding: utf-8 -*-
import json
import pureyaml
import copy
from six import string_types

def get_nested_object(obj, chain):
    """
        Recursive algo for getting nested elements of a dictionary.

        Input: obj - a python dictionary
        Input: chain - a 'list defining the path to a dictionary element
        Returns: object specified by chain (e.g. ['fee', 'fie']) or None

        Example:
            >>> get_nested_object({'foo': {'bar':{'fee': 'fie'}}}, ['foo', 'bar'])
            {'fee': 'fie'}
            >>> get_nested_object({'foo': {'bar':{'fee': 'fie'}}}, ['foo', 'bar', 'fee'])
            fie
    """
    _key = chain.pop(0)
    if _key in obj:
        return get_nested_object(obj[_key], chain) if chain else obj[_key]

def deepupdate(defaults, update):
    """ Recursively fill in missing elements
    of dictionary <update> according to defaults in
    <defaults>.

    Function uses copy.deepcopy() to avoid inadvertently
    copying references. Everything is copied by value.
    """
    for key, value in defaults.items():
        if key not in update:
            update[key] = copy.deepcopy(value)
        elif isinstance(value, dict):
            deepupdate(copy.deepcopy(value), update[key])

####################################
#    CHANNEL NAMESPACES
####################################


class Namespace(object):
    """
        This class accepts any dictionary and creates
        a new object that can be traversed via the
        '.' (dot) operator instead of normal dictionary
        syntax (e.g. d['key'], d.get('key')).

        Example:

            >>> d = {'a':{'b':{'c':'d'}}}
            >>> ns = Namespace(**d)
            >>> ns.a.b.c
            d

        There are also methods to assist in dumping
        the new namespace to JSON and YAML formats.
    """
    def __init__(self, **kw):
        # TODO: basically, the leaf() function, takes a dict and then
        # makes a NS out of it. so, if self.__dict__ gets updated,
        # you could just call leaf() on it again. a merge() function
        # would, then, just merge the two dicts, then run through
        # the result with leaf - updating (merging) the two NS's.
        self.leaf(self, kw)

    def __iter__(self):
        for k, v in self.__dict__.items():
            if isinstance(v, Namespace):
                v = dict(v)
            yield k, v


    @classmethod
    def leaf(cls, ns, d):
        for k, v  in d.items():
            try:
                v = json.loads(json.dumps(v))
            except (TypeError, ValueError):
                pass
            if k == 'app_specific_config':
                ns.__dict__[k] = v
                continue
            if isinstance(v, dict):
                leaf_ns = Namespace(**v)
            else:
                leaf_ns = v
            setattr(ns, k, leaf_ns)


    def serialize(self):
        d = {}
        def unnamespace(ns):
            _d = {}
            for i, j in ns.__dict__.items():
                if isinstance(j, Namespace):
                    _d = unnamespace(j)
                else:
                    _d[i] = j
            return _d

        for k, v in self.__dict__.items():
            if isinstance(v, Namespace):
                d[k] = unnamespace(v)
            else:
                try:
                    d[k] = v
                    json.dumps(d)
                except TypeError:
                    d[k] = str(v)
        return d


    def to_yaml(self, indent=2):
        return pureyaml.dumps(dict(self.serialize()), sort_keys=True, allow_unicode=True, indent=indent)

    def to_json(self, indent=2):
        return json.dumps(dict(self.serialize()), indent=indent)


class ChannelNamespace(Namespace):
    """
        This class has all of the benefits of the
        Namespace class, but it fills any missing
        elements so that the edged Channel object
        can use the '.' operator in source code
        safely.
    """
    def __init__(self, **kw):
        if not kw.get('__ns_no_defaults__'):
            # assure we have a basic namespace
            deepupdate(BASIC_CHANNEL_SCHEMA_DEFAULTS, kw)
            # this key has the bare minimum for any fieldbus-type in exosense
            if kw['protocol_config'].get('application'):
                if 'Modbus_TCP' == kw['protocol_config'].get('application'):
                    deepupdate(MODBUS_TCP_CHANNEL_SCHEMA_DEFAULTS, kw)
                elif 'Modbus_RTU' == kw['protocol_config'].get('application'):
                    deepupdate(MODBUS_RTU_CHANNEL_SCHEMA_DEFAULTS, kw)
                elif 'CANOpen' == kw['protocol_config'].get('application'):
                    deepupdate(CANOPEN_CHANNEL_SCHEMA_DEFAULTS, kw)
                else:
                    deepupdate(CLASSIC_CHANNEL_SCHEMA_DEFAULTS, kw)
        elif '__ns_no_defaults__' in kw:
            kw.pop('__ns_no_defaults__')
        Namespace.__init__(self, **kw)

####################################
#    CHANNEL SCHEMAS
####################################

BASIC_CHANNEL_SCHEMA_TYPE_MAP = {
    "display_name": str,
    "description": str,
    "properties": {
        "data_type": str,
        "data_unit": str,
        "min": float,
        "max": float,
        "precision": float,
        "value_mapping": str,
        "device_diagnostic": bool,
        "data_out": bool,
    },
    "protocol_config": {
        "application": str,
        "interface": str,
        "input_raw": {
            "max": float,
            "min": float,
            "unit": str,
        },
        "multiplier": float,
        "offset": float,
        "sample_rate": float,
        "report_rate": float,
        "report_on_change": bool,
        "report_on_change_tolerance": float,
        "down_sample": str,
        "app_specific_config": {},
    }
}

BASIC_CHANNEL_SCHEMA_DEFAULTS = {
    "display_name": "not specified",
    "description": "not specified",
    "properties": {
        "data_type": "not specified",
        "data_out": False,
    },
    "protocol_config": {
        "application": "not specified",
        "interface": "not specified",
        "multiplier": 1,
        "offset": 0,
        "sample_rate": 1000,
        "report_rate": 1000,
        "report_on_change": False,
        "report_on_change_tolerance": 0.0,
        "down_sample": "ACT",
        "app_specific_config": {},
    }
}

CLASSIC_CHANNEL_SCHEMA_TYPE_MAP = {
    "protocol_config": {
        "app_specific_config": {
            "module": str,
            "function": str,
            "parameters": dict,
            "positionals": list,
        }
    }
}
CLASSIC_CHANNEL_SCHEMA_DEFAULTS = {
    "protocol_config": {
        "app_specific_config": {
            "parameters": {},
            "positionals": [],
        }
    }
}
deepupdate(
    BASIC_CHANNEL_SCHEMA_DEFAULTS,
    CLASSIC_CHANNEL_SCHEMA_DEFAULTS
)


####################################
#    MODBUS TCP CHANNEL SCHEMA
####################################

MODBUS_TCP_CHANNEL_SCHEMA_TYPE_MAP = {
    "protocol_config": {
        "application": str,
        "interface": str,
        "app_specific_config": {
            "ip_address": str,
            "port": int,
            "register_range": str,
            "register_offset": int,
            "register_count":  int,
            "byte_endianness": str,
            "register_endianness": str,
            "evaluation_mode": str,
            "bitmask": hex,
        },
    }
}

MODBUS_TCP_CHANNEL_SCHEMA_DEFAULTS = {
    "protocol_config": {
        "app_specific_config": {
            "ip_address": "127.0.0.1",
            "port": 5020,
            "register_range": "INPUT_COIL",
            "register_offset": 0,
            "register_count":  1,
            "byte_endianness": "not specified",
            "register_endianness": "not specified",
            "evaluation_mode": "not specified",
            "bitmask": 0xFFFF,
        },
    }
}
deepupdate(
    BASIC_CHANNEL_SCHEMA_DEFAULTS,
    MODBUS_TCP_CHANNEL_SCHEMA_DEFAULTS
)
####################################
#    MODBUS RTU CHANNEL SCHEMA
####################################

MODBUS_RTU_CHANNEL_SCHEMA_TYPE_MAP = {
    "protocol_config": {
        "app_specific_config": {
            "slave_id": int,
            "register_range": str,
            "register_offset": int,
            "register_count":  int,
            "byte_endianness": str,
            "register_endianness": str,
            "evaluation_mode": str,
            "bitmask": hex,
        },
    }
}

MODBUS_RTU_CHANNEL_SCHEMA_DEFAULTS = {
    "protocol_config": {
        "app_specific_config": {
            "slave_id": 1,
            "register_range": "not specified",
            "register_offset": None,
            "register_count":  None,
            "byte_endianness": "not specified",
            "register_endianness": "not specified",
            "evaluation_mode": "not specified",
            "bitmask": 0xFFFF,
        },
    }
}
deepupdate(
    BASIC_CHANNEL_SCHEMA_DEFAULTS,
    MODBUS_RTU_CHANNEL_SCHEMA_DEFAULTS
)


####################################
#    CANOPEN CHANNEL SCHEMA
####################################

CANOPEN_CHANNEL_SCHEMA_TYPE_MAP = {
    "protocol_config": {
        "app_specific_config" : {
            "node_id" : hex,
            "msg_index" : hex,
            "offset" : int,
            "data_length" : int,
            "evaluation_mode" : str,
            "bitmask" : hex
        }
    }
}

CANOPEN_CHANNEL_SCHEMA_DEFAULTS = {
    "protocol_config": {
        "app_specific_config" : {
            "node_id" : 0x01,
            "msg_index" : 0x180,
            "offset" : 0,
            "data_length" : 8,
            "evaluation_mode" : "unsigned_integer",
            "bitmask" : 0xFFFFFFFF
        }
    }
}
deepupdate(
    BASIC_CHANNEL_SCHEMA_DEFAULTS,
    CANOPEN_CHANNEL_SCHEMA_DEFAULTS
)


###########################################
#
#    CONFIG APPLICATIONS SCHEMAS
#
###########################################


###########################################
#    MODBUS RTU CONFIG APPLICATIONS SCHEMA
###########################################

MODBUS_RTU_CONFIG_APPLICATIONS_SCHEMA_DEFAULTS = {
    "application_display_name" : "Modbus RTU",
    "interfaces" : [
        {
            "interface" : "/dev/tty1",
            "baud_rate" :  115200,
            "stop_bits" : 0,
            "parity" : "even"
        }
    ],
    "channel_requirements" : {
        "slave_id" : int,
        "register_range" : [
            "INPUT_COIL",
            "HOLDING_COIL",
            "INPUT_REGISTER",
            "HOLDING_REGISTER"
        ],
        "register_offset" : int,
        "register_count" : int,
        "byte_endianness" : [
            "little",
            "big"
        ],
        "register_endianness" : [
            "little",
            "big"
        ],
        "evaluation_mode" : [
            "floating point: ieee754",
            "whole-remainder",
            "signed integer",
            "unsigned",
            "bitmask_int",
            "bitmask_bool",
            "string-ascii"
        ],
        "bitmask" : hex
    }

}

###########################################
#    MODBUS TCP CONFIG APPLICATIONS SCHEMA
###########################################

MODBUS_TCP_CONFIG_APPLICATIONS_SCHEMA_DEFAULTS = {
    "application_display_name" : "Modbus TCP",
    "interfaces" : [
        "/dev/eth0",
        "/dev/wlan0"
    ],
    "channel_requirements" : {
        "ip_address" : str,
        "port" : int,
        "register_range" : [
            "INPUT_COIL",
            "HOLDING_COIL",
            "INPUT_REGISTER",
            "HOLDING_REGISTER"
        ],
        "register_offset" : int,
        "register_count" : int,
        "byte_endianness" : [
            "little",
            "big"
        ],
        "register_endianness" : [
            "little",
            "big"
        ],
        "evaluation_mode" : [
            "floating point: ieee754",
            "whole-remainder",
            "signed integer",
            "unsigned",
            "bitmask_int",
            "bitmask_bool",
            "string-ascii"
        ],
        "bitmask" : hex,
    }
}

###########################################
#    CANOPEN CONFIG APPLICATIONS SCHEMA
###########################################

CANOPEN_CONFIG_APPLICATIONS_SCHEMA_DEFAULTS = {
    "interfaces" : [
        {
            "channel" : "canA-10",
            "bitrate" : 250000
        }
    ],
    "channel_requirements" : {
        "node_id" : hex,
        "msg_index" : hex,
        "offset": int,
        "data_length": int,
        "evaluation_mode" : [
            "REAL32",
            "INT8",
            "INT16",
            "UINT16",
            "UINT32",
            "STRING",
            "BOOLEAN"
        ],
        "bitmask" : hex
    }

}

