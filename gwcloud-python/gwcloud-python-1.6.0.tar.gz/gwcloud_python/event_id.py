from dataclasses import dataclass


@dataclass
class EventID:
    """Object used to help with abstraction of Event IDs. Currently a glorified dictionary."""
    event_id: str
    trigger_id: str = None
    nickname: str = None
    is_ligo_event: bool = False
