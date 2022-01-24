"""
This module establishes methods for interfacing with the Highland Technology T560-2
via its ethernet adapter with a telnet communication protocol.

The T560 is a small digital delay & pulse generator.
It outputs up to four individually timed pulses with 10-ps precision,
given an internal or external trigger.

This module introduces methods for configuring channels, gating, and triggering.
Further documentation and a more extensive command list may be obtained from:

https://www.highlandtechnology.com/DSS/T560DS.shtml
"""

from hvl_ccb.dev.highland_t560.base import (  # noqa: F401
    T560Error,
    T560Communication,
    T560CommunicationConfig,
    AutoInstallMode,
    GateMode,
    Polarity,
    TriggerMode,
)
from hvl_ccb.dev.highland_t560.device import (  # noqa: F401
    T560,
    T560Config,
)
