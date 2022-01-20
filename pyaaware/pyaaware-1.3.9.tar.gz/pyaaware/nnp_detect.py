from typing import List

import numpy as np

import pyaaware


class NNPDetect:
    def __init__(self,
                 channels: (None, int) = None,
                 classes: (None, int) = None,
                 risethresh: (None, List[np.single]) = None,
                 fallthresh: (None, List[np.single]) = None,
                 riseframes: (None, List[int]) = None,
                 fallframes: (None, List[int]) = None,
                 hold: (None, List[int]) = None) -> None:
        self._nnp_detect = pyaaware._NNPDetect()
        self._config = self._nnp_detect.config()

        if channels is not None:
            self._config.channels = channels

        if classes is not None:
            self._config.classes = classes

        if risethresh is not None:
            self._config.risethresh = risethresh

        if fallthresh is not None:
            self._config.fallthresh = fallthresh

        if riseframes is not None:
            self._config.riseframes = riseframes

        if fallframes is not None:
            self._config.fallframes = fallframes

        if hold is not None:
            self._config.hold = hold

        self._nnp_detect.config(self._config)

    @property
    def channels(self) -> int:
        return self._config.channels

    @property
    def classes(self) -> int:
        return self._config.classes

    @property
    def risethresh(self) -> List[np.single]:
        return self._config.risethresh

    @property
    def fallthresh(self) -> List[np.single]:
        return self._config.fallthresh

    @property
    def riseframes(self) -> List[int]:
        return self._config.riseframes

    @property
    def fallframes(self) -> List[int]:
        return self._config.fallframes

    @property
    def hold(self) -> List[int]:
        return self._config.hold

    def reset(self):
        self._nnp_detect.reset()

    def execute_all(self, x: np.ndarray, eof: np.ndarray) -> np.ndarray:
        assert x.ndim == 3
        assert x.shape[0] == self.channels
        assert x.shape[1] == self.classes
        frames = x.shape[2]

        assert eof.ndim == 1
        assert eof.shape[0] == frames

        y = np.empty((self.channels, self.classes, frames), dtype=int)
        for in_idx in range(frames):
            y[:, :, in_idx] = self._nnp_detect.execute(x[:, :, in_idx], bool(eof[in_idx]))

        return y

    def execute(self, x: np.ndarray, eof: bool) -> np.ndarray:
        assert x.ndim == 2
        assert x.shape[0] == self.channels
        assert x.shape[1] == self.classes

        return self._nnp_detect.execute(x, eof)
