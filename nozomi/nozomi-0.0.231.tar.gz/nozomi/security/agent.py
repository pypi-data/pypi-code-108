"""
Nozomi
Broadcastable Module
Copyright Amatino Pty Ltd
"""
from nozomi.data.query_string_conforming import QueryStringConforming
from nozomi.data.sql_conforming import SQLConforming
from nozomi.ancillary.immutable import Immutable
from typing import Union


class Agent(SQLConforming, QueryStringConforming):
    """
    Astract protocol defining an interface for classes who may be granted
    access to read or write objects.
    """
    agent_id: Union[str, int] = NotImplemented

    sql_representation = Immutable(lambda s: s.adapt_integer(s.agent_id))
    query_string_value = Immutable(lambda s: str(s.agent_id))

    def __eq__(self, other) -> bool:
        if not isinstance(other.agent_id, int):
            return False
        if not isinstance(self.agent_id, int):
            return False
        if not isinstance(other, Agent):
            return False
        return other.agent_id == self.agent_id
