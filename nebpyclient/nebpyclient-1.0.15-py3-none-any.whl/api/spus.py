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
from .npods import NPodSpuInput, \
    BondType, \
    BondLACPTransmitRate, \
    BondTransmitHashPolicy
from .updates import UpdateHistory
from .tokens import TokenResponse
from .issues import Issues

__all__ = [
    "SpuSort",
    "SpuFilter",
    "NTPServerInput",
    "SecureEraseSPUInput",
    "ReplaceSpuInput",
    "SetNTPServersInput",
    "NTPServer",
    "IPInfoState",
    "Spu",
    "SpuList",
    "SpuCustomDiagnostic",
    "SpuMixin"
]


class SpuSort:
    """A sort object for services processing units (SPU)

    Allows sorting SPUs on common properties. The sort object allows only one
    property to be specified.
    """

    def __init__(
            self,
            serial: SortDirection = None
    ):
        """Constructs a new sort object for SPUs

        Allows sorting SPUs on common properties. The sort object allows
        only one property to be specified.

        :param serial: Sort direction for the ``serial`` property
        :type serial: SortDirection, optional
        """

        self.__serial = serial

    @property
    def serial(self) -> SortDirection:
        """Sort direction for the ``serial`` property"""
        return self.__serial

    @property
    def as_dict(self):
        result = dict()
        result["serial"] = self.serial
        return result


class SpuFilter:
    """A filter object to filter services processing units (SPU)

    Allows filtering for specific SPUs registered in nebulon ON. The
    filter allows only one property to be specified. If filtering on multiple
    properties is needed, use the ``and_filter`` and ``or_filter`` options to
    concatenate multiple filters.
    """

    def __init__(
            self,
            serial: StringFilter = None,
            not_in_npod: bool = None,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new filter object

        The filter allows only one property to be specified. If filtering on
        multiple properties is needed, use the ``and_filter`` and ``or_filter``
        options to concatenate multiple filters.

        :param serial: Filter based on SPU serial number
        :type serial: StringFilter, optional
        :param not_in_npod: Filter for SPUs that are not in a nPod
        :type not_in_npod: bool, optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: SpuFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: SpuFilter, optional
        """

        self.__serial = serial
        self.__not_in_npod = not_in_npod
        self.__and = and_filter
        self.__or = or_filter

    @property
    def serial(self) -> StringFilter:
        """Filter based on SPU serial number"""
        return self.__serial

    @property
    def not_in_npod(self) -> bool:
        """Filter for SPUs that are not in a nPod"""
        return self.__not_in_npod

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
        result["serial"] = self.serial
        result["notInNPod"] = self.not_in_npod
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class NTPServerInput:
    """An input object to configure a NTP server

    NTP servers are used for automatic time configuration on the services
    processing unit (SPU). The SPU has default network time servers (NTP)
    configured. However, customers can customize them if the default NTP
    servers are not accessible or different time settings are required.
    """

    def __init__(
            self,
            server_hostname: str,
            pool: bool = None,
            prefer: bool = None
    ):
        """Constructs a new input object to configure NTP servers

        NTP servers are used for automatic time configuration on the services
        processing unit (SPU). The SPU has default network time servers (NTP)
        configured. However, customers can customize them if the default NTP
        servers are not accessible or different time settings are required.

        :param server_hostname: The DNS hostname of the NTP server to use
        :type server_hostname: str
        :param pool: Indicates if the specified NTP server hostname is a NTP
            pool. By default, this value is considered ``False``.
        :type pool: bool, optional
        :param prefer: Indicates if the specified NTP server is the preferred
            NTP server. By default, this value is considered ``False``.
        :type prefer: bool, optional
        """

        self.__server_hostname = server_hostname
        self.__pool = pool
        self.__prefer = prefer

    @property
    def server_hostname(self) -> str:
        """The DNS hostname of the NTP server"""
        return self.__server_hostname

    @property
    def pool(self) -> bool:
        """Indicates if the specified NTP server hostname is a NTP pool"""
        return self.__pool

    @property
    def prefer(self) -> bool:
        """Indicates if the specified NTP server is the preferred NTP server"""
        return self.__prefer

    @property
    def as_dict(self):
        result = dict()
        result["serverHostname"] = self.server_hostname
        result["pool"] = self.pool
        result["prefer"] = self.prefer
        return result


class SecureEraseSPUInput:
    """An input object to secure-erase a services processing unit (SPU)

    The secure erase functionality allows a deep-erase of data stored on the
    physical drives attached to the SPU. Only SPUs that are not part of a
    nPod can be secure-erased.
    """

    def __init__(
            self,
            spu_serial: str
    ):
        """Constructs a new input object for secure-erase a SPU

        The secure erase functionality allows a deep-erase of data stored on
        the physical drives attached to the SPU. Only SPUs that are not part
        of a nPod can be secure-erased.

        :param spu_serial: The serial number of the SPU to secure-erase
        :type spu_serial: str
        """

        self.__spu_serial = spu_serial

    @property
    def spu_serial(self) -> str:
        """The serial number of the SPU"""
        return self.__spu_serial

    @property
    def as_dict(self):
        result = dict()
        result["spuSerial"] = self.spu_serial
        return result


class ReplaceSpuInput:
    """An input object to replace a services processing unit (SPU)

    The replace services processing unit (SPU) operation is used to transition
    the configuration of an old, likely failed, SPU to a new replacement unit
    and allows modifying the configuration during the process.
    """

    def __init__(
            self,
            npod_uuid: str,
            previous_spu_serial: str,
            new_spu_info: NPodSpuInput,
            sset_uuid: str
    ):
        """Constructs a new input object to replace a SPU

        The replace services processing unit (SPU) operation is used to
        transition the configuration of an old, likely failed, SPU to a new
        replacement unit and allows modifying the configuration during the
        process.

        :param npod_uuid: The unique identifier of the nPod of the old SPU
            that is being replaced
        :type npod_uuid: str
        :param previous_spu_serial: The serial number of the old SPU that is
            being replaced
        :type previous_spu_serial: str
        :param new_spu_info: Configuration information for the new SPU
        :type new_spu_info: NPodSpuInput
        :param sset_uuid: The storage set information for the existing SPU.
            This information can be obtained from the active replacement
            alert and only used to verify that the correct SPU is selected.
        :type sset_uuid: str
        """

        self.__npod_uuid = npod_uuid
        self.__previous_spu_serial = previous_spu_serial
        self.__new_spu_info = new_spu_info
        self.__sset_uuid = sset_uuid

    @property
    def npod_uuid(self) -> str:
        """The UUID of the nPod of the old SPU that is being replaced"""
        return self.__npod_uuid

    @property
    def previous_spu_serial(self) -> str:
        """The serial number of the old SPU that is being replaced"""
        return self.__previous_spu_serial

    @property
    def new_spu_info(self) -> NPodSpuInput:
        """Configuration information for the new SPU"""
        return self.__new_spu_info

    @property
    def sset_uuid(self) -> str:
        """The storage set information for the existing SPU"""
        return self.__sset_uuid

    @property
    def as_dict(self):
        result = dict()
        result["nPodUUID"] = self.npod_uuid
        result["previousSPUSerial"] = self.previous_spu_serial
        result["newSPUInfo"] = self.new_spu_info
        result["ssetUUID"] = self.sset_uuid
        return result


class SetNTPServersInput:
    """An input object to configure NTP servers

    NTP servers are used for automatic time configuration on the services
    processing unit (SPU). The SPU has default network time servers (NTP)
    configured. However, customers can customize them if the default NTP
    servers are not accessible or different time settings are required.
    """

    def __init__(
            self,
            servers: [NTPServerInput],
            spu_serial: str = None,
            npod_uuid: str = None
    ):
        """Constructs a new input object to configure NTP servers

        NTP servers are used for automatic time configuration on the services
        processing unit (SPU). The SPU has default network time servers (NTP)
        configured. However, customers can customize them if the default NTP
        servers are not accessible or different time settings are required.

        Either a SPU serial number or a nPod uuid must be specified.

        :param servers: List of NTP server configurations that shall be applied
            to an SPU
        :type servers: [NTPServerInput]
        :param spu_serial: The serial number of the services processing unit
        :type spu_serial: str, optional
        :param npod_uuid: The unique identifier of the nPod
        :type npod_uuid: str, optional
        """

        self.__spu_serial = spu_serial
        self.__pod_uuid = npod_uuid
        self.__servers = servers

    @property
    def spu_serial(self) -> str:
        """The serial number of the services processing unit"""
        return self.__spu_serial

    @property
    def pod_uuid(self) -> str:
        """The unique identifier of the nPod"""
        return self.__pod_uuid

    @property
    def servers(self) -> [NTPServerInput]:
        """List of NTP server configurations that shall be applied to an SPU"""
        return self.__servers

    @property
    def as_dict(self):
        result = dict()
        result["spuSerial"] = self.spu_serial
        result["podUUID"] = self.pod_uuid
        result["servers"] = self.servers
        return result


class NTPServer:
    """A network time protocol server

    NTP servers are used for automatic time configuration on the services
    processing unit (SPU).
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new network time protocol server

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__server_hostname = read_value(
            "serverHostname", response, str, True)
        self.__pool = read_value(
            "pool", response, bool, True)
        self.__prefer = read_value(
            "prefer", response, bool, True)

    @property
    def server_hostname(self) -> str:
        """The DNS hostname of the NTP server"""
        return self.__server_hostname

    @property
    def pool(self) -> bool:
        """Indicates if the specified NTP server hostname is a NTP pool"""
        return self.__pool

    @property
    def prefer(self) -> bool:
        """Indicates if the specified NTP server is the preferred NTP server"""
        return self.__prefer

    @staticmethod
    def fields():
        return [
            "serverHostname",
            "pool",
            "prefer",
        ]


class IPInfoState:
    """A state for IP configuration of a SPU logical network interface"""

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new IPInfoState object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__dhcp = read_value(
            "dhcp", response, bool, True)
        self.__addresses = read_value(
            "addresses", response, str, True)
        self.__gateway = read_value(
            "gateway", response, str, True)
        self.__bond_mode = read_value(
            "bondMode", response, BondType, True)
        self.__bond_transmit_hash_policy = read_value(
            "bondTransmitHashPolicy", response, BondTransmitHashPolicy, False)
        self.__bond_mii_monitor_milli_seconds = read_value(
            "bondMIIMonitorMilliSeconds", response, int, False)
        self.__bond_lacp_transmit_rate = read_value(
            "bondLACPTransmitRate", response, BondLACPTransmitRate, False)
        self.__interface_names = read_value(
            "interfaceNames", response, str, True)
        self.__interface_mac = read_value(
            "interfaceMAC", response, str, True)
        self.__half_duplex = read_value(
            "halfDuplex", response, bool, True)
        self.__speed = read_value(
            "speed", response, int, True)
        self.__locked_speed = read_value(
            "lockedSpeed", response, bool, True)
        self.__mtu = read_value(
            "mtu", response, int, True)
        self.__switch_name = read_value(
            "switchName", response, str, True)
        self.__switch_mac = read_value(
            "switchMAC", response, str, True)
        self.__switch_port = read_value(
            "switchPort", response, str, True)

    @property
    def dhcp(self) -> bool:
        """Indicates if DHCP is used for IP addressing"""
        return self.__dhcp

    @property
    def addresses(self) -> [str]:
        """List of IPv4 or IPv6 addresses in CIDR format"""
        return self.__addresses

    @property
    def gateway(self) -> str:
        """The gateway IP address specified for the interface"""
        return self.__gateway

    @property
    def bond_mode(self) -> BondType:
        """The link aggregation mode for the interface"""
        return self.__bond_mode

    @property
    def bond_transmit_hash_policy(self) -> BondTransmitHashPolicy:
        """The active transmit hash policy for the link aggregation"""
        return self.__bond_transmit_hash_policy

    @property
    def bond_mii_monitor_milli_seconds(self) -> int:
        """The active MII monitoring interval in ms for the link aggregation"""
        return self.__bond_mii_monitor_milli_seconds

    @property
    def bond_lacp_transmit_rate(self) -> BondLACPTransmitRate:
        """The active LACP transmit rate for the link aggregation"""
        return self.__bond_lacp_transmit_rate

    @property
    def interface_names(self) -> list:
        """The names of the physical interfaces for the logical interface"""
        return self.__interface_names

    @property
    def interface_mac(self) -> str:
        """The physical address of the interface"""
        return self.__interface_mac

    @property
    def half_duplex(self) -> bool:
        """Indicates if the interface operates in half-duplex"""
        return self.__half_duplex

    @property
    def speed(self) -> int:
        """Indicates the network interface speed"""
        return self.__speed

    @property
    def locked_speed(self) -> bool:
        """Indicates if the network interface speed is locked"""
        return self.__locked_speed

    @property
    def mtu(self) -> int:
        """maximum transfer unit"""
        return self.__mtu

    @property
    def switch_name(self) -> str:
        """The name of the switch this interface connects to"""
        return self.__switch_name

    @property
    def switch_mac(self) -> str:
        """The physical address of the switch port this interface connects to"""
        return self.__switch_mac

    @property
    def switch_port(self) -> str:
        """The port identifier of the switch this interface connects to"""
        return self.__switch_port

    @staticmethod
    def fields():
        return [
            "dhcp",
            "addresses",
            "gateway",
            "bondMode",
            "bondTransmitHashPolicy",
            "bondMIIMonitorMilliSeconds",
            "bondLACPTransmitRate",
            "interfaceNames",
            "interfaceMAC",
            "halfDuplex",
            "speed",
            "lockedSpeed",
            "mtu",
            "switchName",
            "switchMAC",
            "switchPort",
        ]


class Spu:
    """A services processing unit"""

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new services processing unit

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__npod_uuid = read_value(
            "nPod.uuid", response, str, False)
        self.__host_uuid = read_value(
            "host.uuid", response, str, False)
        self.__serial = read_value(
            "serial", response, str, True)
        self.__version = read_value(
            "version", response, str, True)
        self.__spu_type = read_value(
            "spuType", response, str, True)
        self.__hw_revision = read_value(
            "hwRevision", response, str, True)
        self.__control_interface = read_value(
            "controlInterface", response, IPInfoState, False)
        self.__data_interfaces = read_value(
            "dataInterfaces", response, IPInfoState, False)
        self.__lun_uuids = read_value(
            "luns.uuid", response, str, False)
        self.__lun_count = read_value(
            "lunCount", response, int, True)
        self.__physical_drive_wwns = read_value(
            "physicalDrives.wwn", response, str, False)
        self.__physical_drive_count = read_value(
            "physicalDriveCount", response, int, True)
        self.__npod_member_can_talk_count = read_value(
            "podMemberCanTalkCount", response, int, True)
        self.__uptime_seconds = read_value(
            "uptimeSeconds", response, int, True)
        self.__update_history = read_value(
            "updateHistory", response, UpdateHistory, True)
        self.__last_reported = read_value(
            "lastReported", response, datetime, True)
        self.__reset_reason_int = read_value(
            "resetReasonInt", response, int, True)
        self.__reset_reason_string = read_value(
            "resetReasonString", response, str, True)
        self.__ntp_servers = read_value(
            "ntpServers", response, NTPServer, True)
        self.__ntp_status = read_value(
            "ntpStatus", response, str, True)
        self.__time_zone = read_value(
            "timeZone", response, str, True)
        self.__uefi_version = read_value(
            "uefiVersion", response, str, True)
        self.__wiping = read_value(
            "wiping", response, bool, True)

    @property
    def npod_uuid(self) -> str:
        """The services processing unit's nPod identifier"""
        return self.__npod_uuid

    @property
    def host_uuid(self) -> str:
        """The unique identifier of the host the SPU is installed in"""
        return self.__host_uuid

    @property
    def serial(self) -> str:
        """The unique serial number of the SPU"""
        return self.__serial

    @property
    def version(self) -> str:
        """The version of nebOS that is running on the SPU"""
        return self.__version

    @property
    def spu_type(self) -> str:
        """The type of SPU"""
        return self.__spu_type

    @property
    def hw_revision(self) -> str:
        """The hardware revision of the SPU"""
        return self.__hw_revision

    @property
    def control_interface(self) -> IPInfoState:
        """Network information for the control interface"""
        return self.__control_interface

    @property
    def data_interfaces(self) -> [IPInfoState]:
        """Network information for the data interfaces"""
        return self.__data_interfaces

    @property
    def lun_uuids(self) -> [str]:
        """List of unique identifiers of LUNs provisioned on the SPU"""
        return self.__lun_uuids

    @property
    def lun_count(self) -> int:
        """Number of provisioned LUNs on the SPU"""
        return self.__lun_count

    @property
    def physical_drive_wwns(self) -> [str]:
        """List of WWNs for all physical drives attached to the SPU"""
        return self.__physical_drive_wwns

    @property
    def physical_drive_count(self) -> int:
        """Number of physical drives attached to the SPU"""
        return self.__physical_drive_count

    @property
    def npod_member_can_talk_count(self) -> int:
        """Number of SPUs that can successfully communicate with each other"""
        return self.__npod_member_can_talk_count

    @property
    def uptime_seconds(self) -> int:
        """Uptime of the services processing unit in seconds"""
        return self.__uptime_seconds

    @property
    def update_history(self) -> [UpdateHistory]:
        """List of historical updates that were applied to the SPU"""
        return self.__update_history

    @property
    def last_reported(self) -> datetime:
        """Date and time when the SPU last reported state to nebulon ON"""
        return self.__last_reported

    @property
    def reset_reason_int(self) -> int:
        """A int representation of the reason why a SPU was reset"""
        return self.__reset_reason_int

    @property
    def reset_reason_string(self) -> str:
        """A string representation of the reason why a SPU was reset"""
        return self.__reset_reason_string

    @property
    def ntp_servers(self) -> [NTPServer]:
        """List of configured NTP servers"""
        return self.__ntp_servers

    @property
    def ntp_status(self) -> str:
        """Status message for NTP"""
        return self.__ntp_status

    @property
    def time_zone(self) -> str:
        """The configured time zone"""
        return self.__time_zone

    @property
    def uefi_version(self) -> str:
        """Version for UEFI"""
        return self.__uefi_version

    @property
    def wiping(self) -> str:
        """Indicates if the SPU is doing a secure wipe"""
        return self.__wiping

    @staticmethod
    def fields():
        return [
            "nPod{uuid}",
            "host{uuid}",
            "serial",
            "version",
            "spuType",
            "hwRevision",
            "controlInterface{%s}" % ",".join(IPInfoState.fields()),
            "dataInterfaces{%s}" % ",".join(IPInfoState.fields()),
            "luns{uuid}",
            "lunCount",
            "physicalDrives{wwn}",
            "physicalDriveCount",
            "podMemberCanTalkCount",
            "uptimeSeconds",
            "updateHistory{%s}" % ",".join(UpdateHistory.fields()),
            "lastReported",
            "resetReasonInt",
            "resetReasonString",
            "ntpServers{%s}" % ",".join(NTPServer.fields()),
            "ntpStatus",
            "timeZone",
            "uefiVersion",
            "wiping"
        ]


class SpuList:
    """Paginated services processing unit (SPU) list

    Contains a list of SPU objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new SPU list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__items = read_value(
            "items", response, Spu, True)
        self.__more = read_value(
            "more", response, bool, True)
        self.__total_count = read_value(
            "totalCount", response, int, True)
        self.__filtered_count = read_value(
            "filteredCount", response, int, True)

    @property
    def items(self) -> [Spu]:
        """List of SPUs in the pagination list"""
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
            "items{%s}" % ",".join(Spu.fields()),
            "more",
            "totalCount",
            "filteredCount",
        ]


class SpuCustomDiagnostic:
    """A staged custom diagnostics request

    SPU custom diagnostics requests allows customers to run arbitrary
    diagnostic commands on the services processing units as part of
    troubleshooting issues during a support case.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new SpuCustomDiagnostic object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__request_uuid = read_value(
            "requestUID", response, str, True)
        self.__diagnostic_name = read_value(
            "diagnosticName", response, str, True)
        self.__spu_serial = read_value(
            "spuSerial", response, str, True)
        self.__once_only = read_value(
            "onceOnly", response, bool, True)
        self.__note = read_value(
            "note", response, str, True)

    @property
    def request_uuid(self) -> str:
        """The unique identifier or the custom diagnostic request"""
        return self.__request_uuid

    @property
    def diagnostic_name(self) -> str:
        """The human readable name of the custom diagnostic request"""
        return self.__diagnostic_name

    @property
    def spu_serial(self) -> str:
        """The serial number of the SPU on which to run diagnostic"""
        return self.__spu_serial

    @property
    def once_only(self) -> bool:
        """Indicates if this request will disappear after execution"""
        return self.__once_only

    @property
    def note(self) -> str:
        """An optional note for the diagnostic request"""
        return self.__note

    @staticmethod
    def fields():
        return [
            "requestUID",
            "diagnosticName",
            "spuSerial",
            "onceOnly",
            "note",
        ]


class SpuMixin(NebMixin):
    """Mixin to add SPU related methods to the GraphQL client"""

    def get_spus(
            self,
            page: PageInput = None,
            spu_filter: SpuFilter = None,
            sort: SpuSort = None
    ) -> SpuList:
        """Retrieves a list of SPUs

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param spu_filter: A filter object to filter the SPUs on the
            server. If omitted, the server will return all objects as a
            paginated response.
        :type spu_filter: SpuFilter, optional
        :param sort: A sort definition object to sort the SPU objects on
            supported properties. If omitted objects are returned in the order
            as they were created in.
        :type sort: SpuSort, optional

        :returns SpuList: A paginated list of SPUs

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            spu_filter, "SPUFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "SPUSort", False)

        # make the request
        response = self._query(
            name="getSPUs",
            params=parameters,
            fields=SpuList.fields()
        )

        # convert to object
        return SpuList(response)

    def get_spu_custom_diagnostics(
            self,
            spu_serial: str
    ) -> [SpuCustomDiagnostic]:
        """Retrieves a list of custom diagnostic command requests

        Custom diagnostic command requests are used by customer satisfaction
        teams to run arbitrary troubleshooting commands on SPUs. These require
        user confirmation.

        :param spu_serial: The serial number for which to query for custom
            diagnostic command requests
        :type spu_serial: str

        :returns [SpuCustomDiagnostic]: A list of custom diagnostic command
            requests.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["spuSerial"] = GraphQLParam(
            spu_serial, "String", False)

        # make the request
        response = self._query(
            name="spuCustomDiagnostics",
            params=parameters,
            fields=SpuCustomDiagnostic.fields()
        )

        # convert to object
        return [SpuCustomDiagnostic(i) for i in response]

    def claim_spu(
            self,
            spu_serial: str
    ):
        """Adds an unregistered SPU to the organization

        SPUs need to be claimed by an organization before they can be used
        for nPod creation. While the nPod creation command will perform an
        implicit claim, this method allows registering SPUs with an
        organization without creating an nPod.

        Once an SPU was claimed, it will become visible in the ``get_spus``
        query and in the nebulon ON web user interface.

        :param spu_serial: The serial number of the SPU to register with an
            organization.
        :type spu_serial: str

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises Exception: An error when delivering a token to the SPU
        """

        # setup query parameters
        parameters = dict()
        parameters["serial"] = GraphQLParam(
            spu_serial, "String", True)

        # make the request
        response = self._mutation(
            name="claimSPU",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object
        token_response = TokenResponse(response)
        token_response.deliver_token()

    def delete_spu_info(
            self,
            spu_serial: str
    ) -> bool:
        """Allows deletion of SPU information in nebulon ON

        :param spu_serial: The serial number of the SPU
        :type spu_serial: str

        :raises GraphQLError: An error with the GraphQL endpoint.
        :returns bool: If the delete operation was successful
        """

        # setup query parameters
        parameters = dict()
        parameters["serial"] = GraphQLParam(
            spu_serial, "String", True)

        # make the request
        response = self._mutation(
            name="delSPUInfo",
            params=parameters,
            fields=None
        )

        # response is a boolean
        return response

    def ping_spu(
            self,
            spu_serial: str
    ):
        """Turns on the locate LED pattern of the SPU

        Allows identification of an SPU in the servers by turning on the
        locate LED pattern for the SPU. Please consult the Cloud-Defined
        Storage manual for the LED blink patterns.

        :param spu_serial: The serial number of the SPU
        :type spu_serial: str

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises Exception: An error when delivering a token to the SPU
        """

        # setup query parameters
        parameters = dict()
        parameters["serial"] = GraphQLParam(
            spu_serial, "String", True)

        # make the request
        response = self._mutation(
            name="claimSPU",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object
        token_response = TokenResponse(response)
        token_response.deliver_token()

    def send_spu_debug_info(
            self,
            spu_serial: str,
            note: str = None
    ):
        """Allows submitting additional debugging information to nebulon ON

        Used for customers to send additional debug information to nebulon ON
        for troubleshooting and resolve issues.

        :param spu_serial: The serial number of the SPU
        :type spu_serial: str
        :param note: An optional note to attach to the debug information
        :type note: str, optional

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises Exception: An error when delivering a token to the SPU
        """

        # setup query parameters
        parameters = dict()
        parameters["spuSerial"] = GraphQLParam(
            spu_serial, "String", False)
        parameters["note"] = GraphQLParam(
            note, "String", False)

        # make the request
        response = self._mutation(
            name="sendDebugInfo",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object
        token_response = TokenResponse(response)
        token_response.deliver_token()

    def run_custom_diagnostics(
            self,
            spu_serial: str = None,
            npod_uuid: str = None,
            diagnostic_name: str = None,
            request_uuid: str = None
    ):
        """Allows running custom diagnostic commands

        SPU custom diagnostics requests allows customers to run arbitrary
        diagnostic commands on the services processing units as part of
        troubleshooting issues during a support case.

        :param spu_serial: The serial number of the SPU on which to run
            diagnostic
        :type spu_serial: str, optional
        :param npod_uuid: The unique identifier of the nPod on which to run
            diagnostic
        :type npod_uuid: str, optional
        :param diagnostic_name: The name of the diagnostic to run
        :type diagnostic_name: str, optional
        :param request_uuid: The unique identifier of the custom diagnostic
            request to run
        :type request_uuid: str, optional

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises Exception: An error when delivering a token to the SPU
        """

        # setup query parameters
        parameters = dict()
        parameters["spuSerial"] = GraphQLParam(
            spu_serial, "String", False)
        parameters["podUID"] = GraphQLParam(
            npod_uuid, "String", False)
        parameters["diagnosticName"] = GraphQLParam(
            diagnostic_name, "String", False)
        parameters["requestUID"] = GraphQLParam(
            request_uuid, "String", False)

        # make the request
        response = self._mutation(
            name="runCustomDiagnostic",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object
        token_response = TokenResponse(response)
        token_response.deliver_token()

    def release_spu(
            self,
            spu_serial: str
    ):
        """Removes an SPU from an organization

        :param spu_serial: The serial number of the SPU
        :type spu_serial: str

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises Exception: An error when delivering a token to the SPU
        """

        # setup query parameters
        parameters = dict()
        parameters["spuSerial"] = GraphQLParam(
            spu_serial, "String", True)

        # make the request
        response = self._mutation(
            name="releaseSPU",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object
        token_response = TokenResponse(response)
        token_response.deliver_token()

    def set_proxy(
            self,
            spu_serial: str,
            proxy: str
    ):
        """Allows configuring a proxy server for an SPU

        :param spu_serial: The serial number of the SPU
        :type spu_serial: str
        :param proxy: The proxy server IP address
        :type proxy: str

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises Exception: An error when delivering a token to the SPU
        """

        # setup query parameters
        parameters = dict()
        parameters["spuSerial"] = GraphQLParam(spu_serial, "String", True)
        parameters["proxy"] = GraphQLParam(proxy, "String", True)

        # make the request
        response = self._mutation(
            name="setProxy",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object
        token_response = TokenResponse(response)
        token_response.deliver_token()

    def replace_spu(
            self,
            npod_uuid: str,
            previous_spu_serial: str,
            new_spu_info: NPodSpuInput,
            sset_uuid: str
    ):
        """Allows replacing an SPU

        The replace services processing unit (SPU) operation is used to
        transition the configuration of an old, likely failed, SPU to a new
        replacement unit and allows modifying the configuration during the
        process.

        :param npod_uuid: The unique identifier of the nPod of the old SPU
            that is being replaced
        :type npod_uuid: str
        :param previous_spu_serial: The serial number of the old SPU that is
            being replaced
        :type previous_spu_serial: str
        :param new_spu_info: Configuration information for the new SPU
        :type new_spu_info: NPodSpuInput
        :param sset_uuid: The storage set information for the existing SPU.
            This information can be obtained from the active replacement
            alert and only used to verify that the correct SPU is selected.
        :type sset_uuid: str

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises Exception: An error when delivering a token to the SPU
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            ReplaceSpuInput(
                npod_uuid=npod_uuid,
                previous_spu_serial=previous_spu_serial,
                new_spu_info=new_spu_info,
                sset_uuid=sset_uuid
            ),
            "ReplaceSPUInput",
            True
        )

        # make the request
        response = self._mutation(
            name="replaceSPU",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object
        token_response = TokenResponse(response)
        token_response.deliver_token()

    def shutdown_spu(
            self,
            spu_serial: str
    ):
        """Allows shutting down a services processing unit (SPU) 

        This method is used during planned SPU replacement where the SPU needs
        to be shut down so that it no longer serves IO to the host. Only use
        this method when instructed by customer support.

        :param spu_serial: The serial number of the SPU to shut down
        :type spu_serial: str

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises Exception: An error when delivering a token to the SPU
        """

        # setup query parameters
        parameters = dict()
        parameters["spuSerial"] = GraphQLParam(
            spu_serial,
            "String",
            True
        )

        # make the request
        response = self._mutation(
            name="shutdownSPU",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object
        token_response = TokenResponse(response)
        token_response.deliver_token()

    def set_ntp_servers(
            self,
            ntp_servers_input: SetNTPServersInput,
            ignore_warnings: bool = False
    ):
        """Allows configuring the NTP server for an SPU or nPod

        All services processing units us a default NTP server. In some
        situations customers may use their own NTP servers for their datacenter
        infrastructure. This mutation allows them to configure the NTP servers
        for their SPUs or nPod.

        :param ntp_servers_input: The NTP Server configuration to use
        :type ntp_servers_input: SetNTPServersInput
        :param ignore_warnings: If specified and set to ``True`` the nPod creation
            will proceed even if nebulon ON reports warnings. It is advised to
            not ignore warnings. Consequently, the default behavior is that
            the nPod creation will fail when nebulon ON reports validation
            errors.
        :type ignore_warnings: bool, optional

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises Exception: An error when delivering a token to the SPU
        :raises Exception: When nebulon ON reports validation errors or warnings
            and the ``ignore_warnings`` parameter is not set to ``True`` or if the
            nPod creation times out.
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            ntp_servers_input,
            "SetNTPServersInput",
            True
        )

        # make the request
        response = self._mutation(
            name="setNTPServers",
            params=parameters,
            fields=TokenResponse.fields()
        )
        issues = Issues(response=response["issues"])
        issues.assert_no_issues(ignore_warnings=ignore_warnings)

        # convert to object
        token_response = TokenResponse(response)
        token_response.deliver_token()

    def secure_erase_spu(
            self,
            spu_serial: str
    ):
        """Allows to secure-erase data on a services processing unit (SPU)

        The secure erase functionality allows a deep-erase of data stored on
        the physical drives attached to the SPU. Only SPUs that are not part
        of a nPod can be secure-erased.

        :param spu_serial: The serial number of the SPU to secure-erase
        :type spu_serial: str

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises Exception: An error when delivering a token to the SPU
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            SecureEraseSPUInput(
                spu_serial=spu_serial
            ),
            "SecureEraseSPUInput",
            True
        )

        # make the request
        response = self._mutation(
            name="secureEraseSPU",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object
        token_response = TokenResponse(response)
        token_response.deliver_token()
