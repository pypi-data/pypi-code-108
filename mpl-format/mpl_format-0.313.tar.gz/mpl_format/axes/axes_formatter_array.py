from typing import Iterator, Tuple

from numpy import ndarray, empty_like

from mpl_format.axes.axes_formatter import AxesFormatter


class AxesFormatterArray(object):

    def __init__(self, axes: ndarray):
        """
        Create a new AxesFormatterArray

        :param axes: Array of Axes instances.
        """
        self._axes = empty_like(axes, dtype=AxesFormatter)
        if axes.ndim == 1:
            for i in range(axes.shape[0]):
                self._axes[i] = AxesFormatter(axes[i])
        elif axes.ndim == 2:
            for i in range(axes.shape[0]):
                for j in range(axes.shape[1]):
                    self._axes[i, j] = AxesFormatter(axes[i, j])

    def __getitem__(self, item) -> AxesFormatter:

        return self._axes[item]

    @property
    def flat(self) -> Iterator[AxesFormatter]:
        return self._axes.flat

    @property
    def n_dim(self) -> int:
        return self._axes.ndim

    @property
    def size(self) -> int:
        return self._axes.size

    @property
    def shape(self) -> Tuple[int, ...]:
        return self._axes.shape
