from typing import Union, Tuple, Optional
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import ast
from pathlib import Path
from matplotlib.colors import LogNorm
from matplotlib.gridspec import GridSpec
import logging

logger = logging.getLogger(__name__)


def make_segments(x, y):
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    return segments


class Sampler:
    """A class used by Annealer to keep track of its progress."""

    @staticmethod
    def _manage_data(data: pd.DataFrame) -> pd.DataFrame:
        def _handle_weights(weights: str) -> list:
            while "  " in weights:
                weights = weights.replace("  ", " ")
            return ast.literal_eval(weights.replace(" ", ",").replace("[,", "["))

        expected_columns = ["weights", "iteration", "acc_ratio", "accepted", "loss", "parameter"]
        for col in expected_columns:
            if col not in data:
                raise IndexError(f"Missing columns '{col}'")
        if data.empty:
            return data
        if type(data["weights"].iloc[0]) == str:
            data.loc[:, "weights"] = data.loc[:, "weights"].apply(_handle_weights)
        return data

    def __init__(self, data: pd.DataFrame = None):
        if data is not None:
            self._data = Sampler._manage_data(data)
            self.points = None
        else:
            self._data = pd.DataFrame()
            self.points = []

    def append(self, value):
        if self.points is None:
            raise ValueError("Sampler was initialised with an outside history : can not add more points.")
        self.points.append(value)

    def clean(self):
        self._data = pd.DataFrame()
        self.points = []

    def __len__(self):
        if self.points is None:
            return len(self._data.index)
        else:
            return len(self.points)

    def _process(self):
        if self.points is None:
            raise ValueError("Sampler was initialised with an outside history : nothing to process.")
        self._data = pd.DataFrame(
            [[p.weights, p.iteration, p.acc_ratio, p.accepted, p.loss, p.parameter] for p in self.points],
            columns=["weights", "iteration", "acc_ratio", "accepted", "loss", "parameter"],
        )

    @property
    def weights(self):
        if self._data.empty or len(self._data.index) != len(self):
            self._process()
        return pd.DataFrame(index=self._data.index, data=np.array([w for w in self._data.loc[:, "weights"].values]))

    @property
    def acc_ratios(self):
        if self._data.empty or len(self._data.index) != len(self):
            self._process()
        return self._data.loc[:, "acc_ratio"]

    @property
    def accepted(self):
        if self._data.empty or len(self._data.index) != len(self):
            self._process()
        return self._data.loc[:, "accepted"]

    @property
    def losses(self):
        if self._data.empty or len(self._data.index) != len(self):
            self._process()
        return self._data.loc[:, "loss"]

    @property
    def parameters(self):
        if self._data.empty or len(self._data.index) != len(self):
            self._process()
        return self._data.loc[:, "parameter"]

    @property
    def iterations(self):
        if self._data.empty or len(self._data.index) != len(self):
            self._process()
        return self._data.index

    @property
    def data(self):
        if self._data.empty or len(self._data.index) != len(self):
            self._process()
        return self._data


class SamplePoint:
    """A class used by Annealer to keep track of its progress."""

    def __init__(
        self,
        weights,
        iteration,
        acc_ratio,
        accepted,
        loss,
        temp=None,
        demon_loss=None,
        sampler: Union[None, Sampler] = None,
    ):
        if sampler is not None and not isinstance(sampler, Sampler):
            raise TypeError(f"Sampler must be of type 'Sampler', got {type(sampler)}")
        self.weights = weights
        self.iteration = iteration
        self.acc_ratio = acc_ratio
        self.accepted = accepted
        self.loss = loss
        self.temp = temp
        self.demon_loss = demon_loss

        if self.demon_loss is None and self.temp is None:
            raise ValueError("One and only one of temp and demon_loss must be specified")
        if self.demon_loss is not None and self.temp is not None:
            raise ValueError("One and only one of temp and demon_loss must be specified")

        if sampler is not None:
            sampler.append(self)

    @property
    def parameter(self):

        if self.demon_loss is None and self.temp is None:
            raise ValueError("One and only one of temp and demon_loss must be specified")
        if self.demon_loss is not None and self.temp is not None:
            raise ValueError("One and only one of temp and demon_loss must be specified")

        if self.temp is not None:
            return self.temp
        else:
            return self.demon_loss


def plot(
    sampler_path: Union[str, Path, Tuple[Sampler, Sampler]],
    axisfontsize: int = 15,
    step_size: int = 1,
    nweights: int = 10,
    weights_names: Optional[list] = None,
) -> Union[Tuple[plt.Figure, list], None]:
    """From a directory containing 'result.csv' and 'history.csv', produces plots.
    Will produce the file "annealing.pdf" in 'sampler_path' and return the corresponding Figure object.
    If subfolders themselves containing 'result.csv' and 'history.csv' are present, will plot will call itself on them
    too.
    In the plot, will show the first 'nweights'.

    'sampler_path' can also be a tuple of two Sampler objects, the first should then be the full history of the fit and
    the second the point of the local minimum.

    Parameters
    ----------
        sampler_path: Union[str, Path, Tuple[Sampler, Sampler]]
            Either the path to the directory containing the annealing result, or two Sampler objects
        axisfontsize: int
            default value = 15
        step_size: int
            plots every 'step_size' iterations instead of all of them (default value = 1)
        nweights: int
            Number of weights to display in plots (default value = 10)
        weights_names: Optional[list]
            List of names of weights, for axis labels. If None, weights are named using their position index.

    Returns
    -------
    Union[Tuple[plt.Figure, list], None]
        Returns None if the given directory does not contain history.csv or result.csv. Otherwise returns the created
        figure and the weights and loss of the local minimum.
    """

    points = []

    if isinstance(sampler_path, (str, Path)):
        if isinstance(sampler_path, str):
            sampler_path = Path(sampler_path)

        for directory in sampler_path.glob("*"):
            if not directory.is_dir():
                continue
            try:
                int(directory.stem)
            except ValueError:
                continue
            points.append(plot(directory, axisfontsize, step_size, nweights, weights_names)[-1])

        logger.info(f"Plotting annealing results from {sampler_path}...")

        sampler = sampler_path / "history.csv"
        final_sampler = sampler_path / "result.csv"
        if not sampler.is_file():
            logger.warning(f"No file 'history.csv' found in '{sampler_path}'")
            return None
        if not final_sampler.is_file():
            logger.warning(f"No file 'result.csv' found in '{sampler_path}'")
            return None
        sampler = Sampler(pd.read_csv(sampler, index_col=0))
        final_sampler = Sampler(pd.read_csv(final_sampler, index_col=0))

    else:
        sampler, final_sampler = sampler_path

    weights = sampler.weights
    if nweights is None:
        nweights = 0
    else:
        if nweights == "all":
            nweights = len(weights.columns)
        else:
            nweights = min(nweights, len(weights.columns))

    weights = weights.iloc[::step_size, :nweights].values
    losses = sampler.losses.iloc[::step_size].values
    iterations = sampler.iterations.values[::step_size]
    acc_ratios = sampler.acc_ratios.iloc[::step_size].values
    temps = sampler.parameters.values[::step_size]

    final_weights = final_sampler.weights.iloc[0, :nweights].values
    final_loss = final_sampler.losses.values

    grid = GridSpec(3 + nweights, 6, left=0.05, right=0.9, bottom=0.03, top=0.97, hspace=0.3, wspace=0.5)
    fig = plt.figure(figsize=(22, 3 * (nweights + 3)))

    first_ax = fig.add_subplot(grid[0, :])
    second_ax = fig.add_subplot(grid[1, :])
    third_ax = fig.add_subplot(grid[2, :])
    first_ax.set_xlabel("Iterations", fontsize=axisfontsize)
    first_ax.set_ylabel("Temp", fontsize=axisfontsize)
    second_ax.set_xlabel("Iterations", fontsize=axisfontsize)
    second_ax.set_ylabel("Acc. ratio", fontsize=axisfontsize)
    third_ax.set_xlabel("Iterations", fontsize=axisfontsize)
    third_ax.set_ylabel("Loss", fontsize=axisfontsize)
    first_ax.grid(True, ls="--", lw=0.2, alpha=0.5)
    second_ax.grid(True, ls="--", lw=0.2, alpha=0.5)
    third_ax.grid(True, ls="--", lw=0.2, alpha=0.5)
    cmap = plt.get_cmap("inferno")
    first_ax.scatter(iterations, temps, c=temps, cmap=cmap, norm=LogNorm(), s=7)
    second_ax.scatter(iterations, acc_ratios, c=temps, cmap=cmap, norm=LogNorm(), s=7)
    im = third_ax.scatter(iterations, losses, c=temps, cmap=cmap, norm=LogNorm(), s=7)
    third_ax.plot([iterations[0], iterations[-1]], [final_loss[-1], final_loss[-1]], c="black")
    third_ax.text(iterations[0], final_loss[-1], s=f"{round(final_loss[-1], 3)}", c="black")
    fig.subplots_adjust(right=0.8)

    add_colorbar(fig, im, first_ax, axisfontsize)
    add_colorbar(fig, im, second_ax, axisfontsize)
    add_colorbar(fig, im, third_ax, axisfontsize)

    for iplot in range(0, nweights):
        ax1 = fig.add_subplot(grid[iplot + 3, 0:5])
        ax2 = fig.add_subplot(grid[iplot + 3, 5])
        ax1.grid(True, ls="--", lw=0.2, alpha=0.5)
        ax2.grid(True, ls="--", lw=0.2, alpha=0.5)
        ax1.set_xlabel("Iterations")
        ax1.set_ylabel(f"Weights {iplot if weights_names is None else weights_names[iplot]}")
        ax2.set_ylabel("Loss")
        ax2.set_xlabel(f"Weight {iplot if weights_names is None else weights_names[iplot]}")

        ax1.scatter(
            iterations,
            weights[:, iplot],
            s=7,
            c=temps,
            cmap=cmap,
            norm=LogNorm(),
        )
        ax1.plot([iterations[0], iterations[-1]], [final_weights[iplot], final_weights[iplot]], c="black")
        ax1.text(iterations[0], final_weights[iplot], s=f"{round(final_weights[iplot], 3)}", c="black")
        ax2.scatter(weights[:, iplot], losses, s=7, c=temps, cmap=cmap, norm=LogNorm())

        if len(points) > 0:
            for point in points:
                ax2.scatter(point[0][iplot], point[1], s=10, c="blue")
        ax2.scatter(final_weights[iplot], final_loss, s=10, c="red")

        add_colorbar(fig, im, ax2, axisfontsize)

    fig.savefig(str(sampler_path / "annealing.pdf"))
    return fig, [final_weights, final_loss]


def add_colorbar(fig, im, ax, axisfontsize):

    cbar_ax = fig.add_axes(
        [ax.get_position().xmax + 0.01, ax.get_position().ymin, 0.025, ax.get_position().ymax - ax.get_position().ymin]
    )
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar_ax.yaxis.labelpad = 15
    cbar.set_label("Temperature", rotation=270, fontsize=axisfontsize)
