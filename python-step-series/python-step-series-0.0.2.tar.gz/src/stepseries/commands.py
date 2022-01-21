#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""OSC message builders to send to the device."""


from dataclasses import asdict, dataclass, field
from typing import Callable, Optional, Tuple

from pythonosc.osc_message import OscMessage
from pythonosc.osc_message_builder import OscMessageBuilder

from . import responses


@dataclass
class OSCCommand:
    """An abstract class meant to be implemented by OSC command objects."""

    def build(self) -> OscMessage:
        """Converts the builder to a usable OSC message."""

        # Convert the builder to a dictionary
        builder_dict = asdict(self)

        # Extract the values
        # Code is largely copy-paste from pythonosc.UDPClient
        address = builder_dict.pop("address")
        builder_dict.pop("callback", None)
        builder_dict.pop("response_cls", None)

        builder = OscMessageBuilder(address=address)

        # Return as a message string
        for v in builder_dict.values():
            if isinstance(v, bool):
                v = int(v)
            builder.add_arg(v)

        return builder.build()

    def stringify(self) -> str:
        """Converts the builder to an OSC message string."""

        # Convert the builder to a dictionary
        builder_dict = asdict(self)
        builder_dict.pop("callback", None)
        builder_dict.pop("response_cls", None)

        # Extract the values
        address: str = builder_dict.pop("address") + " "

        # Return as a message string
        for v in builder_dict.values():
            if isinstance(v, bool):
                v = int(v)
            if v is None:
                continue
            address += str(v) + " "

        return address[:-1]


@dataclass
class OSCSetCommand(OSCCommand):
    """A command that only performs set functions on the device."""


@dataclass
class OSCGetCommand(OSCCommand):
    """A commands that only performs get functions on the device."""


# System Settings


@dataclass
class SetDestIP(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/system-settings/#setdestip"""  # noqa

    address: str = field(default="/setDestIp", init=False)
    response_cls: responses.DestIP = field(default=responses.DestIP, init=False)


@dataclass
class GetVersion(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/system-settings/#getversion"""  # noqa

    address: str = field(default="/getVersion", init=False)
    response_cls: responses.Version = field(default=responses.Version, init=False)


@dataclass
class GetConfigName(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/system-settings/#getconfigname"""  # noqa

    address: str = field(default="/getConfigName", init=False)
    response_cls: responses.ConfigName = field(default=responses.ConfigName, init=False)


@dataclass
class ReportError(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/system-settings/#reporterror_boolenable"""  # noqa

    address: str = field(default="/reportError", init=False)
    response_cls: Tuple[responses.ErrorCommand, responses.ErrorOSC] = field(
        default_factory=lambda: (responses.ErrorCommand, responses.ErrorOSC), init=False
    )
    enable: bool
    callback: Optional[Callable[..., None]] = None


@dataclass
class ResetDevice(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/system-settings/#resetdevice"""  # noqa

    address: str = field(default="/resetDevice", init=False)
    response_cls: responses.Booted = field(default=responses.Booted, init=False)


# Motor Driver Settings


@dataclass
class SetMicrostepMode(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#setmicrostepmode_intmotorid_intstep_sel"""  # noqa

    address: str = field(default="/setMicrostepMode", init=False)
    motorID: int
    STEP_SEL: int


@dataclass
class GetMicrostepMode(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#setmicrostepmode_intmotorid_intstep_sel"""  # noqa

    address: str = field(default="/getMicrostepMode", init=False)
    response_cls: responses.MicrostepMode = field(
        default=responses.MicrostepMode, init=False
    )
    motorID: int


@dataclass
class EnableLowSpeedOptimize(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#enablelowspeedoptimize_intmotorid_boolenable"""  # noqa

    address: str = field(default="/enableLowSpeedOptimize", init=False)
    response_cls: responses.LowSpeedOptimizeThreshold = field(
        default=responses.LowSpeedOptimizeThreshold, init=False
    )
    motorID: int
    enable: bool


@dataclass
class SetLowSpeedOptimizeThreshold(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#setlowspeedoptimizethreshold_intmotorid_floatlowspeedoptimizationthreshold"""  # noqa

    address: str = field(default="/setLowSpeedOptimizeThreshold", init=False)
    motorID: int
    lowSpeedOptimizationThreshold: float


@dataclass
class GetLowSpeedOptimizeThreshold(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#getlowspeedoptimizethreshold_intmotorid"""  # noqa

    address: str = field(default="/getLowSpeedOptimizeThreshold", init=False)
    response_cls: responses.LowSpeedOptimizeThreshold = field(
        default=responses.LowSpeedOptimizeThreshold, init=False
    )
    motorID: int


@dataclass
class EnableBusyReport(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#enablebusyreport_intmotorid_boolenable"""  # noqa

    address: str = field(default="/enableBusyReport", init=False)
    response_cls: responses.Busy = field(default=responses.Busy, init=False)
    motorID: int
    enable: bool
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetBusy(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#getbusy_intmotorid"""  # noqa

    address: str = field(default="/getBusy", init=False)
    response_cls: responses.Busy = field(default=responses.Busy, init=False)
    motorID: int


@dataclass
class EnableHiZReport(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#enablehizreport_intmotorid_boolenable"""  # noqa

    address: str = field(default="/enableHizReport", init=False)
    response_cls: responses.HiZ = field(default=responses.HiZ, init=False)
    motorID: int
    enable: bool
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetHiZ(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#gethiz_intmotorid"""  # noqa

    address: str = field(default="/getHiZ", init=False)
    response_cls: responses.HiZ = field(default=responses.HiZ, init=False)
    motorID: int


@dataclass
class EnableDirReport(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#enabledirreport_intmotorid_boolenable"""  # noqa

    address: str = field(default="/enableDirReport", init=False)
    response_cls: responses.Dir = field(default=responses.Dir, init=False)
    motorID: int
    enable: bool
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetDir(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#getdir_intmotorid"""  # noqa

    address: str = field(default="/getDir", init=False)
    response_cls: responses.Dir = field(default=responses.Dir, init=False)
    motorID: int


@dataclass
class EnableMotorStatusReport(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#enablemotorstatusreport_intmotorid_boolenable"""  # noqa

    address: str = field(default="/enableMotorStatusReport", init=False)
    response_cls: responses.MotorStatus = field(
        default=responses.MotorStatus, init=False
    )
    motorID: int
    enable: bool
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetMotorStatus(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#getmotorstatus_intmotorid"""  # noqa

    address: str = field(default="/getMotorStatus", init=False)
    response_cls: responses.MotorStatus = field(
        default=responses.MotorStatus, init=False
    )
    motorID: int


@dataclass
class SetPositionReportInterval(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#setpositionreportinterval_intmotorid_intinterval"""  # noqa

    address: str = field(default="/setPositionReportInterval", init=False)
    response_cls: responses.Position = field(default=responses.Position, init=False)
    motorID: int
    interval: int
    callback: Optional[Callable[..., None]] = None


@dataclass
class SetPositionListReportInterval(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#setpositionlistreportinterval_intinterval"""  # noqa

    address: str = field(default="/setPositionListReportInterval", init=False)
    response_cls: responses.PositionList = field(
        default=responses.PositionList, init=False
    )
    interval: int
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetAdcVal(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#getadcval_intmotorid"""  # noqa

    address: str = field(default="/getAdcVal", init=False)
    response_cls: responses.AdcVal = field(default=responses.AdcVal, init=False)
    motorID: int


@dataclass
class GetStatus(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#getstatus_intmotorid"""  # noqa

    address: str = field(default="/getStatus", init=False)
    response_cls: responses.Status = field(default=responses.Status, init=False)
    motorID: int


@dataclass
class GetConfigRegister(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#getconfigregister_intmotorid"""  # noqa

    address: str = field(default="/getConfigRegister", init=False)
    response_cls: responses.ConfigRegister = field(
        default=responses.ConfigRegister, init=False
    )
    motorID: int


@dataclass
class ResetMotorDriver(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-driver-settings/#resetmotordriver_intmotorid"""  # noqa

    address: str = field(default="/resetMotorDriver", init=False)
    motorID: int


# Alarm Settings


@dataclass
class EnableUvloReport(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#enableuvloreport_intmotorid_boolenable"""  # noqa

    address: str = field(default="/enableUvloReport", init=False)
    response_cls: responses.Uvlo = field(default=responses.Uvlo, init=False)
    motorID: int
    enable: bool
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetUvlo(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#getuvlo_intmotorid"""  # noqa

    address: str = field(default="/getUvlo", init=False)
    response_cls: responses.Uvlo = field(default=responses.Uvlo, init=False)
    motorID: int


@dataclass
class EnableThermalStatusReport(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#enablethermalstatusreport_intmotorid_boolenable"""  # noqa

    address: str = field(default="/enableThermalStatusReport", init=False)
    response_cls: responses.ThermalStatus = field(
        default=responses.ThermalStatus, init=False
    )
    motorID: int
    enable: bool
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetThermalStatus(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#getthermalstatus_intmotorid"""  # noqa

    address: str = field(default="/getThermalStatus", init=False)
    response_cls: responses.ThermalStatus = field(
        default=responses.ThermalStatus, init=False
    )
    motorID: int


@dataclass
class EnableOverCurrentReport(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#enableovercurrentreport_intmotorid_boolenable"""  # noqa

    address: str = field(default="/enableOverCurrentReport", init=False)
    response_cls: responses.OverCurrent = field(
        default=responses.OverCurrent, init=False
    )
    motorID: int
    enable: bool
    callback: Optional[Callable[..., None]] = None


@dataclass
class SetOverCurrentThreshold(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#setovercurrentthreshold_intmotorid_intocd_th"""  # noqa

    address: str = field(default="/setOverCurrentThreshold", init=False)
    motorID: int
    OCD_TH: int


@dataclass
class GetOverCurrentThreshold(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#getovercurrentthreshold_intmotorid"""  # noqa

    address: str = field(default="/getOverCurrentThreshold", init=False)
    response_cls: responses.OverCurrentThreshold = field(
        default=responses.OverCurrentThreshold, init=False
    )
    motorID: int


@dataclass
class EnableStallReport(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#enablestallreport_intmotorid_boolenable"""  # noqa

    address: str = field(default="/enableStallReport", init=False)
    response_cls: responses.Stall = field(default=responses.Stall, init=False)
    motorID: int
    enable: bool
    callback: Optional[Callable[..., None]] = None


@dataclass
class SetStallThreshold(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#setstallthreshold_intmotorid_intstall_th"""  # noqa

    address: str = field(default="/setStallThreshold", init=False)
    motorID: int
    STALL_TH: int


@dataclass
class GetStallThreshold(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#getstallthreshold_intmotorid"""  # noqa

    address: str = field(default="/getStallThreshold", init=False)
    response_cls: responses.StallThreshold = field(
        default=responses.StallThreshold, init=False
    )
    motorID: int


@dataclass
class SetProhibitMotionOnHomeSw(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#setprohibitmotiononhomesw_intmotorid_boolenable"""  # noqa

    address: str = field(default="/setProhibitMotionOnHomeSw", init=False)
    motorID: int
    enable: bool


@dataclass
class GetProhibitMotionOnHomeSw(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#getprohibitmotiononhomesw_intmotorid"""  # noqa

    address: str = field(default="/getProhibitMotionOnHomeSw", init=False)
    response_cls: responses.ProhibitMotionOnHomeSw = field(
        default=responses.ProhibitMotionOnHomeSw, init=False
    )
    motorID: int


@dataclass
class SetProhibitMotionOnLimitSw(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#setprohibitmotiononlimitsw_intmotorid_boolenable"""  # noqa

    address: str = field(default="/setProhibitMotionOnLimitSw", init=False)
    motorID: int
    enable: bool


@dataclass
class GetProhibitMotionOnLimitSw(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/alarm-settings/#getprohibitmotiononlimitsw_intmotorid"""  # noqa

    address: str = field(default="/getProhibitMotionOnLimitSw", init=False)
    response_cls: responses.ProhibitMotionOnLimitSw = field(
        default=responses.ProhibitMotionOnLimitSw, init=False
    )
    motorID: int


# Voltage and Current Mode Settings


@dataclass
class SetVoltageMode(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/voltage-and-current-mode-settings/#setvoltagemode_intmotorid"""  # noqa

    address: str = field(default="/setVoltageMode", init=False)
    motorID: int


@dataclass
class SetKval(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/voltage-and-current-mode-settings/#setkval_intmotorid_intholdkval_intrunkval_intacckval_intsetdeckval"""  # noqa

    address: str = field(default="/setKval", init=False)
    motorID: int
    holdKVAL: int
    runKVAL: int
    accKVAL: int
    setDecKVAL: int


@dataclass
class GetKval(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/voltage-and-current-mode-settings/#getkval_intmotorid"""  # noqa

    address: str = field(default="/getKval", init=False)
    response_cls: responses.Kval = field(default=responses.Kval, init=False)
    motorID: int


@dataclass
class SetBemfParam(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/voltage-and-current-mode-settings/#setbemfparam_intmotorid_intint_speed_intst_slp_intfn_slp_acc_intfn_slp_dec"""  # noqa

    address: str = field(default="/setBemfParam", init=False)
    motorID: int
    INT_SPEED: int
    ST_SLP: int
    FN_SLP_ACC: int
    FN_SLP_DEC: int


@dataclass
class GetBemfParam(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/voltage-and-current-mode-settings/#getbemfparam_intmotorid"""  # noqa

    address: str = field(default="/getBemfParam", init=False)
    response_cls: responses.BemfParam = field(default=responses.BemfParam, init=False)
    motorID: int


@dataclass
class SetCurrentMode(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/voltage-and-current-mode-settings/#setcurrentmode_intmotorid"""  # noqa

    address: str = field(default="/setCurrentMode", init=False)
    motorID: int


@dataclass
class SetTval(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/voltage-and-current-mode-settings/#settval_intmotorid_intholdtval_intruntval_intacctval_intsetdectval"""  # noqa

    address: str = field(default="/setTval", init=False)
    motorID: int
    holdTVAL: int
    runTVAL: int
    accTVAL: int
    setDecTVAL: int


@dataclass
class GetTval(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/voltage-and-current-mode-settings/#gettval_intmotorid"""  # noqa

    address: str = field(default="/getTval", init=False)
    response_cls: responses.Tval = field(default=responses.Tval, init=False)
    motorID: int


@dataclass
class GetTval_mA(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/voltage-and-current-mode-settings/#gettval_ma_intmotorid"""  # noqa

    address: str = field(default="/getTval_mA", init=False)
    response_cls: responses.Tval_mA = field(default=responses.Tval_mA, init=False)
    motorID: int


@dataclass
class SetDecayModeParam(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/voltage-and-current-mode-settings/#setdecaymodeparam_intmotorid_intt_fast_intton_min_inttoff_min"""  # noqa

    address: str = field(default="/setDecayModeParam", init=False)
    motorID: int
    T_FAST: int
    TON_MIN: int
    TOFF_MIN: int


@dataclass
class GetDecayModeParam(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/voltage-and-current-mode-settings/#getdecaymodeparam_intmotorid"""  # noqa

    address: str = field(default="/getDecayModeParam", init=False)
    response_cls: responses.DecayModeParam = field(
        default=responses.DecayModeParam, init=False
    )
    motorID: int


# Speed Profile


@dataclass
class SetSpeedProfile(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/speed-profile/#setspeedprofile_intmotorid_floatacc_floatdec_floatmaxspeed"""  # noqa

    address: str = field(default="/setSpeedProfile", init=False)
    motorID: int
    acc: float
    dec: float
    maxSpeed: float


@dataclass
class GetSpeedProfile(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/speed-profile/#getspeedprofile_intmotorid"""  # noqa

    address: str = field(default="/getSpeedProfile", init=False)
    response_cls: responses.SpeedProfile = field(
        default=responses.SpeedProfile, init=False
    )
    motorID: int


@dataclass
class SetFullstepSpeed(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/speed-profile/#setfullstepspeed_intmotorid_floatfullstepspeed"""  # noqa

    address: str = field(default="/setFullstepSpeed", init=False)
    motorID: int
    fullstepSpeed: float


@dataclass
class GetFullstepSpeed(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/speed-profile/#getfullstepspeed_intmotorid"""  # noqa

    address: str = field(default="/getFullstepSpeed", init=False)
    response_cls: responses.FullstepSpeed = field(
        default=responses.FullstepSpeed, init=False
    )
    motorID: int


@dataclass
class SetMaxSpeed(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/speed-profile/#setmaxspeed_intmotorid_floatmaxspeed"""  # noqa

    address: str = field(default="/setMaxSpeed", init=False)
    motorID: int
    maxSpeed: float


@dataclass
class SetAcc(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/speed-profile/#setacc_intmotorid_floatacc"""  # noqa

    address: str = field(default="/setAcc", init=False)
    motorID: int
    acc: float


@dataclass
class SetDec(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/speed-profile/#setdec_intmotorid_floatdec"""  # noqa

    address: str = field(default="/setDec", init=False)
    motorID: int
    dec: float


@dataclass
class SetMinSpeed(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/speed-profile/#setminspeed_intmotorid_floatminspeed"""  # noqa

    address: str = field(default="/setMinSpeed", init=False)
    motorID: int
    minSpeed: float


@dataclass
class GetMinSpeed(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/speed-profile/#getminspeed_intmotorid"""  # noqa

    address: str = field(default="/getMinSpeed", init=False)
    response_cls: responses.MinSpeed = field(default=responses.MinSpeed, init=False)
    motorID: int


@dataclass
class GetSpeed(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/speed-profile/#getspeed_intmotorid"""  # noqa

    address: str = field(default="/getSpeed", init=False)
    response_cls: responses.Speed = field(default=responses.Speed, init=False)
    motorID: int


# Homing


@dataclass
class Homing(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/homing/#homing_intmotorid"""  # noqa

    address: str = field(default="/homing", init=False)
    motorID: int


@dataclass
class GetHomingStatus(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/homing/#sethomingdirection_intmotorid_booldirection"""  # noqa

    address: str = field(default="/getHomingStatus", init=False)
    response_cls: responses.HomingStatus = field(
        default=responses.HomingStatus, init=False
    )
    motorID: int


@dataclass
class SetHomingDirection(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/homing/#sethomingspeed_intmotorid_floatspeed"""  # noqa

    address: str = field(default="/setHomingDirection", init=False)
    motorID: int
    direction: bool


@dataclass
class GetHomingDirection(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/homing/#gethomingdirection_intmotorid"""  # noqa

    address: str = field(default="/getHomingDirection", init=False)
    response_cls: responses.HomingDirection = field(
        default=responses.HomingDirection, init=False
    )
    motorID: int


@dataclass
class SetHomingSpeed(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/homing/#sethomingspeed_intmotorid_floatspeed"""  # noqa

    address: str = field(default="/setHomingSpeed", init=False)
    motorID: int
    speed: float


@dataclass
class GetHomingSpeed(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/homing/#gethomingspeed_intmotorid"""  # noqa

    address: str = field(default="/getHomingSpeed", init=False)
    response_cls: responses.HomingSpeed = field(
        default=responses.HomingSpeed, init=False
    )
    motorID: int


@dataclass
class GoUntil(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/homing/#gountil_intmotorid_boolact_floatspeed"""  # noqa

    address: str = field(default="/goUntil", init=False)
    motorID: int
    ACT: bool
    speed: float


@dataclass
class SetGoUntilTimeout(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/homing/#setgountiltimeout_intmotorid_inttimeout"""  # noqa

    address: str = field(default="/setGoUntilTimeout", init=False)
    motorID: int
    timeOut: int


@dataclass
class GetGoUntilTimeout(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/homing/#getgountiltimeout_intmotorid"""  # noqa

    address: str = field(default="/getGoUntilTimeout", init=False)
    response_cls: responses.GoUntilTimeout = field(
        default=responses.GoUntilTimeout, init=False
    )
    motorID: int


@dataclass
class ReleaseSw(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/homing/#releasesw_intmotorid_boolact_booldir"""  # noqa

    address: str = field(default="/releaseSw", init=False)
    motorID: int
    ACT: bool
    DIR: bool


@dataclass
class SetReleaseSwTimeout(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/homing/#setreleaseswtimeout_intmotorid_inttimeout"""  # noqa

    address: str = field(default="/setReleaseSwTimeout", init=False)
    motorID: int
    timeOut: int


@dataclass
class GetReleaseSwTimeout(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/homing/#setreleaseswtimeout_intmotorid_inttimeout"""  # noqa

    address: str = field(default="/getReleaseSwTimeout", init=False)
    response_cls: responses.ReleaseSwTimeout = field(
        default=responses.ReleaseSwTimeout, init=False
    )
    motorID: int


# Home and Limit Sensors


@dataclass
class EnableHomeSwReport(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/home-and-limit-sensers/#enablehomeswreport_intmotorid_boolenable"""  # noqa

    address: str = field(default="/enableHomeSwReport", init=False)
    response_cls: responses.HomeSw = field(default=responses.HomeSw, init=False)
    motorID: int
    enable: bool
    callback: Optional[Callable[..., None]] = None


@dataclass
class EnableSwEventReport(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/home-and-limit-sensers/#enablesweventreport_intmotorid_boolenable"""  # noqa

    address: str = field(default="/enableSwEventReport", init=False)
    response_cls: responses.SwEvent = field(default=responses.SwEvent, init=False)
    motorID: int
    enable: bool
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetHomeSw(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/home-and-limit-sensers/#gethomesw_intmotorid"""  # noqa

    address: str = field(default="/getHomeSw", init=False)
    response_cls: responses.HomeSw = field(default=responses.HomeSw, init=False)
    motorID: int


@dataclass
class EnableLimitSwReport(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/home-and-limit-sensers/#enablelimitswreport_intmotorid_boolenable"""  # noqa

    address: str = field(default="/enableLimitSwReport", init=False)
    response_cls: responses.LimitSw = field(default=responses.LimitSw, init=False)
    motorID: int
    enable: bool
    callback: Optional[Callable[..., None]] = None


@dataclass
class GetLimitSw(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/home-and-limit-sensers/#getlimitsw_intmotorid"""  # noqa

    address: str = field(default="/getLimitSw", init=False)
    response_cls: responses.LimitSw = field(default=responses.LimitSw, init=False)
    motorID: int


@dataclass
class SetHomeSwMode(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/home-and-limit-sensers/#sethomeswmode_intmotorid_boolsw_mode"""  # noqa

    address: str = field(default="/setHomeSwMode", init=False)
    motorID: int
    SW_MODE: bool


@dataclass
class GetHomeSwMode(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/home-and-limit-sensers/#gethomeswmode_intmotorid"""  # noqa

    address: str = field(default="/getHomeSwMode", init=False)
    response_cls: responses.HomeSwMode = field(default=responses.HomeSwMode, init=False)
    motorID: int


@dataclass
class SetLimitSwMode(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/home-and-limit-sensers/#setlimitswmode_intmotorid_boolsw_mode"""  # noqa

    address: str = field(default="/setLimitSwMode", init=False)
    motorID: int
    SW_MODE: bool


@dataclass
class GetLimitSwMode(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/home-and-limit-sensers/#getlimitswmode_intmotorid"""  # noqa

    address: str = field(default="/getLimitSwMode", init=False)
    response_cls: responses.LimitSwMode = field(
        default=responses.LimitSwMode, init=False
    )
    motorID: int


# Position Management


@dataclass
class SetPosition(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/position-management/#setposition_intmotorid_intnewposition"""  # noqa

    address: str = field(default="/setPosition", init=False)
    motorID: int
    newPosition: int


@dataclass
class GetPosition(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/position-management/#getposition_intmotorid"""  # noqa

    address: str = field(default="/getPosition", init=False)
    response_cls: responses.Position = field(default=responses.Position, init=False)
    motorID: int


@dataclass
class GetPositionList(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/position-management/#getpositionlist"""  # noqa

    address: str = field(default="/getPositionList", init=False)
    response_cls: responses.PositionList = field(
        default=responses.PositionList, init=False
    )


@dataclass
class ResetPos(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/position-management/#resetpos_intmotorid"""  # noqa

    address: str = field(default="/resetPos", init=False)
    motorID: int


@dataclass
class SetElPos(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/position-management/#setelpos_intmotorid_intnewfullstep_intnewmicrostep"""  # noqa

    address: str = field(default="/setElPos", init=False)
    motorID: int
    newFullstep: int
    newMicrostep: int


@dataclass
class GetElPos(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/position-management/#getelpos_intmotorid"""  # noqa

    address: str = field(default="/getElPos", init=False)
    response_cls: responses.ElPos = field(default=responses.ElPos, init=False)
    motorID: int


@dataclass
class SetMark(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/position-management/#setmark_intmotorid_intmark"""  # noqa

    address: str = field(default="/setMark", init=False)
    motorID: int
    MARK: int


@dataclass
class GetMark(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/position-management/#getmark_intmotorid"""  # noqa

    address: str = field(default="/getMark", init=False)
    response_cls: responses.Mark = field(default=responses.Mark, init=False)
    motorID: int


@dataclass
class GoHome(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/position-management/#gohome_intmotorid"""  # noqa

    address: str = field(default="/goHome", init=False)
    motorID: int


@dataclass
class GoMark(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/position-management/#gomark_intmotorid"""  # noqa

    address: str = field(default="/goMark", init=False)
    motorID: int


# Motor Control


@dataclass
class Run(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-control/#run_intmotorid_floatspeed"""  # noqa

    address: str = field(default="/run", init=False)
    motorID: int
    speed: float


@dataclass
class Move(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-control/#move_intmotorid_intstep"""  # noqa

    address: str = field(default="/move", init=False)
    motorID: int
    step: int


@dataclass
class GoTo(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-control/#goto_intmotorid_intposition"""  # noqa

    address: str = field(default="/goTo", init=False)
    motorID: int
    position: int


@dataclass
class GoToDir(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-control/#gotodir_intmotorid_booldir_intposition"""  # noqa

    address: str = field(default="/goToDir", init=False)
    motorID: int
    DIR: bool
    position: int


@dataclass
class SoftStop(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-control/#softstop_intmotorid"""  # noqa

    address: str = field(default="/softStop", init=False)
    motorID: int


@dataclass
class HardStop(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-control/#hardstop_intmotorid"""  # noqa

    address: str = field(default="/hardStop", init=False)
    motorID: int


@dataclass
class SoftHiZ(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-control/#softhiz_intmotorid"""  # noqa

    address: str = field(default="/softHiZ", init=False)
    motorID: int


@dataclass
class HardHiZ(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/motor-control/#hardhiz_intmotorid"""  # noqa

    address: str = field(default="/hardHiZ", init=False)
    motorID: int


# Electromagnetic Brake


@dataclass
class EnableElectromagnetBrake(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/brake/#enableelectromagnetbrake_intmotorid_boolenable"""  # noqa

    address: str = field(default="/enableElectromagnetBrake", init=False)
    motorID: int
    enable: bool


@dataclass
class Activate(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/brake/#activate_intmotorid_boolstate"""  # noqa

    address: str = field(default="/activate", init=False)
    motorID: int
    state: bool


@dataclass
class Free(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/brake/#free_intmotorid_boolstate"""  # noqa

    address: str = field(default="/free", init=False)
    motorID: int
    state: bool


@dataclass
class SetBrakeTransitionDuration(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/brake/#setbraketransitionduration_intmotorid_intduration"""  # noqa

    address: str = field(default="/setBrakeTransitionDuration", init=False)
    motorID: int
    duration: int


@dataclass
class GetBrakeTransitionDuration(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/brake/#getbraketransitionduration_intmotorid"""  # noqa

    address: str = field(default="/getBrakeTransitionDuration", init=False)
    response_cls: responses.BrakeTransitionDuration = field(
        default=responses.BrakeTransitionDuration, init=False
    )
    motorID: int


# Servo Mode


@dataclass
class EnableServoMode(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/servo-mode/#enableservomode_intmotorid_boolenable"""  # noqa

    address: str = field(default="/enableServoMode", init=False)
    motorID: int
    enable: bool


@dataclass
class SetServoParam(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/servo-mode/#setservoparam_intmotorid_floatkp_floatki_floatkd"""  # noqa

    address: str = field(default="/setServoParam", init=False)
    motorID: int
    kP: float
    kI: float
    kD: float


@dataclass
class GetServoParam(OSCGetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/servo-mode/#getservoparam_intmotorid"""  # noqa

    address: str = field(default="/getServoParam", init=False)
    response_cls: responses.ServoParam = field(default=responses.ServoParam, init=False)
    motorID: int


@dataclass
class SetTargetPosition(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/servo-mode/#settargetposition_intmotorid_intposition"""  # noqa

    address: str = field(default="/setTargetPosition", init=False)
    motorID: int
    position: int


@dataclass
class SetTargetPositionList(OSCSetCommand):
    """Documentation: https://ponoor.com/en/docs/step-series/osc-command-reference/servo-mode/#settargetpositionlist_intposition1_intposition2_intposition3_intposition4"""  # noqa

    address: str = field(default="/setTargetPositionList", init=False)
    position1: int
    position2: int
    position3: int
    position4: int
    position5: int = None
    position6: int = None
    position7: int = None
    position8: int = None
