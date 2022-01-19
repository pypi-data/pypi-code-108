from enum import Enum


class Constants:
    """Constants"""

    PYVMP_RECEIVED_FULL_DATA = "PYVMP_RECEIVED_FULL_DATA"
    PYVMP_UNWRAPPED_BYTES = "PYVMP_UNWRAPPED_BYTES"
    PYVMP_PREDICT_DONE = "PYVMP_PREDICT_DONE"
    PYVMP_WRAPPED_DICT = "PYVMP_WRAPPED_DICT"
    PYVMP_SEND_RES_START = "PYVMP_SEND_RES_START"


Tracking = Enum(
    "Tracking",
    [
        Constants.PYVMP_RECEIVED_FULL_DATA,
        Constants.PYVMP_UNWRAPPED_BYTES,
        Constants.PYVMP_PREDICT_DONE,
        Constants.PYVMP_WRAPPED_DICT,
        Constants.PYVMP_SEND_RES_START,
    ],
    start=0,
)  # type: ignore
