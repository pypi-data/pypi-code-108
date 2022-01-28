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
from .filters import UuidFilter, StringFilter
from .sorting import SortDirection


class RoomSort:
    """A sort object for rooms

    Allows sorting rooms in datacenters on common properties. The sort object
    allows only one property to be specified.
    """

    def __init__(
            self,
            name: SortDirection = None
    ):
        """Constructs a new sort object for datacenter rooms

        :param name: Sort direction for the ``name`` property
        :type name: SortDirection, optional
        """

        self.__name = name

    @property
    def name(self) -> SortDirection:
        """Sort direction for the ``name`` property"""
        return self.__name

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        return result


class RoomFilter:
    """A filter object to filter datacenter rooms

    Allows filtering for specific datacenters in nebulon ON. The
    filter allows only one property to be specified. If filtering on multiple
    properties is needed, use the ``and_filter`` and ``or_filter`` options to
    concatenate multiple filters.
    """

    def __init__(
            self,
            uuid: UuidFilter = None,
            datacenter_uuid: UuidFilter = None,
            name: StringFilter = None,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new filter object

        The filter allows only one property to be specified. If filtering on
        multiple properties is needed, use the ``and_filter`` and ``or_filter``
        options to concatenate multiple filters.

        :param uuid: Filter based on datacenter room unique identifiers
        :type uuid: UuidFilter, optional
        :param datacenter_uuid: Filter based on datacenter unique identifiers
        :type datacenter_uuid: UuidFilter, optional
        :param name: Filter based on datacenter room name
        :type name: StringFilter, optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: DataCenterFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: DataCenterFilter, optional
        """

        self.__uuid = uuid
        self.__datacenter_uuid = datacenter_uuid
        self.__name = name
        self.__and = and_filter
        self.__or = or_filter

    @property
    def uuid(self) -> UuidFilter:
        """Filter based on datacenter room unique identifier"""
        return self.__uuid

    @property
    def datacenter_uuid(self) -> UuidFilter:
        """Filter based on datacenter unique identifier"""
        return self.__datacenter_uuid

    @property
    def name(self) -> StringFilter:
        """Filter based on datacenter room name"""
        return self.__name

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
        result["datacenterUUID"] = self.datacenter_uuid
        result["name"] = self.name
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class CreateRoomInput:
    """An input object to create a datacenter room

    Allows the creation of a datacenter room object in nebulon ON. A
    datacenter room record allows customers to logically organize their
    infrastructure by physical location.
    """

    def __init__(
            self,
            datacenter_uuid: str,
            name: str,
            note: str = None,
            location: str = None
    ):
        """Constructs a new input object to create a datacenter room

        :param datacenter_uuid: Unique identifier for the parent datacenter
        :type datacenter_uuid: str
        :param name: Name for the new datacenter room
        :type name: str
        :param note: An optional note for the new datacenter room
        :type note: str, optional
        :param location: An optional location for the new datacenter room
        :type location: str, optional
        """

        self.__datacenter_uuid = datacenter_uuid
        self.__name = name
        self.__note = note
        self.__location = location

    @property
    def datacenter_uuid(self) -> str:
        """Unique identifier for the parent datacenter"""
        return self.__datacenter_uuid

    @property
    def name(self) -> str:
        """Name for the new datacenter room"""
        return self.__name

    @property
    def note(self) -> str:
        """An optional note for the new datacenter room"""
        return self.__note

    @property
    def location(self) -> str:
        """An optional location for the new datacenter room"""
        return self.__location

    @property
    def as_dict(self):
        result = dict()
        result["dataCenterUUID"] = self.datacenter_uuid
        result["name"] = self.name
        result["note"] = self.note
        result["location"] = self.location
        return result


class UpdateRoomInput:
    """An input object to update datacenter room properties

    Allows updating of an existing datacenter room object in nebulon ON. A
    datacenter room record allows customers to logically organize their
    infrastructure by physical location.
    """

    def __init__(
            self,
            name: str = None,
            note: str = None,
            location: str = None
    ):
        """Constructs a new input object to update a datacenter room

        At least one property must be specified.

        :param name: New name for the datacenter room
        :type name: str, optional
        :param note: The new note for the datacenter room. For removing the
            note, provide an empty str.
        :type note: str, optional
        :param location: A new optional location for the datacenter room
        :type location: str, optional
        """

        self.__name = name
        self.__note = note
        self.__location = location

    @property
    def name(self) -> str:
        """New name for the datacenter room"""
        return self.__name

    @property
    def note(self) -> str:
        """The new note for the datacenter room"""
        return self.__note

    @property
    def location(self) -> str:
        """A new optional location for the datacenter room"""
        return self.__location

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["note"] = self.note
        result["location"] = self.location
        return result


class DeleteRoomInput:
    """An input object to delete a datacenter room object

    Allows additional options when deleting a datacenter room. When cascade is
    set to ``True`` all child resources are deleted with the datacenter room if
    no hosts are associated with the datacenter room.
    """

    def __init__(
            self,
            cascade: bool = False
    ):
        """Constructs a new input object to delete a datacenter room object

        :param cascade: If set to True any child resources are deleted with
            the datacenter room if no hosts are associated with it.
        :type cascade: bool
        """

        self.__cascade = cascade

    @property
    def cascade(self) -> bool:
        """Indicates that child items shall be deleted with the room"""
        return self.__cascade

    @property
    def as_dict(self):
        result = dict()
        result["cascade"] = self.cascade
        return result


class Room:
    """A datacenter room object

    A datacenter room record allows customers to logically organize their
    infrastructure by physical location.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new datacenter room object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__name = read_value(
            "name", response, str, True)
        self.__uuid = read_value(
            "uuid", response, str, True)
        self.__note = read_value(
            "note", response, str, True)
        self.__location = read_value(
            "location", response, str, True)
        self.__datacenter_uuid = read_value(
            "datacenter.uuid", response, str, True)
        self.__row_uuids = read_value(
            "rows.uuid", response, str, False)
        self.__row_count = read_value(
            "rowCount", response, int, True)
        self.__rack_count = read_value(
            "rackCount", response, int, True)
        self.__host_count = read_value(
            "hostCount", response, int, True)

    @property
    def uuid(self) -> str:
        """Unique identifier of the datacenter room"""
        return self.__uuid

    @property
    def name(self) -> str:
        """Name of the datacenter room"""
        return self.__name

    @property
    def note(self) -> str:
        """An optional note for the datacenter room"""
        return self.__note

    @property
    def location(self) -> str:
        """An optional location for the datacenter room"""
        return self.__location

    @property
    def datacenter_uuid(self) -> str:
        """Unique identifier of the parent datacenter"""
        return self.__datacenter_uuid

    @property
    def row_uuids(self) -> list:
        """Unique identifiers of rows in the datacenter room"""
        return self.__row_uuids

    @property
    def row_count(self) -> str:
        """Number of rows in the datacenter room"""
        return self.__row_count

    @property
    def rack_count(self) -> str:
        """Number of racks in the datacenter room"""
        return self.__rack_count

    @property
    def host_count(self) -> list:
        """Number of hosts (servers) in the datacenter room"""
        return self.__host_count

    @staticmethod
    def fields():
        return [
            "name",
            "uuid",
            "note",
            "location",
            "datacenter{uuid}",
            "rows{uuid}",
            "rowCount",
            "rackCount",
            "hostCount"
        ]


class RoomList:
    """Paginated datacenter room list object

    Contains a list of datacenter room objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new datacenter room list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__more = read_value(
            "more", response, bool, True)
        self.__total_count = read_value(
            "totalCount", response, int, True)
        self.__filtered_count = read_value(
            "filteredCount", response, int, True)
        self.__items = read_value(
            "items", response, Room, True)

    @property
    def items(self) -> [Room]:
        """List of datacenter rooms in the pagination list"""
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
            "items{%s}" % (",".join(Room.fields())),
            "more",
            "totalCount",
            "filteredCount",
        ]


class RoomsMixin(NebMixin):
    """Mixin to add datacenter room related methods to the GraphQL client"""

    def get_rooms(
            self,
            page: PageInput = None,
            room_filter: RoomFilter = None,
            sort: RoomSort = None
    ) -> RoomList:
        """Retrieves a list of datacenter room objects

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param room_filter: A filter object to filter the datacenter rooms on
            the server. If omitted, the server will return all objects as a
            paginated response.
        :type room_filter: RoomFilter, optional
        :param sort: A sort definition object to sort the datacenter rooms
            on supported properties. If omitted objects are returned in the
            order as they were created in.
        :type sort: RoomSort, optional

        :returns RoomList: A paginated list of datacenter rooms.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            room_filter, "LabFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "LabSort", False)

        # make the request
        response = self._query(
            name="getLabs",
            params=parameters,
            fields=RoomList.fields()
        )

        # convert to object
        return RoomList(response)

    def create_room(
            self,
            datacenter_uuid: str,
            name: str,
            note: str = None,
            location: str = None
    ) -> Room:
        """Allows creation of a new datacenter room object

        A datacenter room record allows customers to logically organize their
        infrastructure by physical location.

        :param datacenter_uuid: Unique identifier for the parent datacenter
        :type datacenter_uuid: str
        :param name: Name for the new datacenter room
        :type name: str
        :param note: An optional note for the new datacenter room
        :type note: str, optional
        :param location: An optional location for the new datacenter room
        :type location: str, optional

        :returns Room: The new datacenter room.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            CreateRoomInput(
                datacenter_uuid=datacenter_uuid,
                name=name,
                note=note,
                location=location
            ),
            "CreateLabInput",
            True
        )

        # make the request
        response = self._mutation(
            name="createLab",
            params=parameters,
            fields=Room.fields()
        )

        # convert to object
        return Room(response)

    def delete_room(
            self,
            uuid: str,
            cascade: bool = False
    ) -> bool:
        """Allows deletion of an existing datacenter room object

        The deletion of a datacenter room is only possible if the room
        has no hosts (servers) associated with any child items. By default,
        deletion of a datacenter room is only allowed when it is not
        referenced by any rows or if the ``cascade`` parameter is set to ``True``.

        :param uuid: The unique identifier of the datacenter room to delete
        :type uuid: str
        :param cascade: If set to True any child items of the datacenter room
            (row, rack) will automatically deleted with this request. If set
            to False or omitted and the datacenter room has child objects, the
            deletion will fail with an error.
        :type cascade: bool, optional

        :returns bool: If the query was successful

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)
        parameters["input"] = GraphQLParam(
            DeleteRoomInput(
                cascade=cascade
            ),
            "DeleteLabInput",
            False
        )

        # make the request
        response = self._mutation(
            name="deleteLab",
            params=parameters,
            fields=None
        )

        # response is a bool
        return response

    def update_room(
            self,
            uuid: str,
            name: str = None,
            note: str = None,
            location: str = None
    ) -> Room:
        """Allows updating properties of an existing datacenter room object

        At least one property must be specified.

        :param uuid: The unique identifier of the datacenter room to update
        :type uuid: str
        :param name: New name for the datacenter room
        :type name: str, optional
        :param note: The new note for the datacenter room. For removing the
            note, provide an empty str.
        :type note: str, optional
        :param location: A new optional location for the new datacenter room
        :type location: str, optional

        :returns Room: The updated datacenter room object.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)
        parameters["input"] = GraphQLParam(
            UpdateRoomInput(
                name=name,
                note=note,
                location=location
            ),
            "UpdateLabInput",
            True
        )

        # make the request
        response = self._mutation(
            name="updateLab",
            params=parameters,
            fields=Room.fields()
        )

        # convert to object
        return Room(response)
