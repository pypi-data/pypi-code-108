def get(hub, wait_in_seconds: int = None, **kwargs):
    # return the static wait time in seconds
    #
    # Define in state:
    # __reconcile_wait__ = {"static": {"wait_in_seconds": 10}}

    if wait_in_seconds is None or wait_in_seconds <= 0:
        raise ValueError("Expecting a single numerical value: wait time in seconds.")
    return wait_in_seconds
