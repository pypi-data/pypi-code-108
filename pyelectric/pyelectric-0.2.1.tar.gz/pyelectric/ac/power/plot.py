from typing import Tuple
from matplotlib import pyplot as plt

from . import Power


def plot_power_triangle(power: Power, *, colors: Tuple[str, str, str] = ('r', 'g', 'b'), linewidth=None, ax=None):
    if ax is None:
        ax = plt
    P, Q, S = power.active, power.reactive, power.apparent
    c1, c2, c3 = colors
    ax.plot([0, P], [0, 0], color=c1, linewidth=linewidth)
    ax.plot([P, P], [0, Q], color=c2, linewidth=linewidth)
    ax.plot([P, 0], [Q, 0], color=c3, linewidth=linewidth)
    P_str, Q_str, S_str = f'$P = {P:.2f}\;W$', f'$Q = {Q:.2f}\;VA_R$', f'$S = {S:.2f}\;VA$'
    P_str, Q_str, S_str = [s.replace('.', ',') for s in [P_str, Q_str, S_str]]

    ax.legend([P_str, Q_str, S_str])
    ax.grid()
