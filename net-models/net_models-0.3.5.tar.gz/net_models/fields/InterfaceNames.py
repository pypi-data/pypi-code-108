import re
import functools

from pydantic.typing import Any, Dict, List, Literal, Tuple, Union

from net_models.utils import get_logger

LOGGER = get_logger(name='NetInterfaceName')

class InterfaceName(str):


    def __new__(cls, v) -> 'BaseInterfaceName':
        return cls.validate(v)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v) -> 'BaseInterfaceName':
        sorted_weights = sorted(BaseInterfaceName._registry.keys(), reverse=True)
        for weight in sorted_weights:
            subclass = BaseInterfaceName._registry[weight]
            model = None
            try:
                model = subclass.validate(v)
                return model
            except AssertionError as e:
                pass

    @classmethod
    def validate_name(cls, v):
        raise NotImplementedError
        LOGGER.warning("Using deprecated classmethod 'validate_name'. Please switch to 'validate'")
        return cls.validate(v)


class BaseInterfaceName(InterfaceName):
    WEIGHT = 0
    _registry = {}

    INTERFACE_REGEX: re.Pattern = None
    INTERFACE_NAMES: Dict[str, str] = None
    DELIMITER: str = ""
    INTERFACE_TYPE_WEIGHT_MAP: Dict[int, List[str]] = None
    INTEFACE_TYPE_MAX_WEIGHT: int = 255
    INTEFACE_TYPE_DEFAULT_WEIGHT: int = 50


    def __init_subclass__(cls, **kwargs):
        cls._registry[cls.WEIGHT] = cls

    def __new__(cls, v):
        return cls.validate(v)

    @classmethod
    def split_interface(cls, interface_name: str) -> Tuple[str, str]:
        try:
            match = re.match(pattern=cls.INTERFACE_REGEX, string=interface_name)
        except TypeError as e:
            msg = f"Expected string or bytes-like object, cannot match on '{type(interface_name)}'"
            LOGGER.debug(msg=msg)
            raise TypeError(msg)
        if match:
            return [match.group("type"), match.group("numbers")]
        else:
            msg = f"Given interface '{interface_name}' did not match parsing pattern."
            LOGGER.debug(msg=msg)
            raise ValueError(msg)

    @classmethod
    def normalize(cls, v):
        interface_type, interface_name = (None, None)
        try:
            interface_type, interface_num = cls.split_interface(interface_name=v)
            match_found = False
            if interface_type in cls.INTERFACE_NAMES.keys():
                match_found = True
                interface_name = interface_type + cls.DELIMITER + interface_num
            else:
                for full_type, short_types in cls.INTERFACE_NAMES.items():
                    for short_type in short_types:
                        if interface_type.lower().startswith(short_type.lower()):
                            match_found = True
                            interface_name = full_type + cls.DELIMITER + interface_num
                            break
                    if match_found:
                        break
            if match_found:
                return interface_name
            else:
                raise ValueError(msg=f"Interface type '{interface_type}' not found in names for {cls.__name__}")
        except (TypeError, ValueError) as e:
            msg = f"Value '{v}' is not a valid name for {cls.__name__}"
            raise ValueError(msg)

    @classmethod
    def validate(cls, v):
        validated_v = None
        try:
            validated_v = cls.normalize(v=v)
        except ValueError as e:
            raise AssertionError(f"Value '{v}' is not a valid name for {cls.__name__}")
        if validated_v is not None:
            return str.__new__(cls, validated_v)

    ### Generic Properties ###
    @functools.cached_property
    def interface_type(self):
        return self.split_interface(interface_name=self)[0]

    @functools.cached_property
    def interface_number(self):
        return self.split_interface(interface_name=self)[1]

    @functools.cached_property
    def short(self):
        return f"{self.INTERFACE_NAMES[self.interface_type][0]}{self.DELIMITER}{self.interface_number}"

    @property
    def long(self):
        return self

    def extract_numbers(self, max_length: int = 6) -> Union[List[int], None]:

        interface_number = self.interface_number
        numbers = [0]*max_length
        NUMBER_REGEX = re.compile(pattern=r"\d+")
        SLOTS_REGEX = re.compile(pattern=r"^(?:\d+)(?:[\/]\d+)*")
        SUBINT_REGEX = re.compile(pattern=r"\.(?P<number>\d+)$")
        CHANNEL_REGEX = re.compile(pattern=r"\:(?P<number>\d+)")

        slots, subint, channel = (None, None, None)
        m = SLOTS_REGEX.search(string=interface_number)
        if m:
            slots = [int(x.group(0)) for x in NUMBER_REGEX.finditer(string=m.group(0))]

        m = CHANNEL_REGEX.search(string=interface_number)
        if m:
            channel = int(m.group("number"))

        m = SUBINT_REGEX.search(string=interface_number)
        if m:
            subint = int(m.group("number"))

        if not any([slots, channel, subint]):
            LOGGER.error(f"Failed to extract numbers from {interface_number}")
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

    def get_weight(self) -> int:
        interface_type = self.interface_type
        for weight, interface_types in self.INTERFACE_TYPE_WEIGHT_MAP.items():
            if interface_type in interface_types:
                return weight
        return self.INTEFACE_TYPE_DEFAULT_WEIGHT

    def get_index(self, max_length: int = 6, max_bits: int = 16) -> int:
        interface_type, numbers = self.interface_type, self.interface_number

        try:
            numbers, len_slots = self.extract_numbers()
            LOGGER.debug(msg=f"Numbers: {numbers}, LenSlots: {len_slots}")
        except ValueError as e:
            LOGGER.error(f"{repr(e)}")
            return 0

        binary_numbers = [format(x, f"0{max_bits}b") for x in numbers]
        reverse_weight = self.INTEFACE_TYPE_MAX_WEIGHT - self.get_weight()
        index_binary = format(reverse_weight, "08b") + format(len_slots, "04b") + "".join(binary_numbers)
        index = int(index_binary, 2)
        LOGGER.debug(msg=f"Interface: '{self}' LenSlots: {len_slots} Index: {index} IndexBinary: {index_binary}")
        return index



class IosInterfaceName(BaseInterfaceName):
    WEIGHT = 200

    INTERFACE_REGEX = re.compile(pattern=r"(?P<type>^[A-z]{2,}(?:[A-z\-])*)(?P<numbers>\d+(?:\/\d+)*(?:\:\d+)?(?:\.\d+)?)(\s*)$")
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
        "MPLS-SR-Tunnel": ["MPLS-SR-Tunnel"]
    }
    INTERFACE_TYPE_WEIGHT_MAP = {
        100: ["Loopback"],
        95: ["Vlan"],
        90: ["BDI"],
        80: ["Tunnel"],
        75: ["pseudowire"],
        40: ['Port-channel']
    }


class JuniperInterfaceName(BaseInterfaceName):
    WEIGHT = 150

    INTERFACE_REGEX = re.compile(pattern=r"(?P<type>^[A-z]{2,}(?:[A-z])*)(?:-)?(?P<numbers>\d+(?:\/\d+)*(?:\:\d+)?(?:\.\d+)?)(\s*)$")
    DELIMITER = "-"
    INTERFACE_NAMES = {
        "xe": ["xe"],
    }
    INTERFACE_TYPE_WEIGHT_MAP = {}


class GenericInterfaceName(BaseInterfaceName):
    WEIGHT = 1

    INTERFACE_REGEX = re.compile(pattern=r"^.*$")


    @classmethod
    def normalize(cls, v):
        return v



    @functools.cached_property
    def short(self):
        return self.long
