"""A parameterized instance of a :class:`~sym.sdk.templates.template.Template`."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from sym.sdk.resource import SymResource
from sym.sdk.user import User


class Flow(SymResource, ABC):
    """The :class:`~sym.sdk.flow.Flow` class contains a particular parameterization
    of a :class:`~sym.sdk.templates.template.Template`.

    Read more about `Flows <https://docs.symops.com/docs/tf-flow>`_.
    """

    @property
    @abstractmethod
    def fields(self) -> Dict[str, Any]:
        """A dictionary with the field structure defined for the :class:`~sym.sdk.flow.Flow`
        in Terraform.
        """

    @property
    @abstractmethod
    def vars(self) -> Dict[str, str]:
        """A dict containing user-supplied values from the :class:`~sym.sdk.flow.Flow`'s definition in Terraform.

        This dict might contain, for example, your team's PagerDuty schedule ID.
        """


class Run(SymResource, ABC):
    """A :class:`~sym.sdk.flow.Run` represents an instance of a :class:`~sym.sdk.flow.Flow`
    in progress.

    For example, each new access request using the `sym:template:approval:1.0`
    :class:`~sym.sdk.templates.template.Template` would generate a new :class:`~sym.sdk.flow.Run`
    with data pertaining to that specific access request.
    """

    @property
    @abstractmethod
    def actors(self) -> Dict[str, User]:
        """A dict mapping :class:`~sym.sdk.events.Event` names to the :class:`~sym.sdk.user.User`
        that created each :class:`~sym.sdk.events.Event`. There will be one entry for each
        :class:`~sym.sdk.events.Event` in the current :class:`~sym.sdk.flow.Run`.

        For example, with a sym:approval :class:`~sym.sdk.flow.Flow`, after the "approve"
        :class:`~sym.sdk.events.Event` is received, the actors may look like this::

            {
                "prompt": <User A>,
                "request": <User A>,
                "approve": <User B>
            }
        """
