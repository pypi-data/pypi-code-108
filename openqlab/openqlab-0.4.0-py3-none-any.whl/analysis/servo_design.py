""":obj:`openqlab.ServoDesign` helps with designing a standard servo circuit."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from warnings import warn

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from numpy import ndarray
from pandas import DataFrame, Series
from pandas.core.indexes.numeric import Float64Index
from scipy import signal
from tabulate import tabulate  # type: ignore

from openqlab import plots
from openqlab.conversion import db
from openqlab.conversion.utils import human_readable
from openqlab.io import DataContainer


def _handle_keysight_files(df: DataContainer) -> DataContainer:
    value = df.copy()
    # Extra handling for Keysight data_files
    columns = ["Amplitude (Vpp)", "Gain (dB)", "Phase (deg)"]
    if value.index.name == "Frequency (Hz)" and value.columns.tolist() == columns:
        del value["Amplitude (Vpp)"]
    return value


class Filter(ABC):
    """
    A container for a second-order analog filter section. Poles and zeros are in units of Hz.

    Parameters
    ----------
    description: :obj:`str`
        A short description of this filter section
    z: :obj:`array-like`
        A zero or list of zeros
    p: :obj:`array-like`
        A pole or list of poles
    k: :obj:`float`
        Gain
    """

    def __init__(
        self,
        corner_frequency: float,
        second_parameter: Optional[float] = None,
        enabled: bool = True,
    ) -> None:
        self._corner_frequency = corner_frequency
        self._second_parameter = second_parameter
        self._enabled = enabled
        self.update()

    def update(self) -> None:
        z, p, k = self.calculate()
        self._zeros = np.atleast_1d(z)
        self._poles = np.atleast_1d(p)
        self._gain = k
        if len(self._zeros) > 2 or len(self._poles) > 2:
            raise ValueError("Filters of higher than second order are not supported.")

    @abstractmethod
    def calculate(self):
        """
        Calculate must be implemented by the specific filter class.

        It should recalculate the zpk and return it.

        Returns
        -------
        :code:`z, p, k`
        """

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, state):
        if not isinstance(state, bool):
            raise TypeError("State has to be a boolean value.")
        self._enabled = state
        self.update()

    @property
    def corner_frequency(self):
        return self._corner_frequency

    @corner_frequency.setter
    def corner_frequency(self, value: float):
        self._corner_frequency = value
        self.update()

    @property
    def second_parameter(self):
        return self._second_parameter

    @second_parameter.setter
    def second_parameter(self, value: Optional[float]):
        self._second_parameter = value
        self.update()

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    def description_long(self) -> str:
        # what is this for?
        return self.description

    @property
    def zeros(self) -> ndarray:
        return self._zeros

    @property
    def poles(self) -> ndarray:
        return self._poles

    @property
    def gain(self) -> float:
        return self._gain

    def discrete_SOS(
        self, sampling_frequency: float
    ) -> ndarray:  # pylint: disable=invalid-name
        """
        Return a discrete-time second order section of this filter, with sampling
        frequency `sampling_frequency`.
        """
        return signal.zpk2sos(*self.discrete_zpk(sampling_frequency))

    def discrete_zpk(self, sampling_frequency: float) -> Tuple[ndarray, ndarray, float]:
        """
        Return the discrete-time transfer function of this filter, evaluated
        for a sampling frequency of `sampling_frequency`.
        """
        z, p, k = self._prewarp(sampling_frequency)
        return signal.bilinear_zpk(z, p, k, sampling_frequency)

    def _prewarp(self, sampling_frequency: float) -> Tuple[ndarray, ndarray, float]:
        """
        Prewarp frequencies of poles and zeros, to correct for the nonlinear
        mapping of frequencies between continuous-time and discrete-time domain.

        Parameters
        ----------
        sampling_frequency: :obj:`float`
            the sampling frequency

        Returns
        -------
        z: :obj:`numpy.ndarray`
            prewarped zeroes
        p: :obj:`numpy.ndarray`
            prewarped poles
        """

        def warp(x):
            return (
                2
                * sampling_frequency
                * x
                / abs(x)
                * np.tan(abs(x / sampling_frequency) * np.pi)
            )

        # since we're calculating in Hz, we need to scale the gain as well
        # by 2pi for each pole and 1/2pi for each zero
        gain: float = self._gain * (2 * np.pi) ** self._relative_degree()
        return warp(self._zeros), warp(self._poles), gain

    def _relative_degree(self) -> int:
        return len(self._poles) - len(self._zeros)


class Integrator(Filter):
    """
    Create an integrator with corner frequency 'corner_frequency', compensated for unity gain at high frequencies.

    Parameters
    ----------
    corner_frequency: :obj:`float`
        The corner frequency.
    sF: :obj:`float`, optional
        Frequency were the ~1/f slope starts, defaults to 0.001 * `corner_frequency`.
    """

    def calculate(self) -> Tuple[float, float, float]:
        z = -self.corner_frequency
        if self.second_parameter is None:
            self.second_parameter = self.corner_frequency * 0.001
        p = -self.second_parameter
        k = 1.0  # Gain = 1
        return z, p, k

    @property
    def description(self) -> str:
        return "Int {0}, Slope {1}".format(
            human_readable(self.corner_frequency, "Hz"),
            human_readable(self.second_parameter, "Hz"),
        )

    @property
    def sF(self):
        return self.second_parameter

    @sF.setter
    def sF(self, value):
        self.second_parameter = value


class Differentiator(Filter):
    """
    Create a differentiator with corner frequency `corner_frequency`,
    compensated for unity gain at low frequencies.

    Parameters
    ----------
    corner_frequency: :obj:`float`
        The corner frequency.
    sF: :obj:`float`, optional
        Frequency were the ~f slope stops, defaults to 10 * `corner_frequency`.

    """

    def calculate(self) -> Tuple[float, float, float]:
        z = -self.corner_frequency
        if self.second_parameter is None:
            self.second_parameter = self.corner_frequency * 10
        p = -self.second_parameter
        k = self.second_parameter / self.corner_frequency
        return z, p, k

    @property
    def description(self) -> str:
        return "Diff {0}, Slope {1}".format(
            human_readable(self.corner_frequency, "Hz"),
            human_readable(self.second_parameter, "Hz"),
        )

    @property
    def sF(self):
        return self.second_parameter

    @sF.setter
    def sF(self, value):
        self.second_parameter = value


class Lowpass(Filter):
    """
    Create a 2nd-order lowpass filter with variable quality factor `second_parameter` (might be referenced as `Q` in the description).

    The default `second_parameter` of ``1/sqrt(2)`` results in a Butterworth filter with flat passband.

    Parameters
    ----------
    corner_frequency: :obj:`float`
        The corner frequency.

    """

    def __init__(
        self,
        corner_frequency: float,
        second_parameter: float = 0.707,
        enabled: bool = True,
    ) -> None:
        super().__init__(corner_frequency, second_parameter, enabled)

    def calculate(self) -> Tuple[List[Any], List[complex], float]:
        z: List = []
        corner_frequency = self.corner_frequency
        second_parameter = self.second_parameter
        p: List[complex] = [
            -corner_frequency / (2 * second_parameter)
            + ((corner_frequency / (2 * second_parameter)) ** 2 - corner_frequency ** 2)
            ** 0.5,
            -corner_frequency / (2 * second_parameter)
            - ((corner_frequency / (2 * second_parameter)) ** 2 - corner_frequency ** 2)
            ** 0.5,
        ]
        k = corner_frequency ** 2

        return z, p, k

    @property
    def description(self) -> str:
        return "LP2 {0}, Q={1:.4g}".format(
            human_readable(self.corner_frequency, "Hz"), self.second_parameter
        )

    @property
    def Q(self):
        return self.second_parameter

    @Q.setter
    def Q(self, value):
        self.second_parameter = value


class Notch(Filter):
    """
    Create a notch filter at frequency `corner_frequency` with a quality
    factor `second_parameter`, where the -3dB filter bandwidth ``bw`` is
    given by ``second_parameter = corner_frequency/bw``.

    Parameters
    ----------
    corner_frequency: :obj:`float`
        Frequency to remove from the spectrum
    second_parameter: :obj:`float`
        Quality factor of the notch filter. Defaults to 1. Referenced as `Q` in description.
    """

    def __init__(
        self,
        corner_frequency: float,
        second_parameter: float = 1,
        enabled: bool = True,
    ) -> None:
        super().__init__(corner_frequency, second_parameter, enabled)

    def calculate(self) -> Tuple[List[complex], List[complex], float]:
        corner_frequency = self.corner_frequency
        second_parameter = self.second_parameter
        z = [corner_frequency * 1j, -corner_frequency * 1j]
        p = [
            -corner_frequency / (2 * second_parameter)
            + ((corner_frequency / (2 * second_parameter)) ** 2 - corner_frequency ** 2)
            ** 0.5,
            -corner_frequency / (2 * second_parameter)
            - ((corner_frequency / (2 * second_parameter)) ** 2 - corner_frequency ** 2)
            ** 0.5,
        ]
        k = 1
        return z, p, k

    @property
    def description(self) -> str:
        return "Notch {0}, Q={1:.4g}".format(
            human_readable(self.corner_frequency, "Hz"), self.second_parameter
        )

    @property
    def Q(self):
        return self.second_parameter

    @Q.setter
    def Q(self, value):
        self.second_parameter = value


class ServoDesign:
    """
    A Servo (controller) design class.

    Current purpose is mainly filter handling and should be used as follows:

    The object itself holds a set of (currently maximum) 5 filters.
    Filter types can be defined as new subclasses to the Filter class.

    The FILTER UTILITY section contains all methods handling filter operations,
    including clear and read.
    Filters should be added using either 'add' or 'addIndexed'.
    Normal 'add' will simply append the filter to the list and fail when the list is fullself.
    'addIndexed' however will overwrite the the filter at the current position
    and fail in case an index out of range was specified.
    """

    MAX_FILTERS = 5
    SAMPLING_RATE = 200e3  # ADwin usually runs with 200 kHz

    def __init__(self) -> None:
        self._plant = None
        self.clear()

    ####################################
    # FILTER UTILITY
    ####################################

    @property
    def filters(
        self,
    ) -> Sequence[Optional[Filter]]:
        """
        Return the global class field filterListself.

        Returns
        -------
        filterList: list
            The global field containing a list of available filters.
        """
        return self._filters

    def clear(self) -> None:
        self._filters: List[Optional[Filter]] = [None] * self.MAX_FILTERS
        self.gain = 1.0

    def _get_first_none_entry(self) -> Optional[int]:
        for i in range(self.MAX_FILTERS):
            if self.filters[i] is None:
                return i
        return None

    def _add_filter_on_index(
        self, filter_: Filter, index: int
    ) -> None:  # pylint: disable=redefined-builtin
        if index >= self.MAX_FILTERS:
            raise IndexError("Max {0} filters are allowed.".format(self.MAX_FILTERS))
        self._filters[index] = filter_

    def add(
        self,
        filter: Filter,
        index: Optional[int] = None,
        override: bool = False,
    ) -> None:  # pylint: disable=redefined-builtin
        """
        Add a filter to the servo. Up to {0} filters can be added. If the list is full and not index is provided, the filter at the last index may be overriden, depending on whether `override` has been set to true or false.

        Parameters
        ----------
        filter: :obj:`Filter`
            the Filter object to be added
        index: :obj:`int`
            optional filter index. Default `None`.
        override: :obj:`bool`
            whether to override filter if adding without index. Defaults to `False`.
        """.format(
            self.MAX_FILTERS
        )
        if index is not None and not 0 <= index < self.MAX_FILTERS:
            raise IndexError(
                f"index needs to be in valid range from 0 to {self.MAX_FILTERS}"
            )

        if not isinstance(filter, Filter):
            raise TypeError("filter must be a Filter() object")

        # check if there is an empty index
        if index is None:
            index = self._get_first_none_entry()

        # if no empty index was found, `None` was returned, check for override
        if index is None and override:
            self._add_filter_on_index(filter, self.MAX_FILTERS - 1)
        elif index is not None:
            self._add_filter_on_index(filter, index)
        else:
            raise IndexError(
                "No filter was added, list was full. You might wanna set `override=True` or remove a filter."
            )

    def get(self, index: int) -> Optional[Filter]:
        """
        Return the filter at given index, None if no filter at position.

        Parameters
        ----------
        index: Integer
            index to look for Filter at. Min 0, max {}.
        Returns
        -------
        :obj:'Filter'
        """.format(
            self.MAX_FILTERS - 1
        )
        if not 0 <= index <= self.MAX_FILTERS - 1:
            raise IndexError(
                "Filter index must be between 0 and {}.".format(self.MAX_FILTERS - 1)
            )
        return self._filters[index]

    def remove(self, index: int) -> None:
        """
        Remove a filter from the servo. Effectively sets the slot at the given index to None.

        Parameters
        ----------
        index: Integer
            the Integer specifying the filters index. Min 0, max {}.
        """.format(
            self.MAX_FILTERS - 1
        )
        if not 0 <= index <= self.MAX_FILTERS - 1:
            raise IndexError(
                "Filter index must be between 0 and {}.".format(self.MAX_FILTERS - 1)
            )
        self._filters[index] = None

    def is_empty(self) -> bool:
        """
        Check whether ServoDesign contains any filter.
        """
        for f in self._filters:
            if f is not None:
                return False
        return True

    def __len__(self) -> int:
        """
        Length of real filters in this ServoDesign.

        If some filter places are `None` they are not counted for this length.
        To get the length of the whole list, use `len(ServoDesign.filters)`.

        Returns
        -------
        :obj:`int`
            Number of filters.
        """
        length = 0
        for f in self._filters:
            if f is not None:
                length += 1
        return length

    ####################################
    # Add Filters the old way
    ####################################

    def integrator(
        self,
        corner_frequency: float,
        fstop: Optional[float] = None,
        enabled: bool = True,
    ) -> None:
        """
        Add an integrator with corner frequency `corner_frequency`,
        compensated for unity gain at high frequencies.

        Parameters
        ----------
        corner_frequency: :obj:`float`
            The corner frequency.
        fstop: :obj:`float`, optional
            Frequency were the ~1/f slope starts,
            defaults to 0.001 * `corner_frequency`.
        """
        self.add(Integrator(corner_frequency, fstop, enabled))

    def differentiator(
        self,
        corner_frequency: float,
        fstop: Optional[float] = None,
        enabled: bool = True,
    ) -> None:
        """
        Add a differentiator with corner frequency `corner_frequency`,
        compensated for unity gain at low frequencies.

        Parameters
        ----------
        corner_frequency: :obj:`float`
            The corner frequency.
        fstop: :obj:`float`, optional
            Frequency were the ~f slope stops, defaults to 1000 * `corner_frequency`.
        """
        self.add(Differentiator(corner_frequency, fstop, enabled))

    def lowpass(
        self,
        corner_frequency: float,
        second_parameter: float = 0.707,
        enabled: bool = True,
    ) -> None:
        """
        Add a 2nd-order lowpass filter with variable quality factor `second_parameter`.

        The default `second_parameter` of ``1/sqrt(2)`` results in a Butterworth filter with flat passband.

        Parameters
        ----------
        parameter: :obj:`type`
            parameter description
        """
        self.add(Lowpass(corner_frequency, second_parameter, enabled))

    def notch(
        self,
        corner_frequency: float,
        second_parameter: float = 1,
        enabled: bool = True,
    ) -> None:
        """
        Add a notch filter at frequency `corner_frequency` with a
        quality factor `second_parameter`, where the -3dB filter bandwidth ``bw``
        is given by ``second_parameter = corner_frequency/bw``.

        Parameters
        ----------
        corner_frequency: :obj:`float`
            Frequency to remove from the spectrum
        second_parameter: :obj:`float`
            Quality factor of the notch filter

        Returns
        -------
        :obj:`Servo`
            the servo object with added notch filter
        """
        self.add(Notch(corner_frequency, second_parameter, enabled))

    ####################################
    # CLASS UTILITY
    ####################################

    def log_gain(self, gain: float) -> None:
        """
        Add gain specified in dB (amplitude scale, i.e. 6dB is a factor of 2).

        Parameters
        ----------
        gain: :obj:`float`
            Gain that should be added
        """
        self.gain *= db.to_lin(gain / 2)

    def zpk(self) -> Tuple[ndarray, ndarray, float]:
        """
        Return combined zeros, poles and gain for all filters.

        Returns
        -------
        zeros: :obj:`numpy.ndarray`
            The zeros of the combined servo
        poles: :obj:`numpy.ndarray`
            The poles of the combined servo
        gain: :obj:`float`
            Gain of the combined servo
        """
        filters = [f for f in self._filters if (f is not None) and f.enabled]
        if filters:
            zeros = np.concatenate([f.zeros for f in filters])
            poles = np.concatenate([f.poles for f in filters])
        else:
            zeros = np.array([])
            poles = np.array([])
        gain = self.gain
        for f in filters:
            gain *= f.gain
        return zeros, poles, gain

    @property
    def plant(self):
        """
        Set the system that the servo should control (usually called the plant),
        which needs to be given as a :obj:`pandas.DataFrame` containing two
        columns with amplitude and phase frequency response. The index is
        assumed to contain the frequencies.
        """
        return self._plant

    @plant.setter
    def plant(self, value):
        if value is None:
            self._plant = None
            return
        if not isinstance(value, pd.DataFrame):
            raise TypeError("Plant must be a pandas DataFrame object")
        if not value.shape[1] >= 2:
            raise Exception("At least two columns (amplitude, phase) required")

        value = _handle_keysight_files(value)

        self._plant = value

    def _apply(
        self,
        freq: Union[ndarray, Float64Index],
        ampl: Optional[Series] = None,
        phase: Optional[Series] = None,
    ) -> DataFrame:
        _, a, p = signal.bode(self.zpk(), freq)  # pylint: disable=unused-variable

        df = pd.DataFrame(
            data=np.column_stack((a, p)), index=freq, columns=["Servo A", "Servo P"]
        )
        df.index.NAME = "Frequency (Hz)"
        if ampl is not None:
            df["Servo+TF A"] = ampl + a
        if phase is not None:
            df["Servo+TF P"] = phase + p
        return df

    def plot(
        self,
        freq: Optional[ndarray] = None,
        plot: bool = True,
        correct_latency: Union[bool, float] = False,
        **kwargs,
    ) -> Union[Figure, DataFrame]:
        """
        Plot the servo response over the frequencies given in `freq`.

        If a plant was set for this servo, then `freq` is ignored and the
        frequency list from the plant is used instead. If both plant and freq are None,
        a list is created from [0,...,10]kHz using numpy.logspace.

        Parameters
        ----------
        freq: :obj:`numpy.ndarray`
            frequencies for plotting calculation.
            Default is 1 to 1e5, with 1000 steps.
        plot: :obj:`bool`
            returns a DataFrame if `False`.
            Defaults to `True`
        correct_latency: :obj:`bool` or :obj:`float`
            If the data has been taken piping through ADwin an extra phase has been added.
            This can be corrected by giving ADwins sample rate (Default 200 kHz).
        **kwargs
            Parameters are passed to the :obj:`pandas.DataFrame.plot` method

        Returns
        -------
        :obj:`matplotlib.figure.Figure` or :obj:`pandas.DataFrame`
            Retuns a DataFrame or a plot
        """
        if self.plant is None and freq is None:
            freq = np.logspace(0, 5, num=1000)

        if self.plant is None:
            df = self._apply(freq)
            df_amplitude = df["Servo A"]
            df_phase = df["Servo P"]
        else:
            df = self._apply(
                self.plant.index, self.plant.iloc[:, 0], self.plant.iloc[:, 1]
            )
            # Correct latency for the plant
            if correct_latency:
                if isinstance(correct_latency, bool):
                    correct_latency = self.SAMPLING_RATE
                print(type(correct_latency))
                df["Servo+TF P"] = df["Servo+TF P"] + 360 * df.index / correct_latency
            df_amplitude = df[["Servo A", "Servo+TF A"]]
            df_phase = df[["Servo P", "Servo+TF P"]]

        if not plot:
            return df

        # Plotting

        plt = plots.amplitude_phase(df_amplitude, df_phase, **kwargs)
        # add 0dB and -135deg markers
        plt.axes[0].hlines(
            0, *plt.axes[0].get_xlim(), colors=(0.6, 0.6, 0.6), linestyles="solid"
        )
        plt.axes[1].hlines(
            -135, *plt.axes[1].get_xlim(), colors=(0.6, 0.6, 0.6), linestyles="solid"
        )
        return plt

    def discrete_form(
        self,
        sampling_frequency: float = SAMPLING_RATE,
        fs: Optional[float] = None,  # pylint: disable=invalid-name
    ) -> Dict[str, Union[float, List[Dict[str, Union[str, ndarray, bool, float]]]]]:
        """
        Convert the servo and its filters to a digital,
        discrete-time representation in terms of second-order sections
        at a sampling frequency of `sampling_frequency`.

        Returns
        -------
        :obj:`list`
            a list containing a dict for each filter with additional information.
        """
        if fs is not None:
            warn("fs is deprecated. use sampling_frequency.", DeprecationWarning)
            sampling_frequency = fs

        filters = [
            {
                "description": f.description,
                "sos": f.discrete_SOS(sampling_frequency).flatten(),
                "enabled": f.enabled,
                "index": i,
            }
            for i, f in enumerate(self._filters)
            if f is not None
        ]

        data: Dict[
            str, Union[float, List[Dict[str, Union[str, ndarray, bool, float]]]]
        ] = {
            "sampling_frequency": sampling_frequency,
            "gain": self.gain,
            "filters": filters,
        }

        return data

    def __str__(self) -> str:
        data = [
            [f.description, f.zeros, f.poles, f.gain]
            for f in self._filters
            if f is not None
        ]

        description: List[List] = [
            ["zeros", "poles", "gain"],
            ["Gain", [], [], self.gain],
        ]
        return tabulate(
            description + data,
            headers="firstrow",
        )

    def __getstate__(
        self,
    ) -> Dict[str, Optional[Union[List[Optional[Filter]], float, str]],]:
        state = self.__dict__.copy()
        plant = state["_plant"]
        if isinstance(plant, pd.DataFrame):
            state["_plant"] = plant.to_json(orient="split")

        return state

    def __setstate__(
        self,
        state: Dict[
            str,
            Optional[Union[List[Optional[Filter]], float, str]],
        ],
    ) -> None:
        if state["_plant"] is not None:
            state["_plant"] = DataContainer.from_json(state["_plant"], orient="split")
        self.__dict__ = state  # pylint: disable=attribute-defined-outside-init
