"""Module msgs.

====
Msgs
====

The Msgs class is intended to be used during testing to send and receive
messages between threads.

:Example: send a message to remote thread

>>> import threading
>>> from scottbrian_utils.msgs import Msgs
>>> def f1(msgs) -> None:
...     print('f1 beta entered')
...     my_msg = msgs.get_msg('beta')
...     print(my_msg)
...     print('f1 beta exiting')
>>> def example1() -> None:
...     print('mainline entered')
...     msgs = Msgs()
...     f1_thread = threading.Thread(target=f1, args=(msgs,))
...     f1_thread.start()
...     msgs.queue_msg('beta', 'hello beta')
...     f1_thread.join()
...     print('mainline exiting')
>>> example1()
mainline entered
f1 beta entered
hello beta
f1 beta exiting
mainline exiting


:Example: a command loop using Msgs

>>> import threading
>>> from scottbrian_utils.msgs import Msgs
>>> import time
>>> def main() -> None:
...     def f1() -> None:
...         print('f1 beta entered')
...         while True:
...             my_msg = msgs.get_msg('beta')
...             print(f'beta received msg: {my_msg}')
...             if my_msg == 'exit':
...                 break
...             else:
...                 # handle message
...                 msgs.queue_msg('alpha', f'msg "{my_msg}" completed')
...         print('f1 beta exiting')
...     print('mainline entered')
...     msgs = Msgs()
...     f1_thread = threading.Thread(target=f1)
...     f1_thread.start()
...     msgs.queue_msg('beta', 'do command a')
...     print(f"alpha received response: {msgs.get_msg('alpha')}")
...     msgs.queue_msg('beta', 'do command b')
...     print(f"alpha received response: {msgs.get_msg('alpha')}")
...     msgs.queue_msg('beta', 'exit')
...     f1_thread.join()
...     print('mainline exiting')
>>> main()
mainline entered
f1 beta entered
beta received msg: do command a
alpha received response: msg "do command a" completed
beta received msg: do command b
alpha received response: msg "do command b" completed
beta received msg: exit
f1 beta exiting
mainline exiting


The msgs module contains:

    1) Msgs class with methods:

       a. get_msg
       b. queue_msg

"""

########################################################################
# Standard Library
########################################################################
import logging
import queue
import threading
from typing import Any, Final, Optional, Union

########################################################################
# Third Party
########################################################################
from scottbrian_utils.diag_msg import get_formatted_call_sequence
from scottbrian_utils.timer import Timer

########################################################################
# Local
########################################################################

########################################################################
# type aliases
########################################################################
IntFloat = Union[int, float]
OptIntFloat = Optional[IntFloat]


########################################################################
# Msg Exceptions classes
########################################################################
class MsgsError(Exception):
    """Base class for exception in this module."""
    pass


class GetMsgTimedOut(MsgsError):
    """Msgs get_msg timed out waiting for msg."""
    pass


########################################################################
# Msgs Class
########################################################################
class Msgs:
    """Msgs class for testing.

    The Msgs class is used to assist in the testing of multi-threaded
    functions. It provides a set of methods that help with test case
    coordination and verification. The test case setup
    involves a mainline thread that starts one or more remote threads.
    The queue_msg and get_msg methods are used for inter-thread
    communications.

    """
    GET_CMD_TIMEOUT: Final[float] = 3.0
    CMD_Q_MAX_SIZE: Final[int] = 10

    ####################################################################
    # __init__
    ####################################################################
    def __init__(self) -> None:
        """Initialize the object."""
        self.msg_array: dict[str, Any] = {}
        self.msg_lock: threading.Lock = threading.Lock()

        # add a logger
        self.logger = logging.getLogger(__name__)

    ####################################################################
    # queue_msg
    ####################################################################
    def queue_msg(self, target: str, msg: Optional[Any] = 'go') -> None:
        """Place a msg on the msg queue for the specified target.

        Args:
            target: arbitrary name that designates the target of the
                   message and which will be used with the get_msg
                   method to retrieve the message
            msg: message to place on queue

        """
        with self.msg_lock:
            if target not in self.msg_array:
                self.msg_array[target] = queue.Queue(
                    maxsize=Msgs.CMD_Q_MAX_SIZE)

        self.msg_array[target].put(msg,
                                   block=True,
                                   timeout=0.5)

    ####################################################################
    # get_msg
    ####################################################################
    def get_msg(self,
                recipient: str,
                timeout: OptIntFloat = GET_CMD_TIMEOUT) -> Any:
        """Get the next message in the queue.

        Args:
            recipient: arbitrary name that designates the target of the
                   message and which will be used with the queue_msg
                   method to identify the intended recipient of the
                   message
            timeout: number of seconds allowed for msg response. A
                       negative value, zero, or None means no timeout
                       will happen. If timeout is not specified, then
                       the default timeout value will be used.

        Returns:
            the received message

        Raises:
            GetMsgTimedOut: {recipient} timed out waiting for msg

        """
        # get a timer (the clock is started when instantiated)
        timer = Timer(timeout=timeout)

        # shared/excl lock here could improve performance
        with self.msg_lock:
            if recipient not in self.msg_array:
                # we need to add the message target if this is the first
                # time the recipient is calling get_msg
                self.msg_array[recipient] = queue.Queue(
                    maxsize=Msgs.CMD_Q_MAX_SIZE)

        while True:
            try:
                msg = self.msg_array[recipient].get(block=True, timeout=0.1)
                return msg
            except queue.Empty:
                pass

            if timer.is_expired():
                caller_info = get_formatted_call_sequence(latest=1, depth=1)
                err_msg = (f'Thread {threading.current_thread()} '
                           f'timed out on get_msg for recipient: {recipient} '
                           f'{caller_info}')
                self.logger.debug(err_msg)
                raise GetMsgTimedOut(err_msg)
