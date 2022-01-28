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
from .common import read_value, NebEnum, DateFormat, PageInput
from .filters import UuidFilter, StringFilter
from .sorting import SortDirection

__all__ = [
    "SendNotificationType",
    "UserSort",
    "UserFilter",
    "UserPreferencesInput",
    "UpdateUserInput",
    "CreateUserInput",
    "UserPreferences",
    "User",
    "UserList",
    "UsersMixin"
]


class SendNotificationType(NebEnum):
    """Defines a user's notification preferences"""

    Disabled = "Disabled"
    """No email notifications are sent to the user"""

    Instant = "Instant"
    """The user will receive email notifications as events are triggered"""

    Daily = "Daily"
    """The user will receive a daily digest of alerts over the last 24 hours"""


class UserSort:
    """A sort object for users

    Allows sorting users on common properties. The sort object allows only one
    property to be specified.
    """

    def __init__(
            self,
            name: SortDirection = None
    ):
        """Constructs a new sort object for users

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


class UserFilter:
    """A filter object to filter users

    Allows filtering for specific user objects in nebulon ON. The
    filter allows only one property to be specified. If filtering on multiple
    properties is needed, use the ``and_filter`` and ``or_filter`` options to
    concatenate multiple filters.
    """

    def __init__(
            self,
            uuid: UuidFilter = None,
            name: StringFilter = None,
            email: StringFilter = None,
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
        :param email: Filter based on user email
        :type email: StringFilter, optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: DataCenterFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: DataCenterFilter, optional
        """
        self.__uuid = uuid
        self.__name = name
        self.__email = email
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
    def email(self) -> StringFilter:
        """Filter based on user email address"""
        return self.__email

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
        result["email"] = self.email
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class UserPreferencesInput:
    """An input object to define user preferences

    User preferences define settings and configuration options for individual
    user accounts in nebulon ON that are not globally configured.
    """

    def __init__(
            self,
            send_notification: SendNotificationType = None,
            time_zone: str = None,
            show_base_two: bool = None,
            date_format: DateFormat = None
    ):
        """Constructs a new input object to define user preferences

        User preferences define settings and configuration options for
        individual user accounts in nebulon ON that are not globally configured.

        :param send_notification: Specifies if, and the rate at which the user
            wants to receive email notifications for alerts in nebulon ON. By
            default, no email notifications are sent.
        :type send_notification: SendNotificationType, optional
        :param time_zone: Allows specifying the user's time zone.
        :type time_zone: str, optional
        :param show_base_two: Allows specifying if the user wants capacity
            values displayed with base2 notation. By default base10 is used.
        :type show_base_two: bool, optional
        :param date_format: Allows configuring the date format for date and
            time values in emails and and other strings
        :type date_format: str, optional
        """

        self.__send_notification = send_notification
        self.__time_zone = time_zone
        self.__show_base_two = show_base_two
        self.__date_format = date_format

    @property
    def send_notification(self) -> SendNotificationType:
        """Specifies if and the rate at which the user receives notifications"""
        return self.__send_notification

    @property
    def time_zone(self) -> str:
        """Specifies the time zone of the user"""
        return self.__time_zone

    @property
    def show_base_two(self) -> bool:
        """Specifies if the user wants capacity values displayed in base2"""
        return self.__show_base_two

    @property
    def date_format(self) -> DateFormat:
        """Specifies the user's preferred date and time formatting"""
        return self.__date_format

    @property
    def as_dict(self):
        result = dict()
        result["sendNotification"] = self.send_notification
        result["timeZone"] = self.time_zone
        result["showBaseTwo"] = self.show_base_two
        result["dateFormat"] = self.date_format
        return result


class UpdateUserInput:
    """An input object to update properties of a user in nebulon ON"""

    def __init__(
            self,
            name: str = None,
            password: str = None,
            note: str = None,
            email: str = None,
            user_group_uuids: [str] = None,
            first_name: str = None,
            last_name: str = None,
            mobile_phone: str = None,
            business_phone: str = None,
            inactive: bool = None,
            policy_uuids: [str] = None,
            send_notification: SendNotificationType = None,
            time_zone: str = None
    ):
        """Constructs a new input object to update properties of users

        :param name: The name of the user
        :type name: str, optional
        :param password: The password of the user. Changing the user's password
            through this API will cause the user to have his password changed
            at next login.
        :type password: str, optional
        :param note: An optional note for the user
        :type note: str, optional
        :param email: The user's business email address
        :type email: str, optional
        :param user_group_uuids: List of unique identifiers this user shall be
            part of. To remove a user from a user group, only specify the UUIDs
            of the groups the user shall be part of
        :type user_group_uuids: [str], optional
        :param first_name: The user's first name
        :type first_name: str, optional
        :param last_name: The user's last name
        :type last_name: str, optional
        :param mobile_phone: The user's mobile phone number
        :type mobile_phone: str, optional
        :param business_phone: The user's business phone number
        :type business_phone: str, optional
        :param inactive: Specifies if the user is inactive / disabled. Inactive
            users are still in the database but can not log in to nebulon ON.
        :type inactive: bool, optional
        :param policy_uuids: List of RBAC policies that shall be assigned to
            the user
        :type policy_uuids: [str], optional
        :param send_notification:  Specifies if, and the rate at which the user
            wants to receive email notifications for alerts in nebulon ON. By
            default, no email notifications are sent.
        :type send_notification: SendNotificationType, optional
        :param time_zone: Allows specifying the user's time zone.
        :type time_zone: str, optional
        """

        self.__name = name
        self.__password = password
        self.__note = note
        self.__email = email
        self.__user_group_uuids = user_group_uuids
        self.__first_name = first_name
        self.__last_name = last_name
        self.__mobile_phone = mobile_phone
        self.__business_phone = business_phone
        self.__inactive = inactive
        self.__policy_uuids = policy_uuids
        self.__send_notification = send_notification
        self.__time_zone = time_zone

    @property
    def name(self) -> str:
        """The name of the user"""
        return self.__name

    @property
    def password(self) -> str:
        """The password of the user"""
        return self.__password

    @property
    def note(self) -> str:
        """An optional note for the user"""
        return self.__note

    @property
    def email(self) -> str:
        """The business email address for the user"""
        return self.__email

    @property
    def user_group_uuids(self) -> [str]:
        """Unique identifiers of user groups the user is part of"""
        return self.__user_group_uuids

    @property
    def first_name(self) -> str:
        """The user's first name"""
        return self.__first_name

    @property
    def last_name(self) -> str:
        """The user's last name"""
        return self.__last_name

    @property
    def mobile_phone(self) -> str:
        """The mobile phone number of the user"""
        return self.__mobile_phone

    @property
    def business_phone(self) -> str:
        """The business phone number of the user"""
        return self.__business_phone

    @property
    def inactive(self) -> bool:
        """Indicates if the user is marked as inactive / disabled"""
        return self.__inactive

    @property
    def policy_uuids(self) -> [str]:
        """List of RBAC policies associated with the user"""
        return self.__policy_uuids

    @property
    def send_notification(self) -> SendNotificationType:
        """The user's notification preferences for alerts"""
        return self.__send_notification

    @property
    def time_zone(self) -> str:
        """The user's time zone"""
        return self.__time_zone

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["password"] = self.password
        result["note"] = self.note
        result["email"] = self.email
        result["userGroupUIDs"] = self.user_group_uuids
        result["firstName"] = self.first_name
        result["lastName"] = self.last_name
        result["mobilePhone"] = self.mobile_phone
        result["businessPhone"] = self.business_phone
        result["inactive"] = self.inactive
        result["sendNotification"] = self.send_notification
        result["timeZone"] = self.time_zone
        return result


class CreateUserInput:
    """An input object to create a new user account in nebulon ON"""

    def __init__(
            self,
            name: str,
            password: str,
            email: str,
            user_group_uuid: str,
            first_name: str,
            last_name: str,
            note: str = None,
            mobile_phone: str = None,
            business_phone: str = None,
            inactive: bool = None,
            policy_uuids: [str] = None,
            send_notification: SendNotificationType = None,
            time_zone: str = None
    ):
        """Constructs a new input object to create a new user in nebulon ON

        :param name: The name of the user
        :type name: str
        :param password: The password of the user. Changing the user's password
            through this API will cause the user to have his password changed
            at next login.
        :type password: str
        :param email: The user's business email address
        :type email: str
        :param user_group_uuid: Unique identifier this user shall be part of.
        :type user_group_uuid: str
        :param first_name: The user's first name
        :type first_name: str
        :param last_name: The user's last name
        :type last_name: str
        :param note: An optional note for the user
        :type note: str, optional
        :param mobile_phone: The user's mobile phone number
        :type mobile_phone: str, optional
        :param business_phone: The user's business phone number
        :type business_phone: str, optional
        :param inactive: Specifies if the user is inactive / disabled. Inactive
            users are still in the database but can not log in to nebulon ON.
        :type inactive: bool, optional
        :param policy_uuids: List of RBAC policies that shall be assigned to
            the user
        :type policy_uuids: [str], optional
        :param send_notification:  Specifies if, and the rate at which the user
            wants to receive email notifications for alerts in nebulon ON. By
            default, no email notifications are sent.
        :type send_notification: SendNotificationType, optional
        :param time_zone: Allows specifying the user's time zone.
        :type time_zone: str, optional
        """

        self.__name = name
        self.__password = password
        self.__note = note
        self.__email = email
        self.__user_group_uuid = user_group_uuid
        self.__first_name = first_name
        self.__last_name = last_name
        self.__mobile_phone = mobile_phone
        self.__business_phone = business_phone
        self.__inactive = inactive
        self.__policy_uuids = policy_uuids
        self.__send_notification = send_notification
        self.__time_zone = time_zone

    @property
    def name(self) -> str:
        """The name of the user"""
        return self.__name

    @property
    def password(self) -> str:
        """The password of the user"""
        return self.__password

    @property
    def note(self) -> str:
        """An optional note for the user"""
        return self.__note

    @property
    def email(self) -> str:
        """The business email address for the user"""
        return self.__email

    @property
    def user_group_uuid(self) -> str:
        """Unique identifier of the user group the user shall be part of"""
        return self.__user_group_uuid

    @property
    def first_name(self) -> str:
        """The user's first name"""
        return self.__first_name

    @property
    def last_name(self) -> str:
        """The user's last name"""
        return self.__last_name

    @property
    def mobile_phone(self) -> str:
        """The mobile phone number of the user"""
        return self.__mobile_phone

    @property
    def business_phone(self) -> str:
        """The business phone number of the user"""
        return self.__business_phone

    @property
    def inactive(self) -> bool:
        """Indicates if the user is marked as inactive / disabled"""
        return self.__inactive

    @property
    def policy_uuids(self) -> [str]:
        """List of RBAC policies associated with the user"""
        return self.__policy_uuids

    @property
    def send_notification(self) -> SendNotificationType:
        """The user's notification preferences for alerts"""
        return self.__send_notification

    @property
    def time_zone(self) -> str:
        """The user's time zone"""
        return self.__time_zone

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["password"] = self.password
        result["note"] = self.note
        result["email"] = self.email
        result["userGroupUUID"] = self.user_group_uuid
        result["firstName"] = self.first_name
        result["lastName"] = self.last_name
        result["mobilePhone"] = self.mobile_phone
        result["businessPhone"] = self.business_phone
        result["inactive"] = self.inactive
        result["sendNotification"] = self.send_notification
        result["timeZone"] = self.time_zone
        return result


class UserPreferences:
    """Settings and configuration options for a user

    User preferences define settings and configuration options for individual
    user accounts in nebulon ON that are not globally configured.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new user preferences object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__send_notification = read_value(
            "sendNotification", response, SendNotificationType, True)
        self.__time_zone = read_value(
            "timeZone", response, str, True)
        self.__show_base_two = read_value(
            "showBaseTwo", response, bool, True)
        self.__date_format = read_value(
            "dateFormat", response, DateFormat, True)

    @property
    def send_notification(self) -> SendNotificationType:
        """Specifies if and the rate at which the user receives notifications"""
        return self.__send_notification

    @property
    def time_zone(self) -> str:
        """Specifies the time zone of the user"""
        return self.__time_zone

    @property
    def show_base_two(self) -> bool:
        """Specifies if the user wants capacity values displayed in base2"""
        return self.__show_base_two

    @property
    def date_format(self) -> DateFormat:
        """Specifies the user's preferred date and time formatting"""
        return self.__date_format

    @staticmethod
    def fields():
        return [
            "sendNotification",
            "timeZone",
            "showBaseTwo",
            "dateFormat",
        ]


class User:
    """A user in nebulon ON"""

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new user object

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
        self.__email = read_value(
            "email", response, str, True)
        self.__first_name = read_value(
            "firstName", response, str, True)
        self.__last_name = read_value(
            "lastName", response, str, True)
        self.__mobile_phone = read_value(
            "mobilePhone", response, str, True)
        self.__business_phone = read_value(
            "businessPhone", response, str, True)
        self.__inactive = read_value(
            "inactive", response, bool, True)
        self.__group_uuids = read_value(
            "groups.uuid", response, str, False)
        self.__support_contact_id = read_value(
            "supportContactID", response, str, False)
        self.__change_password = read_value(
            "changePassword", response, bool, False)
        self.__preferences = read_value(
            "preferences", response, UserPreferences, False)
        self.__policy_uuids = read_value(
            "policies.uuid", response, str, False)

    @property
    def uuid(self) -> str:
        """The unique identifier of the user in nebulon ON"""
        return self.__uuid

    @property
    def name(self) -> str:
        """The name of the user"""
        return self.__name

    @property
    def note(self) -> str:
        """An optional note for the user"""
        return self.__note

    @property
    def email(self) -> str:
        """The business email address for the user"""
        return self.__email

    @property
    def first_name(self) -> str:
        """The user's first name"""
        return self.__first_name

    @property
    def last_name(self) -> str:
        """The user's last name"""
        return self.__last_name

    @property
    def mobile_phone(self) -> str:
        """The mobile phone number of the user"""
        return self.__mobile_phone

    @property
    def business_phone(self) -> str:
        """The business phone number of the user"""
        return self.__business_phone

    @property
    def inactive(self) -> bool:
        """Indicates if the user is marked as inactive / disabled"""
        return self.__inactive

    @property
    def group_uuids(self) -> list:
        """List of user group unique identifiers the user is part of"""
        return self.__group_uuids

    @property
    def support_contact_id(self) -> str:
        """The user identifier for support purposes (OEM)"""
        return self.__support_contact_id

    @property
    def change_password(self) -> bool:
        """Indicates if the user has to change the password during next login"""
        return self.__change_password

    @property
    def preferences(self) -> UserPreferences:
        """The user's personal preferences"""
        return self.__preferences

    @property
    def policy_uuids(self) -> [str]:
        """List of RBAC policies associated with the user"""
        return self.__policy_uuids

    @staticmethod
    def fields():
        return [
            "uuid",
            "name",
            "note",
            "email",
            "firstName",
            "lastName",
            "mobilePhone",
            "businessPhone",
            "inactive",
            "groups{uuid}",
            "preferences{%s}" % (",".join(UserPreferences.fields())),
            "policies{uuid}"
        ]


class UserList:
    """Paginated user list

    Contains a list of user objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new user list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__items = read_value(
            "items", response, User, False)
        self.__more = read_value(
            "more", response, bool, False)
        self.__total_count = read_value(
            "totalCount", response, int, False)
        self.__filtered_count = read_value(
            "filteredCount", response, int, False)

    @property
    def items(self) -> [User]:
        """List of users in the pagination list"""
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
            "items{%s}" % ",".join(User.fields()),
            "more",
            "totalCount",
            "filteredCount",
        ]


class UsersMixin(NebMixin):
    """Mixin to add user related methods to the GraphQL client"""

    def get_users(
            self,
            page: PageInput = None,
            user_filter: UserFilter = None,
            sort: UserSort = None
    ) -> UserList:
        """Retrieves a list of user objects

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param user_filter: A filter object to filter the user objects on the
            server. If omitted, the server will return all objects as a
            paginated response.
        :type user_filter: UserFilter, optional
        :param sort: A sort definition object to sort the user objects on
            supported properties. If omitted objects are returned in the order
            as they were created in.
        :type sort: UserSort, optional

        :returns UserList: A paginated list of users

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            user_filter, "UserFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "UserSort", False)

        # make the request
        response = self._query(
            name="getUsers",
            params=parameters,
            fields=UserList.fields()
        )

        # convert to object
        return UserList(response)

    def get_users_count(
            self,
            user_filter: UserFilter = None
    ) -> int:
        """Get the number of users that match the specified filter

        :param user_filter: A filter object to filter the user objects on the
            server. If omitted, the server will count all objects.
        :type user_filter: UserFilter, optional

        :returns int: The number of users matching the filter

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["filter"] = GraphQLParam(
            user_filter, "UserFilter", False)

        # make the request
        response = self._query(
            name="getUsersCount",
            params=parameters,
            fields=None
        )

        # response is an int
        return response

    def create_user(
            self,
            name: str,
            password: str,
            email: str,
            user_group_uuid: str,
            first_name: str,
            last_name: str,
            note: str = None,
            mobile_phone: str = None,
            business_phone: str = None,
            inactive: bool = None,
            policy_uuids: [str] = None,
            send_notification: SendNotificationType = None,
            time_zone: str = None
    ) -> User:
        """Allows creating a new user in nebulon ON

        :param name: The name of the user
        :type name: str
        :param password: The password of the user. Changing the user's password
            through this API will cause the user to have his password changed
            at next login.
        :type password: str
        :param email: The user's business email address
        :type email: str
        :param user_group_uuid: Unique identifier this user shall be part of.
        :type user_group_uuid: str
        :param first_name: The user's first name
        :type first_name: str
        :param last_name: The user's last name
        :type last_name: str
        :param note: An optional note for the user
        :type note: str, optional
        :param mobile_phone: The user's mobile phone number
        :type mobile_phone: str, optional
        :param business_phone: The user's business phone number
        :type business_phone: str, optional
        :param inactive: Specifies if the user is inactive / disabled. Inactive
            users are still in the database but can not log in to nebulon ON.
        :type inactive: bool, optional
        :param policy_uuids: List of RBAC policies that shall be assigned to
            the user
        :type policy_uuids: [str], optional
        :param send_notification:  Specifies if, and the rate at which the user
            wants to receive email notifications for alerts in nebulon ON. By
            default, no email notifications are sent.
        :type send_notification: SendNotificationType, optional
        :param time_zone: Allows specifying the user's time zone.
        :type time_zone: str, optional

        :returns User: The new user account

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            CreateUserInput(
                name=name,
                password=password,
                email=email,
                user_group_uuid=user_group_uuid,
                first_name=first_name,
                last_name=last_name,
                note=note,
                mobile_phone=mobile_phone,
                business_phone=business_phone,
                inactive=inactive,
                policy_uuids=policy_uuids,
                send_notification=send_notification,
                time_zone=time_zone
            ),
            "CreateUserInput",
            True
        )

        # make the request
        response = self._mutation(
            name="createOrgUser",
            params=parameters,
            fields=User.fields()
        )

        # convert to object
        return User(response)

    def update_user(
            self,
            uuid: str,
            name: str = None,
            password: str = None,
            note: str = None,
            email: str = None,
            user_group_uuids: [str] = None,
            first_name: str = None,
            last_name: str = None,
            mobile_phone: str = None,
            business_phone: str = None,
            inactive: bool = None,
            policy_uuids: [str] = None,
            send_notification: SendNotificationType = None,
            time_zone: str = None
    ) -> User:
        """Allow updating properties of an existing user

        :param uuid: The unique identifier of the user that should be updated
        :type uuid: str
        :param name: The name of the user
        :type name: str, optional
        :param password: The password of the user. Changing the user's password
            through this API will cause the user to have his password changed
            at next login.
        :type password: str, optional
        :param note: An optional note for the user
        :type note: str, optional
        :param email: The user's business email address
        :type email: str, optional
        :param user_group_uuids: List of unique identifiers this user shall be
            part of. To remove a user from a user group, only specify the UUIDs
            of the groups the user shall be part of
        :type user_group_uuids: [str], optional
        :param first_name: The user's first name
        :type first_name: str, optional
        :param last_name: The user's last name
        :type last_name: str, optional
        :param mobile_phone: The user's mobile phone number
        :type mobile_phone: str, optional
        :param business_phone: The user's business phone number
        :type business_phone: str, optional
        :param inactive: Specifies if the user is inactive / disabled. Inactive
            users are still in the database but can not log in to nebulon ON.
        :type inactive: bool, optional
        :param policy_uuids: List of RBAC policies that shall be assigned to
            the user
        :type policy_uuids: [str], optional
        :param send_notification:  Specifies if, and the rate at which the user
            wants to receive email notifications for alerts in nebulon ON. By
            default, no email notifications are sent.
        :type send_notification: SendNotificationType, optional
        :param time_zone: Allows specifying the user's time zone.
        :type time_zone: str, optional

        :returns User: The updated user account

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)
        parameters["input"] = GraphQLParam(
            UpdateUserInput(
                name=name,
                password=password,
                email=email,
                user_group_uuids=user_group_uuids,
                first_name=first_name,
                last_name=last_name,
                note=note,
                mobile_phone=mobile_phone,
                business_phone=business_phone,
                inactive=inactive,
                policy_uuids=policy_uuids,
                send_notification=send_notification,
                time_zone=time_zone
            ),
            "UpdateUserInput",
            True
        )

        # make the request
        response = self._mutation(
            name="updateOrgUser",
            params=parameters,
            fields=User.fields()
        )

        # convert to object
        return User(response)

    def delete_user(
            self,
            uuid: str
    ) -> bool:
        """Allows deletion of a user account

        :param uuid: The unique identifier of the user that should be deleted
        :type uuid: str

        :returns bool: If the query was successful

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)

        # make the request
        response = self._mutation(
            name="deleteOrgUser",
            params=parameters,
            fields=None
        )

        # response is a bool
        return response
