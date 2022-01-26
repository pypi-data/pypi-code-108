import numpy as np
import matplotlib.pyplot as plt

def ExperimentPlot(func):

    def wrapper(self, y, x, Polar=False, yLog=False, xLog=False, rLog=False, Normalize=False, Std=None):

        figure = plt.figure(figsize=(10,5))
        if Polar:
            ax = figure.add_subplot(111, projection='polar')
            if rLog: ax.set_rscale('symlog')
        else:
            ax = figure.add_subplot(111)
            if xLog: ax.set_xscale('log')
            if yLog: ax.set_yscale('log')
            ax.grid(True)

        func(self, x=x, y=y, Polar=Polar, Normalize=Normalize, figure=figure, ax=ax, Std=Std)

        ax.legend(loc='upper left', prop={'family': 'monospace', 'size':7}, edgecolor=(0,0,0), facecolor=(1,1,1))

        plt.show()
        return figure

    return wrapper


# -
