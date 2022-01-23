"""
Nozomi
Secure Resource Module
author: hugh@blinkybeach.com
"""
from typing import Union, List
from nozomi.errors.not_authorised import NotAuthorised
from nozomi.data.datastore import Datastore
from nozomi.security.broadcastable import Broadcastable
from nozomi.security.agent import Agent
from nozomi.resources.resource import Resource
from nozomi.http.query_string import QueryString
from nozomi.http.headers import Headers
from nozomi.security.perspective import Perspective
from nozomi.security.forwarded_agent import ForwardedAgent
from nozomi.data.encodable import Encodable
from typing import Optional, Tuple, Set, Type
from nozomi.security.abstract_session import AbstractSession
from nozomi.ancillary.configuration import Configuration
from nozomi.http.parseable_data import ParseableData


class SecureResource(Resource):
    """
    Abstract class defining an interface for API requests that require
    authentication. Authorisation should be performed in the implementing
    subclass. To authorise a request, call SecureResource.authorise() in the
    subclass compute_response() method.

    Optionally supply an InternalKey to authorise internal requests. The
    underlying retreived resource will need to allow broadcast to the
    Machine Agent.
    """

    path: str = NotImplemented
    session_implementation: Type[AbstractSession] = NotImplemented
    requests_may_change_state: bool = NotImplemented
    allowed_perspectives: Optional[Set[Perspective]] = NotImplemented
    allows_unconfirmed_agents: bool = NotImplemented
    forwarded_agent_implementation: Type[ForwardedAgent] = ForwardedAgent

    def __init__(
        self,
        datastore: Datastore,
        configuration: Configuration
    ) -> None:

        super().__init__(
            datastore=datastore,
            configuration=configuration
        )
        if (
            self.allowed_perspectives is not None
            and not isinstance(self.allowed_perspectives, set)
        ):
            raise NotImplementedError('Implement .allowed_perspectives')

        assert isinstance(self.session_implementation, type)
        assert isinstance(self.requests_may_change_state, bool)
        return

    def compute_response(
        self,
        body: Optional[ParseableData],
        query: Optional[QueryString],
        unauthorised_agent: Agent,
    ) -> Tuple[Union[Broadcastable, List[Broadcastable]], Agent]:
        # Method returning an encodable response, and an Agent authorised to
        # make the request.
        raise NotImplementedError

    def serve(
        self,
        body: Optional[ParseableData],
        query: Optional[QueryString],
        headers: Headers,
        session: AbstractSession = None
    ) -> str:

        SessionImplementation = self.session_implementation
        ForwardedAgentImplementation = self.forwarded_agent_implementation

        if session is None:
            session = SessionImplementation.from_headers(
                headers=headers,
                datastore=self.datastore,
                path=self.path,
                request_may_change_state=self.requests_may_change_state
            )
        if session is not None:
            if (
                    self.allowed_perspectives is not None
                    and session.perspective not in self.allowed_perspectives
            ):
                raise NotAuthorised

        if session is None and self.configuration.internal_psk is None:
            raise NotAuthorised

        if session is None:
            unauthorised_agent = ForwardedAgentImplementation.from_headers(
                internal_key=self.configuration.internal_psk,
                headers=headers,
                datastore=self.datastore,
                configuration=self.configuration
            )
        else:
            unauthorised_agent = session.agent

        if (
                session is not None
                and session.agent_requires_confirmation
                and not session.agent_confirmed
                and not self.allows_unconfirmed_agents
        ):
            raise NotAuthorised

        response, authorised_agent = self.compute_response(
            body=body,
            query=query,
            unauthorised_agent=unauthorised_agent,
        )

        if not isinstance(authorised_agent, Agent):
            raise NotAuthorised

        if session is not None:
            if authorised_agent != session.agent:
                raise NotAuthorised
            assert authorised_agent == session.agent

        self.assert_read_available_to(
            unauthorised_agent=authorised_agent,
            broadcast_candidate=response
        )

        if isinstance(response, list):
            return Encodable.serialise_many(
                Broadcastable.broadcast_many_to(response, authorised_agent)
            )

        return response.broadcast_to(authorised_agent).serialise()
