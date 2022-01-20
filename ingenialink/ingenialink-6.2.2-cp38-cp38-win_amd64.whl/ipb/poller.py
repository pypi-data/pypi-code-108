from .._ingenialink import ffi, lib
from ingenialink.utils._utils import raise_null, raise_err, to_ms
from ingenialink.register import _get_reg_id
from ingenialink.ipb.servo import IPBServo
from ingenialink.poller import Poller


class IPBPoller(Poller):
    """IPB poller.

    Args:
        servo (IPBServo): Servo.
        num_channels (int): Number of channels.

    Raises:
        ILCreationError: If the poller could not be created.

    """
    def __init__(self, servo, num_channels):
        super(IPBPoller, self).__init__(servo, num_channels)
        poller = lib.il_poller_create(servo._cffi_servo, num_channels)
        raise_null(poller)

        self._poller = ffi.gc(poller, lib.il_poller_destroy)

        self._n_ch = num_channels
        self._acq = ffi.new('il_poller_acq_t **')

    def start(self):
        """Start poller."""
        r = lib.il_poller_start(self._poller)
        raise_err(r)

    def stop(self):
        """Stop poller."""
        lib.il_poller_stop(self._poller)

    def configure(self, t_s, sz):
        """Configure the poller.

        Args:
            t_s (int, float): Polling period (s).
            sz (int): Buffer size.

        """
        r = lib.il_poller_configure(self._poller, to_ms(t_s), sz)
        raise_err(r)

    def ch_configure(self, ch, reg):
        """Configure a poller channel mapping.

        Args:
            ch (int): Channel to be configured.
            reg (Register): Register to associate to the given channel.

        Raises:
            TypeError: If the register is not valid.

        """
        _reg, _id = _get_reg_id(reg)
        r = lib.il_poller_ch_configure(self._poller, ch, _reg, _id)
        raise_err(r)

    def ch_disable(self, ch):
        """Disable a channel.

        Args:
            ch (int): Channel to be disabled.

        """
        r = lib.il_poller_ch_disable(self._poller, ch)
        raise_err(r)

    def ch_disable_all(self):
        """Disable all channels."""
        r = lib.il_poller_ch_disable_all(self._poller)
        raise_err(r)

    @property
    def data(self):
        """Obtains processed data.

        Returns:
            tuple (list, list, bool): Time vector, array of data vectors and a
                flag indicating if data was lost.

        """
        lib.il_poller_data_get(self._poller, self._acq)
        acq = ffi.cast('il_poller_acq_t *', self._acq[0])

        t = list(acq.t[0:acq.cnt])

        d = []
        for ch in range(self._n_ch):
            if acq.d[ch] != ffi.NULL:
                d.append(list(acq.d[ch][0:acq.cnt]))
            else:
                d.append(None)

        return t, d, bool(acq.lost)
