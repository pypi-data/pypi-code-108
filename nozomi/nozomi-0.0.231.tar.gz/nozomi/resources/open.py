"""
Nozomi
Secure Resource Module
author: hugh@blinkybeach.com
"""
from nozomi.security.agent import Agent
from nozomi.resources.resource import Resource
from nozomi.http.query_string import QueryString
from nozomi.http.parseable_data import ParseableData
from nozomi.http.headers import Headers
from nozomi.data.encodable import Encodable
from typing import Optional, List, Union, Type
from nozomi.security.abstract_session import AbstractSession
from nozomi.data.datastore import Datastore
from nozomi.ancillary.configuration import Configuration
from nozomi.security.forwarded_agent import ForwardedAgent
from nozomi.errors.not_authorised import NotAuthorised


class OpenResource(Resource):
    """
    Abstract class defining an interface for for resources that do not require
    authentication, but that are aware of a requesting agent. For example, a
    an API path that may be served differently depending on whether a user is
    logged in or not.
    """

    session_implementation: Type[AbstractSession] = NotImplemented
    requests_may_change_state: bool = NotImplemented
    allows_unconfirmed_agents: bool = NotImplemented
    forwarded_agent_implementation: Type[ForwardedAgent] = ForwardedAgent

    def __init__(
        self,
        datastore: Datastore,
        configuration: Configuration
    ) -> None:
        assert isinstance(datastore, Datastore)
        super().__init__(
            datastore=datastore,
            configuration=configuration
        )
        assert isinstance(self.session_implementation, type)
        assert isinstance(self.requests_may_change_state, bool)
        return

    def compute_response(
        self,
        body: Optional[ParseableData],
        query: Optional[QueryString],
        unauthorised_agent: Optional[Agent]
    ) -> Union[Encodable, List[Encodable]]:
        """
        Method returning an Encodable response
        """
        raise NotImplementedError

    def serve(
        self,
        body: Optional[ParseableData],
        query: Optional[QueryString],
        headers: Headers
    ) -> str:

        SessionImplementation = self.session_implementation
        ForwardedAgentClass = self.forwarded_agent_implementation

        requesting_agent: Optional[Agent] = None

        requesting_agent = SessionImplementation.from_headers(
            headers=headers,
            datastore=self.datastore,
            path=self.path,
            request_may_change_state=self.requests_may_change_state
        )

        session = requesting_agent

        if (
                session is not None
                and session.agent_requires_confirmation
                and not session.agent_confirmed
                and not self.allows_unconfirmed_agents
        ):
            raise NotAuthorised

        if requesting_agent is None:
            requesting_agent = ForwardedAgentClass.optionally_from_headers(
                internal_key=self.configuration.internal_psk,
                headers=headers,
                datastore=self.datastore,
                configuration=self.configuration
            )

        response = self.compute_response(
            body=body,
            query=query,
            unauthorised_agent=requesting_agent
        )

        if isinstance(response, list):
            return Encodable.serialise_many(response)

        return response.serialise()
