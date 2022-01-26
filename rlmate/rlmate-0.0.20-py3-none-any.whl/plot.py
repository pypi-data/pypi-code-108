import numpy as np
from collections import deque
import matplotlib.pyplot as plt


def smoothen(arr, window_size=100):
    """Function that computes the sliding mean over the given array.
        For the first numbers n < window_size, the sliding mean is computed using the numbers there are.

    Args:
        arr (float array): scores
        window_size (int, optional): size of sliding window. Defaults to 100.

    Returns:
        (float array, float arrary): list with sliding means, list with stds
    """
    means = []
    stds = []
    for i in range(len(arr)):
        lower = np.maximum(0, i - window_size)
        means.append(arr[lower : i + 1].mean())
        stds.append(arr[lower : i + 1].std())
    return means, stds


def plot_training_progress(
    scores,
    eps_start=None,
    eps_end=None,
    eps_decay=None,
    epsilons=None,
    window_length=250,
    figsize=(12, 12),
    fontsize=18,
    path=None,
    scores_color="c",
    mean_color="r",
    score_range=None,
    epsilon_range=None,
    axis_gap=0.02,
    mark_best=False,
    legend=True,
    ax=None,
    suppress_single_scores=False,
):
    """Plot the training curve given an array of training scores, i.e. training episode returns

    Args:
        scores (float array): scores, i.e. training episode returns
        eps_start (int, optional): epsilon-greedy exploration coefficient in the training beginning. Defaults to 1.
        eps_end (float, optional): epsilon-greedy exploration coefficient in the end of training. Defaults to 0.001.
        eps_decay (float, optional): epsilon-greedy exponential decay factor from eps_start to eps_end. Defaults to 0.999.
        epsilons (list, optional): alternative to eps_start, eps_end and eps_decay. Provide all used eps values. Defaults to []. Will be ignored, if eps_start, eps_end and eps_decay are given
        window_length (int, optional): size of window_length for sliding window. Defaults to 250.
        figsize (tuple, optional): Figure size to use.. Defaults to (12,12).
        fontsize (int, optional): fontsize to use. Defaults to 18.
        path (string, optional): path to save the created plot. Defaults to None.
        scores_color (str, optional): score dot color. Defaults to 'c'.
        mean_color (str, optional): slidign mean color. Defaults to 'r'.
        score_range ((float, float), optional): range to be shown in the plot on the y-axis. Defaults to None.
        epsilon_range ((float, float)), optional): range to be shown in the plot in the epsilon y-axis. Defaults to None.
        axis_gap (float, optional):  gap to be added to score_range and epsilon_range for better readability. Defaults to 0.02.
        mark_best (bool, optional): whether the best observed value should be marked. Defaults to False.
        legend (bool, optional): whether to plot a legend. Defaults to True.
        ax (pyplot axis, optional): pyplot axis to use. Generating a new one if none provided. Defaults to None.
        suppress_single_scores (bool, optional): whether to suppress the single score dots. Defaults to False.

    Returns:
        plt: generated plot.
    """
    # check whether the epsilons are explicitly given and calculate them otherwise
    if (eps_start is not None) or (eps_end is not None) or (eps_decay is not None):
        assert all(
            arg is not None for arg in [eps_start, eps_end, eps_decay]
        ), "You need to provide all of eps_start, eps_end and eps_decay if you want to plot the effect of the epsilon-greedy policy"
        epsilons = []
        for i in range(len(scores)):
            actual_eps = np.max([eps_start * np.power(eps_decay, i), eps_end])
            epsilons.append(actual_eps)

    if epsilons is not None and len(epsilons) > 0:
        assert len(epsilons) == len(
            scores
        ), "The length of the list of epsilon (exploration coefficient) values need to be the same as the amount of scores"

    plot_epsilon = epsilons is not None and len(epsilons) > 0

    # calculate the mean by using the given window_length
    scores_window = deque(maxlen=window_length)

    means = []
    for i, score in enumerate(scores):
        scores_window.append(score)
        means.append(np.mean(scores_window))

    if ax == None:
        # create the figure with the given figsize
        fig, ax1 = plt.subplots(figsize=figsize)
    else:
        ax1 = ax

    ax1.set_ylabel("Return", fontsize=fontsize)
    ax1.set_xlabel("Episode #", fontsize=fontsize)

    x = range(len(scores))

    # plt.xticks(fontsize = fontsize)

    # scatter the scores and the means on one axis
    if not suppress_single_scores:
        ax1.scatter(x, scores, label="Episodes", color=scores_color, alpha=0.8, s=1)
    ax1.plot(range(len(means)), means, label="Sliding Mean", color=mean_color)

    if plot_epsilon:
        # optionally scatter epsilon on the other axis
        ax2 = ax1.twinx()
        ax2.set_ylabel("Random Exploration Coefficient", fontsize=fontsize)
        ax2.plot(x, epsilons, label="Epsilon")
        ax2.axis([0, len(scores), -0, 1])

    # set the given score range or calculate it relative to the given values
    if score_range == None:
        score_min = np.min(scores)
        score_max = np.max(scores)
        score_range = np.abs(score_max - score_min)
        score_min = score_min - axis_gap * score_range
        score_max = score_max + axis_gap * score_range
    else:
        score_min, score_max = score_range
    ax1.set_ylim(score_min, score_max)

    # do the same for epsilon
    if plot_epsilon:
        if epsilon_range == None:
            epsilon_min = eps_end
            epsilon_max = eps_start
            epsilon_range = np.abs(epsilon_max - epsilon_min)
            epsilon_min = epsilon_min - axis_gap * epsilon_range
            epsilon_max = epsilon_max + axis_gap * epsilon_range
        else:
            epsilon_min, epsilon_max = epsilon_range

        ax2.set_ylim(epsilon_min, epsilon_max)
        ax2.tick_params(labelsize=fontsize)

    # set the fontsize of the axis/plt
    ax1.axis()
    plt.axis()
    ax1.tick_params(labelsize=fontsize)

    # ax1.legend(bbox_to_anchor=(0.8, 0.2, 0.15, .102), fontsize = 16, mode = 'expand', ncol=1, handlelength = 7, numpoints = 10)
    # ax1.legend(fontsize = fontsize, ncol = 2, bbox_to_anchor=(0.05, 0.8, 0.9, 0.12), mode = 'expand', scatterpoints=5)
    # ax2.legend(fontsize = fontsize, bbox_to_anchor=(0.675, 0.9, 0.3, 0.12), mode = 'expand')
    if mark_best:
        best = np.argmax(means)
        best_value = -float("inf")
        other_best = None
        plt.axvline(
            x=best, linestyle="dotted", color="#A0A0A0", label="Highest overall result"
        )
        start_id = 0
        while start_id < len(scores):
            value = np.mean(scores[start_id : start_id + window_length])
            if value > best_value:
                other_best = start_id + window_length - 1
                best_value = value
            start_id += window_length

        plt.axvline(x=other_best, linestyle="dotted", color="k", label="Best policy")

    if legend:
        ax1.legend(fontsize=fontsize)
        # ax2.legend()

    if path != None:
        assert ax == None
        plt.savefig(path, bbox_inches="tight")

    return plt


def plot_training_progress_from_file(
    file,
    eps_start=1,
    eps_end=0.001,
    eps_decay=0.999,
    epsilons=[],
    window_length=250,
    figsize=(12, 12),
    fontsize=18,
    path=None,
    scores_color="c",
    mean_color="r",
    score_range=None,
    epsilon_range=None,
    axis_gap=0.02,
    mark_best=True,
    legend=True,
    suppress_singe_scores=False,
):
    """Read the trainings scores from file and plot the training progress.

    Args:
        file (string): path to file
        eps_start (int, optional): exploration coefficient in the training beginning. Defaults to 1.
        eps_end (float, optional): exploration coefficient in the end of training. Defaults to 0.001.
        eps_decay (float, optional): exponential decay factor from eps_start to eps_end. Defaults to 0.999.
        epsilons (list, optional): alternative to eps_start, eps_end and eps_decay. Provide all used eps values. Defaults to [].
        window_length (int, optional): size of window_length for sliding window. Defaults to 250.
        figsize (tuple, optional): Figure size to use.. Defaults to (12,12).
        fontsize (int, optional): fontsize to use. Defaults to 18.
        path (string, optional): path to save the created plot. Defaults to None.
        scores_color (str, optional): score dot color. Defaults to 'c'.
        mean_color (str, optional): slidign mean color. Defaults to 'r'.
        score_range ((float, float), optional): range to be shown in the plot on the y-axis. Defaults to None.
        epsilon_range ((float, float)), optional): range to be shown in the plot in the epsilon y-axis. Defaults to None.
        axis_gap (float, optional):  gap to be added to score_range and epsilon_range for better readability. Defaults to 0.02.
        mark_best (bool, optional): whether the best observed value should be marked. Defaults to False.
        legend (bool, optional): whether to plot a legend. Defaults to True.
        suppress_single_scores (bool, optional): whether to suppress the single score dots. Defaults to False.


    Returns:
        pyplot: Plot
    """
    scores = []
    with open(file, "r") as f:
        first = f.readline()
        try:
            first = float(first)
            scores.append(first)
        except:
            print("Dismiss first line")

        for line in f:
            score = float(line)
            scores.append(score)

    return plot_training_progress(
        scores,
        eps_start,
        eps_end,
        eps_decay,
        epsilons,
        window_length,
        figsize,
        fontsize,
        path,
        scores_color,
        mean_color,
        score_range,
        epsilon_range,
        axis_gap,
        mark_best=mark_best,
        legend=legend,
    )


# todo: this doesn't feel right. the information is encoded in the experiment and should be read from there.
def plot_training_progress_from_experiment(
    exp,
    eps_start_key="-es",
    eps_end_key="-ee",
    eps_decay_key="-ed",
    window_length=250,
    figsize=(12, 12),
    fontsize=18,
    path=None,
    scores_color="c",
    mean_color="r",
    score_range=None,
    epsilon_range=None,
    axis_gap=0.02,
    mark_best=True,
    legend=True,
    suppress_single_scores=False,
):
    """Read the trainings scores from file and plot the training progress.

    Args:
        exp (Experiment): experiment
        window_length (int, optional): size of window_length for sliding window. Defaults to 250.
        figsize (tuple, optional): Figure size to use.. Defaults to (12,12).
        fontsize (int, optional): fontsize to use. Defaults to 18.
        path (string, optional): path to save the created plot. Defaults to None.
        scores_color (str, optional): score dot color. Defaults to 'c'.
        mean_color (str, optional): slidign mean color. Defaults to 'r'.
        score_range ((float, float), optional): range to be shown in the plot on the y-axis. Defaults to None.
        epsilon_range ((float, float)), optional): range to be shown in the plot in the epsilon y-axis. Defaults to None.
        axis_gap (float, optional):  gap to be added to score_range and epsilon_range for better readability. Defaults to 0.02.
        mark_best (bool, optional): whether the best observed value should be marked. Defaults to False.
        legend (bool, optional): whether to plot a legend. Defaults to True.
        suppress_single_scores (bool, optional): whether to suppress the single score dots. Defaults to False.

    Returns:
        pyplot: Plot
    """
    file = exp.scores_file

    def _get(*keys):
        return [exp.exec_args_dict[key] for key in keys]

    try:
        eps_start, eps_end, eps_decay = _get(eps_start_key, eps_end_key, eps_decay_key)
    except KeyError:
        print("Not plotting epsilon", exp.exec_args_dict)
        eps_start = None
        eps_end = None
        eps_decay = None

    epsilons = []

    return plot_training_progress_from_file(
        file,
        eps_start,
        eps_end,
        eps_decay,
        epsilons,
        window_length,
        figsize,
        fontsize,
        path,
        scores_color,
        mean_color,
        score_range,
        epsilon_range,
        axis_gap,
        mark_best=mark_best,
        legend=legend,
    )
