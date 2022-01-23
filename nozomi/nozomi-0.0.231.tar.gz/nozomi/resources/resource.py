"""
Nozomi
Resource Module
Copyright Amatino Pty Ltd
"""
from nozomi.http.query_string import QueryString
from nozomi.http.parseable_data import ParseableData
from nozomi.http.headers import Headers
from nozomi.data.datastore import Datastore
from nozomi.ancillary.immutable import Immutable
from nozomi.data.encodable import Encodable
from nozomi.ancillary.configuration import Configuration
from typing import Any, Optional, Union, List, Dict
from nozomi.security.read_protected import ReadProtected
from nozomi.security.agent import Agent
from nozomi.errors.not_authorised import NotAuthorised
from nozomi.security.broadcastable import Broadcastable


class Resource:
    """Abstract class defining machinery for responding to an API request"""

    def __init__(
        self,
        datastore: Datastore,
        configuration: Configuration
    ) -> None:
        assert isinstance(datastore, Datastore)
        self._datastore = datastore
        self._debug = configuration.debug
        self._configuration = configuration
        return

    datastore = Immutable(lambda s: s._datastore)
    debug = Immutable(lambda s: s._debug)
    configuration = Immutable(lambda s: s._configuration)

    def compute_response(
        self,
        body: Optional[Any],
        query: Optional[QueryString],
        headers: Headers = None
    ) -> Encodable:
        """Return serialisable response data"""
        raise NotImplementedError

    def serve(
        self,
        body: Optional[ParseableData],
        query: Optional[QueryString] = None,
        headers: Headers = None
    ) -> str:
        """Return a string response body to a request"""
        return self.compute_response(
            body=body,
            query=query,
            headers=headers
        ).serialise()

    def assert_read_available_to(
        self,
        unauthorised_agent: Agent,
        broadcast_candidate: Union[ReadProtected, List[ReadProtected]]
    ) -> Agent:
        """
        Raise a NotAuthorised error if this Agent may not read the candidate
        """
        if isinstance(broadcast_candidate, list):
            for candidate in broadcast_candidate:
                if not candidate.grants_read_to(unauthorised_agent):
                    raise NotAuthorised
                continue
            return unauthorised_agent

        if not broadcast_candidate.grants_read_to(unauthorised_agent):
            raise NotAuthorised
        return unauthorised_agent

    class AcknowledgementBroadcast(Broadcastable, Encodable):
        """
        Canned Broadcastable response useful in cases where an acknolwedgement
        response is desired but a broadcast of a protect object is not.
        """
        _DATA = {'result': 'ok'}

        def grants_read_to(self, agent: Agent) -> bool:
            return True

        def broadcast_to(self, _) -> Encodable:
            return self

        def encode(self) -> Dict[str, str]:
            return self._DATA
