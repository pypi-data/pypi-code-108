import matplotlib.pyplot as plt
import numpy as np

import GooseMPL as gplt

plt.style.use(["goose", "goose-latex"])


def distribution(a=100, b=3, g=-0.3, size=10000):

    r = np.random.random(size=size)

    return (a ** g + (b ** g - a ** g) * r) ** (1.0 / g)


data = distribution()

fig, axes = plt.subplots(ncols=3, nrows=2, figsize=(3 * 8, 2 * 6))

# --- histogram ---

bin_edges = gplt.histogram_bin_edges(data, bins=41)

P, x = gplt.histogram(data, bins=bin_edges, density=False)

gplt.hist(P, x, facecolor=[0.2, 0.2, 0.2], axis=axes[0, 0])

P, x = gplt.histogram(data, bins=bin_edges, density=True)

gplt.hist(P, x, facecolor=[0.2, 0.2, 0.2], axis=axes[1, 0])

# --- histogram_log ---

bin_edges = gplt.histogram_bin_edges(data, bins=41, mode="log")

P, x = gplt.histogram(data, bins=bin_edges, density=False)

gplt.hist(P, x, facecolor="b", axis=axes[0, 1])

P, x = gplt.histogram(data, bins=bin_edges, density=True)

gplt.hist(P, x, facecolor="b", axis=axes[1, 1])

# --- histogram_uniform ---

bin_edges = gplt.histogram_bin_edges(data, bins=41, mode="uniform")

P, x = gplt.histogram(data, bins=bin_edges, density=False)

gplt.hist(P, x, facecolor="r", axis=axes[0, 2])

P, x = gplt.histogram(data, bins=bin_edges, density=True)

gplt.hist(P, x, facecolor="r", axis=axes[1, 2])

# --- axes settings ---

axes[0, 0].set_title(r"histogram")
axes[0, 1].set_title(r"histogram\_log")
axes[0, 2].set_title(r"histogram\_uniform")

for ax in axes.ravel():

    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$N(x)$")

plt.savefig("histogram.svg")
plt.close()
