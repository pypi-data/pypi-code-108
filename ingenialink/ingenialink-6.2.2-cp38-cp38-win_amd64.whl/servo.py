from abc import ABC, abstractmethod

from ._ingenialink import ffi, lib
from ingenialink.utils._utils import *
from .network import Network
from .register import REG_DTYPE

from .constants import *


class SERVO_STATE(Enum):
    """Servo states."""
    NRDY = lib.IL_SERVO_STATE_NRDY
    """Not ready to switch on."""
    DISABLED = lib.IL_SERVO_STATE_DISABLED
    """Switch on disabled."""
    RDY = lib.IL_SERVO_STATE_RDY
    """Ready to be switched on."""
    ON = lib.IL_SERVO_STATE_ON
    """Power switched on."""
    ENABLED = lib.IL_SERVO_STATE_ENABLED
    """Enabled."""
    QSTOP = lib.IL_SERVO_STATE_QSTOP
    """Quick stop."""
    FAULTR = lib.IL_SERVO_STATE_FAULTR
    """Fault reactive."""
    FAULT = lib.IL_SERVO_STATE_FAULT
    """Fault."""


class SERVO_FLAGS(Enum):
    """Status Flags."""
    TGT_REACHED = lib.IL_SERVO_FLAG_TGT_REACHED
    """Target reached."""
    ILIM_ACTIVE = lib.IL_SERVO_FLAG_ILIM_ACTIVE
    """Internal limit active."""
    HOMING_ATT = lib.IL_SERVO_FLAG_HOMING_ATT
    """(Homing) attained."""
    HOMING_ERR = lib.IL_SERVO_FLAG_HOMING_ERR
    """(Homing) error."""
    PV_VZERO = lib.IL_SERVO_FLAG_PV_VZERO
    """(PV) Vocity speed is zero."""
    PP_SPACK = lib.IL_SERVO_FLAG_PP_SPACK
    """(PP) SP acknowledge."""
    IP_ACTIVE = lib.IL_SERVO_FLAG_IP_ACTIVE
    """(IP) active."""
    CS_FOLLOWS = lib.IL_SERVO_FLAG_CS_FOLLOWS
    """(CST/CSV/CSP) follow command value."""
    FERR = lib.IL_SERVO_FLAG_FERR
    """(CST/CSV/CSP/PV) following error."""
    IANGLE_DET = lib.IL_SERVO_FLAG_IANGLE_DET
    """Initial angle determination finished."""


class SERVO_MODE(Enum):
    """Operation Mode."""
    OLV = lib.IL_SERVO_MODE_OLV
    """Open loop (vector mode)."""
    OLS = lib.IL_SERVO_MODE_OLS
    """Open loop (scalar mode)."""
    PP = lib.IL_SERVO_MODE_PP
    """Profile position mode."""
    VEL = lib.IL_SERVO_MODE_VEL
    """Velocity mode."""
    PV = lib.IL_SERVO_MODE_PV
    """Profile velocity mode."""
    PT = lib.IL_SERVO_MODE_PT
    """Profile torque mode."""
    HOMING = lib.IL_SERVO_MODE_HOMING
    """Homing mode."""
    IP = lib.IL_SERVO_MODE_IP
    """Interpolated position mode."""
    CSP = lib.IL_SERVO_MODE_CSP
    """Cyclic sync position mode."""
    CSV = lib.IL_SERVO_MODE_CSV
    """Cyclic sync velocity mode."""
    CST = lib.IL_SERVO_MODE_CST
    """Cyclic sync torque mode."""


class SERVO_UNITS_TORQUE(Enum):
    """Torque Units."""
    NATIVE = lib.IL_UNITS_TORQUE_NATIVE
    """Native"""
    MN = lib.IL_UNITS_TORQUE_MNM
    """Millinewtons*meter."""
    N = lib.IL_UNITS_TORQUE_NM
    """Newtons*meter."""


class SERVO_UNITS_POS(Enum):
    """Position Units."""
    NATIVE = lib.IL_UNITS_POS_NATIVE
    """Native."""
    REV = lib.IL_UNITS_POS_REV
    """Revolutions."""
    RAD = lib.IL_UNITS_POS_RAD
    """Radians."""
    DEG = lib.IL_UNITS_POS_DEG
    """Degrees."""
    UM = lib.IL_UNITS_POS_UM
    """Micrometers."""
    MM = lib.IL_UNITS_POS_MM
    """Millimeters."""
    M = lib.IL_UNITS_POS_M
    """Meters."""


class SERVO_UNITS_VEL(Enum):
    """Velocity Units."""
    NATIVE = lib.IL_UNITS_VEL_NATIVE
    """Native."""
    RPS = lib.IL_UNITS_VEL_RPS
    """Revolutions per second."""
    RPM = lib.IL_UNITS_VEL_RPM
    """Revolutions per minute."""
    RAD_S = lib.IL_UNITS_VEL_RAD_S
    """Radians/second."""
    DEG_S = lib.IL_UNITS_VEL_DEG_S
    """Degrees/second."""
    UM_S = lib.IL_UNITS_VEL_UM_S
    """Micrometers/second."""
    MM_S = lib.IL_UNITS_VEL_MM_S
    """Millimeters/second."""
    M_S = lib.IL_UNITS_VEL_M_S
    """Meters/second."""


class SERVO_UNITS_ACC(Enum):
    """Acceleration Units."""
    NATIVE = lib.IL_UNITS_ACC_NATIVE
    """Native."""
    REV_S2 = lib.IL_UNITS_ACC_REV_S2
    """Revolutions/second^2."""
    RAD_S2 = lib.IL_UNITS_ACC_RAD_S2
    """Radians/second^2."""
    DEG_S2 = lib.IL_UNITS_ACC_DEG_S2
    """Degrees/second^2."""
    UM_S2 = lib.IL_UNITS_ACC_UM_S2
    """Micrometers/second^2."""
    MM_S2 = lib.IL_UNITS_ACC_MM_S2
    """Millimeters/second^2."""
    M_S2 = lib.IL_UNITS_ACC_M_S2
    """Meters/second^2."""


@ffi.def_extern()
def _on_state_change_cb(ctx, state, flags, subnode):
    """On state change callback shim."""
    cb = ffi.from_handle(ctx)
    cb(SERVO_STATE(state), flags, subnode)


@ffi.def_extern()
def _on_emcy_cb(ctx, code):
    """On emergency callback shim."""
    cb = ffi.from_handle(ctx)
    cb(code)


class Servo(ABC):
    """Declaration of a general Servo object.

    Args:
        target (str, int): Target ID of the servo.
        dictionary (object):  Path to the dictionary file.

    Raises:
        ILCreationError: If the servo cannot be created.

    """
    _raw_read = {REG_DTYPE.U8: ['uint8_t *', lib.il_servo_raw_read_u8],
                 REG_DTYPE.S8: ['int8_t *', lib.il_servo_raw_read_s8],
                 REG_DTYPE.U16: ['uint16_t *', lib.il_servo_raw_read_u16],
                 REG_DTYPE.S16: ['int16_t *', lib.il_servo_raw_read_s16],
                 REG_DTYPE.U32: ['uint32_t *', lib.il_servo_raw_read_u32],
                 REG_DTYPE.S32: ['int32_t *', lib.il_servo_raw_read_s32],
                 REG_DTYPE.U64: ['uint64_t *', lib.il_servo_raw_read_u64],
                 REG_DTYPE.S64: ['int64_t *', lib.il_servo_raw_read_s64],
                 REG_DTYPE.FLOAT: ['float *', lib.il_servo_raw_read_float],
                 REG_DTYPE.STR: ['uint32_t *', lib.il_servo_raw_read_str]}
    """dict: Data buffer and function mappings for raw read operation."""

    _raw_write = {REG_DTYPE.U8: lib.il_servo_raw_write_u8,
                  REG_DTYPE.S8: lib.il_servo_raw_write_s8,
                  REG_DTYPE.U16: lib.il_servo_raw_write_u16,
                  REG_DTYPE.S16: lib.il_servo_raw_write_s16,
                  REG_DTYPE.U32: lib.il_servo_raw_write_u32,
                  REG_DTYPE.S32: lib.il_servo_raw_write_s32,
                  REG_DTYPE.U64: lib.il_servo_raw_write_u64,
                  REG_DTYPE.S64: lib.il_servo_raw_write_s64,
                  REG_DTYPE.FLOAT: lib.il_servo_raw_write_float}
    """dict: Function mappings for raw write operation."""

    def __init__(self, target):
        self.target = target

        self._info = None

        self.name = DEFAULT_DRIVE_NAME
        """str: Obtains the servo name."""
        self.full_name = None
        """str: Obtains the servo full name."""

    @abstractmethod
    def get_state(self, subnode=1):
        raise NotImplementedError

    @abstractmethod
    def start_status_listener(self):
        raise NotImplementedError

    @abstractmethod
    def stop_status_listener(self):
        raise NotImplementedError

    @abstractmethod
    def subscribe_to_status(self, callback):
        raise NotImplementedError

    @abstractmethod
    def unsubscribe_from_status(self, callback):
        raise NotImplementedError

    @abstractmethod
    def reload_errors(self, dictionary):
        raise NotImplementedError

    @abstractmethod
    def load_configuration(self, config_file, subnode=None):
        raise NotImplementedError

    @abstractmethod
    def save_configuration(self, config_file, subnode=None):
        raise NotImplementedError

    @abstractmethod
    def store_parameters(self, subnode=None):
        raise NotImplementedError

    @abstractmethod
    def restore_parameters(self, subnode=None):
        raise NotImplementedError

    @abstractmethod
    def read(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def write(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def disable(self, subnode=1):
        raise NotImplementedError

    @abstractmethod
    def enable(self, timeout=2., subnode=1):
        raise NotImplementedError

    @abstractmethod
    def fault_reset(self, subnode=1):
        raise NotImplementedError

    @abstractmethod
    def is_alive(self):
        raise NotImplementedError

    @property
    def info(self):
        """dict: Obtains the servo information."""
        return self._info

    @property
    def errors(self):
        raise NotImplementedError

    @property
    def subnodes(self):
        raise NotImplementedError
