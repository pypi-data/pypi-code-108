"""
Nozomi
RequestCredentials Module
author: hugh@blinkybeach.com
"""
from nozomi.http.headers import Headers
from nozomi.security.abstract_session import AbstractSession
from nozomi.ancillary.configuration import Configuration
from typing import TypeVar, Type, Optional
from nozomi.security.agent import Agent

T = TypeVar('T', bound='RequestCredentials')


class RequestCredentials(Headers):

    def __init__(
        self,
        on_behalf_of_agent: bool,
        headers: Headers
    ) -> None:

        self._on_behalf_of = on_behalf_of_agent
        super().__init__(headers)
        return

    @classmethod
    def from_session(
        cls: Type[T],
        session: AbstractSession,
        configuration: Configuration
    ) -> T:

        headers = {
            configuration.session_id_name: session.session_id,
            configuration.session_api_key_name: session.api_key
        }

        return cls(False, headers)

    @classmethod
    def on_behalf_of_agent(
        cls: Type[T],
        agent: Agent,
        configuration: Configuration
    ) -> T:

        headers = {
            configuration.internal_psk_header: configuration.internal_psk,
            configuration.forwarded_agent_header: agent.agent_id
        }

        return cls(True, headers)

    @classmethod
    def optionally_on_behalf_of_agent(
        cls: Type[T],
        agent: Optional[Agent],
        configuration: Configuration
    ) -> T:

        if agent is None:
            return None

        return cls.on_behalf_of_agent(agent, configuration)
