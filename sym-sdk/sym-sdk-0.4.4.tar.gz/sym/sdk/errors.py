"""Common errors that can be thrown."""
from enum import Enum
from typing import Dict, Optional


class SymSDKError(Exception):
    """The base exception class used by Sym's SDK."""

    # To ensure all user-facing errors are informative and actionable,
    # all SymSDKErrors are required to have an error message, a hint as to
    # the next step a user should take, and a relevant link to Sym documentation.
    def __init__(self, message: str, hint: str, doc_url: str, **kwargs):
        super().__init__(message, **kwargs)
        self.message = message
        self.hint = hint
        self.doc_url = doc_url

    def __str__(self):
        return f"{self.message}\n\nHint: {self.hint}\n\nFor more details, see: {self.doc_url}."

    def format_slack(self) -> str:
        """Returns a string representation of this error formatted for display
        in Slack-compatible markdown.
        """
        return f"*{self.message}*\n\n*Hint:* {self.hint}\n\nFor more details, see: {self.doc_url}."


class SymIntegrationError(SymSDKError):
    """Raised when there is an error in an Integration.

    Each exception includes an error code that you can use to reach out to support.
    """

    default_message = "An error occurred."
    default_hint = "Please contact support."
    default_docs_url = "https://docs.symops.com/docs/support"

    def __init__(
        self,
        message: str = "",
        hint: Optional[str] = None,
        doc_url: Optional[str] = None,
        *,
        error_code: Optional[Enum] = None,
        params: Optional[dict] = None,
    ):
        """
        Args:
            error_code: A valid Sym error code
            hint: A helpful suggestion to the User
            params: A dict of relevant values
        """
        self.error_code = error_code
        self.params = params

        super().__init__(
            message=message or self.default_message,
            hint=hint or self.default_hint,
            doc_url=doc_url or self.default_docs_url,
        )

    def _format(self, s: str) -> str:
        try:
            return s.format_map(self.params or {})
        except (KeyError, AttributeError):
            return s

    def format_slack(self) -> str:
        return self._format(super().format_slack())

    def __str__(self):
        return self._format(super().__str__())

    def __repr__(self):
        return self._format(super().__repr__())


class SymIntegrationErrorEnum(SymIntegrationError, Enum):
    """A helper class which allows error codes to be defined as Enum members."""

    def __new__(cls, *args):
        obj = SymIntegrationError.__new__(cls, *args)
        obj._value_ = args
        return obj

    def __call__(self, params: Optional[Dict] = None, **kwargs):
        self.error_code = f"{self.__class__.__name__}:{self.name}"
        self.params = {**(params or {}), **kwargs}
        return self
