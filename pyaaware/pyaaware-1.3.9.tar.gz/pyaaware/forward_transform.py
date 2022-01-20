import numpy as np

import pyaaware


class ForwardTransform:
    def __init__(self,
                 N: (None, int) = None,
                 R: (None, int) = None,
                 bin_start: (None, int) = None,
                 bin_end: (None, int) = None,
                 ttype: (None, str) = None) -> None:
        self._ft = pyaaware._ForwardTransform()
        self._config = self._ft.config()

        if N is not None:
            self._config.N = N

        if R is not None:
            self._config.R = R

        if bin_start is not None:
            self._config.bin_start = bin_start

        if bin_end is not None:
            self._config.bin_end = bin_end

        if ttype is not None:
            self._config.ttype = ttype

        self._ft.config(self._config, False)
        self._bins = self._config.bin_end - self._config.bin_start + 1

    @property
    def N(self) -> int:
        return self._config.N

    @property
    def R(self) -> int:
        return self._config.R

    @property
    def bin_start(self) -> int:
        return self._config.bin_start

    @property
    def bin_end(self) -> int:
        return self._config.bin_end

    @property
    def ttype(self) -> str:
        return self._config.ttype

    @property
    def bins(self) -> int:
        return self._bins

    def reset(self) -> None:
        self._ft.reset()

    def execute_all(self, xt: np.ndarray) -> np.ndarray:
        assert xt.ndim == 2 or xt.ndim == 1

        has_channels = xt.ndim == 2
        samples = xt.shape[0]
        frames = int(np.ceil(samples / self.R) + (self.N - self.R) / self.R)
        x = np.pad(xt, ((0, frames * self.R - samples), (0, 0)), 'constant')

        if has_channels:
            channels = xt.shape[1]
            yf = np.empty((self._bins, channels, frames), dtype=np.csingle)
        else:
            channels = 1
            yf = np.empty((self._bins, frames), dtype=np.csingle)

        for channel in range(channels):
            for frame in range(frames):
                start = frame * self.R
                stop = start + self.R
                tmp = np.empty(self._bins, dtype=np.csingle)
                if has_channels:
                    self._ft.execute(x[start:stop, channel], tmp)
                    yf[:, channel, frame] = tmp
                else:
                    self._ft.execute(x[start:stop], tmp)
                    yf[:, frame] = tmp
            self.reset()

        return yf

    def execute(self, xt: np.ndarray) -> np.ndarray:
        assert xt.ndim == 1
        assert xt.shape[0] == self.R

        yf = np.empty(self._bins, dtype=np.csingle)
        self._ft.execute(xt, yf)
        return yf

    def energy(self, x: np.ndarray) -> np.single:
        return self._ft.energy(x)
