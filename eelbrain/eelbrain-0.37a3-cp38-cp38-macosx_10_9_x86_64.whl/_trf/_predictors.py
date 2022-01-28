"""Predictors for deconvolution"""
# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from itertools import repeat

import numpy as np

from .._data_obj import NDVar, Case, UTS, asndvar, asarray


def epoch_impulse_predictor(shape, value=1, latency=0, name=None, ds=None):
    """Time series with one impulse for each of ``n`` epochs

    Parameters
    ----------
    shape : NDVar | (int, UTS) | str
        Shape of the output. Can be specified as the :class:`NDVar` with the
        data to predict, or an ``(n_cases, time_dimension)`` tuple.
    value : scalar | sequence | str
        Scalar or length ``n`` sequence of scalars specifying the value of each
        impulse (default 1).
    latency : scalar | sequence | str
        Scalar or length ``n`` sequence of scalars specifying the latency of
        each impulse (default 0).
    name : str
        Name for the output :class:`NDVar`.
    ds : Dataset
        If specified, input items (``shape``, ``value`` and ``latency``) can be
        strings to be evaluated in ``ds``.

    Examples
    --------
    See :ref:`exa-impulse` example.
    """
    if isinstance(shape, str):
        shape = asndvar(shape, ds=ds)
    if isinstance(value, str):
        value = asarray(value, ds=ds)
    if isinstance(latency, str):
        latency = asarray(latency, ds=ds)

    if isinstance(shape, NDVar):
        if not shape.has_case:
            raise ValueError(f'shape={shape!r}: has no case dimension')
        n = len(shape)
        time = shape.get_dim('time')
    else:
        n, time = shape
        if not isinstance(time, UTS):
            raise TypeError(f'shape={shape!r}: second item needs to be UTS instance')

    x = np.zeros((n, len(time)))
    t_index = time._array_index(latency)
    if np.isscalar(latency):
        x[:, t_index] = value
    else:
        x[np.arange(n), t_index] = value
    return NDVar(x, (Case, time), name)


def event_impulse_predictor(shape, time='time', value=1, latency=0, name=None, ds=None):
    """Time series with multiple impulses

    Parameters
    ----------
    shape : NDVar | UTS
        Shape of the output. Can be specified as the :class:`NDVar` with the
        data to predict, or an ``(n_cases, time_dimension)`` tuple.
    time : sequence of scalar
        Time points at which impulses occur.
    value : scalar | sequence
        Magnitude of each impulse (default 1).
    latency : scalar | sequence
        Latency of each impulse relative to ``time`` (default 0).
    name : str
        Name for the output :class:`NDVar`.
    ds : Dataset
        If specified, input items (``time``, ``value`` and ``latency``) can be
        strings to be evaluated in ``ds``.
    """
    if isinstance(shape, NDVar):
        uts = shape.get_dim('time')
    elif isinstance(shape, UTS):
        uts = shape
    else:
        raise TypeError(f'shape={shape!r}')

    time, n = asarray(time, ds=ds, return_n=True)

    if isinstance(value, str) or not np.isscalar(value):
        value = asarray(value, ds=ds, n=n)
    else:
        value = repeat(value)

    if isinstance(latency, str) or not np.isscalar(latency):
        latency = asarray(latency, ds=ds, n=n)
    else:
        latency = repeat(latency)

    out = NDVar(np.zeros(len(uts)), uts, name)
    for t, l, v in zip(time, latency, value):
        out[t + l] = v
    return out
