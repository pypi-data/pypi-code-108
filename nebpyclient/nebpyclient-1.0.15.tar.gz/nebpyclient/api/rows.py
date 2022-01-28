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

__all__ = [
    "RowSort",
    "RowFilter",
    "CreateRowInput",
    "UpdateRowInput",
    "Row",
    "RowList",
    "RowMixin"
]


class RowSort:
    """A sort object for rows

    Allows sorting rows on common properties. The sort object allows
    only one property to be specified.
    """

    def __init__(
            self,
            name: SortDirection = None
    ):
        """Constructs a new sort object for rows

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


class RowFilter:
    """A filter object to filter rows in a datacenter.

    Allows filtering for specific rows in nebulon ON. The
    filter allows only one property to be specified. If filtering on multiple
    properties is needed, use the ``and_filter`` and ``or_filter`` options to
    concatenate multiple filters.
    """

    def __init__(
            self,
            uuid: UuidFilter = None,
            name: StringFilter = None,
            room_uuid: UuidFilter = None,
            location: StringFilter = None,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new filter object

        The filter allows only one property to be specified. If filtering on
        multiple properties is needed, use the ``and_filter`` and ``or_filter``
        options to concatenate multiple filters.

        :param uuid: Filter based on row unique identifiers
        :type uuid: UuidFilter, optional
        :param name: Filter based on row name
        :type name: StringFilter, optional
        :param room_uuid: Filter based on the row's room unique identifier
        :type room_uuid: UuidFilter, optional
        :param location: Filter based on the row's location
        :type location: StringFilter, optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: DataCenterFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: DataCenterFilter, optional
        """

        self.__uuid = uuid
        self.__name = name
        self.__room_uuid = room_uuid
        self.__location = location
        self.__and = and_filter
        self.__or = or_filter

    @property
    def uuid(self) -> UuidFilter:
        """Filter based on row unique identifier"""
        return self.__uuid

    @property
    def name(self) -> StringFilter:
        """Filter based on row name"""
        return self.__name

    @property
    def room_uuid(self) -> UuidFilter:
        """Filter based on the room's row unique identifier"""
        return self.__room_uuid

    @property
    def location(self) -> StringFilter:
        """Filter based on rack location"""
        return self.__location

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
        result["labUUID"] = self.room_uuid
        result["name"] = self.name
        result["location"] = self.location
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class CreateRowInput:
    """An input object to create a row

    Allows the creation of a row object in nebulon ON. A
    row record allows customers to logically organize their
    infrastructure by physical location.
    """

    def __init__(
            self,
            room_uuid: str,
            name: str,
            note: str = None,
            location: str = None
    ):
        """Constructs a new input object to create a row

        Allows the creation of a row object in nebulon ON. A
        rack record allows customers to logically organize their
        infrastructure by physical location.

        :param room_uuid: Unique identifier for the parent room
        :type room_uuid: str
        :param name: Name for the new row
        :type name: str
        :param note: An optional note for the new row
        :type note: str, optional
        :param location: An optional location for the new row
        :type location: str, optional
        """

        self.__room_uuid = room_uuid
        self.__name = name
        self.__note = note
        self.__location = location

    @property
    def room_uuid(self) -> str:
        """Unique identifier for the parent room"""
        return self.__room_uuid

    @property
    def name(self) -> str:
        """Name for the new row"""
        return self.__name

    @property
    def note(self) -> str:
        """An optional note for the new row"""
        return self.__note

    @property
    def location(self) -> str:
        """An optional location for the new row"""
        return self.__location

    @property
    def as_dict(self):
        result = dict()
        result["labUUID"] = self.room_uuid
        result["name"] = self.name
        result["note"] = self.note
        result["location"] = self.location
        return result


class UpdateRowInput:
    """An input object to update row properties

    Allows updating of an existing row object in nebulon ON. A row record
    allows customers to logically organize their infrastructure by physical
    location.
    """

    def __init__(
            self,
            room_uuid: str = None,
            name: str = None,
            note: str = None,
            location: str = None
    ):
        """Constructs a new input object to update a row

        At least one property must be specified.

        :param room_uuid: New parent room for the row
        :type room_uuid: str, optional
        :param name: New name for the row
        :type name: str, optional
        :param note: The new note for the row. For removing the note, provide
            an empty str.
        :type note: str, optional
        :param location: A new optional location for the row
        :type location: str, optional
        """

        self.__room_uuid = room_uuid
        self.__name = name
        self.__note = note
        self.__location = location

    @property
    def room_uuid(self) -> str:
        """Unique identifier for a new room for the row"""
        return self.__room_uuid

    @property
    def name(self) -> str:
        """The new name of the row"""
        return self.__name

    @property
    def note(self) -> str:
        """The new note of the row"""
        return self.__note

    @property
    def location(self) -> str:
        """A new optional location for the row"""
        return self.__location

    @property
    def as_dict(self):
        result = dict()
        result["labUUID"] = self.room_uuid
        result["name"] = self.name
        result["note"] = self.note
        result["location"] = self.location
        return result


class DeleteRowInput:
    """An input object to delete a row object

    Allows additional options when deleting a row. When cascade is
    set to ``True`` all child resources are deleted with the datacenter room if
    no hosts are associated with the datacenter room.
    """

    def __init__(
            self,
            cascade: bool
    ):
        """Constructs a new input object to delete a row object

        :param cascade: If set to True any child resources are deleted with
            the row if no hosts are associated with it.
        :type cascade: bool
        """

        self.__cascade = cascade

    @property
    def cascade(self) -> bool:
        """Indicates that child items shall be deleted with the row"""
        return self.__cascade

    @property
    def as_dict(self):
        result = dict()
        result["cascade"] = self.cascade
        return result


class Row:
    """A row object

    A row record allows customers to logically organize their infrastructure
    by physical location.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new row object

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
        self.__room_uuid = read_value(
            "lab.uuid", response, str, False)
        self.__rack_uuids = read_value(
            "racks.uuid", response, str, False)
        self.__rack_count = read_value(
            "rackCount", response, int, True)
        self.__host_count = read_value(
            "hostCount", response, int, True)

    @property
    def uuid(self) -> str:
        """Unique identifier of the row"""
        return self.__uuid

    @property
    def name(self) -> str:
        """Name of the row"""
        return self.__name

    @property
    def note(self) -> str:
        """An optional note for the row"""
        return self.__note

    @property
    def location(self) -> str:
        """An optional location for the row"""
        return self.__location

    @property
    def room_uuid(self) -> str:
        """Unique identifier of the parent room"""
        return self.__room_uuid

    @property
    def rack_uuids(self) -> list:
        """Unique identifiers of racks in the row"""
        return self.__rack_uuids

    @property
    def rack_count(self) -> list:
        """Number of racks in the row"""
        return self.__rack_count

    @property
    def host_count(self) -> list:
        """Number of hosts (servers) in the row"""
        return self.__host_count

    @staticmethod
    def fields():
        return [
            "name",
            "uuid",
            "note",
            "location",
            "lab{uuid}",
            "racks{uuid}",
            "rackCount",
            "hostCount",
        ]


class RowList:
    """Paginated row list object

    Contains a list of row objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new row list object

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
            "items", response, Row, True)

    @property
    def items(self) -> [Row]:
        """List of rows in the pagination list"""
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
            "items{%s}" % (",".join(Row.fields())),
            "more",
            "totalCount",
            "filteredCount",
        ]


class RowMixin(NebMixin):
    """Mixin to add datacenter room related methods to the GraphQL client"""

    def get_rows(
            self,
            page: PageInput = None,
            row_filter: RowFilter = None,
            sort: RowSort = None
    ) -> RowList:
        """Retrieves a list of row objects

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param row_filter: A filter object to filter the row on
            the server. If omitted, the server will return all objects as a
            paginated response.
        :type row_filter: RowFilter, optional
        :param sort: A sort definition object to sort the row on supported
            properties. If omitted objects are returned in the order as they
            were created in.
        :type sort: RowSort, optional

        :returns RowList: A paginated list of rows in a datacenter.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            row_filter, "RowFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "RowSort", False)

        # make the request
        response = self._query(
            name="getRows",
            params=parameters,
            fields=RowList.fields()
        )

        # convert to object
        return RowList(response)

    def create_row(
            self,
            name: str,
            room_uuid: str,
            note: str = None,
            location: str = None
    ) -> Row:
        """Allows creation of a new datacenter room object

        Allows the creation of a row object in nebulon ON. A
        rack record allows customers to logically organize their
        infrastructure by physical location.

        :param room_uuid: Unique identifier for the parent room
        :type room_uuid: str
        :param name: Name for the new row
        :type name: str
        :param note: An optional note for the new row
        :type note: str, optional
        :param location: An optional location for the new row
        :type location: str, optional

        :returns Row: The new row in a datacenter.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            CreateRowInput(
                room_uuid=room_uuid,
                name=name,
                note=note,
                location=location
            ),
            "CreateRowInput",
            True
        )

        # make the request
        response = self._mutation(
            name="createRow",
            params=parameters,
            fields=Row.fields()
        )

        # convert to object
        return Row(response)

    def delete_row(
            self,
            uuid: str,
            cascade: bool = False
    ) -> Row:
        """Allows deletion of an existing row object

        The deletion of a row is only possible if the row has no hosts
        (servers) associated with any child items. By default,
        deletion of a row is only allowed when it is not  referenced by any
        racks or if the ``cascade`` parameter is set to ``True``.

        :param uuid: The unique identifier of the row to delete
        :type uuid: str
        :param cascade: If set to ``True`` any child items of the row (rack) will
            automatically deleted with this request. If set to ``False`` or
            omitted and the row has child objects, the deletion will fail with
            an error.
        :type cascade: bool, optional

        :returns bool: If the query was successful

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)
        parameters["input"] = GraphQLParam(
            DeleteRowInput(
                cascade=cascade
            ),
            "DeleteRowInput",
            False
        )

        # make the request
        response = self._mutation(
            name="deleteRow",
            params=parameters,
            fields=None
        )

        # convert to object
        return response

    def update_row(
            self,
            uuid: str,
            room_uuid: str = None,
            name: str = None,
            note: str = None,
            location: str = None
    ):
        """Allows updating properties of an existing datacenter room object

        At least one property must be specified.

        :param uuid: The unique identifier of the row to update
        :type uuid: str
        :param room_uuid: New parent room for the row
        :type room_uuid: str, optional
        :param name: New name for the row
        :type name: str, optional
        :param note: The new note for the row. For removing the note, provide
            an empty str.
        :type note: str, optional
        :param location: A new optional location for the row
        :type location: str, optional

        :returns Room: The updated datacenter room object.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)
        parameters["input"] = GraphQLParam(
            UpdateRowInput(
                room_uuid=room_uuid,
                name=name,
                note=note,
                location=location,
            ),
            "UpdateRowInput",
            True
        )

        # make the request
        response = self._mutation(
            name="updateRow",
            params=parameters,
            fields=Row.fields()
        )

        # convert to object
        return Row(response)
