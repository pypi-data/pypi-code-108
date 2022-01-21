from __future__ import annotations
from collections import OrderedDict
from pydantic.typing import List, Union
import ipaddress
from net_models.utils import get_interface_index, get_logger, split_interface, INTERFACE_NAMES


LOGGER = get_logger(name="NetCm-Validators")

def ipv4_is_assignable(address: ipaddress.IPv4Interface) -> ipaddress.IPv4Interface:
    """
    This validator check that given IP address is neither broadcast nor network Id.
    These rules apply to netmasks up to /30.

    Args:
        address: ipaddress.IPv4Interface (address with netmask)

    Returns: ipaddress.IPv4Interface

    """
    # Don't validate address if prefix is /31 or /32
    if int(address.with_prefixlen.split("/")[1]) in [31,32]:
        pass
    else:
        assert address.ip not in [
            address.network.network_address,
            address.network.broadcast_address], f"Invalid IPv4 Interface Address: {address}"
    return address


def ipv4s_in_same_subnet(ips: List[ipaddress.IPv4Interface]):
    """
    Checks that all addresses are part of the same subnet
    Args:
        ips: List of IPv4Interface

    Returns: ips

    """

    netmasks = set([x.with_netmask.split('/')[1] for x in ips])
    if len(netmasks) > 1:
        msg = f"Given IPv4 addresses don't have same netmasks {ips}."
        LOGGER.error(msg=msg)
        raise AssertionError(msg)

    for ip in ips:
        other_ips = list(ips)
        other_ips.remove(ip)
        for other_ip in other_ips:
            if other_ip.ip not in ip.network:
                msg = f"IPv4 address {other_ip.ip} is not part of {ip}'s network."
                LOGGER.error(msg=msg)
                raise AssertionError(msg)

    return ips

def sort_interface_dict(interfaces: OrderedDict) -> OrderedDict:
    return OrderedDict(sorted([(x.name, x) for x in interfaces.values()], key=lambda x: get_interface_index(x[0])))

def remove_duplicates_and_sort(data: List) -> List:
    return sorted(set(data))

def expand_vlan_range(vlan_range: Union[List[int], str]) -> List[int]:
    vlan_list = []

    if isinstance(vlan_range, list):
        for item in vlan_range:
            if isinstance(item, int):
                vlan_list.append(item)
            elif isinstance(item, str):
                if "-" not in item:
                    try:
                        vlan_list.append(int(item))
                    except Exception as e:
                        msg = f"Invalid 'vlan_range' element: {item}."
                        LOGGER.error(msg=msg)
                        raise ValueError(msg)
                else:
                    split_result = item.split("-")
                    if len(split_result) != 2:
                        msg = f"Invalid 'vlan_range' element: {item}."
                        LOGGER.error(msg=msg)
                        raise ValueError(msg)
                    else:
                        start, stop = (None, None)
                        try:
                            start, stop = map(int, split_result)
                        except Exception as e:
                            msg = f"Invalid 'vlan_range' element: {item}."
                            LOGGER.error(msg=msg)
                            raise ValueError(msg)

                        if start >= stop:
                                raise ValueError(f"Invalid 'vlan_range' element: {item}. Range beggining >= end.")
                        vlan_list.extend(range(start, stop+1))
            else:
                raise TypeError(f"Invalid 'vlan_range' element type: {type(item)}. Expected Union[str, int].")
    elif isinstance(vlan_range, str):
        if vlan_range in ["all", "none"]:
            return vlan_range
        vlan_list = expand_vlan_range(vlan_range=vlan_range.split(","))
    else:
        raise TypeError(f"Invalid type of 'vlan_range'. Expected Union[list, str], got {type(vlan_range)}.")

    try:
        vlan_list = sorted(set(vlan_list))
    except Exception as e:
        raise
    return vlan_list


def normalize_interface_name(interface_name: str, short: bool = False) -> str:
    interface_type, interface_num = split_interface(interface_name=interface_name)
    if any([x is None for x in [interface_type, interface_num]]):
        msg = f"Failed to split interface_name '{interface_name}'"
        raise ValueError(msg)
    match_found = False
    if interface_type in INTERFACE_NAMES.keys():
        match_found = True
        if short:
            return INTERFACE_NAMES[interface_type][0] + interface_num
        else:
            return interface_type + interface_num
    for full_type, short_types in INTERFACE_NAMES.items():
        for short_type in short_types:
            if interface_type.lower().startswith(short_type.lower()):
                match_found = True
                if short:
                    interface_name = short_types[0] + interface_num
                else:
                    interface_name = full_type + interface_num
    if not match_found:
        msg = f"Given interface name does not comply with valid interface names. Given: {interface_name}, Expected: {list(INTERFACE_NAMES.keys())}"
        LOGGER.error(msg=msg)
        raise AssertionError(msg)

    return interface_name

def validate_unique(values: list):
    values_set = set(values)
    if len(values) != len(values_set):
        msg = f"Duplicate values found in: {values}"
        LOGGER.error(msg=msg)
        raise AssertionError(msg)
    return values

def old_validate_names_unique(values: List[BaseNetModel]):
    names = [x.name for x in values.get("servers")]
    if len(names) != len(set(names)):
        msg = f"Server names must be unique. Names: {names}."
        LOGGER.error(msg=msg)
        raise AssertionError(msg)

    return values

def old_validate_servers_unique(values: List[BaseNetModel]):
    servers = [x.server for x in values.get("servers")]
    if len(servers) != len(set(servers)):
        msg = f"Server addresses must be unique. Servers: {servers}."
        LOGGER.error(msg=msg)
        raise AssertionError(msg)

    return values


def required_together(values, required=List[str]) -> dict:
    for req in required:
        others = list(required)
        others.remove(req)
        if values.get(req) is not None:
            for other in others:
                if values.get(other) is None:
                    msg = f"RequiredTogether: {required}. Got '{req}' but '{other}' is None"
                    LOGGER.error(msg)
                    raise AssertionError(msg)
    return values

def validate_fields_unique(obj_list: List[BaseNetModel], fields: List[str]) -> List[BaseNetModels]:
    """
    This validator takes in a list of models and checks that the fields are not duplicate.
    Typical use case if for verifying that objects have different names/ip (AAA servers, etc)
    Args:
        obj_list: List of models
        fields: names of fields to check for duplicates

    Returns: The original list of models or raises Assertion Error

    """
    duplicate_fields = []
    if not isinstance(fields, list):
        fields = [fields]
    for field in fields:
        model_types = [x.__class__.__name__ for x in obj_list]
        field_list = [getattr(x, field) for x in obj_list]
        field_set = set(field_list)
        if len(field_set) != len(field_list):
            duplicate_fields.append(field)
    if len(duplicate_fields) == 0:
        return obj_list
    else:
        msg = f"Given models ({set(model_types)}) contain duplicate values for the following fields: {duplicate_fields}."
        LOGGER.error(msg=msg)
        raise AssertionError(msg)

def validate_unique_name_field(value: List[BaseNetCmModel]):
    # Filed might be optional
    if value is None:
        return value
    return validate_fields_unique(obj_list=value, fields=['name'])