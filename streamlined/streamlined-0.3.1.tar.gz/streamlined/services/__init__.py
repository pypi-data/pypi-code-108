"""
Services folder is like a toolbox providing necessary tools for different purposes.

These services should be plug and use, decoupled from anything else.
"""

from .dependency_injection import DependencyInjection
from .dependency_tracking import DependencyTracking
from .event_notification import EventNotification
from .reaction import (
    Reaction,
    after,
    before,
    bind_named_reaction,
    bind_reaction,
    raises,
)
from .reference import NameRef, ValueRef
from .scoping import Scoped, Scoping, to_magic_naming
from .service import Service
