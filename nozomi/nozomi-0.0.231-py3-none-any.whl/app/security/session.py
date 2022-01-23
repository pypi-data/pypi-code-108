"""
Nozomi
App Session Module
author: hugh@blinkybeach.com
"""
from nozomi.security.abstract_session import AbstractSession
from nozomi.http.headers import Headers
from nozomi.ancillary.immutable import Immutable
from nozomi.ancillary.configuration import Configuration
from nozomi.security.cookies import Cookies
from nozomi.security.perspective import Perspective
from nozomi.http.redirect import Redirect
from nozomi.http.api_request import ApiRequest
from nozomi.security.standalone_agent import StandaloneAgent
from nozomi.temporal.time import NozomiTime
from nozomi.http.method import HTTPMethod
from nozomi.http.url_parameters import URLParameters
from nozomi.http.url_parameter import URLParameter
from nozomi.errors.not_authenticated import NotAuthenticated
from urllib.request import HTTPError
from typing import Optional, TypeVar, Type, Any, Union
import hmac
from nozomi.security.agent import Agent
from nozomi.security.request_credentials import RequestCredentials

T = TypeVar('T', bound='Session')
ID_TYPE = Union[int, str]


class Session(AbstractSession):

    API_PATH: str = NotImplemented

    def __init__(
        self,
        session_id: ID_TYPE,
        session_key: str,
        api_key: str,
        agent: Agent,
        created: NozomiTime,
        last_utilised: NozomiTime,
        perspective: Perspective
    ) -> None:

        assert isinstance(session_key, str)
        assert isinstance(api_key, str)
        assert isinstance(agent, Agent)
        assert isinstance(created, NozomiTime)
        assert isinstance(last_utilised, NozomiTime)
        assert isinstance(perspective, Perspective)

        self._session_id = session_id
        self._session_key = session_key
        self._api_key = api_key
        self._agent = agent
        self._created = created
        self._last_utilised = last_utilised
        self._perspective = perspective

        return

    agent: Agent = Immutable(lambda s: s._agent)
    perspective: Perspective = Immutable(lambda s: s._perspective)
    api_key: str = Immutable(lambda s: s._api_key)
    session_id: ID_TYPE = Immutable(lambda s: s._session_id)
    session_key: str = Immutable(lambda s: s._session_key)

    agent_id = Immutable(lambda s: s.agent.agent_id)

    def _authenticate_raw_credentials(self, key: str) -> bool:
        """Return True if supplied credentials are authentic"""
        assert isinstance(key, str)
        key_comparison = hmac.compare_digest(key, self._session_key)
        assert isinstance(key_comparison, bool)
        if key_comparison is False:
            return key_comparison
        assert key == self._session_key
        return True

    def _authenticate_headers(
        self,
        headers: Headers,
        configuration: Configuration
    ) -> bool:
        """Return True if credentials derived from Hedaers are authentic"""
        cookies = self._cookies_from_headers(headers, configuration)
        if cookies is None:
            return False
        supplied_id = cookies.value_for(configuration.session_id_name)
        supplied_key = cookies.value_for(configuration.session_cookie_key_name)
        if str(supplied_id) != str(self._session_id):
            return False
        return self._authenticate_raw_credentials(supplied_key)

    def delete(
        self,
        credentials: RequestCredentials,
        configuration: Configuration
    ) -> None:
        """Delete this Session, AKA logout the user"""
        target = URLParameter('session_id', str(self._session_id))
        parameters = URLParameters([target])

        ApiRequest(
            path=self.API_PATH,
            method=HTTPMethod.DELETE,
            configuration=configuration,
            credentials=RequestCredentials,
            data=None,
            url_parameters=parameters
        )
        return None

    @classmethod
    def retrieve(
        cls: Type[T],
        session_id: ID_TYPE,
        credentials: RequestCredentials,
        configuration: Configuration
    ) -> Optional[T]:
        """Return a Session with the given Session ID, if it exists"""

        target = URLParameter('session_id', str(session_id))
        parameters = URLParameters([target])

        request = ApiRequest(
            path=cls.API_PATH,
            method=HTTPMethod.GET,
            configuration=configuration,
            data=None,
            url_parameters=parameters,
            credentials=credentials
        )

        if request.response_data is None:
            return None

        return cls.decode(request.response_data)

    @classmethod
    def decode(cls: Type[T], data: Any) -> T:
        """Return a Session decoded from API response data"""

        return cls(
            data['session_id'],
            data['session_key'],
            data['api_key'],
            StandaloneAgent.decode(data['agent_id']),
            NozomiTime.decode(data['created']),
            NozomiTime.decode(data['last_utilised']),
            Perspective(data['perspective'])
        )

    @classmethod
    def from_headers(
        cls: Type[T],
        headers: Headers,
        credentials: RequestCredentials,
        configuration: Configuration,
        request_may_change_state: bool
    ) -> Optional[T]:
        """
        Return a Session parsed from supplied headers, or None if no
        Session can be parsed.
        """

        if request_may_change_state is True:
            raise NotImplementedError('Cannot change data state from a \
Nozomi Application')
        cookies = cls._cookies_from_headers(headers, configuration)
        if cookies is None:
            return None

        session_id = cookies.value_for(configuration.session_id_name)

        try:
            session = cls.retrieve(
                session_id=session_id,
                configuration=configuration,
                credentials=credentials
            )
        except HTTPError as error:
            if error.code == 404:
                return None
            raise
        if session is None:
            return None

        if not session._authenticate_headers(headers, configuration):
            return None

        return session

    @classmethod
    def require_from_headers(
        cls: Type[T],
        headers: Headers,
        credentials: RequestCredentials,
        configuration: Configuration,
        request_may_change_state: bool = True,
        signin_path: Optional[str] = None
    ) -> T:
        """
        Return a Session parsed from supplied headers, or redirect to the login
        page if the user is not authenticated. Optionally supply a signin path
        to which the user should be redirected if a Session is not available.
        By default the user will be redirected to business signin.
        """
        session = cls.from_headers(
            headers=headers,
            credentials=credentials,
            configuration=configuration,
            request_may_change_state=request_may_change_state
        )
        if session is None:
            if signin_path is None:
                raise NotAuthenticated
            raise Redirect(
                destination=signin_path,
                allow_next=True,
                preserve_arguments=True,
            )
        return session

    @classmethod
    def _cookies_from_headers(
        cls: Type[T],
        headers: Headers,
        configuration: Configuration
    ) -> Optional[Cookies]:
        """
        Return Cookies if Headers appear to contain credentials, but make no
        judgement as to whether those credentials are authentic.
        """
        cookies = Cookies.from_headers(headers)
        if cookies is None:
            return None
        if (
                not cookies.contains(configuration.session_id_name)
                or not cookies.contains(configuration.session_cookie_key_name)
        ):
            return None
        return cookies
