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
from .filters import StringFilter, UuidFilter
from .sorting import SortDirection

__all__ = [
    "NPodGroupSort",
    "NPodGroupList",
    "NPodGroupMixin",
    "NPodGroupFilter",
    "NPodGroup",
    "CreateNPodGroupInput",
    "UpdateNPodGroupInput"
]


class NPodGroupSort:
    """A sort object for nPod groups

    Allows sorting nPod groups on common properties. The sort object allows
    only one property to be specified.
    """

    def __init__(
            self,
            name: SortDirection = None
    ):
        """Constructs a new sort object for nPod groups

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


class NPodGroupFilter:
    """A filter object to filter nPod groups.

    Allows filtering for specific nPod groups in nebulon ON. The
    filter allows only one property to be specified. If filtering on multiple
    properties is needed, use the ``and_filter`` and ``or_filter`` options to
    concatenate multiple filters.
    """

    def __init__(
            self,
            uuid: UuidFilter = None,
            name: StringFilter = None,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new filter object

        The filter allows only one property to be specified. If filtering on
        multiple properties is needed, use the ``and_filter`` and ``or_filter``
        options to concatenate multiple filters.

        :param uuid: Filter based on nPod group unique identifier
        :type uuid: UuidFilter, optional
        :param name: Filter based on nPod group name
        :type name: StringFilter, optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: DataCenterFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: DataCenterFilter, optional
        """
        self.__uuid = uuid
        self.__name = name
        self.__and = and_filter
        self.__or = or_filter

    @property
    def uuid(self) -> UuidFilter:
        """Filter based on nPod group unique identifier"""
        return self.__uuid

    @property
    def name(self) -> StringFilter:
        """Filter based on nPod group name"""
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
        result["name"] = self.name
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class UpdateNPodGroupInput:
    """An input object to update nPod group properties

    Allows updating of an existing nPod group object in nebulon ON. A nPod
    group allows logical grouping of nPods into security domains. Each nPod
    group can receive custom security policies.
    """

    def __init__(
            self,
            name: str,
            note: str = None
    ):
        """Construct a new input object to update nPod groups

        Allows updating of an existing nPod group object in nebulon ON. A nPod
        group allows logical grouping of nPods into security domains. Each nPod
        group can receive custom security policies.

        :param name: The new name of the nPod group
        :type name: str
        :param note: The new note for the nPod group. For removing the note,
            provide an empty str.
        :type note: str, optional
        """

        self.__name = name
        self.__note = note

    @property
    def name(self) -> str:
        """The new name of the nPod group"""
        return self.__name

    @property
    def note(self) -> str:
        """The new note for the nPod group"""
        return self.__note

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["note"] = self.note
        return result


class CreateNPodGroupInput:
    """An input object to create a new nPod group

    Allows creation of a new nPod group object in nebulon ON. A nPod
    group allows logical grouping of nPods into security domains. Each nPod
    group can receive custom security policies.
    """

    def __init__(
            self,
            name: str,
            note: str = None
    ):
        """Construct a new input object to create a nPod group

        Allows creation of a new nPod group object in nebulon ON. A nPod
        group allows logical grouping of nPods into security domains. Each nPod
        group can receive custom security policies.

        :param name: The name of the new nPod group
        :type name: str
        :param note: The note for the new nPod group. For removing the note,
            provide an empty str.
        :type note: str, optional
        """

        self.__name = name
        self.__note = note

    @property
    def name(self) -> str:
        """The name of the nPod group"""
        return self.__name

    @property
    def note(self) -> str:
        """The note for the nPod group"""
        return self.__note

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["note"] = self.note
        return result


class NPodGroup:
    """A group of nPods

    A nPod group allows logical grouping of nPods into security domains. Each
    nPod group can receive custom security policies and contain multiple nPods.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new nPod group

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__uuid = read_value(
            "uuid", response, str, True)
        self.__name = read_value(
            "name", response, str, True)
        self.__note = read_value(
            "note", response, str, True)
        self.__npod_uuids = read_value(
            "nPods.uuid", response, str, False)
        self.__npod_count = read_value(
            "nPodCount", response, int, True)
        self.__host_count = read_value(
            "hostCount", response, int, True)
        self.__spu_count = read_value(
            "spuCount", response, int, True)

    @property
    def uuid(self) -> str:
        """The unique identifier for the nPod group"""
        return self.__uuid

    @property
    def name(self) -> str:
        """The name of the nPod group"""
        return self.__name

    @property
    def note(self) -> str:
        """An optional note for the nPod group"""
        return self.__note

    @property
    def npod_uuids(self) -> [str]:
        """List of nPod unique identifiers in this nPod group"""
        return self.__npod_uuids

    @property
    def npod_count(self) -> int:
        """Number of nPods in this nPod group"""
        return self.__npod_count

    @property
    def host_count(self) -> int:
        """Number of hosts (servers) in this nPod group"""
        return self.__host_count

    @property
    def spu_count(self) -> int:
        """Number of services processing units in this nPod group"""
        return self.__spu_count

    @staticmethod
    def fields():
        return [
            "uuid",
            "name",
            "note",
            "nPods{uuid}",
            "nPodCount",
            "hostCount",
            "spuCount",
        ]


class NPodGroupList:
    """Paginated nPod group list object

    Contains a list of nPod group objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new nPod group list object

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
            "items", response, NPodGroup, True)

    @property
    def items(self) -> list:
        """List of nPod groups in the pagination list"""
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
            "items{%s}" % (",".join(NPodGroup.fields())),
            "more",
            "totalCount",
            "filteredCount",
        ]


class NPodGroupMixin(NebMixin):
    """Mixin to add nPod group related methods to the GraphQL client"""

    def get_npod_groups(
            self,
            page: PageInput = None,
            npod_group_filter: NPodGroupFilter = None,
            sort: NPodGroupSort = None
    ) -> NPodGroupList:
        """Retrieves a list of nPod group objects

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param npod_group_filter: A filter object to filter the items on the
            server. If omitted, the server will return all objects as a
            paginated response.
        :type npod_group_filter: NPodGroupFilter, optional
        :param sort: A sort definition object to sort the objects on supported
            properties. If omitted objects are returned in the order as they
            were created in.
        :type sort: NPodGroupSort, optional

        :returns NPodGroupList: A paginated list of nPod groups.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            npod_group_filter, "NPodGroupFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "NPodGroupSort", False)

        # make the request
        response = self._query(
            name="getNPodGroups",
            params=parameters,
            fields=NPodGroupList.fields()
        )

        # convert to object
        return NPodGroupList(response)

    def create_npod_group(
            self,
            name: str,
            note: str = None
    ) -> NPodGroup:
        """Allows creation of a new nPod group object

        Allows creation of a new nPod group object in nebulon ON. A nPod
        group allows logical grouping of nPods into security domains. Each nPod
        group can receive custom security policies.

        :param name: The name of the new nPod group
        :type name: str
        :param note: The note for the new nPod group. For removing the note,
            provide an empty str.
        :type note: str, optional

        :returns NPodGroup: The new nPod group.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            CreateNPodGroupInput(
                name=name,
                note=note,
            ),
            "CreateNPodGroupInput",
            True
        )

        # make the request
        response = self._mutation(
            name="createNPodGroup",
            params=parameters,
            fields=NPodGroup.fields(),
        )

        # convert to object
        return NPodGroup(response)

    def get_npod_group_count(
            self,
            npod_group_filter: NPodGroupFilter = None
    ) -> int:
        """Retrieves the number of nPod groups matching the filter

        :param npod_group_filter: A filter object to filter the items on the
            server. If omitted, all items are counted on the server
        :type npod_group_filter: NPodGroupFilter, optional

        :returns int: The number of nPod groups matching the filter.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["filter"] = GraphQLParam(
            npod_group_filter,
            "NPodGroupFilter",
            False
        )

        # make the request
        response = self._query(
            name="getNPodGroupCount",
            params=parameters,
            fields=None
        )

        # convert to object
        return response

    def update_npod_group(
            self,
            uuid: str,
            name: str = None,
            note: str = None
    ):
        """Allows updating new nPod group object properties

        Allows updating of an existing nPod group object in nebulon ON. A nPod
        group allows logical grouping of nPods into security domains. Each nPod
        group can receive custom security policies.

        :param uuid: The unique identifier of the nPod group to update
        :type uuid: str
        :param name: The name of the new nPod group
        :type name: str
        :param note: The note for the new nPod group. For removing the note,
            provide an empty str.
        :type note: str, optional

        :returns NPodGroup: The new nPod group.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)
        parameters["input"] = GraphQLParam(
            UpdateNPodGroupInput(
                name=name,
                note=note
            ),
            "UpdateNPodGroupInput",
            True
        )

        # make the request
        response = self._mutation(
            name="updateNPodGroup",
            params=parameters,
            fields=NPodGroup.fields(),
        )

        # convert to object
        return NPodGroup(response)

    def delete_npod_group(
            self,
            uuid: str
    ):
        """Allows deleting a nPod group object

        :param uuid: The unique identifier of the nPod group to delete
        :type uuid: str

        :returns NPodGroup: The new nPod group.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)

        # make the request
        response = self._mutation(
            name="deleteNPodGroup",
            params=parameters,
            fields=None
        )

        # response is boolean
        return response
