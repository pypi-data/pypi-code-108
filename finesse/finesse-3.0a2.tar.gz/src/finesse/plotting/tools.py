import logging

from .style import use
from ..env import warn

LOGGER = logging.getLogger(__name__)

DEFAULT_FORMATS = ("svg",)


def _in_ipython():
    """Checks whether the current script is running under IPython.

    Returns
    -------
    bool
        True if __IPYTHON__ is defined, otherwise False.
    """
    try:
        __IPYTHON__
    except NameError:
        return False
    else:
        return True


def init(mode="display", dpi=None, fmts=None):
    """Sets up default plotting parameters for a desired display mode.

    Parameters
    ----------
    mode : str
        Display mode to use, either 'display' or 'paper'.

    dpi : int, optional
        DPI (Dots per inch) to display and save figures with. Defaults to
        current setting.

    fmts : list of str, optional
        List of image formats to allow for display when running under IPython; defaults to
        :data:`.DEFAULT_FORMATS`.
    """
    import matplotlib as mpl

    if fmts is None:
        fmts = DEFAULT_FORMATS

    if _in_ipython():
        try:
            from IPython.display import set_matplotlib_formats

            ipy = get_ipython()
            try:
                ipy.magic("matplotlib inline")
            except KeyError:
                try:
                    ipy.magic("matplotlib qt")
                except KeyError:
                    warn("Could not set matplotlib backend. Tried inline and Qt.")
            finally:
                set_matplotlib_formats(*fmts)
        except NameError:
            pass

    # TODO (sjr) handle plotting options in user config

    if mode == "display":
        use(["default"])
    elif mode == "paper":
        if not _in_ipython():
            mpl.use("pgf")
        use(["default", "paper"])
    else:
        raise (BaseException("Plotting mode must be either 'display' or 'paper'."))

    if dpi is not None:
        dpi = int(dpi)
        mpl.rcParams.update({"figure.dpi": dpi})
        mpl.rcParams.update({"savefig.dpi": dpi})
    # always apply white background and remove transparency. Make plots readable
    # when using dark background/themes in jupyter notebooks and such
    mpl.rcParams.update(
        {
            "figure.facecolor": (1.0, 1.0, 1.0, 1.0),
        }  # red   with alpha = 30%
    )


def add_colorbar(im, **kwargs):
    """Adds a vertical color bar to an image plot.

    Parameters
    ----------
    im : :class:`matplotlib.image.AxesImage`

      An image plot, e.g. return value of a call to ``plt.imshow()``.

    Returns
    -------
    Handle to the colorbar.
    """
    ## Credit to: https://joseph-long.com/writing/colorbars/
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    import matplotlib.pyplot as plt

    last_axes = plt.gca()
    ax = im.axes
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = fig.colorbar(im, cax=cax, **kwargs)
    plt.sca(last_axes)
    return cbar
