# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import inspect
import warnings

import numpy as np


def _isnan(signal):
    """
    isnan which works for both floats, datetimes and timedeltas.

    This should no longer be needed with numpy 1.18.
    """
    if signal.dtype.kind == 'f':
        return np.isnan(signal)
    elif signal.dtype.kind in 'mM':
        return np.isnat(signal)
    else:
        raise TypeError(f'isnan not available for type {signal.dtype}')


def _find_peaks(signal):
    """
    This function does not deal well with NaN values, so make sure to remove
    them before calling.
    """
    import scipy.signal

    # Pass plateau_size as tuple of None to get left_/right_edges returned but
    # still get all peaks.
    _, peaks_dict = scipy.signal.find_peaks(signal, plateau_size=(None, None))

    res = np.zeros_like(signal, dtype=bool)
    for left, right in zip(peaks_dict['left_edges'],
                           peaks_dict['right_edges']):
        res[left:right+1] = True
    return res


def _get_parts(signal):
    """
    Return a generator over non-masked, non-NaN parts of signal.
    Each part is returned as a tuple with the signal part and a boolean saying
    if the part consist of NaN+masked values (True) or not (False).
    """
    if signal.dtype.kind in 'fmM':
        mask = _isnan(signal)
    else:
        mask = None
    if isinstance(signal, np.ma.MaskedArray):
        if mask is None:
            mask = signal.mask
        else:
            mask = mask.filled(True)

    if mask is None:
        signal_parts = [signal]
        masked_parts = [False]
    else:
        splits = np.flatnonzero(np.logical_xor(mask[1:], mask[:-1])) + 1
        signal_parts = np.split(signal, splits)
        masked_parts = [np.any(part) for part in np.split(mask, splits)]

    return zip(signal_parts, masked_parts)


class EventDetection(object):
    """Container class for event detection functions."""

    @staticmethod
    def changed(signal):
        """Return a boolean array which is True at each position where signal
        is different than at the previous position. The first element in the
        returned array is always False.

        Parameters
        ----------
        signal : np.array
            The array the function should be performed on.

        Returns
        -------
        np.array
            An array of booleans with the same length as signal.
        """
        if not signal.size:
            return np.array([], dtype=bool)

        if signal.dtype.kind in 'fmM':
            isnan = _isnan(signal)
            nans = np.logical_or(isnan[:-1], isnan[1:])
        else:
            nans = np.zeros((signal.size - 1,), dtype=bool)

        diff = np.logical_and(signal[:-1] != signal[1:], np.logical_not(nans))
        if np.ma.isMaskedArray(diff):
            diff = np.ma.concatenate(([False], diff))
            if np.ma.getmaskarray(signal)[0]:
                diff.mask = np.ma.getmaskarray(diff)
                diff.mask[0] = True
            return diff
        else:
            return np.concatenate(([False], diff))

    @staticmethod
    def changed_up(signal):
        """Return a boolean array which is True at each position where signal
        is greater than at the previous position. The first element in the
        returned array is always False.

        Parameters
        ----------
        signal : np.array
            The array the function should be performed on.

        Returns
        -------
        np.array
            An array of booleans with the same length as signal.
        """
        if not signal.size:
            return np.array([], dtype=bool)
        if signal.dtype.kind in 'bu':
            signal = signal.astype(int)

        if signal.dtype.kind == 'M':
            # Create timedelta dtype with same precision
            diff_dtype = (signal[:0] - signal[:0]).dtype
            zero = np.zeros((), dtype=diff_dtype)
        elif signal.dtype.kind == 'm':
            zero = np.zeros((), dtype=signal.dtype)
        else:
            zero = 0

        # Greater than ufunc prints a warning if there are NaNs in signal, but
        # we have a well defined behavior for NaNs, so no need for a warning.
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            diff = np.diff(signal) > zero

        if np.ma.isMaskedArray(diff):
            diff = np.ma.concatenate(([False], diff))
            if np.ma.getmaskarray(signal)[0]:
                diff.mask = np.ma.getmaskarray(diff)
                diff.mask[0] = True
            return diff
        else:
            return np.concatenate(([False], diff))

    @staticmethod
    def changed_down(signal):
        """Return a boolean array which is True where ``signal`` is less than at
        the previous position. The first element in the returned array is
        always ``False``.

        Parameters
        ----------
        signal : np.array
            The array the function should be performed on.

        Returns
        -------
        np.array
            An index array with booleans with the same length as in_arr.
        """
        if not signal.size:
            return np.array([], dtype=bool)
        if signal.dtype.kind in 'bu':
            signal = signal.astype(int)

        if signal.dtype.kind == 'M':
            # Create timedelta dtype with same precision
            diff_dtype = (signal[:0] - signal[:0]).dtype
            zero = np.zeros((), dtype=diff_dtype)
        elif signal.dtype.kind == 'm':
            zero = np.zeros((), dtype=signal.dtype)
        else:
            zero = 0

        # Less than ufunc prints a warning if there are NaNs in signal, but we
        # have a well defined behavior for NaNs, so no need for a warning.
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            diff = np.diff(signal) < zero

        if np.ma.isMaskedArray(diff):
            diff = np.ma.concatenate(([False], diff))
            if np.ma.getmaskarray(signal)[0]:
                diff.mask = np.ma.getmaskarray(diff)
                diff.mask[0] = True
            return diff
        else:
            return np.concatenate(([False], diff))

    @staticmethod
    def local_max(signal):
        """Return a boolean array which is True at each local maximum in
        signal, i.e. between an increase and a decrease in signal. Maxima at
        signal boundaries or near NaN aren't included.

        Parameters
        ----------
        signal : np.array
            The signal the function should be performed on.

        Returns
        -------
        np.array
            An array of booleans with the same length as signal.

        Examples
        --------
        >>> signal = np.array([1, 0, 1, 0, 1, 1, 2, 0])
        >>> peaks = np.array(
        ...     [False, False, True, False, False, False, True, False])
        >>> np.all(local_max(signal) == peaks)
        True
        """
        results = []
        for part, masked in _get_parts(signal):
            if masked:
                results.append(np.zeros(len(part), dtype=bool))
            else:
                results.append(_find_peaks(part))
        return np.concatenate(results)

    @staticmethod
    def local_min(signal):
        """Return a boolean array which is True at each local minimum in
        signal, i.e. between a decrease and an increase in signal. Minima at
        signal boundaries or near NaN aren't included.

        Parameters
        ----------
        signal : np.array
            The signal the function should be performed on.

        Returns
        -------
        np.array
            An array of booleans with the same length as signal.

        Examples
        --------
        >>> signal = np.array([1, 0, 1, 0, -1, -1, -2, 0])
        >>> peaks = np.array(
        ...     [False, True, False, False, False, False, True, False])
        >>> np.all(local_min(signal) == peaks)
        True
        """
        results = []
        for part, masked in _get_parts(signal):
            if masked:
                results.append(np.zeros(len(part), dtype=bool))
            else:
                if part.dtype.kind == 'u':
                    minus_part = -part.astype(int)
                elif part.dtype.kind == 'b':
                    minus_part = ~part
                elif part.dtype.kind == 'M':
                    minus_part = -part.astype(float)
                else:
                    minus_part = -part
                results.append(_find_peaks(minus_part))

        return np.concatenate(results)

    @staticmethod
    def global_max(signal):
        """Return a boolean array which is True when signal is at its maximum
        value.

        Parameters
        ----------
        signal : np.array
            The signal the function should be performed on.

        Returns
        -------
        np.array
            An array of booleans with the same length as signal.

        Examples
        --------
        >>> signal = np.array([1, 0, 1, 0, 1, 1, 2, 0])
        >>> max_ = np.array(
        ...     [False, False, False, False, False, False, True, False])
        >>> np.all(global_max(signal) == max_)
        True
        """
        def nanmax(arr):
            if isinstance(arr, np.ma.MaskedArray):
                arr = arr.compressed()
            if arr.dtype.kind == 'f':
                return np.nanmax(arr)
            elif arr.dtype.kind in 'Mm':
                return np.max(arr[np.logical_not(_isnan(arr))])
            else:
                return np.max(arr)

        if not signal.size:
            return np.array([], dtype=bool)

        mask = signal == nanmax(signal)
        if isinstance(mask, np.ma.MaskedArray):
            return mask.filled(False)
        return mask

    @staticmethod
    def global_min(signal):
        """Return a boolean array which is True when signal is at its minimum
        value.

        Parameters
        ----------
        signal : np.array
            The signal the function should be performed on.

        Returns
        -------
        np.array
            An array of booleans with the same length as signal.

        Examples
        --------
        >>> signal = np.array([1, 0, 1, 0, -1, -1, -2, 0])
        >>> min_ = np.array(
        ...     [False, False, False, False, False, False, True, False])
        >>> np.all(global_min(signal) == min_)
        True
        """
        def nanmin(arr):
            if isinstance(arr, np.ma.MaskedArray):
                arr = arr.compressed()
            if arr.dtype.kind == 'f':
                return np.nanmin(arr)
            elif arr.dtype.kind in 'Mm':
                return np.min(arr[np.logical_not(_isnan(arr))])
            else:
                return np.min(arr)

        if not signal.size:
            return np.array([], dtype=bool)

        mask = signal == nanmin(signal)
        if isinstance(mask, np.ma.MaskedArray):
            return mask.filled(False)
        return mask


GUI_DICT = {
    "Event detection": [
        ("Changed", "ca.changed(a)",
         inspect.getdoc(EventDetection.changed)),
        ("Changed up", "ca.changed_up(a)",
         inspect.getdoc(EventDetection.changed_up)),
        ("Changed down", "ca.changed_down(a)",
         inspect.getdoc(EventDetection.changed_down)),
        ("Local min", "ca.local_min(a)",
         inspect.getdoc(EventDetection.local_min)),
        ("Local max", "ca.local_max(a)",
         inspect.getdoc(EventDetection.local_max)),
        ("Global min", "ca.global_min(a)",
         "Return a boolean array which is True when signal is at its minimum "
         "value."),
        ("Global max", "ca.global_max(a)",
         "Return a boolean array which is True when signal is at its maximum "
         "value."),
    ]
}
