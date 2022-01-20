from halo import Halo
import time
import math
from typing import List, Callable, TypeVar, Optional
from continual.python.sdk.exceptions import FailedError

RESTING_STATES = set(["ONLINE", "OFFLINE", "CANCELLED", "FAILED", "SUCCEEDED"])
FAILED_STATES = set(["FAILED"])

"""Common resting states."""

T = TypeVar("T")


def wait(
    getter: Callable[[], T],
    states: Optional[List[str]] = None,
    echo: bool = False,
    timeout: Optional[int] = None,
) -> T:
    """Wait for state transition.

    Arguments:
        getter: Get resource callable.
        states: Resting state.
        echo: Show progress bar.
        timeout: Maximum time to wait.
    Returns:
        A resource.
    """

    if states is None:
        states = RESTING_STATES
    if timeout is None:
        timeout = math.inf

    spinner = Halo(text="Loading", spinner="dots")
    total_time = 0
    spinner.start()

    while True:
        time.sleep(5)
        resource = getter()
        state = str(resource.state)
        spinner.text = state
        total_time += 5
        if total_time > timeout:
            raise TimeoutError(f"Timeout occured after {total_time} seconds.")
        if state in states:
            break

    if state in ["OFFLINE", "ONLINE", "SUCCEEED"]:
        spinner.succeed()
    elif state in ["CANCELLED", "FAILED"]:
        spinner.fail()
    elif total_time > timeout:
        spinner.text = "TIMEOUT"
        spinner.fail()
    else:
        spinner.stop()
    if state in FAILED_STATES:
        raise FailedError(
            f"{resource.__class__.__name__} transitioned to FAILED state.",
            details=dict(name=resource.name),
        )
    return resource
