# Standard Libraries
import re
# Third party packages
from pydantic.typing import (
    Literal,
    List,
    Union,
    Tuple
)
# Local package
from net_models.config import LOGGER_INTERFACE_UTILS
# Local module


LOGGER = LOGGER_INTERFACE_UTILS

BASE_INTERFACE_REGEX = re.compile(pattern=r"(?P<type>^[A-z]{2,}(?:[A-z\-])*)(?P<numbers>\d+(?:\/\d+)*(?:\:\d+)?(?:\.\d+)?)(\s*)$")
INTEFACE_TYPE_DEFAULT_WEIGHT = 50
INTEFACE_TYPE_MAX_WEIGHT = 255

INTERFACE_NAMES = {
    "Ethernet": ["Et", "Eth"],
    "FastEthernet": ["Fa"],
    "GigabitEthernet": ["Gi"],
    "TenGigabitEthernet": ["Te"],
    "TwentyFiveGigE": ["Twe"],
    "FortyGigabitEthernet": ["Fo"],
    "HundredGigE": ["Hu"],
    "Port-channel": ["Po"],
    "Tunnel": ["Tu"],
    "Vlan": ["Vl"],
    "BDI": ["BDI"],
    "Loopback": ["Lo"],
    "Serial": ["Se"],
    "pseudowire": ["pw"],
    "CEM": ["CEM"],
    "xe-": ["xe-"]

}

INTERFACE_TYPE_WEIGHT_MAP = {
    100: ["Loopback"],
    95: ["Vlan"],
    90: ["BDI"],
    80: ["Tunnel"],
    75: ["pseudowire"],
    40: ['Port-channel']

}

def split_interface(interface_name: str) -> Union[Tuple[str, str], Tuple[None, None]]:
    try:
        match = re.match(pattern=BASE_INTERFACE_REGEX, string=interface_name)
    except TypeError as e:
        LOGGER.error("Expected string or bytes-like object, cannot match on '{}'".format(type(interface_name)))
        return (None, None)
    if match:
        return [match.group("type"), match.group("numbers")]
    else:
        LOGGER.error("Given interface '{}' did not match parsing pattern.".format(interface_name))
        return (None, None)

def extract_numbers(text: str, max_length: int = 6) -> Union[List[int], None]:

    numbers = [0]*max_length
    NUMBER_REGEX = re.compile(pattern=r"\d+")
    SLOTS_REGEX = re.compile(pattern=r"^(?:\d+)(?:[\/]\d+)*")
    SUBINT_REGEX = re.compile(pattern=r"\.(?P<number>\d+)$")
    CHANNEL_REGEX = re.compile(pattern=r"\:(?P<number>\d+)")

    slots, subint, channel = (None, None, None)
    m = SLOTS_REGEX.search(string=text)
    if m:
        slots = [int(x.group(0)) for x in NUMBER_REGEX.finditer(string=m.group(0))]

    m = CHANNEL_REGEX.search(string=text)
    if m:
        channel = int(m.group("number"))

    m = SUBINT_REGEX.search(string=text)
    if m:
        subint = int(m.group("number"))

    if not any([slots, channel, subint]):
        LOGGER.error(f"Failed to extract numbers from {text}")
        return None

    if subint:
        numbers[-1] = subint
    if channel:
        numbers[-2] = channel

    if len(slots) > (max_length - 2):
        msg = f"Cannot unpack {len(slots)} slots with max_length == {max_length}"
        LOGGER.error(msg)
        raise ValueError(msg)
    else:
        offset = (max_length - 2) - len(slots)
        for index, slot in enumerate(slots):
            numbers[offset + index] = slot
    return numbers, len(slots)


def get_weight_by_type(interface_type: str) -> int:
    for weight, interface_types in INTERFACE_TYPE_WEIGHT_MAP.items():
        if interface_type in interface_types:
            return weight
    return INTEFACE_TYPE_DEFAULT_WEIGHT

def get_interface_index(interface_name: str, max_length: int = 6, max_bits: int = 16) -> int:
    interface_type, numbers = split_interface(interface_name=interface_name)

    try:
        numbers, len_slots = extract_numbers(text=numbers, max_length=max_length)
        LOGGER.debug(msg=f"Numbers: {numbers}, LenSlots: {len_slots}")
    except ValueError as e:
        LOGGER.error(f"{repr(e)}")
        return 0

    binary_numbers = [format(x, f"0{max_bits}b") for x in numbers]
    reverse_weight = INTEFACE_TYPE_MAX_WEIGHT - get_weight_by_type(interface_type=interface_type)
    index_binary = format(reverse_weight, "08b") + format(len_slots, "04b") + "".join(binary_numbers)
    index = int(index_binary, 2)
    LOGGER.debug(msg=f"Interface: '{interface_name}' LenSlots: {len_slots} Index: {index} IndexBinary: {index_binary}")
    return index
