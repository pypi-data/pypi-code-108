import numpy as np
import matplotlib.pyplot as plt

def multi_ACFfig(x, nlags=10, linewidth=1):
        """
        Plot sample or residual cross-autocorrelation function

        Parameters
        ----------
        x : array-like
        nlags : int
            The number of lags to use in compute the autocorrelation. Does
            not count the zero lag, which will be returned.
        linewidth : int
            The linewidth for the plots.

        Returns
        -------
        fig : matplotlib.Figure
            The figure that contains the plot axes.
        """

        acovs = _compute_acov(x)
        acorr = _acovs_to_acorrs(acovs)
        acorr = acorr[0:nlags+1]
        bound = 1.96 / np.sqrt(len(x))
        fig = plot_full_acorr(acorr, err_bound=bound, linewidth=linewidth)
        plt.show()
        
        return fig


def _compute_acov(x):
     x = x - x.mean(0)
     leng=len(x)

     result = []
     for lag in range(leng):
         if lag > 0:
             r = np.dot(x[lag:].T, x[:-lag])
         else:
             r = np.dot(x.T, x)

         result.append(r)

     return np.array(result) / len(x)


def _acovs_to_acorrs(acovs):
    sd = np.sqrt(np.diag(acovs[0]))
    return acovs / np.outer(sd, sd)


def plot_full_acorr(acorr, fontsize=8, linewidth=8, xlabel=None, err_bound=None):
    """

    Parameters
    ----------

    """

    #config = MPLConfigurator()
    #config.set_fontsize(fontsize)

    k = acorr.shape[1]
    fig, axes = plt.subplots(k, k, figsize=(10, 10), squeeze=False)

    for i in range(k):
        for j in range(k):
            ax = axes[i][j]
            acorr_plot(acorr[:, i, j], linewidth=linewidth,
                       xlabel=xlabel, ax=ax)

            if err_bound is not None:
                ax.axhline(err_bound, color='b', linestyle='--')
                ax.axhline(-err_bound, color='b', linestyle='--')

    #adjust_subplots()
    #config.revert()

    return fig

def acorr_plot(acorr, linewidth=8, xlabel=None, ax=None):
    import matplotlib.pyplot as plt

    if ax is None:
        ax = plt.gca()

    if xlabel is None:
        xlabel = np.arange(len(acorr))

    ax.vlines(xlabel, [0], acorr, lw=linewidth)

    ax.axhline(0, color='k')
    ax.set_ylim([-1, 1])
    ax.set_xticks(ticks=range(0, len(acorr)+1, 2))


