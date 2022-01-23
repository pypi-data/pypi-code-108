import traceback
import uuid
from types import TracebackType
from typing import List, Type


class Alarm:
    """ Stores all information about a thrown exception. """

    def __init__(
        self,
        exc_type: Type[BaseException],
        exc: BaseException,
        exc_traceback: TracebackType
    ) -> None:
        """
        Create new Alarm

        Args:
            exc_type (:obj:`Type[BaseException]`): type of exception, that was thrown.
            exc (:obj:`BaseException`): exception instance, that was thrown.
            exc_traceback(:obj:`TracebackType`): traceback, that led to the exception.
        """

        # store information about the exception
        self.exc_type = exc_type
        self.exc = exc
        self.exc_traceback = exc_traceback

        # generate unique error code for alert
        self.error_code = str(uuid.uuid1())[0:8]

    def get_exc_name(self) -> str:
        """ returns the exceptions class name """
        return (
            self.exc['error_class']
            if isinstance(self.exc, dict)
            else self.exc.__class__.__name__
        )

    def get_exc_message(self) -> str:
        """ returns the exceptions message """
        return (
            self.exc['error_message']
            if isinstance(self.exc, dict)
            else str(self.exc)
        )

    def get_formatted_traceback_string(self) -> str:
        """ returns a formatted string version of the exceptions traceback """

        # format traceback to string -> ftb
        ftb = ''.join(traceback.format_tb(self.exc_traceback))

        # return printable traceback
        return (
            'Traceback (most recent call last):\n'
            f'{ftb}'
            f'{self.get_exc_name()}: {self.get_exc_message()}'
        )

    def get_traceback_list(self) -> List[str]:
        """returns traceback in form of a list of strings."""

        return traceback.format_tb(self.exc_traceback)
