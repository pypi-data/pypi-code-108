#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""OSC message responses sent from the device."""


import ast
import re
from dataclasses import dataclass as _dataclass
from dataclasses import field
from typing import Any, Callable, Dict, Tuple, TypeVar, Union

# Pylance custom dataclass work around
_T = TypeVar("_T")


def __dataclass_transform__(
    *,
    eq_default: bool = True,
    order_default: bool = False,
    kw_only_default: bool = False,
    field_descriptors: Tuple[Union[type, Callable[..., Any]], ...] = (()),
) -> Callable[[_T], _T]:
    return lambda a: a


# Implement a custom dataclass to parse raw strings
@__dataclass_transform__(field_descriptors=(field,))
def dataclass(*args: Tuple[Any], **kwargs: Dict[str, Any]):
    def wrapper(cls):
        cls = _dataclass(cls, **kwargs)
        original_init = cls.__init__

        def __init__(self, *args, **kwargs):
            # Concat split string args
            if all([isinstance(x, str) for x in args]):
                args = (" ".join(args),)

            # Break down the args
            if len(args) == 1 and isinstance(args[0], str):
                # First look for custom regex strings
                # These will be <field_name>_re
                for i, field_name in enumerate(self.__annotations__.keys()):
                    if field_name.endswith("_re"):
                        match: re.Match = getattr(self, field_name).search(args[0])
                        kwargs[field_name[:-3]] = match[0]
                        args = (
                            (args[0][: match.start()] + args[0][match.end() :]).strip(),
                        )
                args = args[0].split()

                # Now add all to kwargs
                field_names = [
                    k
                    for k in self.__annotations__.keys()
                    if k not in kwargs and not k.endswith("_re")
                ]
                for i, arg in enumerate(args):
                    field_name = field_names[i]
                    kwargs[field_name] = arg
                args = tuple()
                kwargs.pop("address", None)

            # Remove unnecessary address identifier
            args = list(args)
            if args and args[0] == self.address:
                args.pop(0)

            # Eval positional args
            for i, arg in enumerate(args):
                try:
                    args[i] = ast.literal_eval(arg.capitalize())
                except (AttributeError, ValueError, SyntaxError, NameError):
                    # Catch errors for non-strings, bad strings (i.e. ture instead of true)
                    # or non-evalable strings (i.e. class name)
                    pass

            # Eval named args
            for k, v in kwargs.items():
                try:
                    kwargs[k] = ast.literal_eval(v.capitalize())
                except (AttributeError, ValueError, SyntaxError, NameError):
                    # Catch errors for non-strings, bad strings (i.e. ture instead of true)
                    # or non-evalable strings (i.e. class name)
                    pass

            # Now call the generated dataclass init
            original_init(self, *args, **kwargs)

        cls.__init__ = __init__
        return cls

    return wrapper(args[0]) if args else wrapper


@dataclass
class OSCResponse:
    """An abstract class meant to be implemented by OSC resp objects."""

    address: str


# Automatic Messages


@dataclass
class Booted(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/automatically-sent-messages-from-step-400/#booted"""  # noqa

    address: str = field(default="/booted", init=False)
    deviceID: int


@dataclass
class ErrorCommand(OSCResponse, Exception):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/automatically-sent-messages-from-step-400/#errorcommand"""  # noqa

    address: str = field(default="/error/command", init=False)
    errorText: str
    motorID: int = None


@dataclass
class ErrorOSC(OSCResponse, Exception):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/automatically-sent-messages-from-step-400/#errorosc"""  # noqa

    address: str = field(default="/error/osc", init=False)
    errorText: str
    motorID: int = None


@dataclass
class Busy(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/automatically-sent-messages-from-step-400/#busy"""  # noqa

    address: str = field(default="/busy", init=False)
    motorID: int
    state: bool


@dataclass
class HiZ(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/automatically-sent-messages-from-step-400/#hiz"""  # noqa

    address: str = field(default="/HiZ", init=False)
    motorID: int
    state: bool


@dataclass
class MotorStatus(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/automatically-sent-messages-from-step-400/#motorstatus"""  # noqa

    address: str = field(default="/motorStatus", init=False)
    motorID: int
    MOT_STATUS: int


@dataclass
class HomingStatus(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/automatically-sent-messages-from-step-400/#homingstatus"""  # noqa

    address: str = field(default="/homingStatus", init=False)
    motorID: int
    homingStatus: int


@dataclass
class Uvlo(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/automatically-sent-messages-from-step-400/#uvlo"""  # noqa

    address: str = field(default="/uvlo", init=False)
    motorID: int
    state: bool


@dataclass
class ThermalStatus(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/automatically-sent-messages-from-step-400/#thermalstatus"""  # noqa

    address: str = field(default="/thermalStatus", init=False)
    motorID: int
    thermalStatus: int


@dataclass
class OverCurrent(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/automatically-sent-messages-from-step-400/#overcurrent"""  # noqa

    address: str = field(default="/overCurrent", init=False)
    motorID: int


@dataclass
class Stall(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/automatically-sent-messages-from-step-400/#stall"""  # noqa

    address: str = field(default="/stall", init=False)
    motorID: int


# System Settings


@dataclass
class DestIP(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/system-settings/#setdestip"""  # noqa

    address: str = field(default="/destIp", init=False)
    destIp0: int
    destIp1: int
    destIp2: int
    destIp3: int
    isNewDestIp: bool


@dataclass
class Version(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/system-settings/#getversion"""  # noqa

    address: str = field(default="/version", init=False)
    firmware_name: str
    firmware_version: str
    compile_date: str

    # Custom regex to breakout
    compile_date_re: re.Pattern = field(
        default=re.compile(r"\w+ ? \d{1,2} \d{4} .+"), init=False, repr=False
    )


@dataclass
class ConfigName(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/system-settings/#getconfigname"""  # noqa

    address: str = field(default="/configName", init=False)
    configName: str
    sdInitializeSucceeded: bool
    configFileOpenSucceeded: bool
    configFileParseSucceeded: bool


# Motor Driver Settings


@dataclass
class MicrostepMode(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#getmicrostepmode_intmotorid"""  # noqa

    address: str = field(default="/microstepMode", init=False)
    motorID: int
    STEP_SEL: int


@dataclass
class LowSpeedOptimizeThreshold(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#getlowspeedoptimizethreshold_intmotorid"""  # noqa

    address: str = field(default="/lowSpeedOptimizeThreshold", init=False)
    motorID: int
    lowSpeedOptimizeThreshold: float
    optimizationEnabled: bool


@dataclass
class Dir(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#getdir_intmotorid"""  # noqa

    address: str = field(default="/dir", init=False)
    motorID: int
    direction: bool


@dataclass
class AdcVal(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#getadcval_intmotorid"""  # noqa

    address: str = field(default="/adcVal", init=False)
    motorID: int
    ADC_OUT: int


@dataclass
class Status(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#getstatus_intmotorid"""  # noqa

    address: str = field(default="/status", init=False)
    motorID: int
    status: int


@dataclass
class ConfigRegister(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#getconfigregister_intmotorid"""  # noqa

    address: str = field(default="/configRegister", init=False)
    motorID: int
    CONFIG: int


# Alarm Settings


@dataclass
class OverCurrentThreshold(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#getovercurrentthreshold_intmotorid"""  # noqa

    address: str = field(default="/overCurrentThreshold", init=False)
    motorID: int
    overCurrentThreshold: float


@dataclass
class StallThreshold(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#getstallthreshold_intmotorid"""  # noqa

    address: str = field(default="/stallThreshold", init=False)
    motorID: int
    stallThreshold: float


@dataclass
class ProhibitMotionOnHomeSw(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#getprohibitmotiononhomesw_intmotorid"""  # noqa

    address: str = field(default="/prohibitMotionOnHomeSw", init=False)
    motorID: int
    enable: bool


@dataclass
class ProhibitMotionOnLimitSw(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#getprohibitmotiononlimitsw_intmotorid"""  # noqa

    address: str = field(default="/prohibitMotionOnLimitSw", init=False)
    motorID: int
    enable: bool


# Voltage and Current Mode Settings


@dataclass
class Kval(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/voltage-and-current-mode-settings/#getkval_intmotorid"""  # noqa

    address: str = field(default="/kval", init=False)
    motorID: int
    holdKVAL: int
    runKVAL: int
    accKVAL: int
    setDecKVAL: int


@dataclass
class BemfParam(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/voltage-and-current-mode-settings/#getbemfparam_intmotorid"""  # noqa

    address: str = field(default="/bemfParam", init=False)
    motorID: int
    INT_SPEED: int
    ST_SLP: int
    FN_SLP_ACC: int
    FN_SLP_DEC: int


@dataclass
class Tval(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/voltage-and-current-mode-settings/#gettval_intmotorid"""  # noqa

    address: str = field(default="/tval", init=False)
    motorID: int
    holdTVAL: int
    runTVAL: int
    accTVAL: int
    decTVAL: int


@dataclass
class Tval_mA(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/voltage-and-current-mode-settings/#gettval_ma_intmotorid"""  # noqa

    address: str = field(default="/tval_mA", init=False)
    motorID: int
    holdTVAL_mA: float
    runTVAL_mA: float
    accTVAL_mA: float
    decTVAL_mA: float


@dataclass
class DecayModeParam(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/voltage-and-current-mode-settings/#getdecaymodeparam_intmotorid"""  # noqa

    address: str = field(default="/decayModeParam", init=False)
    motorID: int
    T_FAST: int
    TON_MIN: int
    TOFF_MIN: int


# Speed Profile


@dataclass
class SpeedProfile(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/speed-profile/#getspeedprofile_intmotorid"""  # noqa

    address: str = field(default="/speedProfile", init=False)
    motorID: int
    acc: float
    dec: float
    maxSpeed: float


@dataclass
class FullstepSpeed(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/speed-profile/#getfullstepspeed_intmotorid"""  # noqa

    address: str = field(default="/fullstepSpeed", init=False)
    motorID: int
    fullstepSpeed: float


@dataclass
class MinSpeed(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/speed-profile/#getminspeed_intmotorid"""  # noqa

    address: str = field(default="/minSpeed", init=False)
    motorID: int
    minSpeed: float


@dataclass
class Speed(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/speed-profile/#getspeed_intmotorid"""  # noqa

    address: str = field(default="/speed", init=False)
    motorID: int
    speed: float


# Homing


@dataclass
class HomingDirection(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/homing/#gethomingdirection_intmotorid"""  # noqa

    address: str = field(default="/homingDirection", init=False)
    motorID: int
    homingDirection: bool


@dataclass
class HomingSpeed(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/homing/#gethomingspeed_intmotorid"""  # noqa

    address: str = field(default="/homingSpeed", init=False)
    motorID: int
    homingSpeed: float


@dataclass
class GoUntilTimeout(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/homing/#getgountiltimeout_intmotorid"""  # noqa

    address: str = field(default="/goUntilTimeout", init=False)
    motorID: int
    timeout: int


@dataclass
class ReleaseSwTimeout(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/homing/#setreleaseswtimeout_intmotorid_inttimeout"""  # noqa

    address: str = field(default="/releaseSwTimeout", init=False)
    motorID: int
    timeout: int


# Home and Limit Sensors


@dataclass
class SwEvent(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/home-and-limit-sensers/#enablesweventreport_intmotorid_boolenable"""  # noqa

    address: str = field(default="/swEvent", init=False)
    motorID: int


@dataclass
class HomeSw(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/home-and-limit-sensers/#gethomesw_intmotorid"""  # noqa

    address: str = field(default="/homeSw", init=False)
    motorID: int
    swState: bool
    direction: bool


@dataclass
class LimitSw(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/home-and-limit-sensers/#getlimitsw_intmotorid"""  # noqa

    address: str = field(default="/limitSw", init=False)
    motorID: int
    swState: bool
    direction: bool


@dataclass
class HomeSwMode(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/home-and-limit-sensers/#gethomeswmode_intmotorid"""  # noqa

    address: str = field(default="/homeSwMode", init=False)
    motorID: int
    swMode: bool


@dataclass
class LimitSwMode(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/home-and-limit-sensers/#getlimitswmode_intmotorid"""  # noqa

    address: str = field(default="/limitSwMode", init=False)
    motorID: int
    swMode: bool


# Position Management


@dataclass
class Position(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/position-management/#getposition_intmotorid"""  # noqa

    address: str = field(default="/position", init=False)
    motorID: int
    ABS_POS: int


@dataclass
class PositionList(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/position-management/#getpositionlist"""  # noqa

    address: str = field(default="/positionList", init=False)
    position1: int
    position2: int
    position3: int
    position4: int
    position5: int = None
    position6: int = None
    position7: int = None
    position8: int = None


@dataclass
class ElPos(OSCResponse):
    """Documentation https://ponoor.com/en/docs/step-series/osc-command-reference/position-management/#getelpos_intmotorid"""  # noqa

    address: str = field(default="/elPos", init=False)
    motorID: int
    fullstep: int
    microstep: int


@dataclass
class Mark(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/position-management/#getmark_intmotorid"""  # noqa

    address: str = field(default="/mark", init=False)
    motorID: int
    MARK: int


# Electromagnetic Brake


@dataclass
class BrakeTransitionDuration(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/brake/#getbraketransitionduration_intmotorid"""  # noqa

    address: str = field(default="/brakeTransitionDuration", init=False)
    motorID: int
    duration: int


# Servo Mode


@dataclass
class ServoParam(OSCResponse):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/servo-mode/#getservoparam_intmotorid"""  # noqa

    address: str = field(default="/servoParam", init=False)
    motorID: int
    kP: float
    kI: float
    kD: float
