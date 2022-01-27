import matplotlib.pyplot as plt
import numpy as np

import GooseMPL as gplt

plt.style.use(["goose", "goose-latex"])


def distribution(a=100, b=3, g=-0.3, size=10000):

    r = np.random.random(size=size)

    return (a ** g + (b ** g - a ** g) * r) ** (1.0 / g)


data = distribution()

fig, axes = gplt.subplots(ncols=3)

# configure axes

for ax in axes:

    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$\rho(x)$")

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlim([1e0, 1e3])
    ax.set_ylim([1e-3, 1e0])

# histogram

bin_edges = gplt.histogram_bin_edges(data, bins=41)

P, x = gplt.histogram(data, bins=bin_edges, density=True, return_edges=False)

axes[0].plot(x, P, marker="o", linestyle="none", markersize=5.0, color="k")

# histogram_log

bin_edges = gplt.histogram_bin_edges(data, bins=41, mode="log")

P, x = gplt.histogram(data, bins=bin_edges, density=True, return_edges=False)

axes[1].plot(x, P, marker="o", linestyle="none", markersize=5.0, color="b")

# histogram_uniform

bin_edges = gplt.histogram_bin_edges(data, bins=41, mode="uniform")

P, x = gplt.histogram(data, bins=bin_edges, density=True, return_edges=False)

axes[2].plot(x, P, marker="o", linestyle="none", markersize=5.0, color="r")

# add titles

axes[0].set_title(r"histogram")
axes[1].set_title(r"histogram\_log")
axes[2].set_title(r"histogram\_uniform")

# annotate powerlaw in different ways

for ax in axes:

    gplt.grid_powerlaw(exp=-1.3, axis=ax)

plt.savefig("histogram_powerlaw.svg")
plt.close()
