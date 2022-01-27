from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from sym.sdk.resource import SRN

from .template import Template


class ApprovalTemplateStep(str, Enum):
    """The :class:`~sym.sdk.templates.approval.ApprovalTemplateStep` enum lists
    the steps in the :class:`~sym.sdk.templates.approval.ApprovalTemplate`, each of which
    can be used in hooks to fire new :class:`~sym.sdk.events.Event`s.

    Read more about the `steps of the sym:approval template <https://docs.symops.com/docs/sym-approval#steps>`_.
    """

    PROMPT = "prompt"
    REQUEST = "request"
    APPROVE = "approve"
    DENY = "deny"
    ESCALATE = "escalate"
    DEESCALATE = "deescalate"


class ApprovalTemplate(Template, ABC):
    """The :class:`~sym.sdk.templates.approval.ApprovalTemplate` object represents
    a security workflow for access management supported out of the box by Sym.

    Read more about the `sym:approval <https://docs.symops.com/docs/sym-approval>`_
    :class:`~sym.sdk.templates.template.Template`.
    """

    @classmethod
    @abstractmethod
    def prompt(cls, **kwargs):
        """Generates a request to fire an :class:`~sym.sdk.event.Event` of type ``prompt`` to
        pop up a modal for the :class:`~sym.sdk.user.User` to make a request.

        Args:
            **kwargs: Arbitrary additional values to pass through to the fired :class:`~sym.sdk.event.Event`'s payload.
        """

    @classmethod
    @abstractmethod
    def request(cls, *, target_srn: SRN, duration: int, **kwargs):
        """Generates a request to fire an :class:`~sym.sdk.event.Event` of type ``request`` to
        submit a request for access to an :class:`~sym.sdk.target.AccessTarget`.

        Args:
            target_srn: The :class:`~sym.sdk.resource.SRN` of the :class:`~sym.sdk.target.AccessTarget` to request access to.
            duration: How long the escalation should last.
            **kwargs: Arbitrary additional values to pass through to the fired :class:`~sym.sdk.event.Event`'s payload.
        """

    @classmethod
    @abstractmethod
    def approve(cls, *, target_srn: Optional[SRN] = None, duration: Optional[int] = None, **kwargs):
        """Generates a request to fire an :class:`~sym.sdk.event.Event` of type ``approve`` to
        approve an outstanding request for access to an :class:`~sym.sdk.target.AccessTarget`.

        Args:
            target_srn: The :class:`~sym.sdk.resource.SRN` of the :class:`~sym.sdk.target.AccessTarget` to request access to.
                Required only if firing an :class:`~sym.sdk.event.Event` for a :class:`~sym.sdk.flow.Run` which has not had
                a request submitted. Otherwise, defaults to the current :class:`~sym.sdk.flow.Run`'s requested :class:`~sym.sdk.target.AccessTarget`.
            duration: How long the escalation should last.
                Required only if firing an :class:`~sym.sdk.event.Event` for a :class:`~sym.sdk.flow.Run` which has not had
                a request submitted. Otherwise, defaults to the current :class:`~sym.sdk.flow.Run`'s requested duration.
            **kwargs: Arbitrary additional values to pass through to the fired :class:`~sym.sdk.event.Event`'s payload.
        """

    @classmethod
    @abstractmethod
    def deny(cls, *, target_srn: Optional[SRN] = None, duration: Optional[int] = None, **kwargs):
        """Generates a request to fire an :class:`~sym.sdk.event.Event` of type ``deny`` to
        deny an outstanding request for access to an  :class:`~sym.sdk.target.AccessTarget`.

        Args:
            target_srn: The :class:`~sym.sdk.resource.SRN` of the :class:`~sym.sdk.target.AccessTarget` to request access to.
                Required only if firing an :class:`~sym.sdk.event.Event` for a :class:`~sym.sdk.flow.Run` which has not had
                a request submitted. Otherwise, defaults to the current :class:`~sym.sdk.flow.Run`'s requested :class:`~sym.sdk.target.AccessTarget`.
            duration: How long the escalation should last.
                Required only if firing an :class:`~sym.sdk.event.Event` for a :class:`~sym.sdk.flow.Run` which has not had
                a request submitted. Otherwise, defaults to the current :class:`~sym.sdk.flow.Run`'s requested duration.
            **kwargs: Arbitrary additional values to pass through to the fired :class:`~sym.sdk.event.Event`'s payload.
        """

    @classmethod
    @abstractmethod
    def escalate(
        cls, *, target_srn: Optional[SRN] = None, duration: Optional[int] = None, **kwargs
    ):
        """Generates a request to fire an :class:`~sym.sdk.event.Event` of type ``escalate`` to
        begin escalation of a :class:`~sym.sdk.user.User` for an :class:`~sym.sdk.target.AccessTarget`.

        Args:
            target_srn: The :class:`~sym.sdk.resource.SRN` of the :class:`~sym.sdk.target.AccessTarget` to escalate the :class:`~sym.sdk.user.User` for.
                Required only if firing an :class:`~sym.sdk.event.Event` for a :class:`~sym.sdk.flow.Run` which has not had
                a request submitted. Otherwise, defaults to the current :class:`~sym.sdk.flow.Run`'s requested :class:`~sym.sdk.target.AccessTarget`.
            duration: How long the escalation should last.
                Required only if firing an :class:`~sym.sdk.event.Event` for a :class:`~sym.sdk.flow.Run` which has not had
                a request submitted. Otherwise, defaults to the current :class:`~sym.sdk.flow.Run`'s requested duration.
            **kwargs: Arbitrary additional values to pass through to the fired :class:`~sym.sdk.event.Event`'s payload.
        """

    @classmethod
    @abstractmethod
    def deescalate(cls, *, target_srn: Optional[SRN] = None, **kwargs):
        """Generates a request to fire an :class:`~sym.sdk.event.Event` of type ``deescalate`` to
        begin deescalation of a :class:`~sym.sdk.user.User` for an :class:`~sym.sdk.target.AccessTarget`.

        Args:
            target_srn: The :class:`~sym.sdk.resource.SRN` of the :class:`~sym.sdk.target.AccessTarget` to deescalate the :class:`~sym.sdk.user.User` for.
                Required only if firing an :class:`~sym.sdk.event.Event` for a :class:`~sym.sdk.flow.Run` which has not had
                a request submitted. Otherwise, defaults to the current :class:`~sym.sdk.flow.Run`'s requested :class:`~sym.sdk.target.AccessTarget`.
            **kwargs: Arbitrary additional values to pass through to the fired :class:`~sym.sdk.event.Event`'s payload.
        """
