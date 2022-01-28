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
    "RBACRoleSort",
    "RBACRoleFilter",
    "CreateRBACRoleInput",
    "UpdateRBACRoleInput",
    "RBACRole",
    "RBACRoleList",
    "RBACPolicyList",
    "RBACPolicyFilter",
    "CreateRBACPolicyInput",
    "UpdateRBACPolicyInput",
    "RBACPolicy",
    "RBACPolicySort",
    "RBACMixin"
]


class RBACRoleSort:
    """A sort object for RBAC roles

    Allows sorting RBAC roles on common properties. The sort object
    allows only one property to be specified.
    """

    def __init__(
            self,
            name: SortDirection = None
    ):
        """Constructs a new sort object for RBAC roles

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


class RBACRoleFilter:
    """A filter object to filter RBAC roles

    Allows filtering for specific RBAC roles in nebulon ON. The
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

        :param uuid: Filter based on RBAC role unique identifiers
        :type uuid: UuidFilter, optional
        :param name: Filter based on RBAC role name
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
        """Filter based on RBAC role unique identifier"""
        return self.__uuid

    @property
    def name(self) -> StringFilter:
        """Filter based on RBAC role name"""
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


class CreateRBACRoleInput:
    """An input object to create a RBAC role

    Roles in role-based access control define a set of permissions (rights)
    that can be assigned to user groups according to their responsibilities.
    Rights can be added and removed if these responsibilities change and
    propagate to any user that is associated with a role.

    Rights are defined through a string with the format
    `{resource}/{permission}`, where the following resources are available:

    * ``*``
    * ``Datacenter``
    * ``Lab``
    * ``Audit``
    * ``Alert``
    * ``FirmwareUpdate``
    * ``UserGroup``
    * ``nPodGroup``
    * ``Volume``
    * ``PhysicalDrive``
    * ``User``
    * ``nPod``
    * ``SnapshotScheduleTemplate``
    * ``SPU``
    * ``Row``
    * ``Rack``
    * ``nPodTemplate``
    * ``SnapshotSchedule``
    * ``Host``
    * ``LUN``
    * ``Webhook``

    The following permissions are available:

    * ``*`` - everything is permitted
    * ``read`` - read operations are permitted
    * ``create`` - create operations are permitted
    * ``update`` - update operations are permitted
    * ``delete`` - delete operations are permitted
    * ``execute`` - execute operations are permitted (used for operations that \
        do not fall in the above categories)

    The number and type of permissions and resources may change over time and
    users can query the currently available resources and permissions with
    the ``get_metadata`` query.

    """

    def __init__(
            self,
            name: str,
            description: str,
            rights: [str]
    ):
        """Constructs a new input object to create a RBAC role

        :param name: Human readable name for the RBAC role
        :type name: str
        :param description: A description that well describes the role and
            associated rights. The role description should provide enough
            clarity so that users should not have to read individual rights
        :type description: str
        :param rights: List of rights definitions. Please review the class
            description of options for ``resource`` and ``permission`` in the
            rights string that is in the format `{resource}/{permission}`. Use
            the ``get_metadata`` query to retrieve the latest list of options.
        :type rights: [str]
        """

        self.__name = name
        self.__description = description
        self.__rights = rights

    @property
    def name(self) -> str:
        """Human readable name for the RBAC role"""
        return self.__name

    @property
    def description(self) -> str:
        """Description of the RBAC role and associated rights"""
        return self.__description

    @property
    def rights(self) -> list:
        """List of rights definitions for the RBAC role"""
        return self.__rights

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["description"] = self.description
        result["rights"] = self.rights
        return result


class UpdateRBACRoleInput:
    """An input object to update properties a RBAC role

    Roles in role-based access control define a set of permissions (rights)
    that can be assigned to user groups according to their responsibilities.
    Rights can be added and removed if these responsibilities change and
    propagate to any user that is associated with a role.

    Rights are defined through a string with the format
    `{resource}/{permission}`, where the following resources are available:

    * `*`
    * ``Datacenter``
    * ``Lab``
    * ``Audit``
    * ``Alert``
    * ``FirmwareUpdate``
    * ``UserGroup``
    * ``nPodGroup``
    * ``Volume``
    * ``PhysicalDrive``
    * ``User``
    * ``nPod``
    * ``SnapshotScheduleTemplate``
    * ``SPU``
    * ``Row``
    * ``Rack``
    * ``nPodTemplate``
    * ``SnapshotSchedule``
    * ``Host``
    * ``LUN``
    * ``Webhook``

    The following permissions are available:

    * `*` - everything is permitted
    * ``read`` - read operations are permitted
    * ``create`` - create operations are permitted
    * ``update`` - update operations are permitted
    * ``delete`` - delete operations are permitted
    * ``execute`` - execute operations are permitted (used for operations that
       do not fall in the above categories)

    The number and type of permissions and resources may change over time and
    users can query the currently available resources and permissions with
    the ``get_metadata`` query.
    """

    def __init__(
            self,
            name: str = None,
            description: str = None,
            rights: [str] = None
    ):
        """Constructs a new input object to update RBAC role properties

        :param name: Human readable name for the RBAC role
        :type name: str
        :param description: A description that well describes the role and
            associated rights. The role description should provide enough
            clarity so that users should not have to read individual rights
        :type description: str
        :param rights: List of rights definitions. Please review the class
            description of options for ``resource`` and ``permission`` in the
            rights string that is in the format `{resource}/{permission}`. Use
            the ``get_metadata`` query to retrieve the latest list of options.
        :type rights: [str]
        """

        self.__name = name
        self.__description = description
        self.__rights = rights

    @property
    def name(self) -> str:
        """Human readable name for the RBAC role"""
        return self.__name

    @property
    def description(self) -> str:
        """Description of the RBAC role and associated rights"""
        return self.__description

    @property
    def rights(self) -> list:
        """List of rights definitions for the RBAC role"""
        return self.__rights

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["description"] = self.description
        result["rights"] = self.rights
        return result


class RBACRole:
    """A role definition for role-based access control (RBAC)

    Roles in role-based access control define a set of permissions (rights)
    that can be assigned to user groups according to their responsibilities.
    Rights can be added and removed if these responsibilities change and
    propagate to any user that is associated with a role.

    Rights are defined through a string with the format
    `{resource}/{permission}`, where the following permissions are defined:

    * `*` - everything is permitted
    * ``read`` - read operations are permitted
    * ``create`` - create operations are permitted
    * ``update`` - update operations are permitted
    * ``delete`` - delete operations are permitted
    * ``execute`` - execute operations are permitted (used for operations that
       do not fall in the above categories)
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new RBAC role object

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
        self.__description = read_value(
            "description", response, str, True)
        self.__custom = read_value(
            "custom", response, bool, True)
        self.__rights = read_value(
            "rights", response, str, True)

    @property
    def uuid(self) -> str:
        """Unique identifier of the RBAC role"""
        return self.__uuid

    @property
    def name(self) -> str:
        """Human readable name of the RBAC role"""
        return self.__name

    @property
    def description(self) -> str:
        """A comprehensive description of the role and associated rights"""
        return self.__description

    @property
    def custom(self) -> bool:
        """Indicates if the RBAC role was user defined"""
        return self.__custom

    @property
    def rights(self) -> [str]:
        """List of rights definitions in this RBAC role"""
        return self.__rights

    @staticmethod
    def fields():
        return [
            "uuid",
            "name",
            "description",
            "custom",
            "rights",
        ]


class RBACRoleList:
    """Paginated RBAC role list object

    Contains a list of RBAC role objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new RBAC role list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__items = read_value(
            "items", response, RBACRole, False)
        self.__more = read_value(
            "more", response, bool, False)
        self.__total_count = read_value(
            "totalCount", response, int, False)
        self.__filtered_count = read_value(
            "filteredCount", response, int, False)

    @property
    def items(self) -> [RBACRole]:
        """List of RBAC roles in the pagination list"""
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
            "items{%s}" % ",".join(RBACRole.fields()),
            "more",
            "totalCount",
            "filteredCount",
        ]


class RBACPolicySort:
    """A sort object for RBAC policies

    Allows sorting RBAC policies on common properties. The sort object
    allows only one property to be specified.
    """

    def __init__(
            self,
            name: SortDirection = None
    ):
        """Constructs a new sort object for RBAC policies

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


class RBACPolicyFilter:
    """A filter object to filter RBAC policies

    Allows filtering for specific RBAC policies in nebulon ON. The
    filter allows only one property to be specified. If filtering on multiple
    properties is needed, use the ``and_filter`` and ``or_filter`` options to
    concatenate multiple filters.
    """

    def __init__(
            self,
            uuid: UuidFilter = None,
            role_uuid: UuidFilter = None,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new filter object

        The filter allows only one property to be specified. If filtering on
        multiple properties is needed, use the ``and_filter`` and ``or_filter``
        options to concatenate multiple filters.

        :param uuid: Filter based on RBAC role unique identifiers
        :type uuid: UuidFilter, optional
        :param role_uuid: Filter based on RBAC role unique identifiers
        :type role_uuid: UuidFilter, optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: DataCenterFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: DataCenterFilter, optional
        """

        self.__uuid = uuid
        self.__role_uuid = role_uuid
        self.__and = and_filter
        self.__or = or_filter

    @property
    def uuid(self) -> UuidFilter:
        """Filter based on RBAC policy unique identifier"""
        return self.__uuid

    @property
    def role_uuid(self) -> UuidFilter:
        """Filter based on RBAC role unique identifier"""
        return self.__role_uuid

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
        result["roleUUID"] = self.role_uuid
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class CreateRBACPolicyInput:
    """An input object to create a RBAC policy

    Policies in role-based access control associate RBAC roles with users
    and resources in nebulon ON. Scopes can be added and removed from policies,
    users and user groups can be added and removed from policies. Nebulon ON
    will not allow two policies with the same definition.

    Scopes are defined through a string with the format
    `/nPodGroup/{npod_group_uuid}/nPod/{npod_uuid}` with varying length. For
    example:

    - `/nPodGroup/*`:
        scopes the policy to all nPod groups in the organization
    - `/nPodGroup/{npod_group_uuid}/nPod/*`:
        scopes the policy to a specific nPod group in the organization and all
        nPods in this group.
    - `/nPodGroup/{npod_group_uuid}/nPod/{npod_uuid}`:
        scopes the policy to a specific nPod.

    User groups are not added and removed from a policy through this API, but
    through the ``users`` API. Use ``create_user_group``, ``update_user_group``
    for adding and removing user groups to RBAC policies and similarly
    ``create_user`` and ``update_user``.
    """

    def __init__(
            self,
            role_uuid: str,
            scopes: [str]
    ):
        """Constructs a new input object to create a RBAC policy

        Policies in role-based access control associate RBAC roles with users
        and resources in nebulon ON. Scopes can be added and removed from
        policies, users and user groups can be added and removed from policies.
        Nebulon ON will not allow two policies with the same definition.

        Scopes are defined through a string with the format
        `/nPodGroup/{npod_group_uuid}/nPod/{npod_uuid}` with varying length. For
        example:

        - `/nPodGroup/*` scopes the policy to all nPod groups in the
            organization
        - `/nPodGroup/{npod_group_uuid}/nPod/*` scopes the policy to a specific
            nPod group in the organization and all nPods in this group.
        - `/nPodGroup/{npod_group_uuid}/nPod/{npod_uuid}` scopes the policy to a
            specific nPod.

        User groups are not added and removed from a policy through this API,
        but through the ``users`` API. Use ``create_user_group``,
        ``update_user_group`` for adding and removing user groups to RBAC
        policies and similarly ``create_user`` and ``update_user``.

        :param role_uuid: The RBAC role unique identifier to associate with
            the policy
        :type role_uuid: str
        :param scopes: List of scope definitions that this policy applies to.
            At least one scope must be provided.
        :type scopes: [str]
        """

        self.__role_uuid = role_uuid
        self.__scopes = scopes

    @property
    def role_uuid(self) -> str:
        """The RBAC role unique identifier to associate with the policy"""
        return self.__role_uuid

    @property
    def scopes(self) -> [str]:
        """List of scope definitions that this policy applies to"""
        return self.__scopes

    @property
    def as_dict(self):
        result = dict()
        result["roleUUID"] = self.role_uuid
        result["scopes"] = self.scopes
        return result


class UpdateRBACPolicyInput:
    """An input object to update RBAC policy properties

    Policies in role-based access control associate RBAC roles with users
    and resources in nebulon ON. Scopes can be added and removed from policies,
    users and user groups can be added and removed from policies. Nebulon ON
    will not allow two policies with the same definition.

    Scopes are defined through a string with the format
    `/nPodGroup/{npod_group_uuid}/nPod/{npod_uuid}` with varying length. For
    example:

    - `/nPodGroup/*`:
        scopes the policy to all nPod groups in the organization
    - `/nPodGroup/{npod_group_uuid}/nPod/*`:
        scopes the policy to a specific nPod group in the organization and all
        nPods in this group.
    - `/nPodGroup/{npod_group_uuid}/nPod/{npod_uuid}`:
        scopes the policy to a specific nPod.

    User groups are not added and removed from a policy through this API, but
    through the ``users`` API. Use ``create_user_group``, ``update_user_group``
    for adding and removing user groups to RBAC policies and similarly
    ``create_user`` and ``update_user``.
    """

    def __init__(
            self,
            scopes: [str] = None
    ):
        """Constructs a new input object to update RBAC policy properties

        Policies in role-based access control associate RBAC roles with users
        and resources in nebulon ON. Scopes can be added and removed from
        policies, users and user groups can be added and removed from policies.
        Nebulon ON will not allow two policies with the same definition.

        Scopes are defined through a string with the format
        `/nPodGroup/{npod_group_uuid}/nPod/{npod_uuid}` with varying length. For
        example:

        - `/nPodGroup/*` scopes the policy to all nPod groups in the
            organization
        - `/nPodGroup/{npod_group_uuid}/nPod/*` scopes the policy to a specific
            nPod group in the organization and all nPods in this group.
        - `/nPodGroup/{npod_group_uuid}/nPod/{npod_uuid}` scopes the policy to a
            specific nPod.

        User groups are not added and removed from a policy through this API,
        but through the ``users`` API. Use ``create_user_group``,
        ``update_user_group`` for adding and removing user groups to RBAC
        policies and similarly ``create_user`` and ``update_user``.

        :param scopes: List of scope definitions that this policy applies to.
            At least one scope must be provided.
        :type scopes: [str]
        """
        self.__scopes = scopes

    @property
    def scopes(self) -> [str]:
        """List of scope definitions that this policy applies to"""
        return self.__scopes

    @property
    def as_dict(self):
        result = dict()
        result["scopes"] = self.scopes
        return result


class RBACPolicy:
    """A RBAC policy object

    Policies in role-based access control associate RBAC roles with users
    and resources in nebulon ON. Scopes can be added and removed from policies,
    users and user groups can be added and removed from policies. Nebulon ON
    will not allow two policies with the same definition.

    Scopes are defined through a string with the format
    `/nPodGroup/{npod_group_uuid}/nPod/{npod_uuid}` with varying length. For
    example:

    - `/nPodGroup/*` scopes the policy to all nPod groups in the organization
    - `/nPodGroup/{npod_group_uuid}/nPod/*` scopes the policy to a specific nPod
        group in the organization and all nPods in this group.
    - `/nPodGroup/{npod_group_uuid}/nPod/{npod_uuid}` scopes the policy to a
        specific nPod.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new RBAC policy object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__uuid = read_value(
            "uuid", response, str, True)
        self.__role_uuid = read_value(
            "role.uuid", response, str, True)
        self.__scopes = read_value(
            "scopes", response, str, False)
        self.__user_uuids = read_value(
            "users.uuid", response, str, False)
        self.__user_group_uuids = read_value(
            "userGroups.uuid", response, str, False)

    @property
    def uuid(self) -> str:
        """The unique identifier of the RBAC policy"""
        return self.__uuid

    @property
    def role_uuid(self) -> str:
        """The unique identifier of the RBAC role in this policy"""
        return self.__role_uuid

    @property
    def scopes(self) -> [str]:
        """List of scopes this RBAC policy applies to"""
        return self.__scopes

    @property
    def user_uuids(self) -> [str]:
        """List of unique identifiers of explicit users in the RBAC policy"""
        return self.__user_uuids

    @property
    def user_group_uuids(self) -> [str]:
        """List of unique identifiers of user groups in the RBAC policy"""
        return self.__user_group_uuids

    @staticmethod
    def fields():
        return [
            "uuid",
            "role{uuid}",
            "scopes",
            "users{uuid}",
            "userGroups{uuid}",
        ]


class RBACPolicyList:
    """Paginated RBAC policy list object

    Contains a list of RBAC policy objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new RBAC policy list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__items = read_value(
            "items", response, RBACPolicy, True)
        self.__more = read_value(
            "more", response, bool, True)
        self.__total_count = read_value(
            "totalCount", response, int, True)
        self.__filtered_count = read_value(
            "filteredCount", response, int, True)

    @property
    def items(self) -> [RBACPolicy]:
        """List of RBAC policies in the pagination list"""
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
            "items{%s}" % ",".join(RBACPolicy.fields()),
            "more",
            "totalCount",
            "filteredCount",
        ]


class RBACMixin(NebMixin):
    """Mixin to add RBAC related methods to the GraphQL client"""

    def get_rbac_roles(
            self,
            page: PageInput = None,
            rbac_filter: RBACRoleFilter = None,
            sort: RBACRoleSort = None
    ) -> RBACRoleList:
        """Retrieves a list of RBAC role objects

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param rbac_filter: A filter object to filter the RBAC roles on
            the server. If omitted, the server will return all objects as a
            paginated response.
        :type rbac_filter: RBACRoleFilter, optional
        :param sort: A sort definition object to sort the RBAC roles
            on supported properties. If omitted objects are returned in the
            order as they were created in.
        :type sort: RBACRoleSort, optional

        :returns RBACRoleList: A paginated list of RBAC roles.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            rbac_filter, "RBACRoleFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "RBACRoleSort", False)

        # make the request
        response = self._query(
            name="getRBACRoles",
            params=parameters,
            fields=RBACRoleList.fields()
        )

        # convert to object
        return RBACRoleList(response)

    def create_rbac_role(
            self,
            name: str,
            description: str,
            rights: [str]
    ) -> RBACRole:
        """Allows creation of a new RBAC role

        Roles in role-based access control define a set of permissions (rights)
        that can be assigned to user groups according to their responsibilities.
        Rights can be added and removed if these responsibilities change and
        propagate to any user that is associated with a role.

        Rights are defined through a string with the format
        `{resource}/{permission}`. The number and type of permissions and
        resources may change over time and users can query the currently
        available resources and permissions with the ``get_metadata`` query.

        :param name: Human readable name for the RBAC role
        :type name: str
        :param description: A description that well describes the role and
            associated rights. The role description should provide enough
            clarity so that users should not have to read individual rights
        :type description: str
        :param rights: List of rights definitions. Please review the class
            description of options for ``resource`` and ``permission`` in the
            rights string that is in the format `{resource}/{permission}`. Use
            the ``get_metadata`` query to retrieve the latest list of options.
        :type rights: [str]

        :returns RBACRole: The new RBAC role.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            CreateRBACRoleInput(
                name=name,
                description=description,
                rights=rights
            ),
            "CreateRBACRoleInput",
            True
        )

        # make the request
        response = self._mutation(
            name="createRBACRole",
            params=parameters,
            fields=RBACRole.fields()
        )

        # convert to object
        return RBACRole(response)

    def update_rbac_role(
            self,
            uuid: str,
            name: str = None,
            description: str = None,
            rights: [str] = None
    ) -> RBACRole:
        """Allows updating of RBAC role properties

        Roles in role-based access control define a set of permissions (rights)
        that can be assigned to user groups according to their responsibilities.
        Rights can be added and removed if these responsibilities change and
        propagate to any user that is associated with a role.

        Rights are defined through a string with the format
        `{resource}/{permission}`. The number and type of permissions and
        resources may change over time and users can query the currently
        available resources and permissions with the ``get_metadata`` query.

        :param uuid: The RBAC role unique identifier to update
        :type uuid: str
        :param name: Human readable name for the RBAC role
        :type name: str
        :param description: A description that well describes the role and
            associated rights. The role description should provide enough
            clarity so that users should not have to read individual rights
        :type description: str
        :param rights: List of rights definitions. Please review the class
            description of options for ``resource`` and ``permission`` in the
            rights string that is in the format `{resource}/{permission}`. Use
            the ``get_metadata`` query to retrieve the latest list of options.
        :type rights: [str]

        :returns RBACRole: The new RBAC role.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)
        parameters["input"] = GraphQLParam(
            UpdateRBACRoleInput(
                name=name,
                description=description,
                rights=rights
            ),
            "UpdateRBACRoleInput",
            True
        )

        # make the request
        response = self._mutation(
            name="updateRBACRole",
            params=parameters,
            fields=RBACRole.fields()
        )

        # convert to object
        return RBACRole(response)

    def delete_rbac_role(
            self,
            uuid: str
    ) -> bool:
        """Allows deletion of an RBAC role object

        :param uuid: The unique identifier of the RBAC role to delete
        :type uuid: str

        :returns bool: If the query was successful

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)

        # make the request
        response = self._mutation(
            name="deleteRBACRole",
            params=parameters,
            fields=None
        )

        # response is boolean
        return response

    def get_rbac_policies(
            self,
            page: PageInput = None,
            rbac_filter: RBACPolicyFilter = None,
            sort: RBACPolicySort = None
    ) -> RBACPolicyList:
        """Retrieves a list of RBAC policy objects

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param rbac_filter: A filter object to filter the RBAC policies on
            the server. If omitted, the server will return all objects as a
            paginated response.
        :type rbac_filter: RBACPolicyFilter, optional
        :param sort: A sort definition object to sort the RBAC policies
            on supported properties. If omitted objects are returned in the
            order as they were created in.
        :type sort: RBACPolicySort, optional

        :returns RBACPolicyList: A paginated list of RBAC policies.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            rbac_filter, "RBACPolicyFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "RBACPolicySort", False)

        # make the request
        response = self._query(
            name="getRBACPolicies",
            params=parameters,
            fields=RBACPolicyList.fields()
        )

        # convert to object
        return RBACPolicyList(response)

    def create_rbac_policy(
            self,
            role_uuid: str,
            scopes: [str]
    ) -> RBACPolicy:
        """Allows creation of a new RBAC policy

        Policies in role-based access control associate RBAC roles with users
        and resources in nebulon ON. Scopes can be added and removed from
        policies, users and user groups can be added and removed from policies.
        Nebulon ON will not allow two policies with the same definition.

        Scopes are defined through a string with the format
        `/nPodGroup/{npod_group_uuid}/nPod/{npod_uuid}` with varying length. For
        example:

        - `/nPodGroup/*` scopes the policy to all nPod groups in the
            organization
        - `/nPodGroup/{npod_group_uuid}/nPod/*` scopes the policy to a specific
            nPod group in the organization and all nPods in this group.
        - `/nPodGroup/{npod_group_uuid}/nPod/{npod_uuid}` scopes the policy to a
            specific nPod.

        User groups are not added and removed from a policy through this API,
        but through the ``users`` API. Use ``create_user_group``,
        ``update_user_group`` for adding and removing user groups to RBAC
        policies and similarly ``create_user`` and ``update_user``.

        :param role_uuid: The RBAC role unique identifier to associate with
            the policy
        :type role_uuid: str
        :param scopes: List of scope definitions that this policy applies to.
            At least one scope must be provided.
        :type scopes: [str]

        :returns RBACPolicy: The new RBAC policy

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            CreateRBACPolicyInput(
                role_uuid=role_uuid,
                scopes=scopes,
            ),
            "CreateRBACPolicyInput",
            True
        )

        # make the request
        response = self._mutation(
            name="createRBACPolicy",
            params=parameters,
            fields=RBACPolicy.fields()
        )

        # convert to object
        return RBACPolicy(response)

    def update_rbac_policy(
            self,
            uuid: str,
            scopes: [str]
    ) -> RBACPolicy:
        """Allows updating of RBAC policy properties

        Policies in role-based access control associate RBAC roles with users
        and resources in nebulon ON. Scopes can be added and removed from
        policies, users and user groups can be added and removed from policies.
        Nebulon ON will not allow two policies with the same definition.

        Scopes are defined through a string with the format
        `/nPodGroup/{npod_group_uuid}/nPod/{npod_uuid}` with varying length. For
        example:

        - `/nPodGroup/*` scopes the policy to all nPod groups in the
            organization
        - `/nPodGroup/{npod_group_uuid}/nPod/*` scopes the policy to a specific
            nPod group in the organization and all nPods in this group.
        - `/nPodGroup/{npod_group_uuid}/nPod/{npod_uuid}` scopes the policy to a
            specific nPod.

        User groups are not added and removed from a policy through this API,
        but through the ``users`` API. Use ``create_user_group``,
        ``update_user_group`` for adding and removing user groups to RBAC
        policies and similarly ``create_user`` and ``update_user``.

        :param uuid: The RBAC policy unique identifier to update
        :type uuid: str
        :param scopes: List of scope definitions that this policy applies to.
            At least one scope must be provided.
        :type scopes: [str]

        :returns RBACPolicy: The updated RBAC policy

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)
        parameters["input"] = GraphQLParam(
            UpdateRBACPolicyInput(
                scopes=scopes,
            ),
            "UpdateRBACPolicyInput",
            True
        )

        # make the request
        response = self._mutation(
            name="updateRBACPolicy",
            params=parameters,
            fields=RBACPolicy.fields()
        )

        # convert to object
        return RBACPolicy(response)

    def delete_rbac_policy(
            self,
            uuid: str
    ) -> bool:
        """Allows deletion of an RBAC policy object

        :param uuid: The unique identifier of the RBAC policy to delete
        :type uuid: str

        :returns bool: If the query was successful

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)

        # make the request
        response = self._mutation(
            name="deleteRBACPolicy",
            params=parameters,
            fields=None
        )

        # response is boolean
        return response
