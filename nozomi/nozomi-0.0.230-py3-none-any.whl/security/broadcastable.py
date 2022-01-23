"""
Nozomi
Broadcastable Protocol Module
author: hugh@blinkybeach.com
"""
from nozomi.security.agent import Agent
from nozomi.data.encodable import Encodable
from typing import Any, List, Type, TypeVar, Optional
from nozomi.security.privilege import Privilege
from nozomi.security.read_protected import ReadProtected

T = TypeVar('T', bound='Broadcastable')


class Broadcastable(ReadProtected):
    """
    Abstract class defining an interface for concrete classes who may be asked
    to provide a broadcastable representation of themselves. For example,
    an object may contain internal fields that should not be visible outside
    a network. A broadcastable representation of the object would
    strip those fields and return an Encodable version of its data, suitable
    for return to an application.
    """

    def broadcast_to(
        self,
        agent: Agent,
        max_privilege_level: Optional[Privilege] = None
    ) -> Encodable:
        """
        Return an encodable form of this object suitable for broadcast
        to the supplied Agent. Optionally specify the maximum privilege
        level that should be allowed.
        """
        raise NotImplementedError

    @classmethod
    def broadcast_many_to(
        cls: Type[T],
        objects: List[T],
        agent: Agent
    ) -> List[Encodable]:
        """Return a list of encodable forms suitable for broadcast"""
        return [o.broadcast_to(agent) for o in objects]

    class Broadcast(Encodable):
        def __init__(self, encoded_data: Any) -> None:
            self._data = encoded_data
            return

        def encode(self) -> Any:
            return self._data
