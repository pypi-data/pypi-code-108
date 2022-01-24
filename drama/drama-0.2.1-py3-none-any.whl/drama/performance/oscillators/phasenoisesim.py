__author__ = "Paco Lopez Dekker"
__email__ = "F.LopezDekker@tudeft.nl"

import numpy as np
from matplotlib import pyplot as plt
from drama import utils as drtls


def phasenoise(T, dt, fpow, coef):
    """Computer a phase noise run

    Parameters
    ----------
    T :
        param dt:
    fpow :
        powers of f used
    coef :
        corresponsing coefficients
    dt :


    Returns
    -------

    """
    nsamp = int(2 ** np.ceil(np.log2(2 * T / dt)))
    f = np.fft.fftfreq(nsamp, dt)
    fp = np.array([fpow])
    fp = fp.reshape((fp.size, 1))
    cf = np.array(coef)
    cf = cf.reshape((fp.size, 1))
    f[0] = 1
    S = np.sum(np.power(f.reshape((1, nsamp)), fp) * cf, axis=0) * f[1]
    S[0] = 0
    f[0] = 0
    ph = nsamp * np.fft.ifft(np.random.randn(nsamp) * np.sqrt(S))
    return (np.real(ph), S)


def allan_variance(ph, dt, tau):
    """

    Parameters
    ----------
    ph :

    dt :

    tau :


    Returns
    -------

    """
    tausmp = int(np.round(tau / dt))
    tau_ = dt * tausmp
    phs = ph[::tausmp]
    frs = (phs[1:] - phs[0:-1]) / (2 * np.pi * tau_)
    dfrs = frs[1:] - frs[0:-1]
    return np.mean(dfrs ** 2)


def plot_freq(ph, dt, tau, overplot=False, xlim=None, toff=250):
    """

    Parameters
    ----------
    ph :

    dt :

    tau :

    overplot :
         (Default value = False)
    xlim :
         (Default value = None)
    toff :
         (Default value = 250)

    Returns
    -------

    """
    tausmp = int(np.round(tau / dt))
    tau_ = dt * tausmp
    ifr = (ph[tausmp:] - ph[0:-tausmp]) / (2 * np.pi * tau_)
    t = np.arange(ifr.size) * dt - toff + tau_ / 2
    if xlim is None:
        xlim = (0, t.max() / 2)
    mask = (t >= xlim[0]) & (t < xlim[1])
    if overplot:
        plt.plot(t[mask], ifr[mask], label=(r"$\tau=$%3.1f" % tau))
    else:
        plt.figure()
        plt.plot(t[mask], ifr[mask], label=(r"$\tau=$%3.1f" % tau))
        plt.xlabel("Time [s]")
        plt.ylabel(r"$f_{\tau}$ [Hz]")
        ax = plt.gca()
        ax.grid(True)
        plt.tight_layout()


if __name__ == "__main__":
    # random frequency walk as for StereoSAR report
    h_2 = (3e-11) ** 2 * 3 / (2 * np.pi ** 2 * 1e3)
    p, S = phasenoise(10000, 1, -4, h_2)
    pCband = p * 5.4e9
    plot_freq(pCband, 1, 1, xlim=(0, 1200))
    plot_freq(pCband, 1, 100, overplot=True, xlim=(0, 1200))
    plot_freq(pCband, 1, 500, overplot=True, xlim=(0, 1200))

    plt.legend()
    allan_variance(pCband, 1, 100)
