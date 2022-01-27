from math import ceil, floor
import matplotlib.pyplot as plt
from simses.analysis.evaluation.plotting.axis import Axis
from simses.analysis.evaluation.plotting.plotter import Plotting


class MatplotPlotting(Plotting):

    __nbins=100

    class Linestyle:
        DOTTED = 'dotted'
        SOLID = 'solid'
        DASHED = 'dashed'
        DASH_DOT = 'dashdot'

    def __init__(self, title: str=" ", path: str=" "):
        super().__init__()
        self.__title = title
        self.__path = path

    def lines(self, xaxis: Axis, yaxis: [Axis], secondary=[]):
        plt.title(self.__title)
        # plt.ylabel(self.__ylabel)
        plt.xlabel(xaxis.label)
        for y in yaxis:
            plt.plot(xaxis.data, y.data, color=y.color, linestyle=y.linestyle, label=y.label)
        plt.legend()
        plt.grid()
        self.show()

    def show(self):
        plt.savefig(self.__path + self.alphanumerize(self.__title)+'.pdf')
        plt.show()

    def histogram(self, xaxis: Axis, yaxis: [Axis]):
        cols = ceil(len(yaxis) / 2)
        rows = ceil(len(yaxis) / 2)
        fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(16, 9), squeeze=False)
        fig.suptitle(self.__title)
        for x in range(len(yaxis)):
            ydata = yaxis[x]
            row = floor(x / rows)
            col = (x % cols)
            axes[row, col].hist(ydata.data, bins=self.__nbins, density=True, color = ydata.color)
            axes[row, col].set(xlabel=ydata.label)
        self.show()

    def bar(self, yaxis: [Axis], bars: int):
        variables = [yaxis[x:x + bars] for x in range(0, len(yaxis), bars)]
        titles = [yaxis[x].label.split(" ", 1)[1] for x in range(0, len(yaxis), 2)]
        cols = ceil(len(yaxis) / bars)
        rows = ceil(len(yaxis) / (bars + cols))
        fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(16, 9), squeeze=False)
        fig.suptitle(self.__title)
        for i in range(len(variables)):
            variable = variables[i]
            labels = []
            values = []
            colors = []
            for j in range(len(variable)):
                labels.append(variable[j].label.split()[0])
                values.append(variable[j].data.sum())
                colors.append(variable[j].color)
            axes[ceil((i + j) / 4)-1, ceil((i + j) / 2)-1].bar(x=labels,height=values,color=colors)
            axes[ceil((i + j) / 4)-1, ceil((i + j) / 2)-1].set_title(titles[i])
        self.show()

    def subplots(self, xaxis: Axis, yaxis: [Axis]):
        cols = ceil(len(yaxis) / 2)
        rows = ceil(len(yaxis) / 2)
        fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(16, 9), squeeze=False)
        fig.suptitle(self.__title)
        for x in range(len(yaxis)):
            ydata = yaxis[x]
            row = floor(x / rows)
            col = (x % cols)
            axes[row, col].plot(xaxis.data, ydata.data)
            axes[row, col].set(xlabel=xaxis.label, ylabel='', title=ydata.label)
            axes[row, col].grid()
        self.show()

    def sankey_diagram(self, node_links: dict):
        pass

    def sunburst_diagram(self, categories: dict):
        pass