#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""Communication protocols subpackage."""

from .base import (  # noqa: F401
    CommunicationProtocol,
    NullCommunicationProtocol,
)

try:
    from .labjack_ljm import (  # noqa: F401
        LJMCommunication,
        LJMCommunicationConfig,
        LJMCommunicationError,
    )
except (ImportError, ModuleNotFoundError):
    import warnings

    warnings.warn(
        "\n\n  "
        "To use LabJack device controller or related utilities install the LJM Library"
        "\n  "
        "and install hvl_ccb library with a 'labjack' extra feature:"
        "\n\n  "
        "    pip install hvl_ccb[labjack]"
        "\n\n"
    )

from .modbus_tcp import (  # noqa: F401
    ModbusTcpCommunication,
    ModbusTcpConnectionFailedException,
    ModbusTcpCommunicationConfig,
)
from .opc import (  # noqa: F401
    OpcUaCommunication,
    OpcUaCommunicationConfig,
    OpcUaCommunicationIOError,
    OpcUaCommunicationTimeoutError,
    OpcUaSubHandler,
)
from .telnet import (  # noqa: F401
    TelnetCommunication,
    TelnetCommunicationConfig,
    TelnetError,
)
from .serial import (  # noqa: F401
    SerialCommunication,
    SerialCommunicationConfig,
    SerialCommunicationIOError,
)
from .tcp import (  # noqa: F401
    TcpCommunicationConfig,
    Tcp,
)
from .visa import (  # noqa: F401
    VisaCommunication,
    VisaCommunicationError,
    VisaCommunicationConfig,
)
