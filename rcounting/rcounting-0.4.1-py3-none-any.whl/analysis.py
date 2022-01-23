"""
A collection of functions for analysing counting data.
See also https://github.com/cutonbuminband/rcounting/blob/main/doc/examples.org
for examples of working with the data.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from numpy import pi
from numpy.fft import fftshift, irfft, rfft
from scipy.special import i0

from rcounting import counters, utils
from rcounting.units import DAY


def load_csvs(start, n, directory="."):
    """Load n csv files into a single dataframe"""
    results = []
    for _ in range(n):
        path = Path(directory) / Path(f"{start}.csv")
        df = pd.read_csv(path, comment="#")
        if len(df) % 1000 != 0:
            print(path)
        df = df.set_index("comment_id")
        results.append(df)
        start += 1000
    return pd.concat(results)


def hoc_string(df, title):
    """
    Calculate the thread participation table of a data frame.
    Return a string representation of it.
    """
    getter = counters.apply_alias(df.iloc[-1]["username"])

    def hoc_format(username):
        username = counters.apply_alias(username)
        return f"**/u/{username}**" if username == getter else f"/u/{username}"

    df["hoc_username"] = df["username"].apply(hoc_format)
    dt = pd.to_timedelta(df.iloc[-1].timestamp - df.iloc[0].timestamp, unit="s")
    table = df.iloc[1:]["hoc_username"].value_counts().to_frame().reset_index()
    data = table.set_index(table.index + 1).to_csv(None, sep="|", header=0)

    header = f"Thread Participation Chart for {title}\n\nRank|Username|Counts\n---|---|---"
    footer = (
        f"It took {len(table)} counters {utils.format_timedelta(dt)} to complete this thread."
        f" Bold is the user with the get\ntotal counts in this chain logged: {len(df) - 1}"
    )
    return "\n".join([header, data, footer])


def response_graph(df, n=250, username_column="username"):
    """
    Calculate the network graph of the top n counters.
    Create a directed edge a->b in the graph if a has ever replied to b.
    Weight each edge by the number of replies
    """
    indices = df.groupby(username_column).size().sort_values(ascending=False).index[:n]
    edges = df[username_column].isin(indices) & df[username_column].shift(1).isin(indices)
    top = pd.concat([df[username_column], df[username_column].shift()], axis=1).loc[edges]
    top.columns = ["username", "replying_to"]
    graph = top.groupby(["username", "replying_to"], as_index=False).size()
    graph.columns = ["Source", "Target", "Weight"]
    return graph


def effective_number_of_counters(c):
    """
    Calculate the effective number of parties for a given reply distribution.
    See also https://en.wikipedia.org/wiki/Effective_number_of_parties
    """
    normalised_counters = c / c.sum()
    return 1 / (normalised_counters ** 2).sum()


def capture_the_flag_score(submission):
    """Calculate how long each user has had the latest count"""
    submission["score"] = submission["timestamp"].diff().shift(-1)
    return submission.groupby("username")["score"].sum()


def vonmises_distribution(x, mu=0, kappa=1):
    """Calculate the von mises distribution; the gaussian on a circle"""
    return np.exp(kappa * np.cos(x - mu)) / (2.0 * np.pi * i0(kappa))


def normal_distribution(x, mu=0, sigma=1):
    """Calculate the gaussian distribution with mean mu and standard deviation sigma"""
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * np.sqrt(np.pi * 2))


def fft_kde_on_unit_circle(data, n_bins, kernel=vonmises_distribution, **params):
    """The fft approximation to the kde of data on the unit circle

    params:
    data: array-like: The data points to be approximated. Assumed to be distributed on [-pi, pi]
    n_bins: number of bins to use for approximation
    kernel: The kernel used to approximate the data. Default is the gaussian on the circle
    **params: parameters apart from x needed to define the kernel.

    returns:
    x: array-like: points on the unit circle at which to evaluate the density
    kde: Estimated density, normalised so that ∫kde dx = 1.

    In genergal, kernel density estimation means replacing each discrete point
    with some normalised distribution centered at that point, and then adding
    up all these results. Mathematically, this corresponds to convolving the
    original data with the chosen distribution. In fourier space, a convolution
    transforms to a product, so for periodic data we can get a fast
    approximation to this by finding the Fourier transform of our data, the
    Fourier transform of our kernel, multiplying them together and finding the
    inverse transform.

    """

    x_axis = np.linspace(-pi, pi, n_bins + 1, endpoint=True)
    hist, edges = np.histogram(data, bins=x_axis)
    x = np.mean([edges[1:], edges[:-1]], axis=0)
    kernel = kernel(x=x, **params)
    kde = fftshift(irfft(rfft(kernel) * rfft(hist)))
    kde /= np.trapz(kde, x=x)
    return x, kde


def fft_kde(data, n_bins, kernel=vonmises_distribution, **params):
    """Prepare time data for use with `fft_kde_on_unit_circle`"""
    minval = 0
    maxval = DAY
    if kernel == "vonmises_distribution":
        kernel = vonmises_distribution
    elif kernel == "normal_distribution":
        kernel = normal_distribution
    data_on_unit_circle = (data - minval) / (maxval - minval) * 2 * pi - pi
    x, kde = fft_kde_on_unit_circle(data_on_unit_circle, n_bins, kernel, **params)
    x = (x + pi) / (2 * pi) * (maxval - minval) + minval
    kde /= np.trapz(kde, x=x)
    return x, kde
