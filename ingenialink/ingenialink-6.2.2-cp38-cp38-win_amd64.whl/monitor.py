from enum import Enum

from ._ingenialink import ffi, lib
from ingenialink.utils._utils import raise_null, raise_err, to_ms
from ingenialink.register import _get_reg_id


class MONITOR_TRIGGER(Enum):
    """Monitor Trigger Types."""
    IMMEDIATE = lib.IL_MONITOR_TRIGGER_IMMEDIATE
    """Immediate."""
    MOTION = lib.IL_MONITOR_TRIGGER_MOTION
    """Motion start."""
    POS = lib.IL_MONITOR_TRIGGER_POS
    """Positive."""
    NEG = lib.IL_MONITOR_TRIGGER_NEG
    """Negative."""
    WINDOW = lib.IL_MONITOR_TRIGGER_WINDOW
    """Exit window."""
    DIN = lib.IL_MONITOR_TRIGGER_DIN
    """Digital input."""


class Monitor:
    """Monitor.

    Args:
        servo (Servo): Servo instance.

    Raises:
        ILCreationError: If the monitor could not be created.

    """
    def __init__(self, servo):
        monitor = lib.il_monitor_create(servo._cffi_servo)
        raise_null(monitor)

        self._monitor = ffi.gc(monitor, lib.il_monitor_destroy)

        self._acq = ffi.new('il_monitor_acq_t **')

    def start(self):
        """Start the monitor."""
        r = lib.il_monitor_start(self._monitor)
        raise_err(r)

    def stop(self):
        """Stop the monitor."""
        r = lib.il_monitor_stop(self._monitor)
        raise_err(r)

    def wait(self, timeout):
        """Wait until the current acquisition finishes.

        Args:
            timeout (int, float): Timeout (s).

        """
        r = lib.il_monitor_wait(self._monitor, to_ms(timeout))
        raise_err(r)

    @property
    def data(self):
        """Obtain configured data.

        Returns:
            tuple: Current acquisition time and data for all channels.

        """
        lib.il_monitor_data_get(self._monitor, self._acq)
        acq = ffi.cast('il_monitor_acq_t *', self._acq[0])

        t = list(acq.t[0:acq.cnt])

        d = []
        for ch in range(lib.IL_MONITOR_CH_NUM):
            if acq.d[ch] != ffi.NULL:
                d.append(list(acq.d[ch][0:acq.cnt]))
            else:
                d.append(None)

        return t, d

    def configure(self, t_s, delay_samples=0, max_samples=0):
        """Configure the monitor parameters.

        Args:
            t_s (int, float): Sampling period (s, resolution: 1e-4 s).
            delay_samples (int, optional): Delay samples.
            max_samples (int, optional): Maximum acquisition samples.

        """
        r = lib.il_monitor_configure(self._monitor, int(t_s * 1e6),
                                     delay_samples, max_samples)
        raise_err(r)

    def ch_configure(self, ch, reg):
        """Configure a channel mapping.

        Args:
            ch (int): Channel.
            reg (str, Register): Register to be mapped to the channel.

        """
        _reg, _id = _get_reg_id(reg)
        r = lib.il_monitor_ch_configure(self._monitor, ch, _reg, _id)
        raise_err(r)

    def ch_disable(self, ch):
        """Disable a channel.

        Args:
            ch (int): Channel identifier.

        """
        r = lib.il_monitor_ch_disable(self._monitor, ch)
        raise_err(r)

    def ch_disable_all(self):
        """Disable all channels."""
        r = lib.il_monitor_ch_disable_all(self._monitor)
        raise_err(r)

    def trigger_configure(self, mode, delay_samples=0, source=None, th_pos=0.,
                          th_neg=0., din_msk=0):
        """Configure the trigger.

        Args:
            mode (MONITOR_TRIGGER): Trigger mode.
            delay_samples (int, optional): Delay samples.
            source (str, Register, optional): Source register, required for
                MONITOR_TRIGGER.POS, MONITOR_TRIGGER.NEG and
                MONITOR_TRIGGER.WINDOW.
            th_pos (int, float, optional): Positive threshold, used for
                MONITOR_TRIGGER.POS, MONITOR_TRIGGER.WINDOW
            th_neg (int, float, optional): Negative threshold, used for
                MONITOR_TRIGGER.NEG, MONITOR_TRIGGER.WINDOW
            din_msk (int, optional): Digital input mask, used for
                MONITOR_TRIGGER.DIN

        """
        if not isinstance(mode, MONITOR_TRIGGER):
            raise TypeError('Invalid trigger mode')

        _source_required = (MONITOR_TRIGGER.POS, MONITOR_TRIGGER.NEG,
                            MONITOR_TRIGGER.WINDOW)

        if mode in _source_required:
            _reg, _id = _get_reg_id(source)
        else:
            _reg, _id = ffi.NULL, ffi.NULL

        r = lib.il_monitor_trigger_configure(
                self._monitor, mode.value, delay_samples, _reg, _id, th_pos,
                th_neg, din_msk)
        raise_err(r)
