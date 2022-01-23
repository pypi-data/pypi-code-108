"""
Nozomi
Session Module
author: hugh@blinkybeach.com
"""
from datetime import datetime
from nozomi.data.datastore import Datastore
from nozomi.data.encodable import Encodable
from nozomi.data.decodable import Decodable
from nozomi.data.query import Query
from nozomi.security.random_number import RandomNumber
from nozomi.errors.error import NozomiError
from nozomi.errors.bad_request import BadRequest
from nozomi.security.ip_address import IpAddress
from nozomi.security.secret import Secret
from nozomi.security.perspective import Perspective
from nozomi.ancillary.time import NozomiTime
from nozomi.ancillary.immutable import Immutable
from nozomi.security.agent import Agent
from nozomi.security.credentials import Credentials
from nozomi.security.cookies import Cookies
from nozomi.http.headers import Headers
from typing import Any, Dict, TypeVar, Type, Optional
from nozomi.ancillary.configuration import Configuration
import hmac

T = TypeVar('T', bound='Session')


class Session(Encodable, Decodable, Agent):

    _Q_DELETE: Query.optionally_from_file('queries/session/delete.sql')
    _Q_RETRIEVE: Query.optionally_from_file('queries/session/retrieve.sql')
    _Q_CREATE: Query.optionally_from_file('queries/session/create.sql')

    def __init__(
        self,
        session_id: str,
        session_key: str,
        api_key: str,
        agent: Agent,
        created: datetime,
        last_utilised: datetime,
        ip_address: IpAddress,
        perspective: Perspective
    ) -> None:

        assert isinstance(session_id, int)
        assert isinstance(session_key, str)
        assert isinstance(api_key, str)
        assert isinstance(agent, Agent)
        assert isinstance(created, NozomiTime)
        assert isinstance(last_utilised, NozomiTime)
        assert isinstance(ip_address, IpAddress)
        assert isinstance(perspective, Perspective)

        self._session_id = session_id
        self._session_key = session_key
        self._api_key = api_key
        self._agent = agent
        self._created = created
        self._last_utilised = last_utilised
        self._ip_address = ip_address
        self._perspective = perspective

        return

    session_id: int = Immutable(lambda s: s._session_id)
    session_key: str = Immutable(lambda s: s._session_key)
    agent: Agent = Immutable(lambda s: s._human)
    perspective: Perspective = Immutable(lambda s: s._perspective)
    api_key: str = Immutable(lambda s: s._api_key)

    agent_id = Immutable(lambda s: s._human.agent_id)

    Q_RETRIEVE = Immutable(lambda s: s._load_query(s._Q_RETRIEVE))
    Q_CREATE = Immutable(lambda s: s._load_query(s._Q_CREATE))
    Q_DELETE = Immutable(lambda s: s._load_query(s._Q_DELETE))

    def _load_query(self, query: Optional[Query]) -> Query:
        if query is None:
            raise NotImplementedError('A required SQL query is not implemented')
        return query

    def _finds_api_key_authentic(
        self,
        api_key: str
    ) -> bool:
        """Return True if supplied credentials are authentic"""
        assert isinstance(api_key, str)
        key_comparison = hmac.compare_digest(api_key, self._api_key)
        assert isinstance(key_comparison, bool)
        return key_comparison

    def _finds_session_key_authentic(
        self,
        session_key: str
    ) -> bool:
        """Return True if supplied cookie session key is authentic"""
        assert isinstance(session_key, str)
        key_comparison = hmac.compare_digest(session_key, self._session_key)
        assert isinstance(key_comparison, bool)
        return key_comparison

    def delete(
        self,
        configuration: Configuration,
        datastore: Datastore
    ) -> None:
        """Return after deleting this Session."""
        arguments = {
            'session_id': self._session_id,
            'seconds_to_live': configuration.session_seconds_to_live
        }
        self.Q_DELETE.execute(datastore, arguments, atomic=True)
        return None

    def encode(self) -> Dict[str, Any]:

        return {
            'session_id': self._session_id,
            'session_key': self._session_key,
            'api_key': self._api_key,
            'human': self._human.broadcast_to(self._human),
            'created': self._created.encode(),
            'last_utilised': self._last_utilised.encode(),
            'ip_address': self._ip_address.encode(),
            'perspective': self._perspective.value
        }

    @classmethod
    def from_headers(
        cls: Type[T],
        headers: Optional[Headers],
        datastore: Datastore,
        configuration: Configuration,
        request_may_change_state: bool = True
    ) -> Optional[T]:
        """
        Return a Session parsed from Headers, if it exists and supplied credentials
        are authentic
        """
        assert isinstance(request_may_change_state, bool)
        if headers is None:
            return None
        if request_may_change_state is False:
            session = cls.from_cookies_in_headers(
                headers=headers,
                configuration=configuration,
                request_may_change_state=request_may_change_state
            )
            if session is not None:
                return session
        credentials = Credentials.from_headers(headers)
        if credentials is None:
            return None
        session = cls.retrieve(credentials.session_id, datastore)
        if session is None:
            return None
        if not session._finds_api_key_authentic(credentials.api_key):
            return None
        return session

    @classmethod
    def from_cookies_in_headers(
        cls: Type[T],
        headers: Headers,
        datastore: Datastore,
        configuration: Configuration,
        request_may_change_state: bool = True
    ) -> Optional[T]:
        """
        Return a Session parsed from the cookies found in Headers. To provide
        defense against accidental use of cookie authentication for
        state-changing requests, i.e. accidental introduction of a CSRF
        vulnerability, this method requires the caller to assert that state
        change does not occur.
        """
        if request_may_change_state is True:
            raise RuntimeError('Cannot auth with cookies if state may change')
        cookies = Cookies.from_headers(headers)
        if cookies is None:
            return None
        if not cookies.contains(configuration.session_id_name):
            return None
        if not cookies.contains(configuration.session_cookie_key_name):
            return None
        session_id = cookies.value_for(configuration.session_id_name)
        try:
            session_id = int(session_id)
        except Exception:
            return None
        session = cls.retrieve(
            session_id=session_id,
            datastore=datastore
        )
        if session is None:
            return None
        session_key = cookies.value_for(configuration.session_cookie_key_name)
        if not isinstance(session_key, str):
            return None
        if not session._finds_session_key_authentic(session_key):
            return None
        return session

    @classmethod
    def require_from_headers(
        cls: Type[T],
        headers: Optional[Headers],
        datastore: Datastore,
        configuration: Configuration,
        request_may_change_state: bool = True
    ) -> T:
        session = cls.from_headers(
            headers=headers,
            datastore=datastore,
            configuration=configuration,
            request_may_change_state=True
        )
        if session is None:
            raise NozomiError('Not authenticated', 401)
        return session

    @classmethod
    def create(
        cls: Type[T],
        provided_email: str,
        provided_plaintext_secret: str,
        ip_address: IpAddress,
        datastore: Datastore,
        perspective: Perspective,
        configuration: Configuration
    ) -> T:
        """Return a newly minted Session"""

        secret = Secret.retrieve_for_email(provided_email, datastore)
        if secret is None:
            raise NozomiError('Invalid credentials', 401)

        secret_check = secret.matches(provided_plaintext_secret)

        if secret_check is False:
            raise NozomiError('Invalid credentials', 401)

        assert secret_check is True  # Redundant sanity check

        # There is currently a race condition between any Human Profile
        # email change and Session creation.

        input_data = {
            'session_id': RandomNumber(64).urlsafe_base64,
            'session_key': RandomNumber(192).urlsafe_base64,
            'api_key': RandomNumber(192).urlsafe_base64,
            'email_address': provided_email,
            'ip_address': ip_address,
            'human_id': None,
            'seconds_to_live': configuration.session_seconds_to_live,
            'perspective': perspective.perspective_id
        }

        try:
            result = cls.Q_CREATE.execute(datastore, input_data)
        except Exception:
            datastore.rollback()
            raise
        datastore.commit()

        return cls.decode(result)

    @classmethod
    def create_with_request_data(
        cls: Type[T],
        data: Any,
        ip_address: IpAddress,
        datastore: Datastore,
        perspective: Perspective
    ) -> T:
        """Return a newly minted Session"""

        assert isinstance(ip_address, IpAddress)
        assert isinstance(perspective, Perspective)

        if not isinstance(data, dict):
            raise BadRequest('Expected a key/value object (dict)')

        try:
            provided_plaintext_secret = data['secret']
            provided_email = data['email']
        except KeyError as error:
            raise BadRequest('Missing key ')
            raise NozomiError('Missing key ' + str(error.args[0]), 400)

        return cls.create(
            provided_email=provided_email,
            provided_plaintext_secret=provided_plaintext_secret,
            ip_address=ip_address,
            datastore=datastore,
            perspective=perspective
        )

    @classmethod
    def retrieve(
        cls: Type[T],
        session_id: int,
        datastore: Datastore,
        configuration: Configuration
    ) -> Optional[T]:

        assert isinstance(session_id, int)
        arguments = {
            'session_id': session_id,
            'seconds_to_live': configuration.session_seconds_to_live
        }
        result = cls.Q_RETRIEVE.execute(datastore, arguments)
        datastore.commit()
        if result is None:
            return None
        return cls.decode(result)
