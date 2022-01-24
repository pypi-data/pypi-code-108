import time
import numpy as np
from .mc_observer import MCObserver


class EnergyPlotUpdater(MCObserver):

    name = "EnergyPlotUpdater"

    def __init__(self, energy_obs=None, graph=None, mean_plot=None):
        super().__init__()
        self.energy_obs = energy_obs
        self.graph = graph
        self.mean_plot = mean_plot

    def __call__(self, system_changes):
        e = self.energy_obs.mean_energies
        xmax = len(e) + 1
        ymin = np.min(e) - e[0]
        ymax = np.max(e) - e[0]

        if abs(ymax - ymin) < 1E-6:
            return

        self.mean_plot.points = [(i, x - e[0]) for i, x in enumerate(e)]
        y_rng = ymax - ymin
        ymin -= 0.05 * y_rng
        ymax += 0.05 * y_rng
        self.graph.xmax = int(xmax)
        self.graph.ymin = float(ymin)
        self.graph.ymax = float(ymax)
        self.graph.y_ticks_major = float(ymax - ymin) / 10.0
        self.graph.x_ticks_major = float(xmax) / 10.0
        time.sleep(0.01)
