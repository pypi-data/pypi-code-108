import random


def get(hub, min_value: int = None, max_value: int = None, **kwargs):
    # return wait time in seconds which is a random number
    # between min and max (inclusive) values
    #
    # Define in state:
    # __reconcile_wait__ = {"random": {"min_value": 1, "max_value": 10}}

    if min_value is None or max_value is None or min_value >= max_value:
        raise ValueError(
            "Expecting min and max values for the randomly generated wait time in seconds. "
            "For example: min_value=1, max_value=10."
        )

    val = random.randint(min_value, max_value)
    hub.log.debug(f"Random wait time (seconds) between {min_value}-{max_value}: {val}")
    return val
