def get(
    hub,
    wait_in_seconds: int = None,
    multiplier: int = None,
    run_count: int = 0,
    **kwargs,
):
    # return wait time in seconds
    # run_count is an optional argument and is the number of retries already occurred
    # wait time is calculated as wait_in_seconds * (multiplier ^ run_count)
    # For example: wait_in_seconds = 2, multiplier 10,
    # exponential wait times are: 2, 20, 200...
    #
    # Define in the state:
    # __reconcile_wait__ = { "exponential": {"wait_in_seconds": 2, "multiplier": 10}}

    if (
        wait_in_seconds is None
        or multiplier is None
        or wait_in_seconds == 0
        or multiplier == 0
    ):
        raise ValueError(
            "Expecting wait_in_seconds and multiplier to be specified for exponential backoff."
        )

    val = wait_in_seconds
    if run_count:
        val = val * (multiplier ** run_count)

    hub.log.debug(f"Exponential value: {val}")
    return val
