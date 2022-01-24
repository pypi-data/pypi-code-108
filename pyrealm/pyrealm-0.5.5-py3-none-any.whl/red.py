import numpy as np
from scipy.optimize import curve_fit
import warnings
import matplotlib.pyplot as plt
import json


# https://stackoverflow.com/questions/51662473/using-gaussian-mixture-for-1d-array-in-python-sklearn

# Differences between this and Maxime's work
# 1) Gaussian curves estimated simultaneously. Maxime split the data frame
#    and estimated separate curves for each partition.
# 2) Selection using AICc to identify the best representation


def gauss_single(x: np.ndarray, ampl: float, mu: float, sigma:float) -> np.ndarray:
    """Calculates the density of a Gaussian distribution for values in
    ``x`` given the amplitude, mean and variance.

    Args:
        x: An array of values to calculate t
        ampl: The amplitude
        mu: The mean
        sigma: The variance

    Returns:
        An ndarray with the same shape as ``x`` containing density values
    """

    return ampl * np.exp(-(x - mu) ** 2 / (2. * sigma ** 2))


def gauss_multiple(x, *pars):
    """Calculates the density for values in ``x`` of a set of superimposed
     Gaussian distributions. The parameters of those distributions are passed
     in ``pars`` as a sequence of parameters giving the amplitude, mean and
     variance in turn of each Gaussian. This allows the function to be used
     easily with curve_fit.

    Args:
        x: An array of values to calculate t
        *pars: Gaussian parameters

    Returns:
        An ndarray with the same shape as ``x`` containing density values
    """
    if len(x) <= len(pars):
        raise ValueError('Overfitting: more parameters than data')
    try:
        pars = np.array(pars)
        pars = pars.reshape(-1, 3)
    except ValueError:
        raise ValueError('gaussN requires extra parameters in multiples of 3')

    curves = np.array([gauss_single(x, *pr) for pr in pars])

    return curves.sum(axis=0)


def calc_log_lik(obs: np.ndarray, pred: np.ndarray) -> float:
    """Calculates the log-likelihood of the predicted data given the
    observations

    Args:
        obs: An array of observed values
        pred: n array of predicted values of the same shape as ``obs``

    Returns:
        The log likelihood estimate
    """

    n_obs = len(obs)
    res = obs - pred

    return 0.5 * (- n_obs * (np.log(2 * np.pi) + 1 - np.log(n_obs) +
                             np.log(sum(res ** 2))))


def calc_aic(obs: np.ndarray, pred: np.ndarray, params: np.ndarray,
             k: int = 2, aicc: bool = True) -> float:
    """

    Args:
        obs: An array of observed values
        pred: An array of predicted values of the same shape as ``obs``
        params: An array of the estimated parameters used to predict ``pred``
        k: Penalty value.
        aicc: Apply the small sample correction to AIC.

    Returns:
        The AIC or AICc value
    """

    ll = calc_log_lik(obs, pred)
    df = len(params) + 1
    no = len(obs)

    if aicc:
        return (-2 * ll) + (k * df) * (1 + ((df + 1)/(no - df - 1)))
    else:
        return (-2 * ll) + (k * df)


class GaussSelect:

    def __init__(self, x, y):

        self.x = x
        self.y = y

        # Define attributes used in fit() method
        self.nmax = None
        self.use_bounds = None
        self.use_aicc = None
        self.aic = None
        self.fitted = None
        self.fit_complete = False

    def fit(self, n_max=3, use_aicc=True, use_bounds=True):

        self.use_aicc = use_aicc
        self.nmax = n_max
        self.aic = np.empty(n_max + 1)
        self.aic[:] = np.nan
        self.fitted = [None] * (n_max + 1)
        self.use_bounds = use_bounds

        # Null model - no gaussians
        self.fitted[0] = []
        self.aic[0] = calc_aic(self.y, np.ones_like(self.y) * self.y.mean(), self.fitted[0],
                               aicc=self.use_aicc)

        # Loop over gaussian fits
        for ng in np.arange(1, n_max + 1):

            # Initial estimates - provided to the function as a 1D array
            # of contiguous sets of amplitude, mean and sigma
            init = np.ones(3 * ng)

            # Bound the amplitude and sigma to be positive, but not the mean
            if self.use_bounds:
                lbound = (0, -np.inf, 0) * ng
                ubound = (np.inf, np.inf, np.inf) * ng
                bounds = (lbound, ubound)
            else:
                bounds = (-np.inf, np.inf)

            try:
                # Fit the curve and save the estimated parameters
                self.fitted[ng], _ = curve_fit(gauss_multiple, self.x, self.y, p0=init,
                                               bounds=bounds)

                # Get the predictions for this number of gaussians
                yp = gauss_multiple(self.x, self.fitted[ng])

                # Estimate AIC
                self.aic[ng] = calc_aic(self.y, yp, self.fitted[ng],
                                        aicc=self.use_aicc)

            except RuntimeError as err:
                warnings.warn(f'Could not fit multiple gaussian for n = {ng}: {err}')

        self.fit_complete = True

    def plot(self, res=101):

        if self.fit_complete:
            # Interpolate closely spaced points across x
            xplot = np.linspace(np.min(self.x), np.max(self.x), res)

            # Get predictions for null model and each gaussian fit
            # interpolating NaN for models that did not fit.
            yplots = [np.ones_like(xplot) * self.y.mean()]

            for cf in self.fitted[1:]:

                if cf is not None:
                    yplots.append(gauss_multiple(xplot, cf))
                else:
                    no_fit = np.empty_like(xplot)
                    no_fit[:] = np.nan
                    yplots.append(no_fit)

            # Plot worse models in grey
            best_fit = np.nanargmin(self.aic)
            worse_models = np.delete(np.arange(len(self.fitted)), best_fit)

            for idx in worse_models:

                plt.plot(xplot, yplots[idx], 'grey')

            plt.plot(xplot, yplots[best_fit], 'red')

        plt.scatter(self.x, self.y)

        plt.show()




#
# mort = '/Users/dorme/Research/REALM/Files_from_Maxime/Nouveau dossier/sukumar_mort.json'
# recr = '/Users/dorme/Research/REALM/Files_from_Maxime/Nouveau dossier/sukumar_recr.json'
#
# mort_data = json.load(open(mort))
# recr_data = json.load(open(recr))
#
# species = ["LAGL", "TERT", "HELI", "ANOL", "TECG", "TECG",
#            "RAND", "SYZC", "PHYE", "KYDC", "STET", "GRET"]
#
# size_class_bounds = np.array([0, 0.9993767, 1.5991664, 2.5628244, 4.1307247,
#                               6.7151617, 11.0502286, 18.5878071, 32.429648,
#                               59.8845962, 117.383105, 235.2833097, 480])
#
# size_class_widths = np.diff(size_class_bounds, n=1)
# size_class_mids = size_class_bounds[:-1] + size_class_widths / 2
# ln_size_class_mids = np.log(size_class_mids)
#
#
# for sp in species:
#
#     sp_mort_data = mort_data[sp]['survivors']
#     sp_recr_data = recr_data[sp]['recruits.or.dead']
#
#     first = [rw['1988-1992'] for rw in sp_mort_data]
#
#     rates = first[:-1] / size_class_widths
#
#     g = GaussSelect(ln_size_class_mids, rates)
#     g.plot()
#     g.fit(use_bounds=False)
#     g.plot()
#
#
# mort_data['GRET']['survivors']
#
# ## Components
#
# # T Model
# default_settings =
# {'a_hd': 116.0,
#  'ca_ratio': 390.43,
#  'h_max': 25.33,
#  'rho_s': 200.0,
#  'lai': 1.8,
#  'sla': 14.0,
#  'tau_f': 4.0,
#  'tau_r': 1.04,
#  'par_ext': 0.5,
#  'yld': 0.17,
#  'zeta': 0.17,
#  'resp_r': 0.913,
#  'resp_s': 0.044,
#  'resp_f': 0.1}