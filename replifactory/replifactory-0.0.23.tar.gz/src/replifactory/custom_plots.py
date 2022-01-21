import pandas as pd
from growth_rate import adaptive_window_doubling_time
from matplotlib import pyplot as plt


def plot_doubling_time_vs_od(time_values, od_values, dilution_timepoints=None):
    # global plt
    # if plt is None:
    #     import matplotlib.pyplot as plt

    # if od_values.min() <= 0:
    #     od_values = od_values-od_values.min()+1e-6
    od_values[od_values <= 0] = 1e-6

    df = pd.DataFrame(od_values, index=time_values, columns=["od"])

    ttd, td, err = adaptive_window_doubling_time(df.index.values, df.od.values, dilution_timepoints=dilution_timepoints)
    dftd = pd.DataFrame(td, index=ttd, columns=["td"])
    dftd.loc[:, "error"] = err
    dftd.index = dftd.index.astype(int)
    comb = df.merge(dftd, left_index=True, right_index=True)

    plt.figure(figsize=[12, 6])
    markers, caps, bars = plt.errorbar(comb.od, comb.td, yerr=comb.error, fmt="r.")
    [bar.set_alpha(0.5) for bar in bars]
    plt.ylim(0.3, 17)
    plt.xlim(-0.05, 1.5)
    plt.yscale("log")
    plt.yticks([0.5, 1, 2, 3, 4, 5, 10], labels=[0.5, 1, 2, 3, 4, 5, 10])
    plt.grid()
    plt.title("Effect of culture density on growth rate")
    plt.xlabel("Optical Density")
    plt.ylabel("Doubling time [hours]")