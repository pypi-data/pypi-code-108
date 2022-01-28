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

from .common import read_value
from .users import UserPreferences
from .graphqlclient import GraphQLParam, NebMixin

__all__ = [
    "LoginState",
    "LoginResults",
    "SessionMixin"
]


class LoginResults:
    """Result of a login request"""

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new LoginResults object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__success = read_value(
            "success", response, bool, True)
        self.__message = read_value(
            "message", response, str, True)
        self.__expiration = read_value(
            "expiration", response, str, True)
        self.__user_uuid = read_value(
            "userUID", response, str, True)
        self.__organization_name = read_value(
            "organizationName", response, str, True)
        self.__eula_accepted = read_value(
            "eulaAccepted", response, bool, True)
        self.__user_preferences = read_value(
            "userPreferences", response, dict, True)

    @property
    def success(self) -> bool:
        """Indicates if the login was successful"""
        return self.__success

    @property
    def message(self) -> str:
        """A message describing the login result"""
        return self.__message

    @property
    def expiration(self) -> str:
        """Describes when the session will expire"""
        return self.__expiration

    @property
    def user_uuid(self) -> str:
        """The unique identifier of the user that logged in"""
        return self.__user_uuid

    @property
    def organization_name(self) -> str:
        """The name of the organization the user logged in"""
        return self.__organization_name

    @property
    def user_preferences(self) -> UserPreferences:
        """User preferences associated with the logged in user"""
        return self.__user_preferences

    @property
    def eula_accepted(self) -> bool:
        """Indicates if a user in the org has accepted the EULA"""
        return self.__eula_accepted

    @staticmethod
    def fields():
        return [
            "success",
            "message",
            "expiration",
            "userUID",
            "organizationName",
            "userPreferences{%s}" % (",".join(UserPreferences.fields())),
            "eulaAccepted",
        ]


class LoginState:
    """Represents the session state of a user"""

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new LoginState object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__organization = read_value(
            "organization", response, str, False)
        self.__username = read_value(
            "username", response, str, False)
        self.__expiration = read_value(
            "expiration", response, str, False)
        self.__user_uuid = read_value(
            "userUID", response, str, False)

    @property
    def organization(self) -> str:
        """Name of the organization for this session"""
        return self.__organization

    @property
    def username(self) -> str:
        """The name of the user for this session"""
        return self.__username

    @property
    def expiration(self) -> str:
        """Describes when the session expires"""
        return self.__expiration

    @property
    def user_uuid(self) -> str:
        """The user identifier of the user for this session"""
        return self.__user_uuid

    @staticmethod
    def fields():
        return [
            "organization",
            "username",
            "expiration",
            "userUID",
        ]


class SessionMixin(NebMixin):
    """Mixin to add session related methods to the GraphQL client"""

    def login(
            self,
            username: str,
            password: str
    ) -> LoginResults:
        """Login to nebulon ON

        :param username: nebulon ON username
        :type username: str
        :param password: nebulon ON password
        :type password: str

        :returns LoginResults: Login request result

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup parameters
        parameters = dict()
        parameters["username"] = GraphQLParam(username, "String", True)
        parameters["password"] = GraphQLParam(password, "String", True)

        # make the request
        response = self._mutation(
            name="login",
            params=parameters,
            fields=LoginResults.fields()
        )

        # convert to object
        return LoginResults(response)

    def get_session_state(self) -> LoginState:
        """Allows querying for the current login state

        :returns LoginState: Session state

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        response = self._query(
            name="loginStatus",
            params=None,
            fields=LoginState.fields()
        )

        # convert to object
        return LoginState(response)

    def logout(self) -> bool:
        """Logout from nebulon ON

        :returns bool: If the logout request was successful

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # make the request
        response = self._mutation(
            name="logout",
            params=None,
            fields=None
        )

        # response is of type bool
        return response
