import os
from replifactory.growth_rate import adaptive_window_doubling_time
from replifactory.util import read_csv_tail
import time
import numpy as np
import matplotlib.pyplot as plt


def plot_culture(culture, last_hours=24, plot_growth_rate=False):
    od_filepath = os.path.join(culture.directory, "od.csv")
    df = read_csv_tail(filepath=od_filepath, lines=last_hours * 60)
    t = df.index.values
    od = df.values.ravel()
    t_min = t[-1] - last_hours * 3600
    odw = od[t > t_min]
    tw = t[t > t_min]
    drug_concentration_file = os.path.join(culture.directory, "medium2_concentration.csv")
    tdose = None
    dosevalues = None
    if os.path.exists(drug_concentration_file):
        dosedf = read_csv_tail(drug_concentration_file, lines=50 + last_hours * 10)
        tdose = dosedf.index.values
        dosevalues = dosedf.values.ravel()[tdose > t_min]
        tdose = tdose[tdose > t_min]

    # fig = plot_gr(tw, odw, tdose)

    # plot growth rate
    od_values = odw
    time_values = tw
    dilution_timepoints = tdose
    od = np.array(od_values)
    t = np.array(time_values)

    fig, ax = plt.subplots(figsize=[16, 8], dpi=100)
    # i = 0
    # lines = []
    ax.plot(t / 3600, od, "k.", label="Optical Density")
    # ax.set_ylim(-0.05, 1.6)
    od[od <= 0] = 1e-6
    ax.set_ylabel("Optical Density")
    ax.set_xlabel("Time [hours]")

    # Growth rate
    if plot_growth_rate:
        ax2 = ax.twinx()
        #
        td_timepoints, td, tderr = adaptive_window_doubling_time(t, od, dilution_timepoints=dilution_timepoints)

        markers, caps, bars = ax2.errorbar(td_timepoints / 3600, td, tderr,
                                           alpha=0.5, label="doubling time")
        [bar.set_alpha(0.1) for bar in bars]
        try:
            td = np.array(td)
            tderr = np.array(tderr)
            tdmax = np.nanmax(td[tderr < 0.05])
            tdmin = np.nanmin(td[tderr < 0.05])
            ax2.set_ylim(tdmin * 0.5, tdmax * 1.2)
        except:
            pass
        ax2.grid(color="xkcd:light blue", linestyle=":", alpha=0.8)
        ax2.yaxis.set_tick_params(color="xkcd:cerulean")
        ax2.set_ylabel("Doubling time [hours]", color="xkcd:cerulean")

    if tdose is not None:
        ax3 = fig.axes[0].twinx()
        ax3.step(tdose / 3600, dosevalues, "r^-", where="post", label="dose")
        ax3.spines["left"].set_position(("axes", -0.1))
        ax3.yaxis.set_label_position("left")
        ax3.yaxis.set_ticks_position("left")
        ax3.yaxis.set_tick_params(color="r")
        ax3.set_ylabel("Dose [mM]", color="r")
        ax3.grid(color="r", linestyle=":", alpha=0.5)

    handles, labels = [], []
    for axis in fig.axes:
        handle, label = axis.get_legend_handles_labels()
        axis.legend([])
        handles += handle
        labels += label
    ax.legend(handles, labels, loc=2)

    xticks = ax.get_xticks()
    for axis in fig.axes:
        axis.set_xticks(xticks)

    tmin = xticks[0]
    xtick_labels = [round(t - tmin, 2) for t in xticks]
    # fig.axes[1].set_ylim(0.1, 10)
    ax.set_xticklabels(xtick_labels)
    # fig.axes[1].set_yticks([])

    ax.set_yscale("log")
    od_ticks = [0.001, 0.01, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 1]
    ax.set_yticks(od_ticks)
    ax.set_yticklabels(od_ticks)
    ax.set_ylim(0.0008, 1.6)
    ax.grid(color="k", linestyle="--", alpha=0.3)
    ax.set_xlabel("Time [hours from %s]" % time.ctime(tmin * 3600))

    plot_title = "%s %s" % (culture.name, culture.directory)
    fig.axes[0].set_title(plot_title)
    return fig


def plot_temperature(culture, fig, last_hours):
    df = read_csv_tail(os.path.join(culture.device.directory, "temperature.csv"), last_hours * 60)
    ax4 = fig.axes[0].twinx()
    ax4.plot(df.index.values/3600, df.temperature_vials, ".", label="temperature")
    ax4.spines["right"].set_position(("axes", 0.1))
    ax4.yaxis.set_label_position("right")
    ax4.yaxis.set_ticks_position("right")
    ax4.legend()
