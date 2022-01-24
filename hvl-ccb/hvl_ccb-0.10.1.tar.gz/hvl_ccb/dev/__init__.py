#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""Devices subpackage."""

import sys

from .base import (  # noqa: F401
    Device,
    DeviceExistingException,
    DeviceSequenceMixin,
    DeviceFailuresException,
    SingleCommDevice,
)
from .crylas import (  # noqa: F401
    CryLasLaser,
    CryLasLaserConfig,
    CryLasLaserSerialCommunication,
    CryLasLaserSerialCommunicationConfig,
    CryLasLaserError,
    CryLasLaserNotReadyError,
    CryLasAttenuator,
    CryLasAttenuatorConfig,
    CryLasAttenuatorSerialCommunication,
    CryLasAttenuatorSerialCommunicationConfig,
    CryLasAttenuatorError,
)
from .ea_psi9000 import (  # noqa: F401
    PSI9000,
    PSI9000Config,
    PSI9000VisaCommunication,
    PSI9000VisaCommunicationConfig,
    PSI9000Error,
)
from .fug import (  # noqa: F401
    FuG,
    FuGConfig,
    FuGSerialCommunication,
    FuGSerialCommunicationConfig,
    FuGError,
    FuGErrorcodes,
    FuGDigitalVal,
    FuGTerminators,
    FuGPolarities,
    FuGReadbackChannels,
    FuGMonitorModes,
    FuGRampModes,
)
from .heinzinger import (  # noqa: F401
    HeinzingerDI,
    HeinzingerPNC,
    HeinzingerConfig,
    HeinzingerPNCError,
    HeinzingerPNCMaxVoltageExceededException,
    HeinzingerPNCMaxCurrentExceededException,
    HeinzingerPNCDeviceNotRecognizedException,
    HeinzingerSerialCommunication,
    HeinzingerSerialCommunicationConfig,
)

try:
    from .labjack import (  # noqa: F401
        LabJack,
        LabJackError,
        LabJackIdentifierDIOError,
    )
except (ImportError, ModuleNotFoundError):
    import warnings

    warnings.warn(
        "\n\n  "
        "To use LabJack device controller or related utilities install LJM Library and"
        "\n  "
        "install the hvl_ccb library with a 'labjack' extra feature:"
        "\n\n  "
        "    pip install hvl_ccb[labjack]"
        "\n\n"
    )

from .lauda import (  # noqa: F401
    LaudaProRp245eTcpCommunicationConfig,
    LaudaProRp245eTcpCommunication,
    LaudaProRp245eConfig,
    LaudaProRp245e,
)
from .mbw973 import (  # noqa: F401
    MBW973,
    MBW973Config,
    MBW973ControlRunningException,
    MBW973PumpRunningException,
    MBW973Error,
    MBW973SerialCommunication,
    MBW973SerialCommunicationConfig,
)
from .newport import (  # noqa: F401
    NewportSMC100PP,
    NewportSMC100PPConfig,
    NewportStates,
    NewportSMC100PPSerialCommunication,
    NewportSMC100PPSerialCommunicationConfig,
    NewportConfigCommands,
    NewportMotorError,
    NewportControllerError,
    NewportSerialCommunicationError,
    NewportUncertainPositionError,
    NewportMotorPowerSupplyWasCutError,
)
from .pfeiffer_tpg import (  # noqa: F401
    PfeifferTPG,
    PfeifferTPGConfig,
    PfeifferTPGSerialCommunication,
    PfeifferTPGSerialCommunicationConfig,
    PfeifferTPGError,
)
if sys.platform == 'darwin':
    import warnings

    warnings.warn("\n\n  PicoSDK is not available for Darwin OSs\n")
else:
    try:
        from .picotech_pt104 import (  # noqa: F401
            Pt104,
            Pt104ChannelConfig,
            Pt104CommunicationType,
            Pt104DeviceConfig,
        )
    except (ImportError, ModuleNotFoundError):
        import warnings

        warnings.warn(
            "\n\n  "
            "To use PicoTech PT-104 device controller or related utilities install"
            "\n  "
            "PicoSDK and install the hvl_ccb library with a 'picotech' extra feature:"
            "\n\n  "
            "    $ pip install hvl_ccb[picotech]"
            "\n\n"
        )

from .rs_rto1024 import (  # noqa: F401
    RTO1024,
    RTO1024Error,
    RTO1024Config,
    RTO1024VisaCommunication,
    RTO1024VisaCommunicationConfig,
)
from .se_ils2t import (  # noqa: F401
    ILS2T,
    ILS2TConfig,
    ILS2TException,
    ILS2TModbusTcpCommunication,
    ILS2TModbusTcpCommunicationConfig,
    IoScanningModeValueError,
    ScalingFactorValueError,
)
from .sst_luminox import (  # noqa: F401
    Luminox,
    LuminoxConfig,
    LuminoxSerialCommunication,
    LuminoxSerialCommunicationConfig,
    LuminoxMeasurementType,
    LuminoxMeasurementTypeError,
    LuminoxOutputMode,
    LuminoxOutputModeError,
)
from .visa import (  # noqa: F401
    VisaDevice,
    VisaDeviceConfig,
)

if sys.platform == 'darwin':
    import warnings

    warnings.warn("\n\n LibTiePie SDK is not available for Darwin OSs\n")
else:
    try:
        from .tiepie import (  # noqa: F401
            TiePieGeneratorConfig,
            TiePieGeneratorSignalType,
            TiePieGeneratorMixin,
            TiePieI2CHostConfig,
            TiePieI2CHostMixin,
            TiePieOscilloscope,
            TiePieOscilloscopeConfig,
            TiePieOscilloscopeResolution,
            TiePieOscilloscopeAutoResolutionModes,
            TiePieDeviceConfig,
            TiePieDeviceType,
            TiePieError,
            get_device_by_serial_number,
            TiePieOscilloscopeChannelCoupling,
            TiePieOscilloscopeChannelConfig,
            TiePieOscilloscopeRange,
            TiePieOscilloscopeTriggerKind,
            TiePieOscilloscopeTriggerLevelMode,
            TiePieHS5,
            TiePieHS6,
            TiePieWS5,
        )
    except (ImportError, ModuleNotFoundError):
        import warnings

        warnings.warn(
            "\n\n  "
            "To use TiePie devices controllers or related utilities install LibTiePie"
            "\n  "
            "and install the hvl_ccb library with a 'tiepie' extra feature:"
            "\n\n  "
            "    $ pip install hvl_ccb[tiepie]"
            "\n\n"
        )

from .supercube2015 import (  # noqa: F401
    constants as supercube_constants2015,
    Supercube2015WithFU,
    Supercube2015Base,
)
