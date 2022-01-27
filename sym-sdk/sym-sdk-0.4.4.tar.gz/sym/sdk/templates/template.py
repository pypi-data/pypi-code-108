from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from sym.sdk.resource import SymResource


class TemplateStep(str, Enum):
    """The :class:`~sym.sdk.templates.template.TemplateStep` class represents general steps which may
    be part of any :class:`~sym.sdk.templates.template.Template`.
    """

    IGNORE = "ignore"
    """Fire an :class:`~sym.sdk.event.Event` of type ``ignore`` to ullify the incoming
    :class:`~sym.sdk.event.Event` and send a message to the acting :class:`~sym.sdk.user.User`
    """


class Template(SymResource, ABC):
    """The :class:`~sym.sdk.templates.template.Template` object represents a
    common security workflow supported out of the box by Sym.

    Read more about `Templates <https://docs.symops.com/docs/available-templates>`_.
    """

    @classmethod
    @abstractmethod
    def ignore(cls, *, message: Optional[str] = None, **kwargs):
        """Generates a request to fire an :class:`~sym.sdk.event.Event` of type ``ignore`` to
        nullify the incoming :class:`~sym.sdk.event.Event` and send a message to the acting :class:`~sym.sdk.user.User`.

        Args:
            message: The message to send to the :class:`~sym.sdk.user.User` who triggered the original :class:`~sym.sdk.event.Event`.
            **kwargs: Arbitrary additional values to pass through to the fired :class:`~sym.sdk.event.Event`'s payload.
        """
