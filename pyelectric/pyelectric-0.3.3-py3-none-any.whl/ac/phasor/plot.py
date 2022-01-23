from contextlib import suppress
from typing import List, Optional, Tuple, Union

import numpy as np
from matplotlib import pyplot as plt

from . import Phasor


def plot_complex(zs: Union[complex, List[complex]], color: str = None):
    if isinstance(zs, complex):
        zs = [zs]
    vectors = np.array([[z.real, z.imag] for z in zs])
    origin = np.zeros(vectors.T.shape)
    plt.quiver(*origin, vectors[:, 0], vectors[:, 1],
               color=color, angles='xy', scale_units='xy', scale=1)

    limit = max([max([abs(z.real), abs(z.imag)]) for z in zs])
    plt.xlim((-limit, limit))
    plt.ylim((-limit, limit))
    plt.grid(True, which='both')
    plt.ylabel('Im')
    plt.xlabel('Re')


def plot_phasor(*phasor_list: Phasor, color: str = None, unitary: bool = False, **kwargs):
    if unitary:
        phasor_list = [p/p.abs for p in phasor_list]
    plot_complex([p.value for p in phasor_list], color=color, **kwargs)


def plot_phasor_in_time(
    phasor: Phasor,
    time_range: Tuple[float, float, float],
    frequency: float,
    is_cos: bool = False, *,
    color: str = None,
    **kwargs
):
    t1 = time_range[0]
    t2 = time_range[1]
    num: float = 1000
    with suppress(IndexError):
        num = time_range[2] or num

    t = np.linspace(t1, t2, num)
    w = 2*np.pi*frequency
    A = phasor.abs*np.sqrt(2)
    theta = phasor.phase

    def f(t):
        if is_cos:
            return A*np.cos(w*t + theta)
        else:
            return A*np.sin(w*t + theta)

    plt.plot(t, f(t), color=color, **kwargs)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True, which='both')
