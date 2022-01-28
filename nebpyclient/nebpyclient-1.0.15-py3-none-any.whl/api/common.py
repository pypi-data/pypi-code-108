#
# Copyright 2020 Nebulon, Inc.
# All Rights Reserved.
#
# DISCLAIMER: THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
# EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
# OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

from enum import Enum
from datetime import datetime

__all__ = [
    "read_value",
    "time_to_str",
    "parse_time",
    "NebEnum",
    "PageInput",
    "DateFormat",
    "ResourceType",
]


def parse_time(value: str) -> datetime:
    """Parse and convert JSON encoded string to a datetime object

    Parses a ``str`` and converts it to a ``datetime`` object. If the string is
    not a valid JSON (JavaScript) encoded datetime object, this function will
    return the minimum datetime value (`datetime.min`).

    :param value: The string value to parse
    :type value: str

    :returns datetime: A ``datetime`` version of the provided JSON-time string
    """

    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return datetime.min


def time_to_str(value: datetime) -> str:
    """Convert a datetime object to a JSON (JavaScript) compliant string

    Formats the provided datetime object to a ``str`` that is compliant with the
    JSON schema. Example: `2020-01-01T10:10:10Z`.

    :param value: The ``datetime`` object to convert
    :type value: datetime

    :raises ValueError: If the provided value is not a valid datetime object

    :returns str: the JSON (JavaScript) compliant version of the date and time
    """

    if value is None or not isinstance(value, datetime):
        raise ValueError("provided value is not a valid datetime object")

    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def read_value(
        key_path: str,
        data: dict,
        data_type: type,
        mandatory=True
) -> any:
    """Helper function to extract values from a response dict

    Allows extraction of nested values from a dictionary for convenience.
    This also allows for type checking and for validating that mandatory
    properties were supplied.

    :param key_path: A JSONPath-like path to a value in the dictionary. Each
        hierarchy is separated via a dot. Example: `parent_key.child_key` will
        lookup a value in the provided dict `data["parent_key"]["child_key"]`
    :type key_path: str
    :param data: A dictionary of values, typically JSON returned from the
        nebulon ON API. Values will be looked up in this dict
    :type data: dict
    :param data_type: The expected data type for the lookup value. If the
        lookup value is a list, the expected element type shall be supplied.
    :type data_type: type
    :param mandatory: Indicates if the lookup value must be provided. If set
        to ``True`` the lookup value must not be ``None`` or a ``ValueError`` is
        raised.

    :returns any: Returns the value in the dict (if found) that is identified
        via the provided key_path. If the value is not found or if the value
        is None while mandatory, a ValueError is raised.

    :raises ValueError: If the value indicated by ``key_path`` is not found in
        the dict supplied in ``data``, if the lookup value is None while it is a
        mandatory value, or if the supplied ``data_type`` does not match the
        lookup value data type.
    """

    # build the path. we expect a ``key_path`` that looks like this:
    # "key1.key2.key3" -> ["key1", "key2", "key3"]
    segments = key_path.split(".")

    # segments should always have at least one element that exists in the
    # dictionary that is provided via ``data``.
    if data is None or len(segments) == 0 or segments[0] not in data:
        if mandatory:
            raise Exception(f"provided key {key_path} is invalid for {data}")

        return None

    # handle the current key. this could be any key in the hierarchy
    key = segments[0]
    value = data[key]

    # first we need to check for it to be not None if it is a mandatory value.
    # it is ok to return None if the value is not mandatory
    if value is None:
        if mandatory:
            raise Exception(f"required property {key} was not set")

        return None

    # if there are more children, we need to return the contents of these
    # instead of the current value
    if len(segments) > 1:

        child_key = ".".join(segments[1:])

        # handle lists separately
        if isinstance(value, list):
            return [read_value(child_key, i, data_type, mandatory)
                    for i in value]

        # single items we can just return
        return read_value(child_key, value, data_type, mandatory)

    # this is the last element in the hierarchy and we need to convert it to
    # the expected data_type. Handle list separately
    if isinstance(value, list):
        return [__convert_value(key, i, data_type) for i in value]

    return __convert_value(key, value, data_type)


def __convert_value(
        key: str,
        value: any,
        data_type: type
) -> any:
    """Verify a named value for the specified type and convert if necessary

    Allows type checking of a named value against a provided data type. It also
    cleans up any type issues that may result from JSON encoding and decoding.

    :param key: The name of the key in a dictionary. While this parameter is
        not used for the type checking, it is used to provide a meaningful
        error message.
    :type key: str
    :param value: The value in the dictionary that will be type-checked. If the
        supplied value is ``None``, type checking is omitted.
    :type: any
    :param data_type: The type that ``value`` needs to match or what it will be
        converted to.
    :type: type

    :raises ValueError: An error indicating if there are any issues with the
        supplied value matching the provided data type.

    :returns any: The converted value in the specified type.
    """

    if value is None:
        return None

    if isinstance(value, data_type):
        return value

    # convert any integers if a float is expected. This can happen during
    # JSON encoding and decoding.
    if data_type == float and isinstance(value, int):
        return float(value)

    # datetime objects are supplied as a JSON (JavaScript) string.
    if data_type == datetime and isinstance(value, str):
        return parse_time(value)

    # enumerations are supplied as strings
    if issubclass(data_type, NebEnum) and isinstance(value, str):
        return getattr(data_type, "parse")(value)

    # dicts are interpreted as objects, so we instantiate a new object from
    # the provided dictionary. This may fail if the supplied data_type does
    # not have a constructor that accepts a dictionary.
    if isinstance(value, dict):
        return data_type(value)

    # if we got to this place an invalid data type was supplied and we raise
    # a ValueError.
    error = f"{key} of invalid type {data_type}, got {value.__class__}"
    raise ValueError(error)


class NebEnum(Enum):
    """An enumeration that is used in nebulon ON

    This enumeration is used as a parent class to provide convenience functions
    for encoding and decoding enumerations that are defined in nebulon ON.
    """

    @classmethod
    def parse(
            cls,
            value: str
    ):
        """Construct a new ``Enum`` from the provided ``str`` value.

        :param value: A string representation of a member of this ``Enum``.
        :type value: str

        :raises ValueError: If the value is not a member of the ``NebEnum``

        :returns Enum: The ``NebEnum`` value that matches the provided value.
        """

        if value is None or len(value) == 0:
            raise ValueError("provided value may not be None or empty")

        for item in cls:
            if value == item.value:
                # found a matching value
                return item

        raise ValueError(f"Could not parse value '{value}'")


class DateFormat(NebEnum):
    """Defines available date and time format options

    Examples:
        * ANSIC: ``Mon Jan _2 15:04:05 2006``
        * UnixDate: ``Mon Jan _2 15:04:05 MST 2006``
        * RubyDate: ``Mon Jan 02 15:04:05 -0700 2006``
        * RFC822: ``02 Jan 06 15:04 MST``
        * RFC822Z: ``02 Jan 06 15:04 -0700``
        * RFC850: ``Monday, 02-Jan-06 15:04:05 MST``
        * RFC1123: ``Mon, 02 Jan 2006 15:04:05 MST``
        * RFC1123Z: ``Mon, 02 Jan 2006 15:04:05 -0700``
        * RFC3339: ``2006-01-02T15:04:05Z07:00``
        * RFC3339Nano: ``2006-01-02T15:04:05.999999999Z07:00``
        * Kitchen: ``3:04PM``
        * Stamp: ``Jan _2 15:04:05``
        * StampMilli: ``Jan _2 15:04:05.000``
        * StampMicro: ``Jan _2 15:04:05.000000``
        * StampNano: ``Jan _2 15:04:05.000000000``

    """

    ANSIC = "ANSIC"
    UNIX_DATE = "UnixDate"
    RUBY_DATE = "RubyDate"
    RFC822 = "RFC822"
    RFC822_Z = "RFC822Z"
    RFC850 = "RFC850"
    RFC1123 = "RFC1123"
    RFC1123_Z = "RFC1123Z"
    RFC3339 = "RFC3339"
    RFC3339_NANO = "RFC3339Nano"
    KITCHEN = "Kitchen"
    STAMP = "Stamp"
    STAMP_MILLI = "StampMilli"
    STAMP_MICRO = "StampMicro"
    STAMP_NANO = "StampNano"


class ResourceType(NebEnum):
    """Defines a resource type in a nebulon infrastructure"""

    Unknown = "Unknown"
    """The resource type is not known"""

    Datacenter = "Datacenter"
    """A datacenter location information resource"""

    Host = "Host"
    """A server or host resource"""

    Disk = "Disk"
    """A physical drive or physical disk resource"""

    Pod = "Pod"
    """A nPod resource"""

    PodGroup = "PodGroup"
    """A group of nPods """

    Lab = "Lab"
    """A room or lab in a datacenter"""

    Rack = "Rack"
    """A rack in a datacenter row"""

    Row = "Row"
    """A row in a datacenter"""

    Snapshot = "Snapshot"
    """A point-in-time checkpoint of a storage volume"""

    SPU = "SPU"
    """A services processing unit"""

    VM = "VM"
    """A virtual machine"""

    Volume = "Volume"
    """A storage volume"""

    NetworkInterface = "NetworkInterface"
    """A network interface"""


class PageInput:
    """Defines input properties for pagination

    Allows specifying which page to return from the server for API calls that
    support pagination. It allows to specify the page number and the quantity
    of items to return in the page. Default values for a page are page number
    1 and 100 items per page.
    """

    def __init__(
            self,
            page: int = 1,
            count: int = 100
    ):
        """Constructs a new PageInput object.

        Allows specifying which page to return from the server for API calls
        that support pagination. It allows to specify the page number and the
        quantity of items to return in the page. Default values for a page
        are page number 1 and 100 items per page.

        :param page: The page number. Defaults to 1.
        :type page: int, optional
        :param count: The maximum number of items to include in a page.
            Defaults to 100.
        :type count: int, optional

        :raises ValueError: If an out of range ``page`` number is provided
        :raises ValueError: If an out of range ``count`` number is provided
        """

        if page < 1:
            raise ValueError("page must be a positive int")

        if count < 1:
            raise ValueError("count must be a positive int")

        self.__page = page
        self.__count = count

    @property
    def page(self) -> int:
        """Specifies the page number to return"""
        return self.__page

    @property
    def count(self) -> int:
        """Specifies the maximum number of items to include per page"""
        return self.__count

    @property
    def as_dict(self):
        result = dict()
        result["page"] = self.page
        result["count"] = self.count
        return result
