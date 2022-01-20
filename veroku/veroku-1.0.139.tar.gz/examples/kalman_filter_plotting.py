import numpy as np
from ipywidgets import interact
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse

"""
A helper module for the Kalman filter example notebook.
"""


def _get_ellipse_patch(cov, mean, std_devs=2):
    eigen_values_array, eigen_vectors_array = np.linalg.eig(cov)
    max_len_eig_vector = eigen_vectors_array[:, np.argmax(eigen_values_array)]
    angle = np.arctan2(max_len_eig_vector[1], max_len_eig_vector[0])
    std_dev_primary_comp = np.sqrt(eigen_values_array[0])
    std_dev_secondary_comp = np.sqrt(eigen_values_array[1])

    ellipse = matplotlib.patches.Ellipse(mean,
                                         std_dev_primary_comp * std_devs,
                                         std_dev_secondary_comp * std_devs,
                                         angle=angle,
                                         fc=(1, 0, 0, 0),
                                         ec=(0, 0, 1, 1),
                                         lw=2)
    return ellipse


def _add_ellipse(ax, ellipse):
    ax.add_patch(ellipse)


def _get_2d_std_dev_ellipses(gaussians):
    ellipse_patches = []
    for g in gaussians:
        ellipse_patch = _get_ellipse_patch(g.get_cov(), g.get_mean())
        ellipse_patches.append(ellipse_patch)
    return ellipse_patches


# TODO: Consider removing this.
def _plot_2d_std_dev_ellipses(gaussians):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    patches = _get_2d_std_dev_ellipses(gaussians)
    for patch in patches:
        ax.add_patch(patch)
    ax.autoscale()


# TODO: The widget breaks when moving the slider in reverse. Fix this.
def inferred_system_state_widget(X_dist_over_time, X_meas_over_time, X_true_over_time):
    """
    Plot a series of two dimensional Gaussian state distributions (as standard-deviation ellipses) together with the
    ground truth state and state-space measurements.
    :param X_dist_over_time: The time evolution series of the state distributions.
    :type X_dist_over_time: Gaussian list
    :param X_meas_over_time: The measurements over time.
    :type X_meas_over_time: array like list
    :param X_true_over_time: The ground truth time evolution series of the state.
    :type X_true_over_time: array like list
    """
    all_xs = X_meas_over_time[:, 0].tolist() + X_true_over_time[:, 0].tolist()
    all_ys = X_meas_over_time[:, 1].tolist() + X_true_over_time[:, 1].tolist()
    ylims = [min(all_ys), max(all_ys)]
    xlims = [min(all_xs), max(all_xs)]

    height = ylims[1] - ylims[0]
    width = xlims[1] - xlims[0]

    legend_elements = [Line2D([0], [0], marker='o', color='w', label='Scatter', markerfacecolor='b', markersize=15),
                       Line2D([0], [0], marker='o', color='w', label='Scatter', markerfacecolor='r', markersize=15),
                       Line2D([0], [0], marker='o', color='w', label='Scatter', markerfacecolor='k', markersize=15)]

    estimated_cov_ellipses = _get_2d_std_dev_ellipses(X_dist_over_time)
    estimated_means_array = np.concatenate([p.get_mean().T for p in X_dist_over_time])
    last_timestep_index = len(estimated_cov_ellipses) - 1

    def update(t=0):
        """Remove old lines from plot and plot new one"""
        fig_width = 20
        fig, ax = plt.subplots(figsize=(fig_width, fig_width * height / width))
        ax.set_ylim(ylims)
        ax.set_xlim(xlims)
        ax.grid(True)
        [l.remove() for l in ax.patches]
        ax.add_patch(estimated_cov_ellipses[t])
        plt.scatter(estimated_means_array[t:t + 1, 0], estimated_means_array[t:t + 1, 1], color='b')
        plt.scatter(X_meas_over_time[t - 1, 0], X_meas_over_time[t - 1, 1], color='r')
        plt.plot(X_true_over_time[:t, 0], X_true_over_time[:t, 1], color='k', marker='o')
        plt.legend(legend_elements, ['estimate', 'measurement', 'truth'])
        plt.show()

    interact(update, t=(1, last_timestep_index-1));
