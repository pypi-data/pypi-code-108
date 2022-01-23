"""
Nozomi
Read Protected Protocol
Copyright Amatino Pty Ltd
"""
from nozomi.security.agent import Agent
from nozomi.errors.not_authorised import NotAuthorised


class ReadProtected:
    """
    Abstract Protocol defining an interface for objects to whom read access
    is limited
    """

    def grants_read_to(self, agent: Agent) -> bool:
        """Return True if an Agent may read this object"""
        raise NotImplementedError

    def assert_read_available_to(self, agent: Agent) -> None:
        """Throw a NotAuthorised error if read unavailable"""
        if not self.grants_read_to(agent):
            raise NotAuthorised
        return
