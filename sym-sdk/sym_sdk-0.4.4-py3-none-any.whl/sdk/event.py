"""Triggers for the various steps of a :class:`~sym.sdk.events.Flow`."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict

from sym.sdk.flow import Flow, Run
from sym.sdk.resource import SRN, SymResource
from sym.sdk.templates import Template
from sym.sdk.user import User


class Payload(SymResource):
    """The :class:`~sym.sdk.events.Payload` object contains the data of the
    :class:`~sym.sdk.events.Event`.
    """

    @property
    @abstractmethod
    def timestamp(self) -> datetime:
        """A datetime object indicating when the :class:`~sym.sdk.events.Event` was created."""

    @property
    @abstractmethod
    def fields(self) -> Dict[str, Any]:
        """A dict containing the values submitted by the user who created
        the :class:`~sym.sdk.events.Event`
        """

    @property
    @abstractmethod
    def srn(self) -> SRN:
        """The :class:`~sym.sdk.resource.SRN` of the :class:`~sym.sdk.events.Event` instance."""

    @property
    @abstractmethod
    def user(self) -> User:
        """The :class:`~sym.sdk.user.User` who triggered the :class:`~sym.sdk.events.Event`."""


class EventMeta(SymResource, ABC):
    """Contains metadata about an :class:`~sym.sdk.events.Event` instance."""


class Event(SymResource, ABC):
    """The :class:`~sym.sdk.events.Event` class contains information on an event which has been
    received by Sym, routed to a :class:`~sym.sdk.flow.Run` of a :class:`~sym.sdk.flow.Flow`, and is
    triggering specific user-defined Handlers.

    Each Handler will be invoked with a single argument, which is an instance of this class.
    This :class:`~sym.sdk.events.Event` instance will describe the current execution state,
    and can be used to dynamically alter the behavior and control flow of
    Templates.

    Read more about `Handlers <https://docs.symops.com/docs/handlers>`_.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the :class:`~sym.sdk.events.Event`."""

    @property
    @abstractmethod
    def payload(self) -> Payload:
        """A :class:`~sym.sdk.events.Payload` object, which contains the primary data
        of the :class:`~sym.sdk.events.Event`.
        """

    @property
    @abstractmethod
    def meta(self) -> EventMeta:
        """An :class:`~sym.sdk.events.EventMeta` object, which contains metadata
        about the :class:`~sym.sdk.events.Event` instance.
        """

    @property
    @abstractmethod
    def template(self) -> Template:
        """A :class:`~sym.sdk.templates.template.Template` object, indicating which
        :class:`~sym.sdk.templates.template.Template` the current :class:`~sym.sdk.flow.Flow` inherits from.
        """

    @property
    @abstractmethod
    def flow(self) -> Flow:
        """A :class:`~sym.sdk.flow.Flow` object, indicating the :class:`~sym.sdk.flow.Flow` that
        the current :class:`~sym.sdk.flow.Run` is an instance of.
        """

    @property
    @abstractmethod
    def run(self) -> Run:
        """A :class:`~sym.sdk.flow.Run` object, indicating the current
        :class:`~sym.sdk.flow.Run`."""

    @property
    def user(self) -> User:
        """The :class:`~sym.sdk.user.User` who triggered the :class:`~sym.sdk.events.Event`."""
        return self.payload.user
