import numpy as np

import pyaaware


class InverseTransform:
    def __init__(self,
                 N: (None, int) = None,
                 R: (None, int) = None,
                 bin_start: (None, int) = None,
                 bin_end: (None, int) = None,
                 ttype: (None, str) = None,
                 gain: (None, np.single) = None) -> None:
        self._it = pyaaware._InverseTransform()
        self._config = self._it.config()

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

        if gain is not None:
            self._config.gain = gain

        self._it.config(self._config, False)
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
    def gain(self) -> np.single:
        return self._config.gain

    @property
    def bins(self) -> int:
        return self._bins

    def reset(self) -> None:
        self._it.reset()

    def execute_all(self, xf: np.ndarray) -> np.ndarray:
        assert xf.ndim == 3 or xf.ndim == 2

        has_channels = xf.ndim == 3
        bins = np.shape(xf)[0]
        assert bins == self._bins

        if has_channels:
            channels = xf.shape[1]
            frames = xf.shape[2]
        else:
            channels = 1
            frames = xf.shape[1]

        samples = frames * self.R

        if has_channels:
            yt = np.empty((samples, channels), dtype=np.single)
        else:
            yt = np.empty(samples, dtype=np.single)

        for channel in range(channels):
            for frame in range(frames):
                start = frame * self.R
                stop = start + self.R
                tmp = np.empty(self.R, dtype=np.single)
                if has_channels:
                    self._it.execute(xf[:, channel, frame], tmp)
                    yt[start:stop, channel] = tmp
                else:
                    self._it.execute(xf[:, frame], tmp)
                    yt[start:stop] = tmp
            self.reset()

        return yt

    def execute(self, xf: np.ndarray) -> np.ndarray:
        assert xf.ndim == 1
        assert xf.shape[0] == self._bins

        yt = np.empty(self.R, dtype=np.single)
        self._it.execute(xf, yt)
        return yt
