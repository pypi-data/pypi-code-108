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
    "RackSort",
    "RackFilter",
    "CreateRackInput",
    "UpdateRackInput",
    "Rack",
    "RackList",
    "RacksMixin"
]


class RackSort:
    """A sort object for racks

    Allows sorting racks on common properties. The sort object allows
    only one property to be specified.
    """

    def __init__(
            self,
            name: SortDirection = None
    ):
        """Constructs a new sort object for racks

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


class RackFilter:
    """A filter object to filter racks.

    Allows filtering for specific racks in nebulon ON. The
    filter allows only one property to be specified. If filtering on multiple
    properties is needed, use the ``and_filter`` and ``or_filter`` options to
    concatenate multiple filters.
    """

    def __init__(
            self,
            uuid: UuidFilter = None,
            name: StringFilter = None,
            row_uuid: UuidFilter = None,
            location: StringFilter = None,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new filter object

        The filter allows only one property to be specified. If filtering on
        multiple properties is needed, use the ``and_filter`` and ``or_filter``
        options to concatenate multiple filters.

        :param uuid: Filter based on rack unique identifiers
        :type uuid: UuidFilter, optional
        :param name: Filter based on rack name
        :type name: StringFilter, optional
        :param row_uuid: Filter based on the rack's row unique identifier
        :type row_uuid: UuidFilter, optional
        :param location: Filter based on the rack's location
        :type location: StringFilter, optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: DataCenterFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: DataCenterFilter, optional
        """

        self.__uuid = uuid
        self.__name = name
        self.__row_uuid = row_uuid
        self.__location = location
        self.__and = and_filter
        self.__or = or_filter

    @property
    def uuid(self) -> UuidFilter:
        """Filter based on rack unique identifier"""
        return self.__uuid

    @property
    def name(self) -> StringFilter:
        """Filter based on rack name"""
        return self.__name

    @property
    def row_uuid(self) -> UuidFilter:
        """Filter based on the rack's row unique identifier"""
        return self.__row_uuid

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
        result["rowUUID"] = self.row_uuid
        result["name"] = self.name
        result["location"] = self.location
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class CreateRackInput:
    """An input object to create a rack

    Allows the creation of a rack object in nebulon ON. A
    rack record allows customers to logically organize their
    infrastructure by physical location.
    """

    def __init__(
            self,
            row_uuid: str,
            name: str,
            note: str = None,
            location: str = None
    ):
        """Constructs a new input object to create a rack

        Allows the creation of a rack object in nebulon ON. A
        rack record allows customers to logically organize their
        infrastructure by physical location.

        :param row_uuid: Unique identifier for the parent row
        :type row_uuid: str
        :param name: Name for the new rack
        :type name: str
        :param note: An optional note for the new rack
        :type note: str, optional
        :param location: An optional location for the new rack
        :type location: str, optional
        """

        self.__row_uuid = row_uuid
        self.__name = name
        self.__note = note
        self.__location = location

    @property
    def row_uuid(self) -> str:
        """Unique identifier for the parent row"""
        return self.__row_uuid

    @property
    def name(self) -> str:
        """Name for the new rack"""
        return self.__name

    @property
    def note(self) -> str:
        """An optional note for the new rack"""
        return self.__note

    @property
    def location(self) -> str:
        """An optional location for the new rack"""
        return self.__location

    @property
    def as_dict(self):
        result = dict()
        result["rowUUID"] = self.row_uuid
        result["name"] = self.name
        result["note"] = self.note
        result["location"] = self.location
        return result


class UpdateRackInput:
    """An input object to update rack properties

    Allows updating of an existing rack object in nebulon ON. A
    rack record allows customers to logically organize their
    infrastructure by physical location.
    """

    def __init__(
            self,
            row_uuid: str = None,
            name: str = None,
            note: str = None,
            location: str = None
    ):
        """Constructs a new input object to update a rack

        At least one property must be specified.

        :param row_uuid: New parent row for the rack
        :type row_uuid: str, optional
        :param name: New name for the rack
        :type name: str, optional
        :param note: The new note for the rack. For removing the note, provide
            an empty str.
        :type note: str, optional
        :param location: A new optional location for the rack
        :type location: str, optional
        """

        self.__row_uuid = row_uuid
        self.__name = name
        self.__note = note
        self.__location = location

    @property
    def row_uuid(self) -> str:
        """Unique identifier for a new row for the rack"""
        return self.__row_uuid

    @property
    def name(self) -> str:
        """The new name of the rack"""
        return self.__name

    @property
    def note(self) -> str:
        """The new note of the rack"""
        return self.__note

    @property
    def location(self) -> str:
        """A new optional location for the rack"""
        return self.__location

    @property
    def as_dict(self):
        result = dict()
        result["rowUUID"] = self.row_uuid
        result["name"] = self.name
        result["note"] = self.note
        result["location"] = self.location
        return result


class Rack:
    """A rack in a datacenter

    A rack record allows customers to logically organize their infrastructure
    by physical location.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new rack object

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
        self.__row_uuid = read_value(
            "row.uuid", response, str, False)
        self.__host_uuids = read_value(
            "hosts.uuid", response, str, False)
        self.__host_count = read_value(
            "hostCount", response, int, True)

    @property
    def uuid(self) -> str:
        """Unique identifier of the rack"""
        return self.__uuid

    @property
    def name(self) -> str:
        """Name of the rack"""
        return self.__name

    @property
    def note(self) -> str:
        """An optional note for the rack"""
        return self.__note

    @property
    def location(self) -> str:
        """An optional location for the rack"""
        return self.__location

    @property
    def row_uuid(self) -> str:
        """Unique identifier of the parent row"""
        return self.__row_uuid

    @property
    def host_uuids(self) -> list:
        """Unique identifiers of hosts in the rack"""
        return self.__host_uuids

    @property
    def host_count(self) -> list:
        """Number of hosts (servers) in the rack"""
        return self.__host_count

    @staticmethod
    def fields():
        return [
            "name",
            "uuid",
            "note",
            "location",
            "row{uuid}",
            "hosts{uuid}",
            "hostCount",
        ]


class RackList:
    """Paginated rack list object

    Contains a list of rack objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new rack list object

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
            "items", response, Rack, True)

    @property
    def items(self) -> [Rack]:
        """List of racks in the pagination list"""
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
            "items{%s}" % (",".join(Rack.fields())),
            "more",
            "totalCount",
            "filteredCount",
        ]


class RacksMixin(NebMixin):
    """Mixin to add datacenter room related methods to the GraphQL client"""

    def get_racks(
            self,
            page: PageInput = None,
            rack_filter: RackFilter = None,
            sort: RackSort = None
    ) -> RackList:
        """Retrieves a list of rack objects

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param rack_filter: A filter object to filter the racks on
            the server. If omitted, the server will return all objects as a
            paginated response.
        :type rack_filter: RackFilter, optional
        :param sort: A sort definition object to sort the racks on supported
            properties. If omitted objects are returned in the order as they
            were created in.
        :type sort: RackSort, optional

        :returns RackList: A paginated list of racks in a datacenter.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            rack_filter, "RackFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "RackSort", False)

        # make the request
        response = self._query(
            name="getRacks",
            params=parameters,
            fields=RackList.fields()
        )

        # convert to object
        return RackList(response)

    def create_rack(
            self,
            name: str,
            row_uuid: str,
            note: str = None,
            location: str = None
    ) -> Rack:
        """Allows creation of a new rack object

        A rack record allows customers to logically organize their
        infrastructure by physical location.

        :param row_uuid: Unique identifier for the parent row
        :type row_uuid: str
        :param name: Name for the new rack
        :type name: str
        :param note: An optional note for the new rack
        :type note: str, optional
        :param location: An optional location for the new rack
        :type location: str, optional

        :returns Rack: The new rack.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            CreateRackInput(
                row_uuid=row_uuid,
                name=name,
                note=note,
                location=location
            ),
            "CreateRackInput",
            True
        )

        # make the request
        response = self._mutation(
            name="createRack",
            params=parameters,
            fields=Rack.fields()
        )

        # convert to object
        return Rack(response)

    def delete_rack(
            self,
            uuid: str
    ) -> bool:
        """Allows deletion of an existing rack object

        The deletion of a rack is only possible if the rack has no hosts
        (servers) associated.

        :param uuid: The unique identifier of the datacenter room to delete
        :type uuid: str

        :returns bool: If the query was successful

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)

        # make the request
        response = self._mutation(
            name="deleteRack",
            params=parameters,
            fields=None
        )

        # response is a bool
        return response

    def update_rack(
            self,
            uuid: str,
            row_uuid: str = None,
            name: str = None,
            note: str = None,
            location: str = None
    ) -> Rack:
        """Allows updating properties of an existing rack object

        At least one property must be specified.

        :param uuid: The unique identifier of the rack to update
        :type uuid: str
        :param row_uuid: New parent row for the rack
        :type row_uuid: str, optional
        :param name: New name for the rack
        :type name: str, optional
        :param note: The new note for the rack. For removing the note, provide
            an empty str.
        :type note: str, optional
        :param location: A new optional location for the rack
        :type location: str, optional

        :returns Rack: The updated rack object.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)
        parameters["input"] = GraphQLParam(
            UpdateRackInput(
                row_uuid=row_uuid,
                name=name,
                note=note,
                location=location,
            ),
            "UpdateRackInput",
            True
        )

        # make the request
        response = self._mutation(
            name="updateRack",
            params=parameters,
            fields=Rack.fields()
        )

        # convert to object
        return Rack(response)
