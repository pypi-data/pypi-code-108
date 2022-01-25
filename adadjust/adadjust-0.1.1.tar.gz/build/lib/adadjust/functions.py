from typing import Callable, Union, Optional, Collection
from scipy.optimize import leastsq
import logging
import numpy as np
import tablewriter
import pandas as pd
import matplotlib.pyplot as plt
from colorstylecycler import Cycler

logger = logging.getLogger(__name__)


class Function:
    def __init__(self, method: Callable, equation: str):

        """
        Mathematical function to fit on some data.
        For now, only 1-D functions are supported.

        Examples:
        >>> from adadjust import Function
        >>> # noinspection PyShadowingNames
        >>> import numpy as np
        >>> # noinspection PyShadowingNames
        >>> import matplotlib.pyplot as plt
        >>> plt.rcParams.update({"text.usetex": True})  # Needs texlive installed
        >>>
        >>> nsamples = 1000
        >>> a = 0.3
        >>> b = -10
        >>> xstart = 0
        >>> xend = 1
        >>> noise = 0.01
        >>> x = np.linspace(xstart, xend, nsamples)
        >>> y = a * x ** 2 + b + np.random.normal(0, noise, nsamples)
        >>>
        >>>
        >>> def linfunc(xx, p):
        >>>     return xx * p[0] + p[1]
        >>>
        >>>
        >>> def square(xx, p):
        >>>     return xx ** 2 * p[0] + p[1]
        >>>
        >>>
        >>> func = Function(linfunc, "$a \\times p[0] + p[1]$")
        >>> func2 = Function(square, "$a^2 \\times p[0] + p[1]$")
        >>>
        >>> params = func.fit(x, y, np.array([0, 0]))[0]
        >>> rr = func.compute_rsquared(x, y, params)
        >>>
        >>> params2 = func2.fit(x, y, np.array([0, 0]))[0]
        >>> rr2 = func2.compute_rsquared(x, y, params2)
        >>>
        >>> table = Function.make_table(
        >>> [func, func2], [params, params2], [rr, rr2], caption="Linear and Square fit", path_output="table.pdf"
        >>> )
        >>> table.compile()
        >>> Function.plot(x, [func, func2], [params, params2], y=y, rsquared=[rr, rr2])
        >>> plt.gcf().savefig("plot.pdf")

        Parameters
        ----------
        method: Callable
            The function to fit. It must take as first argument the x on which to compute the function, then
            the adjustable parameters in one tuple, then and any number of additionnal arguments.
        equation: str
            The function's equation in LaTeX, for rendering. Adjustable parameters must be specified through the
            synthax 'p[i]'. For example, a linear function's equation would be '$p[0] \\times x + p[1]$'.
        """
        self.method = method
        self.equation = equation

    def __call__(self, *args):
        return self.method(*args)

    def make_result_equation(self, params: Union[list, tuple, np.ndarray], r: Optional[float] = None) -> str:
        """From a given set of adjustable parameter values, and an optionnal r² value, replaces the 'p[i]' in the
        function's equation by their corresponding values in 'params'. If r² is specified, will be appended to the
        equation in a new line.

        Examples:
        >>> from adadjust import Function
        >>> def func(x, p):
        >>>     return p[0] * x + p[1]
        >>> f = Function(func, "$p[0] \\times x + p[1]$")
        >>> res = f.make_result_equation((1, -2), 0.8)
        "\\setlength{\\parindent}{0cm} $1 \\times x - 2$\\\\$r^2=0.8$"

        Parameters
        ----------
        params: Union[list, tuple, np.ndarray]
        r: Optional[float]

        Returns
        -------
        str
            The equation with values instead of 'p[i]'
        """
        s = self.equation
        for iparam in range(len(params)):
            param = params[iparam]
            if param < 0:
                s = s.replace(f"+ p[{iparam}]", format_x(param))
                s = s.replace(f"+p[{iparam}]", format_x(param))
                s = s.replace(f"- p[{iparam}]", format_x(float(str(param).replace("-", ""))))
                s = s.replace(f"-p[{iparam}]", format_x(float(str(param).replace("-", ""))))
                s = s.replace(f"p[{iparam}]", f"({format_x(param)})")
            else:
                s = s.replace(f"p[{iparam}]", f"{format_x(param)}")
        if r is not None:
            s = f"{s}\\\\$r^2={r}$"
        s = "".join(["\\setlength{\\parindent}{0cm} ", s])
        return s

    def fit(
        self,
        x: np.ndarray,
        y: np.ndarray,
        init: np.ndarray,
        yerrup: Optional[np.ndarray] = None,
        yerrdown: Optional[np.ndarray] = None,
        args: tuple = (),
        **kwargs,
    ):
        """Adjust the function on 'x' and 'y' by using least square method.

        Parameters
        ----------
        x: np.ndarray
            The coordinates on which to fit
        y: np.ndarray
            The results on which to fit
        init: np.ndarray
            The initial values of the function's parameters
        yerrup: Optional[np.ndarray]
            The upper error of 'y', used to weight the data points
        yerrdown: Optional[np.ndarray]
            The lower error of 'y', used to weight the data points
        args: tuple
            Any additionnal arguments to give to self.method
        **kwargs
            Any additionnal keyword arguments to pass to scipy.optimize.leastsq

        Returns
        -------
        Same as scipy.optimize.leastsq
        """

        def my_error(*args_):
            yfit = self(x, *args_)
            weight = np.ones_like(yfit)
            if yerrdown is None:
                if yerrup is None:
                    return (yfit - y) ** 2
                weight[yfit > y] = yerrup[yfit > y]
            weight[yfit <= y] = yerrdown[yfit <= y]
            return (yfit - y) ** 2 / weight ** 2

        if len(x) < len(init):
            logger.warning("Can not fit a function with less observations than parameters")
            return None
        if len(x) == len(init):
            logger.warning("Fitting a function with the same number of observations than parameters")
        results = leastsq(my_error, x0=init, args=args, **kwargs)
        return results

    def predict(self, x: np.ndarray, params: np.ndarray, *args):
        """Same as calling self(x, params, *args)"""
        return self.method(x, params, *args)

    def compute_rsquared(self, x: np.ndarray, y: np.ndarray, params: np.ndarray, *args) -> float:
        """Comptue the r² of a fit result.

        r² indicates how much better the fitted parameters are compared to simply predicting the means of 'y'. It can be
        negative if the fit is worse than predicting the mean. If r²=0, the parameters predict the mean of 'y'. If
        r²=1, the fit is perfect (all predicted points perfectly match observations).

        Note that if the mean of 'y' also is a perfect fit (i.e, an ohrizontal line), the value of r is not defined for
        a division by 0 would occur.

        Parameters
        ----------
        x: np.ndarray
            The coordinates on which the fit was done
        y: np.ndarray
            The results on which the fit was done
        params: np.ndarray
            The fitted values of the function's parameters
        *args
            additionnal arguments to pass to self.method

        Returns
        -------
        float
            r² value
        """
        rss = np.sum((y - self(x, params, *args)) ** 2)
        tss = np.sum((y - np.mean(y)) ** 2)
        rr = 1 - (rss / tss)
        return rr

    @staticmethod
    def make_table(
        functions: Collection["Function"],
        params: Collection[np.ndarray],
        rsquared: Optional[Collection[float]] = None,
        **table_kwargs,
    ) -> tablewriter.TableWriter:
        """Create a TableWriter object representing the fit results of several Function objects.

        Parameters
        ----------
        functions: Collection[Function]
            Several Functions fitted on the same data, passed in a collection of any kind.
        params: Collection[np.ndarray]
            The fitted parameters of the Functions.
        rsquared: Optional[Collection[float]]
            The r²s of the Functions.
        table_kwargs
            Any additionnal keyword arguments to give to TableWriter

        Returns
        -------
        tablewriter.TableWriter
        """
        nparams = max([len(par) for par in params])
        # noinspection PyUnresolvedReferences
        data = [
            [format_x(params[if_][ip], True) if ip < nparams else np.nan for ip in range(len(params[if_]))]
            for if_ in range(len(functions))
        ]

        table_g = pd.DataFrame(
            columns=[f"param {i}" for i in range(nparams)], index=[f.equation for f in functions], data=data
        )
        if rsquared is not None:
            s = pd.DataFrame(index=table_g.index, data=rsquared, columns=["$r^2$"])
            table_g = pd.concat([table_g, s], axis=1)

        return tablewriter.TableWriter(data=table_g, **table_kwargs)

    @staticmethod
    def plot(
        x: np.ndarray,
        functions: Collection["Function"],
        params: Collection[np.ndarray],
        y: Optional[np.ndarray] = None,
        ax: Optional[plt.Axes] = None,
        yerr: Optional[np.ndarray] = None,
        xerr: Optional[np.ndarray] = None,
        xshow: Optional[np.ndarray] = None,
        rsquared: Collection[float] = None,
        argss: Collection[tuple] = None,
        **plot_kwargs,
    ) -> plt.Axes:
        """
        Plots the result of the fits of several Function.

        Parameters
        ----------
        x: np.ndarray
            The 'x' on which the fit was done
        functions: Collection[Function]
            A collection of Functions that were fitted on 'x'
        params: Collection[np.ndarray]
            The fitter parameters of the Functions
        y: Optional[np.ndarray]
            The measured 'y' values used in the fit.
        ax: Optional[plt.Axes]
            The plt.Axes on which to plot. Will use plt.gca() if None.
        yerr: Optional[np.ndarray]
            The error on y. See plt.errorbar.
        xerr: Optional[np.ndarray]
            The error on x. See plt.errorbar.
        xshow: Optional[np.ndarray]
            The values of 'x' on which the fitted function should be plotted. If None, uses 'x'
        rsquared: Collection[float]
            The r² of the fitted Functions
        argss: Collection[tuple]
            The additionnal arguments the the fitted Functions
        **plot_kwargs
            Any keyword arguments to pass to plot methods.
            * 'lw' will be used for plotting the Functions (default value = 4)
            * 'fmt' or 'marker' will be used for plotting 'y' vs 'x' (default value = "o")
            * 's' will be used for plotting 'y' vs 'x' (default value = 10)
            * 'label' will define the label of 'y' vs 'x' (default value = "data")
            Any other arguments must be valid for plt.scatter, plt.errorbar and plt.plot.

        Returns
        -------
        plt.Axes
        """
        if argss is None:
            argss = [[] for _ in functions]
        if ax is None:
            ax = plt.gca()
        if rsquared is None:
            rsquared = [None for _ in functions]

        nitems = len(functions)
        fmt = plot_kwargs.get("fmt", "o")
        ms = plot_kwargs.get("s", 10)
        lw = plot_kwargs.get("lw", 4)
        ylabel = plot_kwargs.get("label", "data")

        if "fmt" in plot_kwargs:
            del plot_kwargs["fmt"]
        if "s" in plot_kwargs:
            del plot_kwargs["s"]
        if "lw" in plot_kwargs:
            del plot_kwargs["lw"]
        if "label" in plot_kwargs:
            del plot_kwargs["label"]

        cycler = Cycler(ncurves=nitems, color_start="darkred", color_end="darkblue")
        plt.rc("axes", prop_cycle=cycler.cycler)

        if y is not None:
            if yerr is None and xerr is None:
                ax.scatter(x=x, y=y, c="black", marker=fmt, label=ylabel, s=ms, **plot_kwargs)
            else:
                ax.errorbar(x=x, y=y, yerr=yerr, xerr=xerr, c="black", fmt=fmt, s=ms, label=ylabel, **plot_kwargs)

        if xshow is not None:
            x = xshow
        for function, param, r, args in zip(functions, params, rsquared, argss):
            ax.plot(
                x,
                function(x, param, *args),
                label=function.make_result_equation(param, r),
                lw=lw,
                **plot_kwargs,
            )
        ax.legend()
        return ax


def format_x(s: Union[float, int], with_dollar: bool = False) -> str:
    """For a given number, will put it in scientific notation if its absolute value is lower than 0.01 and greater than,
    1000 using LaTex synthax. If 'with_dollar' is True and if s is in LaTeX synthax, will return $2.0\\cdot 10^{3}$
    instead of 2.0\\cdot 10^{3}.

    Parameters
    ----------
    s: Union[float, int]
    with_dollar: bool
        Default to False

    Returns
    -------
    str
    """
    if 1000 > abs(s) > 0.01:
        xstr = str(round(s, 2))
    else:
        xstr = "{:.4E}".format(s)
        if "E-" in xstr:
            lead, tail = xstr.split("E-")
            middle = "-"
        else:
            lead, tail = xstr.split("E")
            middle = ""
        lead = round(float(lead), 2)
        tail = round(float(tail), 2)
        if with_dollar:
            xstr = ("$\\cdot 10^{" + middle).join([str(lead), str(tail)]) + "}$"
        else:
            xstr = ("\\cdot 10^{" + middle).join([str(lead), str(tail)]) + "}"
    return xstr
