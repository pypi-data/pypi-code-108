from typing import NamedTuple, Callable

from unipipeline.brokers.uni_broker_message_manager import UniBrokerMessageManager
from unipipeline.message_meta.uni_message_meta import UniMessageMeta


class UniBrokerConsumer(NamedTuple):
    topic: str
    id: str
    group_id: str
    unwrapped: bool
    prefetch_count: int
    message_handler: Callable[[UniMessageMeta, UniBrokerMessageManager], None]
