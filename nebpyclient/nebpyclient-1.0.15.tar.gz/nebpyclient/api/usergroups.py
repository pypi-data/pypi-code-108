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
    "UserGroupSort",
    "UserGroupFilter",
    "CreateUserGroupInput",
    "UpdateUserGroupInput",
    "UserGroup",
    "UserGroupList",
    "UserGroupMixin"
]


class UserGroupSort:
    """A sort object for user groups

    Allows sorting user groups on common properties. The sort object allows
    only one property to be specified.
    """

    def __init__(
            self,
            name: SortDirection = None
    ):
        """Constructs a new sort object for user groups

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


class UserGroupFilter:
    """A filter object to filter user groups

    Allows filtering for specific user groups in nebulon ON. The
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

        :param uuid: Filter based on user unique identifiers
        :type uuid: UuidFilter, optional
        :param name: Filter based on user name
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
        """Filter based on users unique identifier"""
        return self.__uuid

    @property
    def name(self) -> StringFilter:
        """Filter based on user name"""
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


class CreateUserGroupInput:
    """An input object to create a new user group in nebulon ON"""

    def __init__(
            self,
            name: str,
            policy_uuids: [str],
            note: str = None
    ):
        """Constructs a new input object to create a new user group

        :param name: The name of the user group
        :type name: str
        :param policy_uuids: List of RBAC policies that shall be assigned to
            the user group
        :type policy_uuids: [str], optional
        :param note: An optional note for the user
        :type note: str, optional
        """

        self.__name = name
        self.__policy_uuids = policy_uuids
        self.__note = note

    @property
    def name(self) -> str:
        """The name of the user group"""
        return self.__name

    @property
    def policy_uuids(self) -> [str]:
        """List of RBAC policies associated with the user group"""
        return self.__policy_uuids

    @property
    def note(self) -> str:
        """An optional note for the user group"""
        return self.__note

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["note"] = self.note
        result["policyUUIDs"] = self.policy_uuids
        return result


class UpdateUserGroupInput:
    """An input object to update properties of a user group in nebulon ON"""

    def __init__(
            self,
            name: str = None,
            policy_uuids: [str] = None,
            note: str = None
    ):
        """Constructs a new input object to update properties of user groups

        :param name: New name for the user group
        :type name: str, optional
        :param policy_uuids: List of RBAC policies that shall be assigned to
            the user group
        :type policy_uuids: [str], optional
        :param note: An optional note for the user
        :type note: str, optional
        """

        self.__name = name
        self.__policy_uuids = policy_uuids
        self.__note = note

    @property
    def name(self) -> str:
        """The name of the user group"""
        return self.__name

    @property
    def policy_uuids(self) -> [str]:
        """List of RBAC policies associated with the user group"""
        return self.__policy_uuids

    @property
    def note(self) -> str:
        """An optional note for the user group"""
        return self.__note

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["note"] = self.note
        result["policyUUIDs"] = self.policy_uuids
        return result


class UserGroup:
    """A user group in nebulon ON

    User groups allow grouping users for more convenient management of
    permissions and policies
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new user group object

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
        self.__user_uuids = read_value(
            "users.uuid", response, str, False)
        self.__policy_uuids = read_value(
            "policies.uuid", response, str, False)

    @property
    def uuid(self) -> str:
        """The unique identifier of the user group in nebulon ON"""
        return self.__uuid

    @property
    def name(self) -> str:
        """The name of the user group"""
        return self.__name

    @property
    def note(self) -> str:
        """An optional note for the user"""
        return self.__note

    @property
    def user_uuids(self) -> [str]:
        """List of user unique identifiers that are part of the group"""
        return self.__user_uuids

    @property
    def policy_uuids(self) -> [str]:
        """List of RBAC policies associated with the user group"""
        return self.__policy_uuids

    @staticmethod
    def fields():
        return [
            "uuid",
            "name",
            "note",
            "users{uuid}",
            "policies{uuid}",
        ]


class UserGroupList:
    """Paginated user group list

    Contains a list of user group objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new user group list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__items = read_value(
            "items", response, UserGroup, True)
        self.__more = read_value(
            "more", response, bool, True)
        self.__total_count = read_value(
            "totalCount", response, int, True)
        self.__filtered_count = read_value(
            "filteredCount", response, int, True)

    @property
    def items(self) -> list:
        """List of user groups in the pagination list"""
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
            "items{%s}" % ",".join(UserGroup.fields()),
            "more",
            "totalCount",
            "filteredCount",
        ]


class UserGroupMixin(NebMixin):
    """Mixin to add user group related methods to the GraphQL client"""

    def get_user_groups(
            self,
            page: PageInput = None,
            ug_filter: UserGroupFilter = None,
            sort: UserGroupSort = None
    ) -> UserGroupList:
        """Retrieves a list of user group objects

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param ug_filter: A filter object to filter the user group objects on
            the server. If omitted, the server will return all objects as a
            paginated response.
        :type ug_filter: UserGroupFilter, optional
        :param sort: A sort definition object to sort the user group objects on
            supported properties. If omitted objects are returned in the order
            as they were created in.
        :type sort: UserGroupSort, optional

        :returns UserGroupList: A paginated list of user groups

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(page, "PageInput", False)
        parameters["filter"] = GraphQLParam(ug_filter, "UserGroupFilter", False)
        parameters["sort"] = GraphQLParam(sort, "UserGroupSort", False)

        # make the request
        response = self._query(
            name="getUserGroups",
            params=parameters,
            fields=UserGroupList.fields()
        )

        # convert to object
        return UserGroupList(response)

    def get_user_group_count(
            self,
            user_filter: UserGroupFilter = None
    ) -> int:
        """Get the number of user groups that match the specified filter

        :param user_filter: A filter object to filter the user group objects on
            the server. If omitted, the server will count all objects.
        :type user_filter: UserGroupFilter, optional

        :returns int: The number of user groups matching the filter

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["filter"] = GraphQLParam(
            user_filter, "UserFilter", False)

        # make the request
        response = self._query(
            name="getUserGroupsCount",
            params=parameters,
            fields=None
        )

        # response is an int
        return response

    def create_user_group(
            self,
            name: str,
            policy_uuids: [str],
            note: str = None
    ) -> UserGroup:
        """Allows creating a new user group in nebulon ON

        :param name: The name of the user group
        :type name: str
        :param policy_uuids: List of RBAC policies that shall be assigned to
            the user group
        :type policy_uuids: [str], optional
        :param note: An optional note for the user
        :type note: str, optional

        :returns User: The new user group

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            CreateUserGroupInput(
                name=name,
                policy_uuids=policy_uuids,
                note=note
            ),
            "CreateUserGroupInput",
            True
        )

        # make the request
        response = self._mutation(
            name="createOrgUserGroup",
            params=parameters,
            fields=UserGroup.fields()
        )

        # convert to object
        return UserGroup(response)

    def update_user_group(
            self,
            uuid: str,
            name: str = None,
            policy_uuids: [str] = None,
            note: str = None
    ) -> UserGroup:
        """Allow updating properties of an existing user group

        :param name: New name for the user group
        :type name: str, optional
        :param policy_uuids: List of RBAC policies that shall be assigned to
            the user group
        :type policy_uuids: [str], optional
        :param note: An optional note for the user
        :type note: str, optional

        :returns UserGroup: The updated user group

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)
        parameters["input"] = GraphQLParam(
            UpdateUserGroupInput(
                name=name,
                policy_uuids=policy_uuids,
                note=note
            ),
            "UpdateUserGroupInput",
            True
        )

        # make the request
        response = self._mutation(
            name="updateOrgUserGroup",
            params=parameters,
            fields=UserGroup.fields()
        )

        # convert to object
        return UserGroup(response)

    def delete_user_group(
            self,
            uuid: str
    ) -> bool:
        """Allows deletion of a user group

        :param uuid: The unique identifier of the user group that should be
            deleted
        :type uuid: str

        :returns bool: If the query was successful

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)

        # make the request
        response = self._mutation(
            name="deleteOrgUserGroup",
            params=parameters,
            fields=None
        )

        # response is a boolean
        return response
