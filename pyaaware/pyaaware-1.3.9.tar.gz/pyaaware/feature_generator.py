import numpy as np

import pyaaware


class FeatureGenerator:
    def __init__(self,
                 frame_size: (None, int) = None,
                 feature_mode: (None, str) = None,
                 num_classes: (None, int) = None,
                 truth_mutex: (None, int) = None,
                 bin_start: (None, int) = None,
                 bin_end: (None, int) = None) -> None:
        self._fg = pyaaware._FeatureGenerator()
        self._config = self._fg.config()

        if frame_size is not None:
            self._config.frame_size = frame_size

        if feature_mode is not None:
            self._config.feature_mode = feature_mode

        if num_classes is not None:
            self._config.num_classes = num_classes

        if truth_mutex is not None:
            self._config.truth_mutex = truth_mutex

        if bin_start is not None:
            self._config.bin_start = bin_start

        if bin_end is not None:
            self._config.bin_end = bin_end

        self._fg.config(self._config)
        self._bins = self._config.bin_end - self._config.bin_start + 1

    @property
    def frame_size(self) -> int:
        return self._config.frame_size

    @property
    def feature_mode(self) -> str:
        return self._config.feature_mode

    @property
    def num_classes(self) -> int:
        return self._config.num_classes

    @property
    def truth_mutex(self) -> int:
        return self._config.truth_mutex

    @property
    def bin_start(self) -> int:
        return self._config.bin_start

    @property
    def bin_end(self) -> int:
        return self._config.bin_end

    @property
    def num_bands(self) -> int:
        return self._fg.num_bands()

    @property
    def stride(self) -> int:
        return self._fg.stride()

    @property
    def step(self) -> int:
        return self._fg.step()

    @property
    def decimation(self) -> int:
        return self._fg.decimation()

    @property
    def feature_size(self) -> int:
        return self._fg.feature_size()

    @property
    def feature_len(self) -> int:
        return self.num_bands * self.stride

    def reset(self) -> None:
        self._fg.reset()

    def execute_all(self, xf: np.ndarray, truth_in: (None, np.ndarray) = None) -> (np.ndarray, np.ndarray):
        assert xf.ndim == 3 or xf.ndim == 2

        has_channels = xf.ndim == 3
        bins = xf.shape[0]
        assert bins == self._bins

        if has_channels:
            channels = xf.shape[1]
            input_frames = xf.shape[2]
        else:
            channels = 1
            input_frames = xf.shape[1]

        if truth_in is not None:
            assert truth_in.ndim == xf.ndim
            assert truth_in.shape[0] == self.num_classes
            if has_channels:
                assert truth_in.shape[1] == channels
                assert truth_in.shape[2] == input_frames
            else:
                assert truth_in.shape[1] == input_frames

        output_frames = int(input_frames / (self.step * self.decimation))

        if has_channels:
            feature = np.empty((self.feature_len, channels, output_frames), dtype=np.single)
            truth = np.empty((self.num_classes, channels, output_frames), dtype=np.single)
        else:
            feature = np.empty((self.feature_len, output_frames), dtype=np.single)
            truth = np.empty((self.num_classes, output_frames), dtype=np.single)

        for channel in range(channels):
            output_frame = 0
            for input_frame in range(input_frames):
                if truth_in is not None:
                    if has_channels:
                        self._fg.execute(xf[:, channel, input_frame], truth_in[:, channel, input_frame])
                    else:
                        self._fg.execute(xf[:, input_frame], truth_in[:, input_frame])
                else:
                    if has_channels:
                        self._fg.execute(xf[:, channel, input_frame])
                    else:
                        self._fg.execute(xf[:, input_frame])

                if self._fg.eof():
                    if has_channels:
                        feature[:, channel, output_frame] = self._fg.feature()
                        truth[:, channel, output_frame] = self._fg.truth()
                    else:
                        feature[:, output_frame] = self._fg.feature()
                        truth[:, output_frame] = self._fg.truth()
                    output_frame += 1

        return feature, truth

    def execute(self, xf: np.ndarray, truth_in: (None, np.ndarray) = None) -> None:
        assert xf.ndim == 1

        bins = xf.shape[0]
        assert bins == self._bins

        if truth_in is not None:
            assert truth_in.ndim == 1
            assert truth_in.shape[0] == self.num_classes

        if truth_in is not None:
            self._fg.execute(xf, truth_in)
        else:
            self._fg.execute(xf)

    def eof(self) -> bool:
        return self._fg.eof()

    def feature(self) -> np.ndarray:
        return self._fg.feature()

    def truth(self) -> np.ndarray:
        return self._fg.truth()
