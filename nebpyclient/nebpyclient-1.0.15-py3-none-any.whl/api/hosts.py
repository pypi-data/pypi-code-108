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

from .graphqlclient import GraphQLParam, NebMixin
from datetime import datetime
from .common import PageInput, read_value
from .filters import StringFilter
from .sorting import SortDirection

__all__ = [
    "Dimm",
    "Host",
    "HostSort",
    "HostFilter",
    "HostsMixin",
    "HostList",
    "UpdateHostInput"
]


class HostFilter:
    """A filter object to filter hosts.

    Allows filtering for specific hosts in nebulon ON. The filter allows only
    one property to be specified. If filtering on multiple properties is
    needed, use the ``and_filter`` and ``or_filter`` options to concatenate
    multiple filters.
    """

    def __init__(
            self,
            uuid: StringFilter = None,
            name: StringFilter = None,
            model: StringFilter = None,
            manufacturer: StringFilter = None,
            chassis_serial: StringFilter = None,
            board_serial: StringFilter = None,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new filter object

        The filter allows only one property to be specified. If filtering on
        multiple properties is needed, use the ``and_filter`` and ``or_filter``
        options to concatenate multiple filters.

        :param uuid: Filter based on host unique identifier
        :type uuid: UuidFilter, optional
        :param name: Filter based on host name
        :type name: StringFilter, optional
        :param model: Filter based on model name
        :type model: StringFilter, optional
        :param manufacturer: Filter based on manufacturer name
        :type manufacturer: StringFilter, optional
        :param chassis_serial: Filter based on chassis serial
        :type chassis_serial: StringFilter, optional
        :param board_serial: Filter based on board serial
        :type board_serial: StringFilter, optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: DataCenterFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: DataCenterFilter, optional
        """

        self.__uuid = uuid
        self.__name = name
        self.__model = model
        self.__manufacturer = manufacturer
        self.__chassis_serial = chassis_serial
        self.__board_serial = board_serial
        self.__and = and_filter
        self.__or = or_filter

    @property
    def uuid(self) -> StringFilter:
        """Filter based on host unique identifier"""
        return self.__uuid

    @property
    def name(self) -> StringFilter:
        """Filter based on host name"""
        return self.__name

    @property
    def model(self) -> StringFilter:
        """Filter based on host model name"""
        return self.__model

    @property
    def manufacturer(self) -> StringFilter:
        """Filter based on host manufacturer name"""
        return self.__manufacturer

    @property
    def chassis_serial(self) -> StringFilter:
        """Filter based on host chassis serial number"""
        return self.__chassis_serial

    @property
    def board_serial(self) -> StringFilter:
        """Filter based on board serial number"""
        return self.__board_serial

    @property
    def and_filter(self):
        """Allows concatenation of multiple filters via logical AND"""
        return self.__and

    @property
    def or_filter(self):
        """Allows concatenation of multiple filters via logical OR"""
        return self.__or

    @property
    def as_dict(self):
        result = dict()
        result["uuid"] = self.uuid
        result["name"] = self.name
        result["model"] = self.model
        result["manufacturer"] = self.manufacturer
        result["chassisSerial"] = self.chassis_serial
        result["boardSerial"] = self.board_serial
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class UpdateHostInput:
    """An input object to update host properties

    Allows updating of an existing host object in nebulon ON. Only few
    properties of a host are user modifiable. Most properties are automatically
    populated by the host's services processing unit (SPU).
    """

    def __init__(
            self,
            name: str = None,
            rack_uuid: str = None,
            note: str = None
    ):
        """Constructs a new input object to update a host

        :param name: The name of the host (server)
        :type name: str, optional
        :param rack_uuid: Allows assigning the host (server) to a rack
        :type rack_uuid: str, optional
        :param note: An optional note for the host
        :type note: str, optional
        """

        self.__name = name
        self.__rack_uuid = rack_uuid
        self.__note = note

    @property
    def name(self) -> str:
        """Name of the host"""
        return self.__name

    @property
    def rack_uuid(self) -> str:
        """Associated unique identifier of a rack associated with the host"""
        return self.__rack_uuid

    @property
    def note(self) -> str:
        """Optional note for the host"""
        return self.__note

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["rackUUID"] = self.rack_uuid
        result["note"] = self.note
        return result


class HostSort:
    """A sort object for hosts

    Allows sorting hosts on common properties. The sort object allows only one
    property to be specified.
    """

    def __init__(
            self,
            name: SortDirection = None,
            model: SortDirection = None,
            manufacturer: SortDirection = None
    ):
        """Constructs a new sort object for hosts

        The sort object allows only one property to be specified.

        :param name: Sort direction for the ``name`` property
        :type name: SortDirection, optional
        :param model: Sort direction for the ``model`` property
        :type model: SortDirection, optional
        :param manufacturer: Sort direction for the ``manufacturer`` property
        :type manufacturer: SortDirection, optional
        """

        self.__name = name
        self.__model = model
        self.__manufacturer = manufacturer

    @property
    def name(self) -> SortDirection:
        """Sort direction for the ``name`` property of a host object"""
        return self.__name

    @property
    def model(self) -> SortDirection:
        """Sort direction for the ``model`` property of a host object"""
        return self.__model

    @property
    def manufacturer(self) -> SortDirection:
        """Sort direction for the ``manufacturer`` property of a host object"""
        return self.__manufacturer

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["model"] = self.model
        result["manufacturer"] = self.manufacturer
        return result


class Dimm:
    """A memory DIMM object"""

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new DIMM object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__location = read_value(
            "location", response, str, True)
        self.__manufacturer = read_value(
            "manufacturer", response, str, True)
        self.__size_bytes = read_value(
            "sizeBytes", response, int, True)

    @property
    def location(self) -> str:
        """Location of the DIMM in the server"""
        return self.__location

    @property
    def manufacturer(self) -> str:
        """Manufacturer name for the DIMM"""
        return self.__manufacturer

    @property
    def size_bytes(self) -> int:
        """Memory DIMM size in bytes"""
        return self.__size_bytes

    @staticmethod
    def fields():
        return [
            "location",
            "manufacturer",
            "sizeBytes",
        ]


class Host:
    """A host or server that contains a nebulon SPU"""

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new host object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__uuid = read_value(
            "uuid", response, str, True)
        self.__chassis_serial = read_value(
            "chassisSerial", response, str, True)
        self.__board_serial = read_value(
            "boardSerial", response, str, True)
        self.__name = read_value(
            "name", response, str, True)
        self.__model = read_value(
            "model", response, str, True)
        self.__note = read_value(
            "note", response, str, True)
        self.__npod_uuid = read_value(
            "nPod.uuid", response, str, False)
        self.__spu_serials = read_value(
            "spus.serial", response, str, True)
        self.__spu_count = read_value(
            "spuCount", response, int, True)
        self.__rack_uuid = read_value(
            "rack.uuid", response, str, False)
        self.__manufacturer = read_value(
            "manufacturer", response, str, True)
        self.__cpu_count = read_value(
            "cpuCount", response, int, True)
        self.__cpu_type = read_value(
            "cpuType", response, str, True)
        self.__cpu_manufacturer = read_value(
            "cpuManufacturer", response, str, True)
        self.__cpu_core_count = read_value(
            "cpuCoreCount", response, int, True)
        self.__cpu_thread_count = read_value(
            "cpuThreadCount", response, int, True)
        self.__cpu_speed = read_value(
            "cpuSpeed", response, int, True)
        self.__dimm_count = read_value(
            "dimmCount", response, int, True)
        self.__dimms = read_value(
            "dimms", response, Dimm, True)
        self.__memory_bytes = read_value(
            "memoryBytes", response, int, True)
        self.__lom_hostname = read_value(
            "lomHostname", response, str, True)
        self.__lom_address = read_value(
            "lomAddress", response, str, True)
        self.__boot_time = read_value(
            "bootTime", response, datetime, True)

    @property
    def uuid(self) -> str:
        """Unique identifier of the host"""
        return self.__uuid

    @property
    def chassis_serial(self) -> str:
        """Chassis serial number of the host"""
        return self.__chassis_serial

    @property
    def board_serial(self) -> str:
        """Board serial number of the host"""
        return self.__board_serial

    @property
    def name(self) -> str:
        """Name of the host"""
        return self.__name

    @property
    def model(self) -> str:
        """Model of the host"""
        return self.__model

    @property
    def note(self) -> str:
        """Optional note for the host"""
        return self.__note

    @property
    def npod_uuid(self) -> str:
        """The unique identifier of the nPod this host is part of"""
        return self.__npod_uuid

    @property
    def spu_serials(self) -> [str]:
        """List of SPU serial numbers that are installed in this host"""
        return self.__spu_serials

    @property
    def spu_count(self) -> int:
        """Number of SPUs installed in this host"""
        return self.__spu_count

    @property
    def rack_uuid(self) -> str:
        """Unique identifier associated with this host"""
        return self.__rack_uuid

    @property
    def manufacturer(self) -> str:
        """Manufacturer name for this host"""
        return self.__manufacturer

    @property
    def cpu_count(self) -> int:
        """Number of installed CPUs in this host"""
        return self.__cpu_count

    @property
    def cpu_type(self) -> str:
        """CPU type of the CPUs installed in this host"""
        return self.__cpu_type

    @property
    def cpu_manufacturer(self) -> str:
        """CPU manufacturer of the CPUs installed in this host"""
        return self.__cpu_manufacturer

    @property
    def cpu_core_count(self) -> int:
        """Number of cores of the installed CPUs"""
        return self.__cpu_core_count

    @property
    def cpu_thread_count(self) -> int:
        """Number of threads of the installed CPUs"""
        return self.__cpu_thread_count

    @property
    def cpu_speed(self) -> int:
        """CPU clock speed"""
        return self.__cpu_speed

    @property
    def dimm_count(self) -> int:
        """Number of DIMMs installed in this host"""
        return self.__dimm_count

    @property
    def dimms(self) -> [Dimm]:
        """List of DIMMs installed in this host"""
        return self.__dimms

    @property
    def memory_bytes(self) -> int:
        """Total memory installed in the server in bytes"""
        return self.__memory_bytes

    @property
    def lom_hostname(self) -> str:
        """Hostname of the lights out management address of the host"""
        return self.__lom_hostname

    @property
    def lom_address(self) -> str:
        """IP address of the lights out management address of the host"""
        return self.__lom_address

    @property
    def boot_time(self) -> datetime:
        """Date and time when the host booted"""
        return self.__boot_time

    @staticmethod
    def fields():
        return [
            "uuid",
            "chassisSerial",
            "boardSerial",
            "name",
            "model",
            "note",
            "nPod{uuid}",
            "spus{serial}",
            "spuCount",
            "rack{uuid}",
            "manufacturer",
            "cpuCount",
            "cpuType",
            "cpuManufacturer",
            "cpuCoreCount",
            "cpuThreadCount",
            "cpuSpeed",
            "dimmCount",
            "dimms{%s}" % (",".join(Dimm.fields())),
            "memoryBytes",
            "lomHostname",
            "lomAddress",
            "bootTime",
        ]


class HostList:
    """Paginated host list object

    Contains a list of host objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new host list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__more = read_value(
            "more", response, bool, False)
        self.__total_count = read_value(
            "totalCount", response, int, False)
        self.__filtered_count = read_value(
            "filteredCount", response, int, False)
        self.__items = read_value(
            "items", response, Host, False)

    @property
    def items(self) -> [Host]:
        """List of hosts in the pagination list"""
        return self.__items

    @property
    def more(self) -> bool:
        """Indicates if there are more items on the server"""
        return self.__more

    @property
    def total_count(self) -> int:
        """The total number of items on the server"""
        return self.__total_count

    @property
    def filtered_count(self) -> int:
        """The number of items on the server matching the provided filter"""
        return self.__filtered_count

    @staticmethod
    def fields():
        return [
            "items{%s}" % (",".join(Host.fields())),
            "more",
            "totalCount",
            "filteredCount",
        ]


class HostsMixin(NebMixin):
    """Mixin to add host related methods to the GraphQL client"""

    def get_hosts(
            self,
            page: PageInput = None,
            h_filter: HostFilter = None,
            sort: HostSort = None
    ) -> HostList:
        """Retrieves a list of host objects

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param h_filter: A filter object to filter the hosts on the
            server. If omitted, the server will return all objects as a
            paginated response.
        :type h_filter: HostFilter, optional
        :param sort: A sort definition object to sort the host objects
            on supported properties. If omitted objects are returned in the
            order as they were created in.
        :type sort: HostSort, optional

        :returns HostList: A paginated list of hosts.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            h_filter, "HostFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "HostSort", False)

        # make the request
        response = self._query(
            name="getHosts",
            params=parameters,
            fields=HostList.fields()
        )

        # convert to object
        return HostList(response)

    def update_host(
            self,
            uuid: str,
            name: str = None,
            rack_uuid: str = None,
            note: str = None
    ):
        """Allows updating properties of a host object

        :param uuid: The unique identifier of the host to update
        :type uuid: str
        :param name: The new name of the host (server)
        :type name: str, optional
        :param rack_uuid: Allows assigning the host (server) to a rack
        :type rack_uuid: str, optional
        :param note: An optional note for the host
        :type note: str, optional
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "String", True)
        parameters["input"] = GraphQLParam(
            UpdateHostInput(
                name=name,
                rack_uuid=rack_uuid,
                note=note
            ),
            "UpdateHostInput",
            True
        )

        # make the request
        response = self._mutation(
            name="updateHost",
            params=parameters,
            fields=Host.fields()
        )

        # convert to object
        return Host(response)
