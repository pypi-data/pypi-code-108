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
from .common import PageInput, read_value
from .filters import StringFilter, IntFilter, UuidFilter
from .sorting import SortDirection
from .tokens import TokenResponse

__all__ = [
    "PhysicalDriveSort",
    "PhysicalDriveUpdatesSort",
    "PhysicalDriveFilter",
    "PhysicalDriveUpdatesFilter",
    "LocatePhysicalDriveInput",
    "UpdatePhysicalDriveFirmwareInput",
    "PhysicalDrive",
    "PhysicalDriveList",
    "PhysicalDriveUpdate",
    "PhysicalDriveUpdatesList",
    "PhysicalDriveMixin"
]


class PhysicalDriveSort:
    """A sort object for physical drives

    Allows sorting physical drives on common properties. The sort object allows
    only one property to be specified.
    """

    def __init__(
            self,
            wwn: SortDirection = None,
            size_bytes: SortDirection = None,
            model: SortDirection = None,
            vendor: SortDirection = None,
            interface_type: SortDirection = None
    ):
        """Constructs a new sort object for physical drives

        Allows sorting physical drives on common properties. The sort object
        allows only one property to be specified.

        :param wwn: Sort direction for the ``wwn`` property
        :type wwn: SortDirection, optional
        :param size_bytes: Sort direction for the ``size_bytes`` property
        :type size_bytes: SortDirection, optional
        :param model: Sort direction for the ``model`` property
        :type model: SortDirection, optional
        :param vendor: Sort direction for the ``vendor`` property
        :type vendor: SortDirection, optional
        :param interface_type: Sort direction for the ``interface_type`` property
        :type interface_type: SortDirection, optional
        """

        self.__interface_type = interface_type
        self.__vendor = vendor
        self.__model = model
        self.__size_bytes = size_bytes
        self.__wwn = wwn

    @property
    def interface_type(self) -> SortDirection:
        """Sort direction for the ``interface_type`` property"""
        return self.__interface_type

    @property
    def vendor(self) -> SortDirection:
        """Sort direction for the ``vendor`` property"""
        return self.__vendor

    @property
    def model(self) -> SortDirection:
        """Sort direction for the ``model`` property"""
        return self.__model

    @property
    def size_bytes(self) -> SortDirection:
        """Sort direction for the ``size_bytes`` property"""
        return self.__size_bytes

    @property
    def wwn(self) -> SortDirection:
        """Sort direction for the ``wwn`` property"""
        return self.__wwn

    @property
    def as_dict(self):
        result = dict()
        result["wwn"] = self.wwn
        result["sizeBytes"] = self.size_bytes
        result["model"] = self.model
        result["vendor"] = self.vendor
        result["interfaceType"] = self.interface_type
        return result


class PhysicalDriveUpdatesSort:
    """A sort object for physical drive updates

    Allows sorting physical drive updates on common properties. The sort object
    allows only one property to be specified.
    """

    def __init__(
            self,
            vendor: SortDirection,
            model: SortDirection,
            npod_uuid: SortDirection,
            spu_serial: SortDirection,
            wwn: SortDirection
    ):
        """Constructs a new sort object for physical drive updates

        :param vendor: Sort direction for the ``vendor`` property
        :type vendor: SortDirection, optional
        :param model: Sort direction for the ``model`` property
        :type model: SortDirection, optional
        :param npod_uuid: Sort direction for the ``npod_uuid`` property
        :type npod_uuid: SortDirection, optional
        :param spu_serial: Sort direction for the ``spu_serial`` property
        :type spu_serial: SortDirection, optional
        :param wwn: Sort direction for the ``wwn`` property
        :type wwn: SortDirection, optional
        """

        self.__vendor = vendor
        self.__model = model
        self.__npod_uuid = npod_uuid
        self.__spu_serial = spu_serial
        self.__wwn = wwn

    @property
    def vendor(self) -> SortDirection:
        """Sort direction for the ``vendor`` property"""
        return self.__vendor

    @property
    def model(self) -> SortDirection:
        """Sort direction for the ``model`` property"""
        return self.__model

    @property
    def npod_uuid(self) -> SortDirection:
        """Sort direction for the ``npod_uuid`` property"""
        return self.__npod_uuid

    @property
    def spu_serial(self) -> SortDirection:
        """Sort direction for the ``spu_serial`` property"""
        return self.__spu_serial

    @property
    def wwn(self) -> SortDirection:
        """Sort direction for the ``wwn`` property"""
        return self.__wwn

    @property
    def as_dict(self):
        result = dict()
        result["vendor"] = self.vendor
        result["model"] = self.model
        result["nPodUUID"] = self.npod_uuid
        result["spuSerial"] = self.spu_serial
        result["wwn"] = self.wwn
        return result


class PhysicalDriveFilter:
    """A filter object to filter physical drives.

    Allows filtering for specific physical drives in nebulon ON. The
    filter allows only one property to be specified. If filtering on multiple
    properties is needed, use the ``and_filter`` and ``or_filter`` options to
    concatenate multiple filters.
    """

    def __init__(
            self,
            wwn: StringFilter,
            size_bytes: IntFilter,
            model: StringFilter,
            vendor: StringFilter,
            interface_type: StringFilter,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new filter object

        The filter allows only one property to be specified. If filtering on
        multiple properties is needed, use the ``and_filter`` and ``or_filter``
        options to concatenate multiple filters.

        :param wwn: Filter based on physical drive WWN
        :type wwn: StringFilter, optional
        :param size_bytes: Filter based on physical drive size
        :type size_bytes: IntFilter, optional
        :param model: Filter based on physical drive model
        :type model: StringFilter, optional
        :param vendor: Filter based on physical drive vendor
        :type vendor: StringFilter, optional
        :param interface_type: Filter based on physical drive interface
        :type interface_type: StringFilter, optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: DataCenterFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: DataCenterFilter, optional
        """

        self.__wwn = wwn
        self.__size_bytes = size_bytes
        self.__model = model
        self.__vendor = vendor
        self.__interface_type = interface_type
        self.__and = and_filter
        self.__or = or_filter

    @property
    def wwn(self) -> StringFilter:
        """Filter based on physical drive WWN"""
        return self.__wwn

    @property
    def size_bytes(self) -> IntFilter:
        """Filter based on physical drive size"""
        return self.__size_bytes

    @property
    def model(self) -> StringFilter:
        """Filter based on physical drive model"""
        return self.__model

    @property
    def vendor(self) -> StringFilter:
        """Filter based on physical drive vendor"""
        return self.__vendor

    @property
    def interface_type(self) -> StringFilter:
        """Filter based on physical drive interface"""
        return self.__interface_type

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
        result["wwn"] = self.wwn
        result["sizeBytes"] = self.size_bytes
        result["model"] = self.model
        result["vendor"] = self.vendor
        result["interfaceType"] = self.interface_type
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class PhysicalDriveUpdatesFilter:
    """A filter object to filter physical drive updates

    Allows filtering for specific physical drive updates in nebulon ON. The
    filter allows only one property to be specified. If filtering on multiple
    properties is needed, use the ``and_filter`` and ``or_filter`` options to
    concatenate multiple filters.
    """

    def __init__(
            self,
            npod_uuid: UuidFilter,
            spu_serial: StringFilter,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new filter object

        The filter allows only one property to be specified. If filtering on
        multiple properties is needed, use the ``and_filter`` and ``or_filter``
        options to concatenate multiple filters.

        :param npod_uuid: Filter based on nPod unique identifier
        :type npod_uuid: UuidFilter, optional
        :param spu_serial: Filter based on SPU serial number
        :type spu_serial: StringFilter, optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: DataCenterFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: DataCenterFilter, optional
        """

        self.__npod_uuid = npod_uuid
        self.__spu_serial = spu_serial
        self.__and = and_filter
        self.__or = or_filter

    @property
    def npod_uuid(self) -> UuidFilter:
        """Allows filtering based on nPod unique identifier"""
        return self.__npod_uuid

    @property
    def spu_serial(self) -> StringFilter:
        """Allows filtering based on SPU serial number"""
        return self.__spu_serial

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
        result["nPodUUID"] = self.npod_uuid
        result["spuSerial"] = self.spu_serial
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class LocatePhysicalDriveInput:
    """An input object to turn on the physical drive locate LED

    Allows turning on the locate LED of a physical drive identified by WWN to
    easily find it in a server.
    """

    def __init__(
            self,
            wwn: str,
            duration_seconds: int
    ):
        """Constructs a new input object to locate a physical drive

        :param wwn: The world-wide name of the physical drive
        :type wwn: str
        :param duration_seconds: The number of seconds after which the locate
            LED will automatically be turned off again
        :type duration_seconds: int
        """

        self.__wwn = wwn
        self.__duration_seconds = duration_seconds

    @property
    def wwn(self) -> str:
        """The world-wide name of the physical drive"""
        return self.__wwn

    @property
    def duration_seconds(self) -> int:
        """Number of seconds after which the locate LED will turn off"""
        return self.__duration_seconds

    @property
    def as_dict(self):
        result = dict()
        result["wwn"] = self.wwn
        result["durationSeconds"] = self.duration_seconds
        return result


class UpdatePhysicalDriveFirmwareInput:
    """An input object to update physical drive firmware

    Allows updating all physical drives in an SPU or nPod to the recommended
    drive firmware level
    """

    def __init__(
            self,
            accept_eula: bool,
            npod_uuid: str = None,
            spu_serial: str = None,
    ):
        """Constructs a new input object to update physical drive firmware

        :param accept_eula: Specify ``True`` if you accept the physical drive
            end user license agreement. If not specified or set to ``False`` the
            update will fail.
        :type accept_eula: bool
        :param npod_uuid: The nPod unique identifier. Specify either ``npod_uuid``
            or ``spu_serial``
        :type npod_uuid: str, optional
        :param spu_serial: The SPU serial number. Specify either ``npod_uuid``
            or ``spu_serial``.
        :type spu_serial: str, optional
        """

        self.__npod_uuid = npod_uuid
        self.__spu_serial = spu_serial
        self.__accept_eula = accept_eula

    @property
    def npod_uuid(self) -> str:
        """The nPod unique identifier"""
        return self.__npod_uuid

    @property
    def spu_serial(self) -> str:
        """The SPU serial number"""
        return self.__spu_serial

    @property
    def accept_eula(self) -> bool:
        """Indicates if the user accepts the end user license agreement"""
        return self.__accept_eula

    @property
    def as_dict(self):
        result = dict()
        result["nPodUUID"] = self.npod_uuid
        result["spuSerial"] = self.spu_serial
        result["acceptEULA"] = self.accept_eula

        return result


class PhysicalDrive:
    """A physical drive

    Represents a physical drive that is attached to a services processing unit
    in a server.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new physical drive object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__spu_serial = read_value(
            "spu.serial", response, str, False)
        self.__wwn = read_value(
            "wwn", response, str, True)
        self.__media_type = read_value(
            "mediaType", response, str, True)
        self.__position = read_value(
            "position", response, int, True)
        self.__state = read_value(
            "state", response, int, True)
        self.__state_display = read_value(
            "stateDisplay", response, str, True)
        self.__unadmitted = read_value(
            "unadmitted", response, bool, True)
        self.__size_bytes = read_value(
            "sizeBytes", response, int, True)
        self.__vendor = read_value(
            "vendor", response, str, True)
        self.__model = read_value(
            "model", response, str, True)
        self.__serial = read_value(
            "serial", response, str, True)
        self.__firmware_revision = read_value(
            "firmwareRevision", response, str, True)
        self.__interface_type = read_value(
            "interfaceType", response, str, True)

    @property
    def spu_serial(self) -> str:
        """The serial number of the SPU that the physical drive connects to"""
        return self.__spu_serial

    @property
    def wwn(self) -> str:
        """The unique world-wide name of the physical drive"""
        return self.__wwn

    @property
    def media_type(self) -> str:
        """The media type of the physical drive"""
        return self.__media_type

    @property
    def position(self) -> int:
        """The position or slot in the host's storage enclosure"""
        return self.__position

    @property
    def state(self) -> int:
        """The physical drive state.

        Possible values are:
        - 1: PdNormal : normal
        - 2: PdFailed: failed, can’t handle IO
        - 3: PdMissing: device is missing
        - 4: PdVacant: data on device has been vacated
        - 5: PdIncompatible: device is incompatible to other devices
        """
        return self.__state

    @property
    def state_display(self) -> str:
        """The physical drive state as a string"""
        return self.__state_display

    @property
    def unadmitted(self) -> bool:
        """Indicates if the physical drive is not yet used for data storage"""
        return self.__unadmitted

    @property
    def size_bytes(self) -> int:
        """The physical capacity of the physical drive in bytes"""
        return self.__size_bytes

    @property
    def vendor(self) -> str:
        """The vendor for the physical drive"""
        return self.__vendor

    @property
    def model(self) -> str:
        """The model of the physical drive"""
        return self.__model

    @property
    def serial(self) -> str:
        """The serial number of the physical drive"""
        return self.__serial

    @property
    def firmware_revision(self) -> str:
        """The firmware revision of the physical drive"""
        return self.__firmware_revision

    @property
    def interface_type(self) -> str:
        """The interface type of the physical drive"""
        return self.__interface_type

    @staticmethod
    def fields():
        return [
            "spu{serial}",
            "wwn",
            "mediaType",
            "id",
            "position",
            "state",
            "stateDisplay",
            "unadmitted",
            "sizeBytes",
            "vendor",
            "model",
            "serial",
            "firmwareRevision",
            "interfaceType",
        ]


class PhysicalDriveList:
    """Paginated physical drive list object

    Contains a list of datacenter objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new physical drive list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__items = read_value(
            "items", response, PhysicalDrive, False)
        self.__more = read_value(
            "more", response, bool, False)
        self.__total_count = read_value(
            "totalCount", response, int, False)
        self.__filtered_count = read_value(
            "filteredCount", response, int, False)

    @property
    def items(self) -> list:
        """List of physical drive in the pagination list"""
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
            "items{%s}" % ",".join(PhysicalDrive.fields()),
            "more",
            "totalCount",
            "filteredCount",
        ]


class PhysicalDriveUpdate:
    """An update for a physical drive

    nebulon ON only reports recommended physical drive updates.
    """

    def __init__(
            self,
            response
    ):
        """Constructs a new physical drive update list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__npod_uuid = read_value(
            "nPod.uuid", response, str, False)
        self.__spu_serial = read_value(
            "spu.serial", response, str, False)
        self.__wwn = read_value(
            "wwn", response, str, True)
        self.__old_firmware_rev = read_value(
            "oldFirmwareRev", response, str, True)
        self.__new_firmware_rev = read_value(
            "newFirmwareRev", response, str, True)
        self.__vendor = read_value(
            "vendor", response, str, True)
        self.__model = read_value(
            "model", response, str, True)

    @property
    def npod_uuid(self) -> str:
        """The unique identifier of the nPod this update is relevant for"""
        return self.__npod_uuid

    @property
    def spu_serial(self) -> str:
        """The serial number of the SPU this update is relevant for"""
        return self.__spu_serial

    @property
    def wwn(self) -> str:
        """The unique WWN of the physical drive this update is relevant for"""
        return self.__wwn

    @property
    def old_firmware_rev(self) -> str:
        """The firmware revision this update replaces"""
        return self.__old_firmware_rev

    @property
    def new_firmware_rev(self) -> str:
        """The firmware revision this update will install"""
        return self.__new_firmware_rev

    @property
    def vendor(self) -> str:
        """The vendor of the physical drive this update is relevant for"""
        return self.__vendor

    @property
    def model(self) -> str:
        """The model of the physical drive this update is relevant for"""
        return self.__model

    @staticmethod
    def fields():
        return [
            "nPod{uuid}",
            "spu{serial}",
            "wwn",
            "oldFirmwareRev",
            "newFirmwareRev",
            "vendor",
            "model",
        ]


class PhysicalDriveUpdatesList:
    """Paginated physical drive update list object

    Contains a list of physical drive update objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new drive update list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__items = read_value(
            "items", response, PhysicalDriveUpdate, False)
        self.__more = read_value(
            "more", response, bool, False)
        self.__total_count = read_value(
            "totalCount", response, int, False)
        self.__filtered_count = read_value(
            "filteredCount", response, int, False)

    @property
    def items(self) -> [PhysicalDriveUpdate]:
        """List of physical drive updates in the pagination list"""
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
            "items{%s}" % ",".join(PhysicalDriveUpdate.fields()),
            "more",
            "totalCount",
            "filteredCount",
        ]


class PhysicalDriveMixin(NebMixin):
    """Mixin to add physical drive related methods to the GraphQL client"""

    def get_physical_drives(
            self,
            page: PageInput = None,
            pd_filter: PhysicalDriveFilter = None,
            sort: PhysicalDriveSort = None
    ) -> PhysicalDriveList:
        """Retrieves a list of physical drive objects

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param pd_filter: A filter object to filter the physical drives on the
            server. If omitted, the server will return all objects as a
            paginated response.
        :type pd_filter: PhysicalDriveFilter, optional
        :param sort: A sort definition object to sort the physical drive objects
            on supported properties. If omitted objects are returned in the
            order as they were created in.
        :type sort: PhysicalDriveSort, optional

        :returns PhysicalDriveList: A paginated list of physical drives.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            pd_filter, "PhysicalDriveFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "PhysicalDriveSort", False)

        # make the request
        response = self._query(
            name="getPhysicalDrives",
            params=parameters,
            fields=PhysicalDriveList.fields()
        )

        # convert to object
        return PhysicalDriveList(response)

    def get_physical_drive_updates(
            self,
            page: PageInput = None,
            pd_filter: PhysicalDriveUpdatesFilter = None,
            sort: PhysicalDriveUpdatesSort = None
    ) -> PhysicalDriveUpdatesList:
        """Retrieves a list of physical drive update objects

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param pd_filter: A filter object to filter the physical drive updates
            on the server. If omitted, the server will return all objects as a
            paginated response.
        :type pd_filter: PhysicalDriveUpdatesFilter, optional
        :param sort: A sort definition object to sort the physical drive update
            objects on supported properties. If omitted objects are returned in
            the order as they were created in.
        :type sort: PhysicalDriveUpdatesSort, optional

        :returns PhysicalDriveUpdatesList: A paginated list of physical drive
            updates.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            pd_filter, "PhysicalDriveUpdatesFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "PhysicalDriveUpdatesSort", False)

        # make the request
        response = self._query(
            name="getPhysicalDriveUpdates",
            params=parameters,
            fields=PhysicalDriveUpdatesList.fields()
        )

        # convert to object
        return PhysicalDriveUpdatesList(response)

    def locate_physical_drive(
            self,
            wwn: str,
            duration_seconds: int
    ):
        """Turn on the locate LED of a physical drive

        :param wwn: The world-wide name of the physical drive
        :type wwn: str
        :param duration_seconds: The number of seconds after which the locate
            LED will automatically be turned off again
        :type duration_seconds: int

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises Exception: When token delivery to the relevant SPU fails
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            LocatePhysicalDriveInput(
                wwn=wwn,
                duration_seconds=duration_seconds
            ),
            "LocatePhysicalDriveInput",
            True
        )

        # make the request
        response = self._mutation(
            name="locatePhysicalDrive",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object
        token_response = TokenResponse(response)
        token_response.deliver_token()

    def update_physical_drive_firmware(
            self,
            accept_eula: bool,
            npod_uuid: str = None,
            spu_serial: str = None
    ):
        """Update the firmware of physical drives

        :param accept_eula: Specify ``True`` if you accept the physical drive
            end user license agreement. If not specified or set to ``False`` the
            update will fail.
        :type accept_eula: bool
        :param npod_uuid: The nPod unique identifier. Specify either ``npod_uuid``
            or ``spu_serial``
        :type npod_uuid: str, optional
        :param spu_serial: The SPU serial number. Specify either ``npod_uuid``
            or ``spu_serial``.
        :type spu_serial: str, optional

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises Exception: When token delivery to the relevant SPU fails
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            UpdatePhysicalDriveFirmwareInput(
                accept_eula=accept_eula,
                npod_uuid=npod_uuid,
                spu_serial=spu_serial
            ),
            "UpdatePhysicalDriveFirmwareInput",
            True
        )

        # make the request
        response = self._mutation(
            name="updatePhysicalDriveFirmware",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object
        token_response = TokenResponse(response)
        token_response.deliver_token()
