try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

if framework:
    print('Loading plot utility functions...')

from omfit_classes.utils_base import _available_to_user_plot
from omfit_classes.utils_math import is_uncertain, interp1e, unsorted_unique, RectBivariateSplineNaN, point_to_line
from omfit_classes.sortedDict import SortedDict

# explicit imports
import numpy as np
from xarray import Dataset, DataArray
import uncertainties
import inspect
from scipy import interpolate, integrate
import matplotlib
from matplotlib import pyplot, gridspec, cm
from matplotlib.widgets import RectangleSelector, RadioButtons, AxesWidget
from mpl_toolkits.mplot3d import Axes3D
import platform
import re

default_colorblind_line_cycle = [
    '#1f77b4',
    '#ff7f0e',
    '#2ca02c',
    '#d62728',
    '#9467bd',
    '#8c564b',
    '#e377c2',
    '#7f7f7f',
    '#bcbd22',
    '#17becf',
]
default_matplotlib_line_cycle = eval(re.sub(r'.*(\[.*\]).*', r'\1', str(matplotlib.rcParams['axes.prop_cycle'])))
default_colorblind_line_cycle = matplotlib.cycler('color', default_colorblind_line_cycle)
default_matplotlib_cmap_cycle = 'viridis'
matplotlib.style.core.USER_LIBRARY_PATHS.append(OMFITsrc + '/extras/styles')
matplotlib.style.core.reload_library()
# Colormap definition for "Standard Gamma-II" colormap from IDL
# fmt: off
_r = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               4, 9, 14, 19, 23, 28, 33, 38, 42, 47, 52, 57, 61, 66, 71, 76,
               81, 81, 81, 81, 81, 81, 81, 81, 80, 80, 80, 80, 80, 80, 80, 79,
               84, 89, 94, 99, 104, 109, 114, 119, 124, 129, 134, 139, 144, 149, 154, 159,
               164, 169, 174, 180, 185, 190, 196, 201, 206, 212, 217, 222, 228, 233, 255, 255,
               255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
               255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
               255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
               255, 255, 255, 248, 240, 232, 225, 217, 209, 202, 194, 186, 179, 171, 163, 168,
               173, 178, 183, 188, 193, 198, 203, 209, 214, 219, 224, 229, 234, 239, 244, 249,
               255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
               255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
               255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
               255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255])
_g = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 5, 10, 16, 21, 27, 32, 37, 43, 48, 54, 59, 64, 70, 75,
               81, 85, 90, 95, 100, 105, 109, 114, 119, 124, 129, 134, 138, 143, 148, 153,
               158, 163, 163, 163, 163, 163, 163, 163, 163, 163, 163, 163, 163, 163, 163, 163,
               163, 163, 163, 163, 163, 163, 163, 163, 163, 163, 163, 163, 163, 163, 163, 163,
               163, 169, 175, 181, 187, 193, 199, 205, 212, 218, 224, 230, 236, 242, 248, 255,
               255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
               255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
               255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
               255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255])
_b = np.array([0, 5, 10, 15, 20, 26, 31, 36, 41, 46, 52, 57, 62, 67, 72, 78,
               83, 88, 93, 98, 104, 109, 114, 119, 124, 130, 135, 140, 145, 150, 156, 161,
               166, 171, 176, 182, 187, 192, 197, 202, 208, 213, 218, 223, 228, 234, 239, 244,
               249, 255, 250, 245, 239, 234, 228, 223, 218, 212, 207, 201, 196, 190, 185, 180,
               174, 169, 163, 158, 152, 147, 142, 136, 131, 125, 120, 114, 109, 104, 98, 93,
               87, 82, 76, 71, 66, 60, 55, 49, 44, 38, 33, 28, 22, 17, 11, 6,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 4, 9, 14, 19, 24, 28, 33, 38, 43, 48, 53, 57, 62, 67, 72,
               77, 82, 77, 71, 65, 59, 53, 47, 41, 36, 30, 24, 18, 12, 6, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 3, 6, 9, 12, 16, 19, 22, 25, 29, 32, 35, 38, 41, 45, 48,
               51, 54, 58, 61, 64, 67, 71, 74, 77, 80, 83, 87, 90, 93, 96, 100,
               103, 106, 109, 112, 116, 119, 122, 125, 129, 132, 135, 138, 142, 145, 148, 151,
               154, 158, 161, 164, 167, 171, 174, 177, 180, 183, 187, 190, 193, 196, 200, 203,
               206, 209, 213, 216, 219, 222, 225, 229, 232, 235, 238, 242, 245, 248, 251, 255])
# fmt: on
_rgb = np.column_stack((_r, _g, _b)) / 255.0
cm.register_cmap(cmap=matplotlib.colors.ListedColormap(_rgb, name='Standard Gamma-II'))
matplotlib.rcParams['image.cmap'] = default_matplotlib_cmap_cycle
matplotlib.rcParamsDefault.update(matplotlib.rcParams)

if platform.system() == 'Darwin':
    rightClickMPLindex = 2
    middleClickMPLindex = 3
else:
    rightClickMPLindex = 3
    middleClickMPLindex = 2


@_available_to_user_plot
def autofmt_sharexy(trim_xlabel=True, trim_ylabel=True, fig=None):
    # todo: docstring
    if fig is None:
        fig = pyplot.gcf()
    autofmt_sharex(trim_ylabel=trim_ylabel, fig=fig)
    autofmt_sharey(trim_xlabel=trim_xlabel, fig=fig)


@_available_to_user_plot
def autofmt_sharey(trim_xlabel=True, fig=None, wspace=0):
    """
    Prunes y-tick labels and y-axis labels from all but the first cols axes
    and moves cols (optionally) closer together.

    :param trim_xlabel: bool. prune right ytick label to prevent overlap.

    :param fig: Figure. Defaults to current figure.

    :param wspace: Horizontal spacing between axes.
    """
    if fig is None:
        fig = pyplot.gcf()

    for a in fig.axes:

        if hasattr(a, 'is_first_col') and not a.is_first_col():
            for yt in a.get_yticklabels():
                yt.set_visible(False)
            a.set_ylabel('')

        if len(a.get_xticklabels()) and trim_xlabel:
            try:
                a.xaxis.major.locator.set_params(prune='upper')
            except Exception:
                pass

    fig.subplots_adjust(wspace=wspace)


@_available_to_user_plot
def autofmt_sharex(trim_ylabel=True, fig=None, hspace=0):
    """
    Prunes x-tick labels and x-axis labels from all but the last row axes
    and moves rows (optionally) closer together.

    :param trim_ylabel: bool. prune top ytick label to prevent overlap.

    :param fig: Figure. Defaults to current figure.

    :param hspace: Vertical spacing between axes.
    """
    if fig is None:
        fig = pyplot.gcf()

    for a in fig.axes:
        if hasattr(a, 'is_last_row') and not a.is_last_row():
            for xt in a.get_xticklabels():
                xt.set_visible(False)
            a.set_xlabel('')
            a.xaxis.get_offset_text().set_visible(False)

        if len(a.get_yticklabels()) and trim_ylabel:
            try:
                a.yaxis.major.locator.set_params(prune='upper')
            except Exception:
                pass

    fig.subplots_adjust(hspace=hspace)


@_available_to_user_plot
def uerrorbar(x, y, ax=None, **kwargs):
    r"""
    Given arguments y or x,y where x and/or y have uncertainties, feed the
    appropriate terms to matplotlib's errorbar function.

    If y or x is more than 1D, it is flattened along every dimension but the last.

    :param x: array of independent axis values

    :param y: array of values with uncertainties, for which shaded error band is plotted

    :param ax: The axes instance into which to plot (default: pyplot.gca())

    :param \**kwargs: Passed to ax.errorbar

    :return: list. A list of ErrorbarContainer objects containing the line, bars, and caps of each (x,y) along the last dimension.
    """
    result = []

    # set default key word arguments
    if ax is None:
        ax = pyplot.gca()
    kwargs.setdefault('marker', 'o')
    kwargs.pop('axes', None)  # don't let them use this because we used ax
    if 'linestyle' not in kwargs and 'ls' not in kwargs:
        kwargs['linestyle'] = ''
    if np.all(std_devs(y) == 0) and np.all(std_devs(x) == 0):
        kwargs.setdefault('capsize', 0)

    # enable combinations of 1D and 2D x's and y's
    y = np.array(y)
    y = y.reshape(-1, y.shape[-1])
    x = np.array(x)
    x = x.reshape(-1, x.shape[-1])
    if x.shape[0] == 1 and y.shape[0] > 1:  # one x for all y's
        x = np.tile(x[0, :], y.shape[0]).reshape(-1, x.shape[-1])

    # plot each (x,y) and collect container objects
    for xi, yi in zip(x, y):
        tmp = ax.errorbar(nominal_values(xi), nominal_values(yi), xerr=std_devs(xi), yerr=std_devs(yi), **kwargs)
        result.append(tmp)

    return result


class Uband(object):
    """
    This class wraps the line and PollyCollection(s) associated with a banded
    errorbar plot for use in the uband function.

    """

    def __init__(self, line, bands):
        """
        :param line: Line2D
            A line of the x,y nominal values

        :param bands: list of PolyCollections
            The fill_between and/or fill_betweenx PollyCollections spanning the std_devs of the x,y data

        """
        from matplotlib.cbook import flatten

        self.line = line  # matplotlib.lines.Line2D
        self.bands = list(flatten([bands]))  # matplotlib.collections.PolyCollection(s)

    def __getattr__(self, attr):
        if attr in ['set_color', 'set_lw', 'set_linewidth', 'set_dashes', 'set_linestyle']:

            def _band_line_method(method, *args, **kw):
                """
                Call the same method for line and band.
                Returns Line2D method call result.
                """
                for band in self.bands:
                    getattr(band, method)(*args, **kw)
                return getattr(self.line, method)(*args, **kw)

            return lambda *args, **kw: _band_line_method(attr, *args, **kw)
        else:
            return getattr(self.line, attr)


@_available_to_user_plot
def uband(x, y, ax=None, fill_kwargs=None, **kwargs):
    r"""
    Given arguments x,y where either or both have uncertainties, plot x,y using pyplot.plot
    of the nominal values and surround it with with a shaded error band using matplotlib's
    fill_between and/or fill_betweenx.

    If y or x is more than 1D, it is flattened along every dimension but the last.

    :param x: array of independent axis values

    :param y: array of values with uncertainties, for which shaded error band is plotted

    :param ax: The axes instance into which to plot (default: pyplot.gca())

    :param fill_kwargs: dict. Passed to pyplot.fill_between

    :param \**kwargs: Passed to pyplot.plot

    :return: list. A list of Uband objects containing the line and bands of each (x,y) along
             the last dimension.

    """

    result = []
    if ax is None:
        ax = pyplot.gca()
    if fill_kwargs is None:
        fill_kwargs = {}
    fill_kwargs.setdefault('alpha', 0.25)

    # enable combinations of 1D and 2D x's and y's
    y = np.array(y)
    y = y.reshape(-1, y.shape[-1])
    x = np.array(x)
    x = x.reshape(-1, x.shape[-1])
    if x.shape[0] == 1 and y.shape[0] > 1:  # one x for all y's
        x = np.tile(x[0, :], y.shape[0]).reshape(-1, x.shape[-1])

    # plot each (x,y) and collect the lines/bands into a single object
    for xi, yi in zip(x, y):
        xnom = np.atleast_1d(np.squeeze(uncertainties.unumpy.nominal_values(xi)))
        xerr = np.atleast_1d(np.squeeze(uncertainties.unumpy.std_devs(xi)))
        ynom = np.atleast_1d(np.squeeze(uncertainties.unumpy.nominal_values(yi)))
        yerr = np.atleast_1d(np.squeeze(uncertainties.unumpy.std_devs(yi)))

        (l,) = ax.plot(xnom, ynom, **kwargs)

        fkwargs = copy.copy(fill_kwargs)  # changes to fill_kwargs propagate to the next call of uband!
        fkwargs.setdefault('color', l.get_color())
        bands = []
        if np.any(yerr != 0):
            bandy = ax.fill_between(xnom, ynom - yerr, ynom + yerr, **fkwargs)
            bands.append(bandy)
        if np.any(xerr != 0):
            bandx = ax.fill_betweenx(ynom, xnom - xerr, xnom + xerr, **fkwargs)
            bands.append(bandx)

        tmp = Uband(l, bands)
        result.append(tmp)

    return result


@_available_to_user_plot
def hardcopy(fn, bbox_inches='tight', fig=None, **keyw):
    # todo: docstring
    if fig is None:
        fig = pyplot.gcf()
    tmp = {}
    tmp['ps.usedistiller'] = matplotlib.rcParams['ps.usedistiller']
    tmp['text.usetex'] = matplotlib.rcParams['text.usetex']
    matplotlib.rcParams['ps.usedistiller'] = 'ghostscript'
    matplotlib.rcParams['text.usetex'] = True
    os.system('rm %s/.config/matplotlib/tex.cache/*' % os.environ['HOME'])
    try:
        fig.savefig(fn, bbox_inches=bbox_inches, **keyw)
        printi('Saved to %s' % (fn))
    except Exception:
        printe('Error in saving file')
    matplotlib.rcParams['ps.usedistiller'] = tmp['ps.usedistiller']
    matplotlib.rcParams['text.usetex'] = tmp['text.usetex']
    return fn


@_available_to_user_plot
def set_fontsize(fig=None, fontsize='+0'):
    """
    For each text object of a figure fig, set the font size to fontsize

    :param fig: matplotlib.figure object

    :param fontsize: can be an absolute number (e.g 10) or a relative number (-2 or +2)

    :return: None
    """

    def match(artist):
        return artist.__module__ == "matplotlib.text"

    if is_int(fig) or isinstance(fig, str):
        fontsize = fig
        fig = pyplot.gcf()

    if fig is None:
        fig = pyplot.gcf()

    fontS = fontsize
    for textobj in fig.findobj(match=match):
        if '+' in fontsize or '-' in fontsize:
            fontS = textobj.get_fontsize() + eval(fontsize)
        textobj.set_fontsize(fontS)


def user_lines_cmap_cycle():
    """
    return colormap chosen by the user for representation of lines
    """
    mapper = {'blind': 'viridis'}
    try:
        tmp = OMFIT['MainSettings']['SETUP']['PlotAppearance']['lines.cmap'][0]
        return mapper.get(tmp, tmp)
    except KeyError:
        pass
    except Exception as _excp:
        printe(_excp)
    return default_matplotlib_cmap_cycle


def user_image_cmap_cycle():
    """
    return colormap chosen by the user for representation of images
    """
    try:
        return OMFIT['MainSettings']['SETUP']['PlotAppearance']['image.cmap']
    except KeyError:
        pass
    except Exception as _excp:
        printe(_excp)
    return default_matplotlib_cmap_cycle


@_available_to_user_plot
def color_cycle(n=10, k=None, cmap_name=None):
    """
    Utility function to conveniently return the color of an index in a colormap cycle

    :param n: number of uniformly spaced colors, or array defining the colors' spacings

    :param k: index of the color (if None an array of colors of length n will be returned)

    :param cmap_name: name of the colormap

    :return: color of index k from colormap cmap_name made of n colors, or array of colors of length n if k is None
             Note: if n is an array, then the associated ScalarMappable object is also returned (e.g. for use in a colorbar)

    """
    if cmap_name is None:
        cmap_name = user_lines_cmap_cycle()

    if np.iterable(n):
        nm = matplotlib.colors.Normalize(np.nanmin(n), np.nanmax(n))
        sm = matplotlib.cm.ScalarMappable(cmap=cmap_name, norm=nm)
        sm.set_array(n)
        colors = sm.cmap(sm.norm(n))
        if k is not None:
            return colors[k], sm
        else:
            return colors, sm

    else:
        cmap = getattr(cm, cmap_name)
        if k is not None:
            return cmap(k / max([1.0, float(n - 1)]))
        else:
            tmp = []
            for k in range(n):
                tmp.append(cmap(k / max([1.0, float(n - 1)])))
            return tmp


@_available_to_user_plot
def cycle_cmap(length=50, cmap=None, start=None, stop=None, ax=None):
    """
    Set default color cycle of matplotlib based on colormap

    Note that the default color cycle is not changed if ax parameter is set; only the axes's color cycle will be changed

    :param length: The number of colors in the cycle

    :param cmap: Name of a matplotlib colormap

    :param start: Limit colormap to this range (0 < start < stop 1)

    :param stop: Limit colormap to this range (0 < start < stop 1)

    :param ax: If ax is not None, then change the axes's color cycle instead of the default color cycle

    :return: color_cycle
    """

    if cmap is None:
        cmap = user_lines_cmap_cycle()

    cmap = getattr(pyplot.cm, cmap)

    crange = [0, 1]
    if start is not None:
        crange[0] = start
    if stop is not None:
        crange[1] = stop

    assert 0 <= crange[0] <= 1
    assert 0 <= crange[1] <= 1

    color_cycle = [RGB_to_HEX(*rgb[:3]) for rgb in cmap(np.linspace(crange[0], crange[1], num=length))]

    if ax is None:
        from cycler import cycler

        pyplot.rc('axes', prop_cycle=cycler('color', color_cycle))
    else:
        ax.set_prop_cycle(color_cycle)

    return color_cycle


@_available_to_user_plot
def contrasting_color(line_or_color):
    """
    Given a matplotlib color specification or a line2D instance or a list with a line2D instance as the first element,
    pick and return a color that will contrast well. More complicated than just inversion as inverting blue gives
    yellow, which doesn't display well on a white background.

    :param line_or_color: matplotlib color spec, line2D instance, or list w/ line2D instance as the first element

    :return: 4 element array
        RGBA color specification for a contrasting color
    """
    # Get the RGBA values for the color to transform
    if isinstance(line_or_color, matplotlib.lines.Line2D):
        color = line_or_color.get_color()
    elif np.iterable(line_or_color) and isinstance(line_or_color[0], matplotlib.lines.Line2D):
        color = line_or_color[0].get_color()
    else:
        color = line_or_color
    color = np.array(matplotlib.colors.to_rgba(color))
    # Split RGB from A and transform to HSV
    alpha = color[3]
    color0 = color[0:3]
    color = matplotlib.colors.rgb_to_hsv(color0)
    # Make sure black and white change and that colors are fairly bright
    value_lims = [0.5, 0.9]
    sat_lims = [0.75, 0.95]
    color[1] = min([max([color[1], value_lims[0]]), value_lims[1]])
    color[2] = min([max([color[2], sat_lims[0]]), sat_lims[1]])
    # Rotate the hue. 1/3 seems to look better than 1/2.
    color[0] = (color[0] + 0.333) % 1
    # Transform back to RGB, put the A back in, and return
    return np.append(matplotlib.colors.hsv_to_rgb(color), alpha)


@_available_to_user_plot
def associated_color(line_or_color):
    """
    Given a matplotlib color specification or a line2D instance or a list with a line2D instance as the first element,
    pick and return a color that will look thematically linked to the first color, but still distinguishable.

    :param line_or_color: matplotlib color spec, line2D instance, or list w/ line2D instance as the first element

    :return: 4 element array
        RGBA color specification for a related, similar (but distinguishable) color
    """
    # Get the RGBA values for the color to transform
    if isinstance(line_or_color, matplotlib.lines.Line2D):
        color = line_or_color.get_color()
    elif np.iterable(line_or_color) and isinstance(line_or_color[0], matplotlib.lines.Line2D):
        color = line_or_color[0].get_color()
    else:
        color = line_or_color
    color = np.array(matplotlib.colors.to_rgba(color))
    # Split RGB from A and transform to HSV
    alpha = color[3]
    color0 = color[0:3]
    color = matplotlib.colors.rgb_to_hsv(color0)
    # Change saturation
    if color[1] <= 0.4:
        color[1] *= 2
    else:
        color[1] *= 0.75
    # Change brightness
    if color[2] <= 0.25:
        color[2] = 0.5 + color[2]
    elif color[2] <= 0.4:
        color[2] *= 1.8
    else:
        color[2] *= 0.45
    # Shift the hue slightly.
    color[0] = (color[0] - 0.1) % 1
    # Transform back to RGB, put the A back in, and return
    return np.append(matplotlib.colors.hsv_to_rgb(color), alpha)


@_available_to_user_plot
def blur_image(im, n, ny=None):
    """blurs the image by convolving with a gaussian kernel of typical
    size n. The optional keyword argument ny allows for a different
    size in the y direction.
    """

    def gauss_kern(size, sizey=None):
        """Returns a normalized 2D gauss kernel array for convolutions"""
        size = int(size)
        if not sizey:
            sizey = size
        else:
            sizey = int(sizey)
        x, y = np.mgrid[-size : size + 1, -sizey : sizey + 1]
        g = np.exp(-(x ** 2 / float(size) + y ** 2 / float(sizey)))
        return g / g.sum()

    from scipy import signal

    g = gauss_kern(n, sizey=ny)
    improc = signal.convolve(im, g, mode='same')
    return improc


@_available_to_user_plot
def pcolor2(*args, fast=False, **kwargs):
    r"""
    Plots 2D data as a patch collection.
    Differently from matplotlib.pyplot.pcolor the mesh is extended by one element so that the number of tiles equals
    the number of data points in the Z matrix.
    The X,Y grid does not have to be rectangular.

    :param \*args: Z or X,Y,Z data to be plotted

    :param fast: bool
        Use pcolorfast instead of pcolor. Speed improvements may be dramatic.
        However, pcolorfast is marked as experimental and may produce unexpected behavior.

    :param \**kwargs: these arguments are passed to matplotlib.pyplot.pclor

    :return: None
    """
    ax = kwargs.pop('ax', None)
    if ax is None:
        ax = pylab.gca()

    cmap = kwargs.pop('cmap', None)
    if cmap is None:
        cmap = cm.get_cmap()
    cmap.set_bad(color='w', alpha=1.0)
    kwargs['cmap'] = cmap

    naughty_list = ['interpolation']
    kw2 = {k: v for k, v in kwargs.items() if k not in naughty_list}
    if len(args) == 1:
        if fast:
            obj = ax.pcolorfast(np.ma.masked_invalid(args[0]), **kw2)
        else:
            obj = ax.pcolor(np.ma.masked_invalid(args[0]), **kw2)
    else:
        if len(args[0].shape) == 1:
            xy1d = True
            xdata, ydata = np.meshgrid(args[0], args[1])
        else:
            xy1d = False
            xdata = args[0]
            ydata = args[1]
        masked = np.ma.masked_invalid(args[2])
        if fast:
            if xy1d:
                # pcolorfast doesn't print the z coordinate if x,y are 2D, so try to reduce to 1d if possible
                xdata = xdata[0, :]
                ydata = ydata[:, 0]
                inner_edges = (xdata[:-1] + xdata[1:]) / 2.0
                xdata = np.append(np.append(inner_edges[0] - xdata[1] + xdata[0], inner_edges), inner_edges[-1] + xdata[-1] - xdata[-2])
                inner_edges = (ydata[:-1] + ydata[1:]) / 2.0
                ydata = np.append(np.append(inner_edges[0] - ydata[1] + ydata[0], inner_edges), inner_edges[-1] + ydata[-1] - ydata[-2])
                # pcolorfast says it's even faster if given a tuple of (min, max) for x and y, for even spacing
                if (np.max(abs(np.diff(np.diff(xdata)))) == 0) and (np.max(abs(np.diff(np.diff(ydata)))) == 0):
                    xdata = (np.min(xdata), np.max(xdata))
                    ydata = (np.min(ydata), np.max(ydata))
                obj = ax.pcolorfast(xdata, ydata, masked, **kw2)
            else:
                xdata, ydata = meshgrid_expand(xdata, ydata)
                obj = ax.pcolorfast(xdata, ydata, masked, **kw2)
        else:
            xdata, ydata = meshgrid_expand(xdata, ydata)
            obj = ax.pcolor(xdata, ydata, masked, **kw2)

    return obj


@_available_to_user_plot
def image(*args, **kwargs):
    r"""
    Plots 2D data as an image.

    Much faster than pcolor/pcolor2(fast=False), but the data have to be on a rectangular X,Y grid

    :param \*args: Z or X,Y,Z data to be plotted

    :param \**kwargs: these arguments are passed to pcolorfast
    """

    from omfit_classes.omfit_dmp import mpl_dump, mpl_dump_enable

    mpl_dump_enable[0] = False

    try:

        # todo: add clipping

        ax = kwargs.pop('ax', None)
        if ax is None:
            ax = pylab.gca()

        cmap = kwargs.pop('cmap', None)
        if cmap is None:
            cmap = cm.get_cmap()
        cmap.set_bad(color='w', alpha=1.0)
        kwargs['cmap'] = cmap

        zlim = kwargs.pop('zlim', None)

        if len(args) == 1:
            zdata = args[0]
            xdata = np.linspace(0, zdata.shape[1] - 1, zdata.shape[1])
            ydata = np.linspace(0, zdata.shape[0] - 1, zdata.shape[0])

        elif len(args) >= 3:
            xdata = args[0]
            ydata = args[1]
            zdata = args[2]
            if xdata is None:
                xdata = np.linspace(0, zdata.shape[1] - 1, zdata.shape[1])
            if ydata is None:
                ydata = np.linspace(0, zdata.shape[0] - 1, zdata.shape[0])

        zdata = np.ma.masked_invalid(zdata)

        # accounts for data where x,ymax is at min
        if xdata[0] > xdata[-1]:
            xdata = xdata[::-1]
            zdata = zdata[:, ::-1]
        if ydata[0] > ydata[-1]:
            ydata = ydata[::-1]
            zdata = zdata[::-1, :]

        extent = [np.nanmin(xdata), np.nanmax(xdata), np.nanmin(ydata), np.nanmax(ydata)]
        ax.plot([extent[0], extent[1]], [extent[2], extent[3]])
        del ax.lines[-1]

        kwargs.setdefault('fast', True)
        obj = pcolor2(xdata, ydata, zdata, ax=ax, **kwargs)
        if zlim is not None:
            norm = matplotlib.colors.Normalize(vmin=zlim[0], vmax=zlim[1])
            obj.set_norm(norm)
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])
    finally:
        mpl_dump_enable[0] = True

    dumpDict = {'args': [ax], 'func': 'image'}
    args = list(args)
    # for DMP purposes reduce color scale to 16bits
    if len(args) == 1 and args[0].dtype.name.startswith('float'):
        args[0] = args[0].astype(np.float16)
    if len(args) == 3 and args[2].dtype.name.startswith('float'):
        args[2] = args[2].astype(np.float16)
    dumpDict['args'].extend(args)
    kwargs.pop('ax', None)
    dumpDict['kwargs'] = kwargs
    mpl_dump(dumpDict)

    return obj


@_available_to_user_plot
def meshgrid_expand(xdata, ydata):
    """
    returns the veritices of the mesh, if the xdata and ydata were the centers of the mesh
    xdata and ydata are 2D matrices, which could for example be generated by np.meshgrid

    :param xdata: center of the mesh

    :param ydata: center of the mesh

    :return:
    """
    dxdx, dxdy = np.gradient(xdata)
    dydx, dydy = np.gradient(ydata)

    xdata2 = np.vstack((xdata, xdata[-1, :] + dxdx[-1, :]))
    dxdy2 = np.vstack((dxdy, dxdy[-1, :]))
    xdata3 = np.hstack((xdata2, xdata2[:, -1:] + dxdy2[:, -1:]))

    ydata2 = np.hstack((ydata, ydata[:, -1:] + dydy[:, -1:]))
    dydx2 = np.hstack((dydx, dydx[:, -1:]))
    ydata3 = np.vstack((ydata2, ydata2[-1, :] + dydx2[-1, :]))

    dxdx3, dxdy3 = np.gradient(xdata3)
    dydx3, dydy3 = np.gradient(ydata3)
    dx3 = dxdx3 + dxdy3
    dy3 = dydx3 + dydy3

    xdata4 = xdata3 - dx3 / 2.0
    ydata4 = ydata3 - dy3 / 2.0
    return xdata4, ydata4


@_available_to_user_plot
def map_HBS_to_RGB(H, B, S=1.0, cmap=None):
    """
    map to a RGB colormap separate HUE, BRIGHTNESS and SATURATIONS arrays

    :param H: HUE data (any shape array)

    :param B: BRIGHTNESS data (any shape array)

    :param S: SATURATION data (any shape array)

    :param cmap: matplotlib.colormap to be used

    :return: RGB array (shape of input array with one more dimension of size 3 (RGB) )
    """
    if cmap is None:
        cmap = user_image_cmap_cycle()
    if isinstance(cmap, str):
        cmap = cm.get_cmap(cmap, 256)
    x = np.linspace(0, 1, cmap.N)
    shapes = list(H.shape)

    w = np.zeros((H.size, 3))
    for n in range(H.size):
        v = H.flatten()[n]
        t = cmap(np.nanargmin(abs(x - v)))
        v = colorsys.rgb_to_hls(t[0], t[1], t[2])
        if is_float(S * 1.0):
            w[n] = colorsys.hls_to_rgb(v[0], B.flatten()[n], S)
        else:
            w[n] = colorsys.hls_to_rgb(v[0], B.flatten()[n], S.flatten()[n])

    shapes.append(3)
    return w.reshape(shapes)


@_available_to_user_plot
def RGB_to_HEX(R, G, B):
    """
    Convert color from numerical RGB to hexadecimal representation

    :param R: integer 0<x<255 or float 0.0<x<1.0

    :param G: integer 0<x<255 or float 0.0<x<1.0

    :param B: integer 0<x<255 or float 0.0<x<1.0

    :return: hexadecimal representation of the color
    """
    if not isinstance(R, int):
        R = int(round(255 * R))
    if not isinstance(G, int):
        G = int(round(255 * G))
    if not isinstance(B, int):
        B = int(round(255 * B))
    return '#%02x%02x%02x' % (R, G, B)


@_available_to_user_plot
def plotc(*args, **kwargs):
    r"""
    Plot the various curves defined by the arguments [X],Y,[Z]
    where X is the x value, Y is the y value, and Z is the color.
    If one argument is given it is interpreted as Y; if two, then X, Y; if three
    then X, Y, Z.  If all three are given, then it is passed to plotc and the
    labels are discarded.
    If Z is omitted, a rainbow of colors is used, with blue for the first curve
    and red for the last curve.  A different color map can be given with the
    cmap keyword (see http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps
    for other options). If X is omitted, then the (ith) index of Y is used as the x value.

    :param \*args:

    :param \**kwargs:

    :return:
    """

    ax = kwargs.pop('ax', None)
    if ax is None:
        ax = pylab.gca()

    args = list(args)
    X = args.pop(0)
    Y = None
    Z = None

    if len(args) >= 1 and not isinstance(args[0], str):
        Y = args.pop(0)
        if len(args) >= 1 and not isinstance(args[0], str):
            Z = args.pop(0)

    # from list to matrix, this is done to work nicely with across function of SortedDict
    def list2mat(inv):
        outv = inv
        if isinstance(inv, list):
            outv = np.array(inv).T
        return outv

    X = list2mat(X)
    Y = list2mat(Y)
    Z = list2mat(Z)

    if Y is None and Z is None:
        Y = X
        X = np.linspace(0, Y.shape[0] - 1, Y.shape[0])

    if len(X.shape) == len(Y.shape) == 1 and Z is None:
        return ax.plot(X, Y, *args, **kwargs)

    Y = np.reshape(Y, (Y.shape[0], -1))
    if len(X.shape) == 1:
        X = np.tile(X.flatten(), (Y.shape[1], 1)).T

    try:
        tmp_prop_cycle = matplotlib.rcParams['axes.prop_cycle']
        nlines = Y.shape[1]
        pyplot.ioff()
        LC = []

        if Z is not None:
            vmax = kwargs.pop('vmax', None)
            vmin = kwargs.pop('vmin', None)
            kwargs.setdefault('norm', [vmin, vmax])

            if len(Z.shape) == 1:
                Z = np.tile(Z.flatten(), (Y.shape[1], 1)).T

            # lets plot it normally, since this sets the axes and other stuff that I do not know about
            ax.plot(X.flatten(), Y.flatten(), '.')
            del ax.lines[-1]

            def _plotc(x, y, z, *args, **kwargs):
                points = np.array([x, y]).T.reshape(-1, 1, 2)
                segments = np.concatenate([points[:-1], points[1:]], axis=1)
                if kwargs['norm'][0] is None:
                    kwargs['norm'] = [np.nanmin(Z), kwargs['norm'][1]]
                if kwargs['norm'][1] is None:
                    kwargs['norm'] = [kwargs['norm'][0], np.nanmax(Z)]
                if not isinstance(kwargs['norm'], pyplot.Normalize):
                    kwargs['norm'] = pyplot.Normalize(kwargs['norm'][0], kwargs['norm'][1])
                lc = matplotlib.collections.LineCollection(segments, *args, **kwargs)
                lc.set_array(z)
                ax.add_collection(lc)
                return lc

            for k in range(nlines):
                x = X[:, k]
                y = Y[:, k]
                z = Z[:, k]
                LC.append(_plotc(x, y, z, *args, **kwargs))

        else:
            labels = kwargs.pop('labels', ['_line' + str(k) for k in range(1, nlines + 1)])
            cmap = getattr(cm, kwargs.pop('cmap', default_matplotlib_cmap_cycle))
            for k in range(nlines):
                x = X[:, k]
                y = Y[~np.isnan(x), k]
                x = x[~np.isnan(x)]
                kwargs['label'] = labels[k]
                kwargs['color'] = cmap(k / max([1, float(nlines - 1)]))
                ax.plot(x, y, *args, **kwargs)
                LC.append(ax.lines[-1])

    finally:
        matplotlib.rcParams['axes.prop_cycle'] = tmp_prop_cycle
        pyplot.draw()
        pyplot.ion()

    return LC


@_available_to_user_plot
def title_inside(string, x=0.5, y=0.9, ax=None, **kwargs):
    r"""
    Write the title of a figure inside the figure axis rather than outside

    :param string: title string

    :param x: x location of the title string (default 0.5, that is centered)

    :param y: y location of the title string (default 0.875)

    :param ax: axes to operate on

    :param \**kwargs: additional keywords passed to pyplot.title

    :return: pyplot.title text object
    """
    kwargs.setdefault('va', 'top')
    if ax is None:
        return pyplot.title(string, x=x, y=y, **kwargs)
    else:
        return ax.set_title(string, x=x, y=y, **kwargs)


@_available_to_user_plot
def increase_resolution(*args, **kwargs):
    """
    This function takes 1 (Z) or 3 (X,Y,Z) 2D tables and interpolates them to higher resolution by bivariate spline interpolation.
    If 1 (3) table(s) is(are) provided, then the second(fourth) argument is the resolution increase,
    which can be a positive or negative integer integer: res=res0*2^n
    or a float which sets the grid size in the units provided by the X and Y tables
    """
    oneInput = False
    args = list(args)
    if len(args) in [1, 2]:
        args.insert(1, np.arange(args[0].shape[1]))
        args.insert(2, np.arange(args[0].shape[0]))
        oneInput = True
    Qin = args[0]
    Rin = args[1]
    Zin = args[2]

    if len(Rin.shape) == 2:
        Rin = Rin[0, :]
    if len(Zin.shape) == 2:
        Zin = Zin[:, 0]

    if len(args) == 4:
        kwargs['resolution'] = args[3]
    resolution = kwargs['resolution']
    quiet = kwargs.get('quiet', True)

    if resolution == 0:
        Q = Qin
        R = Rin
        Z = Zin
    elif is_int(resolution):
        if resolution > 0:
            if not quiet:
                printi('Increasing tables resolution by factor of ' + str(abs(resolution) + 1) + ' ...')
            nr = len(Rin)
            nz = len(Zin)
            for k in range(resolution):
                nr = nr + nr - 1
                nz = nz + nz - 1
            R = np.linspace(min(Rin), max(Rin), nr)
            Z = np.linspace(min(Zin), max(Zin), nz)
            Q = RectBivariateSplineNaN(Zin, Rin, Qin)(Z, R)
        elif resolution < 0:
            if not quiet:
                printi('Decreasing tables resolution by factor of ' + str(abs(resolution) + 1) + ' ...')
            R = Rin[::-resolution]
            Z = Zin[::-resolution]
            Q = Qin[::-resolution, ::-resolution]
    elif is_float(resolution):
        if not quiet:
            printi('Interpolating tables to ' + str(resolution) + ' m resolution ...')
        R = np.linspace(min(Rin), max(Rin), int(np.ceil((max(Rin) - min(Rin)) / resolution)))
        Z = np.linspace(min(Zin), max(Zin), int(np.ceil((max(Zin) - min(Zin)) / resolution)))
        Q = RectBivariateSplineNaN(Zin, Rin, Qin)(Z, R)

    if oneInput:
        return Q
    else:
        return Q, R, Z


@_available_to_user_plot
class infoScatter(object):
    r"""
    improved version of: http://wiki.scipy.org/Cookbook/Matplotlib/Interactive_Plotting

    Callback for matplotlib to display an annotation when points are clicked on

    :param x: x of the annotations

    :param y: y of the annotations

    :param annotes: list of string annotations

    :param axis: axis on which to operate on (default to current axis)

    :param tol: vicinity in pixels where to look for annotations

    :param func: function to call with signature: func(x,y,annote,visible,axis)

    :param all_on: Make all of the text visible to begin with

    :param suppress_canvas_draw: Do not actively draw the canvas if all_on is True, makes plotting faster there are many subplots


    :param \**kw: extra keywords passed to matplotlib text class
    """

    def __init__(self, x, y, annotes, axis=None, tol=5, func=None, all_on=False, suppress_canvas_draw=False, **kw):
        self.data = list(zip(x, y, annotes))
        self.tol = tol
        if axis is None:
            self.axis = pylab.gca()
        else:
            self.axis = axis
        self.drawnAnnotations = {}
        self.func = func
        self.kw = kw
        self.kw.setdefault('clip_on', True)
        if all_on:
            for cur_x, cur_y, cur_annote in zip(x, y, annotes):
                self.drawAnnote(self.axis, cur_x, cur_y, cur_annote, redraw_canvas=False)
            if not suppress_canvas_draw:
                self.axis.figure.canvas.draw()
        self.axis.figure.canvas.mpl_connect('button_press_event', self)

    def __call__(self, event):
        if event.inaxes:
            clickX = event.x
            clickY = event.y
            if self.axis is None or self.axis == event.inaxes:
                winner = [None, None]
                for k, (xd, yd, a) in enumerate(self.data):
                    x, y = self.axis.transData.transform((xd, yd))
                    d = np.sqrt((x - clickX) ** 2 + (y - clickY) ** 2)
                    if d < self.tol:
                        if winner[0] is None or d < winner[0]:
                            winner = [d, k]

                if winner[0] is not None:
                    self.drawAnnote(event.inaxes, self.data[winner[1]][0], self.data[winner[1]][1], self.data[winner[1]][2])

    def drawAnnote(self, axis, x, y, annote, redraw_canvas=True):
        """
        Draw the annotation on the plot
        """
        if (x, y) in self.drawnAnnotations:
            markers = self.drawnAnnotations[(x, y)]
            for m in markers:
                m.set_visible(not m.get_visible())
            if redraw_canvas:
                self.axis.figure.canvas.draw()
        else:
            printi(annote)
            t = axis.text(x, y, annote, **self.kw)
            m = axis.scatter([x], [y], marker='+', c='r', zorder=100)
            self.drawnAnnotations[(x, y)] = (t, m)
            if redraw_canvas:
                self.axis.figure.canvas.draw()
        if self.func is not None:
            self.func(x, y, annote, m.get_visible(), axis)

    def drawSpecificAnnote(self, annote):
        annotesToDraw = [(x, y, a) for x, y, a in self.data if a == annote]
        for x, y, a in annotesToDraw:
            self.drawAnnote(self.axis, x, y, a)


@_available_to_user_plot
def infoPoint(fig=None):
    """
    print x,y coordinates where the user clicks

    :param fig: matplotlib figure
    """
    from matplotlib import pyplot

    if fig is None:
        fig = pyplot.gcf()

    def onclick(event):
        print(event.xdata, event.ydata)

    fig.canvas.mpl_connect('button_press_event', onclick)


@_available_to_user_plot
def XKCDify(
    ax,
    mag=1.0,
    f1=50,
    f2=0.01,
    f3=15,
    bgcolor='w',
    xaxis_loc=None,
    yaxis_loc=None,
    xaxis_arrow='+',
    yaxis_arrow='+',
    ax_extend=0.1,
    expand_axes=False,
    ylabel_rot=78,
):

    """
    XKCD plot generator by, Jake Vanderplas; Modified by Sterling Smith

    This is a script that will take any matplotlib line diagram, and convert it
    to an XKCD-style plot.  It will work for plots with line & text elements,
    including axes labels and titles (but not axes tick labels).

    The idea for this comes from work by Damon McDougall
      http://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg25499.html

    This adjusts all lines, text, legends, and axes in the figure to look
    like xkcd plots.  Other plot elements are not modified.

    :param ax: Axes instance
        the axes to be modified.
    :param mag: float
        the magnitude of the distortion
    :param f1, f2, f3: int, float, int
        filtering parameters.  f1 gives the size of the window, f2 gives
        the high-frequency cutoff, f3 gives the size of the filter
    :param xaxis_loc, yaxis_log: float
        The locations to draw the x and y axes.  If not specified, they
        will be drawn from the bottom left of the plot
    :param xaxis_arrow: str
        where to draw arrows on the x axes.  Options are '+', '-', '+-', or ''
    :param yaxis_arrow: str
        where to draw arrows on the y axes.  Options are '+', '-', '+-', or ''
    :param ax_extend: float
        How far (fractionally) to extend the drawn axes beyond the original
        axes limits
    :param expand_axes: bool
        if True, then expand axes to fill the figure (useful if there is only
        a single axes in the figure)
    :param ylabel_rot: float
        number of degrees to rotate the y axis label
    """
    import pylab as pl
    import matplotlib.font_manager as fm

    fontfn = os.sep.join([os.path.dirname(__file__), '..', 'extras', 'graphics', 'fonts', 'Humor-Sans.ttf'])

    def xkcd_line(x, y, xlim=None, ylim=None, mag=1.0, f1=30, f2=0.05, f3=15):
        """
        Mimic a hand-drawn line from (x, y) data

        Parameters
        ----------
        x, y : array_like
            arrays to be modified
        xlim, ylim : data range
            the assumed plot range for the modification.  If not specified,
            they will be guessed from the  data
        mag : float
            magnitude of distortions
        f1, f2, f3 : int, float, int
            filtering parameters.  f1 gives the size of the window, f2 gives
            the high-frequency cutoff, f3 gives the size of the filter

        Returns
        -------
        x, y : np.ndarrays
            The modified lines
        """
        from scipy import interpolate, signal

        x = np.asarray(x)
        y = np.asarray(y)

        # get limits for rescaling
        if xlim is None:
            xlim = (x.min(), x.max())
        if ylim is None:
            ylim = (y.min(), y.max())

        if xlim[1] == xlim[0]:
            xlim = ylim

        if ylim[1] == ylim[0]:
            ylim = xlim

        # scale the data
        x_scaled = (x - xlim[0]) * 1.0 / (xlim[1] - xlim[0])
        y_scaled = (y - ylim[0]) * 1.0 / (ylim[1] - ylim[0])

        # compute the total distance along the path
        dx = x_scaled[1:] - x_scaled[:-1]
        dy = y_scaled[1:] - y_scaled[:-1]
        dist_tot = np.sum(np.sqrt(dx * dx + dy * dy))

        # number of interpolated points is proportional to the distance
        Nu = int(200 * dist_tot)
        u = np.arange(-1, Nu + 1) * 1.0 / (Nu - 1)

        # interpolate curve at sampled points
        k = min(3, len(x) - 1)
        res = interpolate.splprep([x_scaled, y_scaled], s=0, k=k)
        x_int, y_int = interpolate.splev(u, res[0])

        # we'll perturb perpendicular to the drawn line
        dx = x_int[2:] - x_int[:-2]
        dy = y_int[2:] - y_int[:-2]
        dist = np.sqrt(dx * dx + dy * dy)

        # create a filtered perturbation
        coeffs = mag * np.random.normal(0, 0.01, len(x_int) - 2)
        b = signal.firwin(f1, f2 * dist_tot, window=('kaiser', f3))
        response = signal.lfilter(b, 1, coeffs)

        x_int[1:-1] += response * dy / dist
        y_int[1:-1] += response * dx / dist

        # un-scale data
        x_int = x_int[1:-1] * (xlim[1] - xlim[0]) + xlim[0]
        y_int = y_int[1:-1] * (ylim[1] - ylim[0]) + ylim[0]

        return x_int, y_int

    # Get axes aspect
    ext = ax.get_window_extent().extents
    aspect = (ext[3] - ext[1]) / (ext[2] - ext[0])

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    xspan = xlim[1] - xlim[0]
    yspan = ylim[1] - xlim[0]

    xax_lim = (xlim[0] - ax_extend * xspan, xlim[1] + ax_extend * xspan)
    yax_lim = (ylim[0] - ax_extend * yspan, ylim[1] + ax_extend * yspan)

    if xaxis_loc is None:
        xaxis_loc = ylim[0]

    if yaxis_loc is None:
        yaxis_loc = xlim[0]

    # Draw axes
    xaxis = pl.Line2D([xax_lim[0], xax_lim[1]], [xaxis_loc, xaxis_loc], linestyle='-', color='k')
    yaxis = pl.Line2D([yaxis_loc, yaxis_loc], [yax_lim[0], yax_lim[1]], linestyle='-', color='k')

    # ttk.Label axes3, 0.5, 'hello', fontsize=14)
    ax.text(xax_lim[1], xaxis_loc - 0.02 * yspan, ax.get_xlabel(), fontsize=14, ha='right', va='top', rotation=12)
    ax.text(yaxis_loc - 0.02 * xspan, yax_lim[1], ax.get_ylabel(), fontsize=14, ha='right', va='top', rotation=ylabel_rot)
    ax.set_xlabel('')
    ax.set_ylabel('')

    # Add title
    ax.text(0.5 * (xax_lim[1] + xax_lim[0]), yax_lim[1], ax.get_title(), ha='center', va='bottom', fontsize=16)
    ax.set_title('')

    Nlines = len(ax.lines)
    lines = [xaxis, yaxis] + [ax.lines.pop(0) for i in range(Nlines)]

    for line in lines:
        x, y = line.get_data()

        x_int, y_int = xkcd_line(x, y, xlim, ylim, mag, f1, f2, f3)

        # create foreground and background line
        lw = line.get_linewidth()
        line.set_linewidth(2 * lw)
        line.set_data(x_int, y_int)

        # don't add background line for axes
        if (line is not xaxis) and (line is not yaxis):
            line_bg = pl.Line2D(x_int, y_int, color=bgcolor, linewidth=8 * lw)

            ax.add_line(line_bg)
        ax.add_line(line)

    # Draw arrow-heads at the end of axes lines
    arr1 = 0.03 * np.array([-1, 0, -1])
    arr2 = 0.02 * np.array([-1, 0, 1])

    arr1[::2] += np.random.normal(0, 0.005, 2)
    arr2[::2] += np.random.normal(0, 0.005, 2)

    x, y = xaxis.get_data()
    if '+' in str(xaxis_arrow):
        ax.plot(x[-1] + arr1 * xspan * aspect, y[-1] + arr2 * yspan, color='k', lw=2)
    if '-' in str(xaxis_arrow):
        ax.plot(x[0] - arr1 * xspan * aspect, y[0] - arr2 * yspan, color='k', lw=2)

    x, y = yaxis.get_data()
    if '+' in str(yaxis_arrow):
        ax.plot(x[-1] + arr2 * xspan * aspect, y[-1] + arr1 * yspan, color='k', lw=2)
    if '-' in str(yaxis_arrow):
        ax.plot(x[0] - arr2 * xspan * aspect, y[0] - arr1 * yspan, color='k', lw=2)

    # Change all the fonts to humor-sans.
    prop = fm.FontProperties(fname=fontfn, size=16)
    for text in ax.texts:
        text.set_fontproperties(prop)

    # modify legend
    leg = ax.get_legend()
    if leg is not None:
        leg.set_frame_on(False)

        for child in leg.get_children():
            if isinstance(child, pl.Line2D):
                x, y = child.get_data()
                child.set_data(xkcd_line(x, y, mag=10, f1=100, f2=0.001))
                child.set_linewidth(2 * child.get_linewidth())
            if isinstance(child, pl.Text):
                child.set_fontproperties(prop)

    # Set the axis limits
    ax.set_xlim(xax_lim[0] - 0.1 * xspan, xax_lim[1] + 0.1 * xspan)
    ax.set_ylim(yax_lim[0] - 0.1 * yspan, yax_lim[1] + 0.1 * yspan)

    # adjust the axes
    ax.set_xticks([])
    ax.set_yticks([])

    if expand_axes:
        ax.figure.set_facecolor(bgcolor)
        ax.set_axis_off()
        ax.set_position([0, 0, 1, 1])

    return ax


@_available_to_user_plot
def autoscale_y(ax, margin=0.1):
    """
    Rescales the y-axis based on the data that is visible given the current xlim of the axis.
    Created by eldond at 2017 Mar 23  20:26

    This function was taken from an answer by DanKickstein on stackoverflow.com
    http://stackoverflow.com/questions/29461608/matplotlib-fixing-x-axis-scale-and-autoscale-y-axis
    http://stackoverflow.com/users/1078391/danhickstein

    I don't think this function considers shaded bands such as would be used to display error bars. Increasing the
    margin may be a good idea when dealing with such plots.

    :param ax: a matplotlib axes object

    :param margin: The fraction of the total height of the y-data to pad the upper and lower ylims
    """

    printd('autoscale_y()...')

    def get_bottom_top(line2):
        xd = line2.get_xdata()
        yd = line2.get_ydata()
        lo, hi = ax.get_xlim()
        with warnings.catch_warnings(record=False) as w:
            # Ignore RuntimeWarnings for these calculations (could be caused by NaNs in xd or yd)
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            if (len(xd) == 2) and (xd[0] == 0.0) and (xd[1] == 1.0):
                # Special case to handle axhline - added by D. Eldon
                y_displayed = yd
            else:
                y_displayed = np.array(yd)[((xd >= lo) & (xd <= hi))]
        if len(y_displayed) > 1:
            h = np.nanmax(y_displayed) - np.nanmin(y_displayed)
            bot2 = np.nanmin(y_displayed) - margin * h
            top2 = np.nanmax(y_displayed) + margin * h
            return bot2, top2
        else:
            printd('Could not find any elements of y_displayed in range')
            return np.inf, -np.inf

    lines = ax.get_lines()
    bot, top = np.inf, -np.inf

    for j, line in enumerate(lines):
        printd(' line', j)
        new_bot, new_top = get_bottom_top(line)
        printd('   new_bot = {:}, new_top = {:}'.format(new_bot, new_top))
        if new_bot < bot:
            bot = new_bot
        if new_top > top:
            top = new_top

    if (bot < top) and (bot > (-np.inf)) and (top < np.inf):
        printd('Set ylim to ', bot, top)
        ax.set_ylim(bot, top)
    else:
        printd('Did not set ylim because one of these was False:')
        printd('   bot > (-np.inf) = {:}, bot = {:}'.format(bot > (-np.inf), bot))
        printd('   top < np.inf = {:}, top = {:}'.format(top < np.inf, top))
        printd('   bot < top = {:}'.format(bot < top))

    printd('Done with autoscale_y().')
    return


@_available_to_user_plot
def set_linearray(lines, values=None, cmap=default_matplotlib_cmap_cycle, vmin=None, vmax=None):
    """
    Set colors of lines to colormapping of values.

    Other good sequential colormaps are YlOrBr and autumn.
    A good diverging colormap is bwr.

    :param lines:  Lines to set colors.
    :type lines: list
    :param values: Values corresponding to each line. Default is indexing.
    :type values: array like
    :param cmap: Valid matplotlib colormap name.
    :type cmap: str
    :param vmax: Upper bound of colormapping.
    :type vmax: float
    :param vmin: Lower bound of colormapping.
    :type vmin: float

    :return: ScalarMappable. A mapping object used for colorbars.

    """
    from matplotlib.cbook import flatten

    if values is None:
        values = list(range(len(lines)))
    nm = matplotlib.colors.Normalize(vmin, vmax)
    sm = matplotlib.cm.ScalarMappable(cmap=cmap, norm=nm)
    sm.set_array(values)
    colors = sm.cmap(sm.norm(values))
    for l, c in zip(lines, colors):
        if isinstance(l, matplotlib.container.ErrorbarContainer):
            for li in flatten(l.lines):
                li.set_color(c)
        else:
            l.set_color(c)

    return sm


@_available_to_user_plot
def pi_multiple(x, pos=None):
    """
    Provides a string representation of x that is a multiple of the
    fraction pi/'denominator'.

    See multiple_formatter documentation for more info.
    """

    func = multiple_formatter()
    return func(x, pos)


@_available_to_user_plot
def multiple_formatter(denominator=24, number=np.pi, latex=r'\pi'):
    """
    Returns a tick formatting function that creates tick labels in
    multiples of 'number'/'denominator'.

    Code from https://stackoverflow.com/a/53586826/6605826

    :param denominator: The denominator of the fraction that tick labels
      are created in multiples of.
    :param number: The numerator of the fraction that tick labels are
      created in multiples of
    :param latex: The latex string used to represent 'number'
    """

    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    def _multiple_formatter(x, pos):
        den = denominator
        num = np.int(np.rint(den * x / number))
        com = gcd(num, den)
        (num, den) = (int(num / com), int(den / com))
        if den == 1:
            if num == 0:
                return r'$0$'
            if num == 1:
                return r'$%s$' % latex
            elif num == -1:
                return r'$-%s$' % latex
            else:
                return r'$%s%s$' % (num, latex)
        else:
            if num == 1:
                return r'$\frac{%s}{%s}$' % (latex, den)
            elif num == -1:
                return r'$\frac{-%s}{%s}$' % (latex, den)
            else:
                return r'$\frac{%s%s}{%s}$' % (num, latex, den)

    return _multiple_formatter


@_available_to_user_plot
def convert_ticks_to_pi_multiple(axis=None, major=2, minor=4):
    """
    Given an axis object, force its ticks to be at multiples of pi, with the
    labels formatted nicely [...,-2pi,-pi,0,pi,2pi,...]

    :param axis: An axis object, such as pyplot.gca().xaxis

    :param major: int
        Denominator of pi for major tick marks. 2: major ticks at 0, pi/2., pi, ...
        Can't be greater than 24.

    :param minor: int
        Denominator of pi for minor tick marks. 4: minor ticks at 0, pi/4., pi/2., ...

    :return: None
    """
    axis = pyplot.gca().xaxis if axis is None else axis
    major = min([major, 24])
    axis.set_major_locator(MultipleLocator(np.pi / major))
    axis.set_minor_locator(MultipleLocator(np.pi / minor))
    axis.set_major_formatter(FuncFormatter(pi_multiple))


@_available_to_user_plot
def is_colorbar(ax):
    """
    Guesses whether a set of Axes is home to a colorbar

    https://stackoverflow.com/a/53568035/6605826

    :param ax: Axes instance

    :return: bool
        True if the x xor y axis satisfies all of the following and thus looks like it's probably a colorbar:
        No ticks, no tick labels, no axis label, and range is (0, 1)
    """
    xcb = (len(ax.get_xticks()) == 0) and (len(ax.get_xticklabels()) == 0) and (len(ax.get_xlabel()) == 0) and (ax.get_xlim() == (0, 1))
    ycb = (len(ax.get_yticks()) == 0) and (len(ax.get_yticklabels()) == 0) and (len(ax.get_ylabel()) == 0) and (ax.get_ylim() == (0, 1))
    return xcb != ycb  # != is effectively xor in this case, since xcb and ycb are both bool
    # xor trick from https://stackoverflow.com/a/433161/6605826


@_available_to_user_plot
def tag_plots_abc(
    fig=None, axes=None, corner=[1, 1], font_size=matplotlib.rcParams['xtick.labelsize'], skip_suspected_colorbars=True, start_at=0
):
    """
    Tag plots with (a), (b), (c), ...

    :param fig: Specify a figure instance instead of letting the function pick the most recent one

    :param axes: Specify a plot axes instance or list/array of plot axes instances instead of letting the function use
        fig.get_axes()

    :param corner: Which corner does the tag go in? [0, 0] for bottom left, [1, 0] for bottom right, etc.

    :param font_size: Font size of the annotation.

    :param skip_suspected_colorbars: bool
        Try to detect axes which are home to colorbars and skip tagging them. An Axes instance is suspected of having a
        colorbar if either the xaxis or yaxis satisfies all of these conditions:
        - Length of tick list is 0
        - Length of tick label list is 0
        - Length of axis label is 0
        - Axis range is (0,1)

    :param start_at: int
        Offset value for skipping some numbers. Useful if you aren't doing real subfigs, but two separate plots and
        placing them next to each other in a publication. Set to 1 to start at (b) instead of (a), for example.
    """
    from matplotlib.cbook import flatten

    if fig is None:
        fig = pyplot.gcf()
    if axes is None:
        axes = fig.get_axes()

    letters = string.ascii_lowercase + string.ascii_uppercase
    tag_x = abs(corner[0] - 0.005)
    tag_y = abs(corner[1] - 0.025)
    tag_ha = ['left', 'right'][corner[0]]
    tag_va = ['bottom', 'top'][corner[1]]
    printd('Plot tag information: ', tag_x, tag_y, tag_ha, tag_va)

    valid_axes = [ax for ax in flatten(np.atleast_1d(axes)) if not (skip_suspected_colorbars and is_colorbar(ax))]

    j = 0 + start_at
    for i, ax in enumerate(valid_axes):
        if ax.axison:
            # Thanks to Suever for pointing out ax.axison: http://stackoverflow.com/a/42660787/6605826
            ax.annotate(
                ' ({:}) '.format(letters[j]), xy=(tag_x, tag_y), xycoords='axes fraction', ha=tag_ha, va=tag_va, fontsize=font_size
            ).draggable(True)
            j += 1
    return


@_available_to_user_plot
def mark_as_interactive(ax, interactive=True):
    """
    Mark an axis as interactive or not

    :param ax: axis

    :param interactive: boolean

    :return: axis
    """
    ax.is_interactive = interactive
    return ax


@_available_to_user_plot
class View1d(object):
    """
    Plot 2D or 3D data as line-plots with interactive navigation through the
    alternate dimensions. Navigation uses the 4 arrow keys to traverse up to 2 alternate
    dimensions.

    The data must be on a regular grid, and is formed into a xarray DataArray if not already.

    Uses matplotlib line plot for float/int data, OMFIT uerrrorbar for uncertainty variables.

    Examples:

    The view1d can be used to interactively explore data. For usual arrays it draws line slices.

    >> t = np.arange(20)
    >> s = np.linspace(0,2*np.pi,60)
    >> y = np.sin(np.atleast_2d(s).T+np.atleast_2d(t))
    >> da = xarray.DataArray(y,coords=SortedDict([('space',s),('time',t)]),name='sine')
    >> v = View1d(da.transpose('time','space'),dim='space',time=10)

    For uncertainties arrays, it draws errorbars using the uerrorbar function. Multiple views
    with the same dimensions can be linked for increased speed (eliminate redundant calls to redraw).

    >> y_u = unumpy.uarray(y+(random(y.shape)-0.5),random(y.shape))
    >> da_u = xarray.DataArray(y_u,coords=SortedDict([('space',s),('time',t)]),name='measured')
    >> v_u = View1d(da_u,dim='space',time=10,axes=pyplot.gca())
    >> v.link(v_u) # v will remain connected to keypress events and drive vu

    Variable dependent axis data can be viewed if x and y share a regular grid in some coordinates,

    >> x = np.array([s+(random(s.shape)-0.5)*0.2 for i in t]).T
    >> da_x = xarray.DataArray(x,coords=SortedDict([('space',s),('time',t)]),name='varspace')
    >> ds = da_u.to_dataset().merge(da_x.to_dataset())
    >> v_x = View1d(ds,name='measured',dim='varspace',time=10,axes=pyplot.gca())
    >> v.link(v_x)

    """

    def __init__(
        self,
        data,
        coords=None,
        dims=None,
        name=None,
        dim=None,
        axes=None,
        dynamic_ylim=False,
        use_uband=False,
        cornernote_options=None,
        plot_options=None,
        **indexers,
    ):
        r"""

        :param data: DataArray or array-like
            2D or 3D data values to be viewed.
        :param coords: dict-like
            Dictionary of Coordinate objects that label values along each dimension.
        :param dims: tuple
            Dimension names associated with this array.
        :param name: string
            Label used in legend. Empty or beginning with '_' produces no legend label.
            If the data is a DataArray it will be renamed before plotting.
            If the data is a Dataset, the name specifies which of its existing data_vars to plot.
        :param dim: string, DataArray
            Dimension plotted on x-axis. If DataArray, must have same dims as data.
        :param axes: Axes instance
            The axes plotting is done in.
        :param dynamic_ylim: bool
            Re-scale y limits of axes when new slices are plotted.
        :param use_uband: bool
            Use uband instead of uerrorbar to plot uncertainties variables.
        :param cornernote_options: dict
            Key word arguments passed to cornernote (such as root, shot, device). If this is present, then cornernote
            will be updated with the new time if there is only one time to show, or the time will be erased from the
            cornernote if more than one time is shown by this View1d instance (such as by freezing one slice).
        :param plot_options: dict
            Key word arguments passed to plot/uerrorbar/uband.

        :param \**indexers: dict
            Dictionary with keys given by dimension names and values given by
            arrays of coordinate index values. Must include all dimensions other,
            than the fundamental.

        """
        # check args and make Dataset if needed
        if isinstance(data, DataArray):
            if coords or dims:
                raise ValueError("View cannot re-assign coords/dims to data that is already a DataArray")
            if name:
                data.name = name
            elif not data.name:  # require name
                name = 'viewdata'
                data.name = name
            else:
                name = data.name
            data = data.to_dataset()
        elif isinstance(data, Dataset):
            if coords or dims:
                raise ValueError("View cannot re-assign coords/dims to data that is already a Dataset")
        else:
            if name is None:
                name = 'viewdata'
            data = DataArray(data, coords=coords, dims=dims, name=name).to_dataset()
        # check key words
        self.dynamic_ylim = dynamic_ylim
        self.cornernote_options = cornernote_options
        if plot_options:
            self.plot_options = plot_options
        else:
            self.plot_options = {}

        # Make figure & axes if needed
        if not axes:
            axes = pyplot.gca()
        self.figure, self.axes = axes.get_figure(), axes

        # make view aware of full data, the slice data, and slice indexes
        self.links = []
        self.is_uncertain = is_uncertain(data[name].values)
        self.data = data
        self.name = name
        if dim:
            if isinstance(dim, DataArray):
                if not dim.name:
                    dim.name = 'dim'
                data = data.merge(dim.to_dataset())
                dim = dim.name
            self.dim = dim
            # reduce any large datasets just to the things we need
            self.data = Dataset(dict(((self.name, self.data[self.name]), (dim, self.data[dim]))))
            # put dimension at front of indexing
            if dim in self.data.dims:
                dim0 = dim
            elif dim in self.data.data_vars:
                dim0 = set(self.data.dims).difference(list(indexers.keys())).pop()  # indexers must reduce to 1D
            else:
                raise ValueError("Argument `dim` must be in DataArray dims or in Dataset")
            dims = list(self.data.dims.keys())
            dims.insert(0, dims.pop(dims.index(dim0)))
            self.data = self.data.transpose(*dims)
        else:
            self.dim = list(self.data.dims.keys())[0]
        self.values = self.data.isel(**indexers)
        self.indexes = SortedDict(indexers)
        for key, val in list(self.indexes.items()):
            self.indexes[key] = np.atleast_1d(val)

        # use metadata for labeling
        self.axes.set_xlabel(dim)
        self.label_prefix = self.plot_options.pop('label', '')
        self._label_indexers_visible = True
        lbl = self._get_label()

        # actual plotting
        self.use_uband(use_uband)
        self._inactive = []
        if self.is_uncertain:
            self._active = self._uplot(self.values[self.dim], self.values[self.name], ax=self.axes, label=lbl, **self.plot_options)
        else:
            self._active = self.axes.plot(self.values[self.dim], self.values[self.name], label=lbl, **self.plot_options)

        # Update annotations
        if self.cornernote_options is not None:
            self._update_cornernote()
        legend = self.axes.legend(loc=0)
        legend.draggable(True)

        self.figure.canvas.draw_idle()

        # store all views within the axes for safe keeping (persistence)
        if not hasattr(self.axes, 'views'):
            self.axes.views = []
        self.axes.views.append(self)
        self.axes.is_interactive = True

        # connect up the key/link driven navigation
        self._accelerate = False
        self.cid = self.figure.canvas.mpl_connect('key_press_event', self.key_command)
        if not hasattr(self.figure, 'shortcuts'):
            self.figure.shortcuts = SortedDict()
        self.figure.shortcuts['left'] = 'Reduce index of first non-axial dimension'
        self.figure.shortcuts['right'] = 'Increase index of first non-axial dimension'
        self.figure.shortcuts['up'] = 'Reduce index of second non-axial dimension'
        self.figure.shortcuts['down'] = 'Increase index of second non-axial dimension'
        self.figure.shortcuts['shift+up/down/left/right'] = 'Accelerate: Change index by one fifth the range'
        self.figure.shortcuts['a'] = 'Toggle accelerate all on/off'
        self.figure.shortcuts['w'] = 'Persist current slice of viewed data'
        self.figure.shortcuts['e'] = 'Erase all persisting slices of viewed data except the active one'

    def use_uband(self, use=True):
        """Toggle use of uband instead of uerrorbar for plotting function"""
        self._use_uband = use
        if use:
            self._uplot = uband
        else:
            self._uplot = uerrorbar

    def set_label_indexers_visible(self, visible=True):
        """Include the current indexers in line labels."""
        self._label_indexers_visible = visible
        # update plot
        self.isel(draw=False, **self.indexes)

    def _get_label(self):
        """(Re-)Set the view Line's label indicating the current indexes slicing"""
        if self.label_prefix:
            lbl = self.label_prefix + ' ' + self.name
        else:
            lbl = self.name
        if not self.name:
            return lbl
        for k, i in list(self.indexes.items()):
            i = np.unique(np.clip(i, 0, self.data[k].size - 1))
            if self._label_indexers_visible and len(i) < self.data[k].shape[0]:  # don't label if not sliced at all
                if len(i) == 1:
                    lbl += ', {key} = {vals} {units}'.format(
                        name=self.name, key=k, vals=self.data[k][i].values[0], units=self.data[k][i].attrs.get('units', '')
                    )
                else:
                    lbl += ', {key} = {vals}'.format(name=self.name, key=k, vals=self.data[k][i].values)
        return lbl.rstrip(', ').lstrip(', ')

    def key_command(self, event, draw=True, **plot_options):
        """
        Use arrows to navigate up to 2 extra dimensions by incrementing
        the slice indexes.

        Use w/e to write/erase slices to persist outside on navigation.

        """
        # prevent infinite loops
        if not hasattr(self, '_lastevent'):
            self._lastevent = None
        if self._lastevent == event:
            return
        self._lastevent = event

        # drivers can override plot_options
        self.plot_options.update(plot_options)

        # get standard key press name
        if not event.key:
            return
        key_press = event.key.lower()

        # had to add this because mac Tk doesn't register shift+key
        if key_press == 'a':
            self._accelerate = not self._accelerate
        # slice navigation
        if key_press in ['left', 'right', 'down', 'up', 'shift+left', 'shift+right', 'shift+up', 'shift+down']:
            # select dimension being changed
            if key_press in ['left', 'right', 'shift+left', 'shift+right']:
                dim = list(self.indexes.keys())[0]
            if key_press in ['down', 'up', 'shift+up', 'shift+down']:
                i = min(len(self.indexes) - 1, 1)
                dim = list(self.indexes.keys())[i]
            # apply change in right direction
            if key_press in ['left', 'down']:
                self.indexes[dim] -= 1 + self._accelerate * (int(self.data[dim].size // 5) - 1)
            if key_press in ['shift+left', 'shift+down']:
                self.indexes[dim] -= int(self.data[dim].size // 5)
            if key_press in ['right', 'up']:
                self.indexes[dim] += 1 + self._accelerate * (int(self.data[dim].size // 5) - 1)
            if key_press in ['shift+right', 'shift+up']:
                self.indexes[dim] += int(self.data[dim].size // 5)
            # update plot
            self.isel(draw=False, **self.indexes)

        # snapshot write / erase
        if key_press == 'w':
            self._add_lines()
            if isinstance(self._inactive[-1][0], matplotlib.container.ErrorbarContainer):
                plot_options['color'] = self._inactive[-1][0].lines[0].get_color()
            else:
                plot_options['color'] = self._inactive[-1][0].get_color()
        if key_press == 'e':
            self._clear_lines()

        # drive linked views, then draw once
        for link in self.links:
            link.key_command(event, draw=False, **plot_options)
        if draw:
            self.figure.canvas.draw_idle()
            # if linked to views in other figures draw those too
            otherfigs = unsorted_unique([self.figure] + [v.figure for v in self.links])[1:]
            for f in otherfigs:
                f.canvas.draw_idle()
        return

    def _add_lines(self):
        """Plot a persistent snapshot of the current slice"""
        lbl = self._get_label()
        if self.is_uncertain:
            ys = self.values[self.name].values.reshape(self.values[self.name].shape[0], -1)
            xs = self.values[self.dim].values.reshape(self.values[self.dim].shape[0], -1)
            if xs.shape[1] == 1:
                xs = np.tile(xs, ys.shape[1])
            for x, y in zip(xs.T, ys.T):
                if self._use_uband:
                    self._inactive.append(uband(x, y, ax=self.axes, label=lbl, **self.plot_options))
                else:
                    self._inactive.append(uerrorbar(x, y, ax=self.axes, label=lbl, **self.plot_options))
        else:
            self._inactive.append(self.axes.plot(self.values[self.dim], self.values[self.name], label=lbl, **self.plot_options))

        # Update annotations
        if self.cornernote_options is not None:
            self._update_cornernote()

    def _clear_lines(self):
        """Remove otherwise persistent snapshots"""
        from matplotlib.cbook import flatten

        for lines in self._inactive:
            if lines in self.axes.containers:  # bug in matplotlib ErrorbarContainer.remove
                for l in flatten(lines.lines):
                    l.remove()
                self.axes.containers.remove(lines)
            else:
                for l in lines:
                    l.remove()
        self._inactive = []
        self.isel(**self.indexes)  # redraw current slice

    def isel(self, draw=True, **indexers):
        """
        Re-slice the data along its extra dimensions using indexes.
        """
        from matplotlib.cbook import flatten

        self.indexes = SortedDict(indexers)
        # only plot valid indexers (but allow keeping track of others)
        for dim in indexers:
            indexers[dim] = np.unique(np.clip(self.indexes[dim], 0, self.data[dim].size - 1))

        self.values = self.data.isel(**indexers).transpose(*self.data[self.name].dims)  # make sure dim order stays consistent
        lbl = self._get_label()
        # update errorbar container lines
        if self.is_uncertain:
            # can't animate PollyCollection - have to delete and draw new
            if self._use_uband:
                colors = []
                for obj in self._active:
                    colors.append(obj.get_color())
                    if isinstance(obj, Uband):
                        if obj.line in self.axes.lines:
                            self.axes.lines.remove(obj.line)
                        for band in obj.bands:
                            if band in self.axes.collections:
                                self.axes.collections.remove(band)
                    else:  # assume errorbar container
                        for l in flatten(obj.lines):
                            if l in self.axes.lines:
                                self.axes.lines.remove(l)
                            if l in self.axes.collections:
                                self.axes.collections.remove(l)
                self._active = []
                ys = self.values[self.name].values.reshape(self.values[self.name].shape[0], -1)
                xs = self.values[self.dim].values.reshape(self.values[self.dim].shape[0], -1)
                if xs.shape[0] == 1 and ys.shape[0] == 1:
                    xs = xs.T
                    ys = ys.T
                if xs.shape[1] == 1:
                    xs = np.tile(xs, ys.shape[1])
                lim = (np.nanmin(nominal_values(ys)), np.nanmax(nominal_values(ys)))
                match_colors = not 'color' in self.plot_options  # keep same color even if not explicitly set the first time
                for i, (xi, yi) in enumerate(zip(xs.T, ys.T)):
                    if match_colors and i < len(colors):
                        self.plot_options['color'] = colors[i]
                    self._active.append(self._uplot(xi, yi, ax=self.axes, label=lbl, **self.plot_options)[0])
                    if match_colors:
                        self.plot_options.pop('color', None)

            # painfully update only the individual pieces of a ErrorbarContainer for faster redraw
            else:
                ys = self.values[self.name].values.reshape(self.values[self.name].shape[0], -1)
                xs = self.values[self.dim].values.reshape(self.values[self.dim].shape[0], -1)
                if xs.shape[1] == 1:
                    xs = np.tile(xs, ys.shape[1])
                lim = (np.nanmin(nominal_values(ys)), np.nanmax(nominal_values(ys)))
                for i, (xi, yi) in enumerate(zip(xs.T, ys.T)):
                    container = self._active[i]
                    y, ye = nominal_values(yi), std_devs(yi)
                    x, xe = nominal_values(xi), std_devs(xi)
                    # matplotlib error bar does not do multiple lines at once, so safe to simply flatten
                    x, xe = x.flatten(), xe.flatten()
                    line, capinfo, barinfo = container.lines
                    if len(barinfo) == 2:  # X and Y errors
                        (xbars, ybars) = barinfo
                        if len(capinfo):  # With end-caps
                            xtop, xbot, ytop, ybot = capinfo
                        else:  # Without end-caps
                            xtop, xbot, ytop, ybot = None, None, None, None
                    else:  # Y errors only
                        (ybars,) = barinfo[0]
                        if len(capinfo):  # With end-caps
                            ytop, ybot = capinfo
                        else:  # Without end-caps
                            ytop, ybot = None, None
                        xtop, xbot = None, None

                    yt, yb = y + ye, y - ye
                    xt, xb = x + xe, x - xe
                    line.set_data([x, y])
                    if ybot:
                        ytop.set_data([x, yt])
                        ybot.set_data([x, yb])
                    new_segments_y = [np.array([[xn, yts], [xn, ybs]]) for xn, yts, ybs in zip(x, yt, yb)]
                    ybars.set_segments(new_segments_y)
                    if xbot:
                        xtop.set_data([xt, y])
                        xbot.set_data([xb, y])
                        new_segments_x = [np.array([[xts, yn], [xbs, yn]]) for xts, xbs, yn in zip(xt, xb, y)]
                        xbars.set_segments(new_segments_x)
                    container.set_label(lbl)
        # update simple lines
        else:
            lim = (np.nanmin(self.values[self.name]), np.nanmax(self.values[self.name]))
            xlen = len(self._active[0].get_xdata())
            ys = self.values[self.name].values.reshape(xlen, -1).T
            if self.dim in self.data.dims:  # usual case where x is a 1D dimension
                xs = [self.values[self.dim]] * ys.shape[0]
            else:  # special case where x is a dataset variable
                xs = self.values[self.dim].values.reshape(xlen, -1).T
            # update each line
            for line, x, y in zip(self._active, xs, ys):
                line.set_data([x, y])
                line.set_label(lbl)
            # remove lines that got crunched into upper/lower bounds
            for line in self._active[len(ys) :]:
                self.axes.lines.remove(line)
                self._active.remove(line)
        # make sure the new labels get into the legend
        if self.axes.get_legend():
            visible = self.axes.get_legend().get_visible()
            leg = self.axes.legend(loc=0)
            leg.draggable(True)
            leg.set_visible(visible)

        # expand axis limits if necessary
        if self.dynamic_ylim:
            ylim = self.axes.get_ylim()
            if ylim[0] > lim[0]:
                self.axes.set_ylim(ymin=lim[0])
            if ylim[1] < lim[1]:
                self.axes.set_ylim(ymax=lim[1])

        # Update annotations
        if self.cornernote_options is not None:
            self._update_cornernote()

        if draw:
            self.figure.canvas.draw_idle()

    def _update_cornernote(self):
        """
        If indexing by time and if there is only one index, use it to look up the time for the current index and then
        update the cornernote.
        """
        if len(self.indexes) == 1 and 'time' in list(self.indexes.keys()):
            time_index = np.unique(np.clip(self.indexes['time'], 0, self.data['time'].size - 1))
            times = self.data.coords['time'].values[time_index]
            co = self.cornernote_options
            root = co.get('root', None)
            device = co.get('device', None)
            shot = co.get('shot', None)

            if len(time_index) == 1 and not self._inactive:
                cornernote(root=root, device=device, shot=shot, time=times[0], ax=self.axes)
            elif len(time_index) == 2 and not self._inactive:
                cornernote(root=root, device=device, shot=shot, time='{}, {}'.format(times[0], times[1]), ax=self.axes)
            else:
                cornernote(root=root, device=device, shot=shot, time='', ax=self.axes)

    def link(self, view, disconnect=True):
        """
        Link all actions in this view to the given view.

        :param view: View1d. A view that will be driven by this View's key press responses.
        :param disconnect: bool. Disconnect key press events from driven view.

        """
        self.links.append(view)
        # disconnect the key/link driven navigation
        if disconnect:
            view.figure.canvas.mpl_disconnect(view.cid)

        return

    def unlink(self, view):
        """
        Unlink actions in this view from controlling the given view.
        """
        if view in self.links:
            self.links.remove(view)
            # reconnect the key driven navigation if no other link
            reconnect = True
            for a in self.figure.axes:
                if hasattr(a, 'views'):
                    for v in a.views:
                        if self in v.links:
                            reconnect = False
            if reconnect:
                view.cid = view.figure.canvas.mpl_connect('key_press_event', view.key_command)
        return


@_available_to_user_plot
class View2d(object):
    """
    Plot 2D data with interactive slice viewers attached to the 2D Axes.
    Left clicking on the 2D plot refreshes the line plot slices, right clicking
    overplots new slices.

    The original design of this viewer was for data on a rectangular grid, for which
    x and y are 1D arrays defining the axes but may be irregularly spaced. In this case,
    the line plot points correspond to the given data. If x or y is a 2D array,
    the data is assumed irregular and interpolated to a regular grid using
    scipy.interpolate.griddata.

    **Example:**

    Explore a basic 2D np array without labels,

    >> x = np.linspace(-1, 1, 200)
    >> y = np.linspace(-2, 2, 200)
    >> xx, yy = meshgrid(x, y)
    >> z = np.exp(-xx**2 - yy**2)
    >> v = View2d(z)

    To add more meaningful labels to the axes and data do,

    >> v = View2d(z, coords={'x':x, 'y':y}, dims=('x', 'y'), name='wow')

    or use a DataArray,

    >> d = DataArray(z, coords={'x':x, 'y':y}, dims=('x', 'y'), name='wow')
    >> v = View2d(d)

    Note that the coordinates should be 1D. Initializing a view with regular grid,
    2D coordinates will result in an attempt to slice them appropriately.
    This is done for consistency with some matplotlib 2D plotting routines,
    but is not recommended.

    >> v = View2d(z, coords=dict(x=x, y=y), dims=('x', 'y'))

    If you have irregularly distributed 2D data, it is recomended that you first interpolate
    it to a 2D grid in whatever way is most applicable. If you do not, initializing a view
    will result in an attempt to linearly interpolate to a automatically chosen grid.

    >> x = np.random.rand(1000)
    >> y = np.random.rand(1000) * 2
    >> z = np.exp(-x**2 - y**2)
    >> v = View2d(z, coords=dict(x=x, y=y), dims=('x', 'y'))

    The same applies for 2D collections of irregular points and values.

    >> x = x.reshape((50, 20))
    >> y = y.reshape((50, 20))
    >> z = z.reshape((50, 20))
    >> v = View2d(z, coords=[('x', x), ('y', y)], dims=('x', 'y'))


    """

    def __init__(
        self,
        data,
        coords=None,
        dims=None,
        name=None,
        axes=None,
        quiet=False,
        use_uband=False,
        contour_levels=0,
        imag_options={},
        plot_options={'marker': '', 'ls': '-'},
        **indexers,
    ):
        r"""

        :param data: DataArray or array-like
            2D or 3D data values to be viewed.
        :param coords: dict-like
            Dictionary of Coordinate objects that label values along each dimension.
        :param dims: tuple
            Dimension names associated with this array.
        :param name: string
            Label used in legend. Empty or begining with '_' produces no legend label.
        :param dim: string, DataArray
            Dimension plotted on x-axis. If DataArray, must have same dims as data.
        :param axes: Axes instance
            The axes plotting is done in.
        :param quiet: bool
            Suppress printed messages.
        :param use_uband: bool
            Use uband for 1D slice plots instead of uerrorbar.
        :param contour_levels: int or np.ndarray
            Number of or specific levels used to draw black contour lines over the 2D image.
        :param imag_options: dict
            Key word arguments passed to the DataArray plot method (modified pcolormesh).
        :param plot_options: dict
            Key word arguments passed to plot or uerrorbar. Color will be determined by cmap variable.

        :param \**indexers: dict
            Dictionary with keys given by dimension names and values given by
            arrays of coordinate index values.

        """
        # check args and make Dataset if needed
        if isinstance(data, DataArray):
            if coords or dims:
                raise ValueError("View cannot re-assign coords/dims to data that is already a DataArray")
            if name:
                data.name = name
            elif not data.name:  # require name
                name = 'viewdata'
                data.name = name
            else:
                name = data.name
            data = data
        elif isinstance(data, Dataset):
            if coords or dims:
                raise ValueError("View cannot re-assign coords/dims to data that is already a Dataset")
            data = data[list(data.data_vars.keys())]
        else:
            if name is None:
                name = 'viewdata'
            try:
                data = DataArray(data, coords=coords, dims=dims, name=name)
            except Exception as error:
                # turn the flexible input styles into the standard coords dict, dims list
                if coords is not None:
                    coords = OrderedDict(coords)
                if isinstance(dims, dict):
                    x0, x1 = list(dims.values())[:2]
                    dims = list(dims.keys())[:2]
                elif dims is not None:
                    x0, x1 = [coords[k] for k in dims[:2]]
                else:
                    x0, x1 = list(coords.values())[:2]
                    dims = list(coords.keys())[:2]
                # check if called with 2D coordinates of a regular grid
                if (
                    (x0.shape == data.shape and x1.shape == data.shape)
                    and np.all(x0 == np.roll(x0, -1, axis=0))
                    and np.all(x1 == np.roll(x1, -1, axis=1))
                ):
                    coords_1d = {dims[0]: x0[0], dims[1]: x1[:, 0]}
                    data = DataArray(data, coords=coords_1d, dims=dims, name=name)
                # interpolate weird inputs to a nice 2D grid
                else:
                    if not quiet:
                        printe("WARNING: Could not directly form a DataArray from inputs.")
                        printe("  {:}".format(error))
                        printe("  > Interpolating to a regular grid.")
                    # make a regular grid
                    x0, x1 = np.ravel(x0), np.ravel(x1)
                    dx0, dx1 = np.diff(sorted(x0)), np.diff(sorted(x1))
                    n0 = int((np.nanmax(x0) - np.nanmin(x0)) / np.median(dx0[np.where(dx0 != 0)]))
                    n1 = int((np.nanmax(x1) - np.nanmin(x1)) / np.median(dx1[np.where(dx1 != 0)]))
                    i0 = np.linspace(np.nanmin(x0), np.nanmax(x0), min(500, n0))
                    i1 = np.linspace(np.nanmin(x1), np.nanmax(x1), min(500, n1))
                    data = interpolate.griddata((x0, x1), np.ravel(data), (i0[None, :], i1[:, None]), method='linear')
                    data = data.reshape((i1.shape[0], i0.shape[0])).T
                    data = DataArray(data, coords=[(k, x) for k, x in zip(dims, (i0, i1))], dims=dims, name=name)

        # pass on key words
        if not np.shape(contour_levels) and contour_levels == 0:
            contour_levels = None  # captures 0.0, 0, None, False, etc.
        self._contour_levels = contour_levels
        self._use_uband = use_uband
        self.plot_options = plot_options
        self.plot_cmap = plot_options.get('cmap', None)
        self.imag_options = imag_options

        # store basic inputs
        self.data = data
        # make alarm for timing
        self.alarm = None
        # empty list of links
        self.links = []

        # Make figure & main axes if needed
        if axes == None:
            fig = pyplot.figure(figsize=(10, 8))
            gs = matplotlib.gridspec.GridSpec(4, 4)
            gs.update(wspace=0.05, hspace=0.05)
            axm = fig.add_subplot(gs[1:, :-1])  # main 2D plot
        else:  # make a grid within the original axes location
            fig = axes.get_figure()
            axm = axes
            rect = axm.get_position().bounds
            gs = matplotlib.gridspec.GridSpec(4, 4, left=rect[0], bottom=rect[1], right=rect[0] + rect[2], top=rect[1] + rect[3])
            axm.set_position(gs[1:, :-1].get_position(fig))  # main 2D plot
        # add surrounding axes
        axx = fig.add_subplot(gs[0, :-1], sharex=axm)
        axy = fig.add_subplot(gs[1:, -1], sharey=axm)
        axr = fig.add_subplot(gs[0, -1])
        # add to class
        self.fig = fig
        self.axm = axm
        self.axx = axx
        self.axy = axy
        self.axr = axr
        self.old_xmin = 0.0
        self.old_xmax = 0.0
        self.old_ymin = 0.0
        self.old_ymax = 1.0

        # autoscaling behaves poorly
        for ax in [axm, axy, axx, axr]:
            ax.autoscale(False)
        # store within the axes for safe keeping (persistence)
        if not hasattr(self.axm, 'views'):
            self.axm.views = []
        self.axm.views.append(self)
        self.axm.is_interactive = True

        # 2D plot with colorbar
        axm.set_xlabel(data.dims[0])
        axm.set_ylabel(data.dims[1])
        self._set_values(self.data, **imag_options)
        axm.axis('tight')
        self.colorbar = self.fig.colorbar(self.image, ax=[axm, axy, axx, axr], use_gridspec=True, shrink=0.75, anchor=(0, 0.0))
        self.colorbar.set_label(self.data.name)
        if not self.plot_cmap:
            self.plot_cmap = self.axm.collections[-1].get_cmap()

        # 1D plots aesthetics
        axx.set_ylabel(data.name)
        # axx.set_ylim(np.nanmin(data),np.nanmax(data))
        loc = pyplot.MaxNLocator(5)
        axx.yaxis.set_major_locator(loc)
        axy.set_xlabel(data.name)
        # axy.set_xlim(np.nanmin(data),np.nanmax(data))
        loc = pyplot.MaxNLocator(5)
        axy.xaxis.set_major_locator(loc)
        pyplot.setp(axy.xaxis.get_majorticklabels(), rotation=90)
        for tl in axx.xaxis.get_ticklabels() + axy.yaxis.get_ticklabels():
            tl.set_visible(False)

        # connect axes to events
        self.RectangleSelector = RectangleSelector(
            self.axm,
            self.line_select_callback,
            drawtype='box',
            useblit=True,  # minspanx=0, minspany=0,
            button=[1, 3],  # don't use middle button
            spancoords='data',
        )
        self.fig.canvas.mpl_connect('button_press_event', self.line_select_callback)
        self.fig.canvas.mpl_connect('key_press_event', self.toggle_selector)
        # connect radio buttons
        self.radio = RadioButtons(
            axr,
            ('data', 'd/d-' + self.data.dims[0], 'd/d-' + self.data.dims[1], 'int-' + self.data.dims[0], 'int-' + self.data.dims[1]),
            activecolor='black',
        )
        self.radio.on_clicked(self._radio_select)
        self.radio.selected = 'data'
        self._log_toggled = False
        if hasattr(self.fig, 'shortcuts'):
            self.fig.shortcuts['j'] = 'Toggle log scaling of 2D image data.'
        else:
            printe('No shortcuts attribute so no log scaling')
        self.fig.canvas.draw_idle()

    def use_uband(self, use=True):
        """Toggle use of uband instead of uerrorbar in 1D slice plots"""
        self._use_uband = use

    def key_navigate_cuts(self, key_press):
        if key_press in ['left', 'right']:
            dat = self.data[self.data.dims[0]]
            xmin, xmax, std = self.get_vslice_args()
        else:
            dat = self.data[self.data.dims[1]]
            xmin, xmax, std = self.get_hslice_args()
        imin = np.abs(dat.values - xmin).argmin()
        imax = np.abs(dat.values - xmax).argmin()
        # imax = max(imax,min(imin,len(dat)-2))
        if key_press in ['right', 'up']:
            imax_new = imax + 1
            imin_new = imin + 1
        else:
            imax_new = imax - 1
            imin_new = imin - 1
        # Bound the results
        max_index = min(max(imax_new, 0), len(dat) - 1)
        min_index = min(max(imin_new, 0), len(dat) - 1)
        if key_press in ['left', 'right']:
            self.vslice(dat[min_index].values, dat[max_index].values, std)
        else:

            self.hslice(dat[min_index].values, dat[max_index].values, std)
        # if self.alarm:
        #     OMFITaux['rootGUI'].after_cancel(self.alarm)
        #     self.alarm=None
        # self.alarm=OMFITaux['rootGUI'].after(100,None)

    def _set_values(self, values, draw=True, log_toggled=False, **kw):
        r"""
        Plots the main 2D image in axm.
        Optionally re-sets displayed values and axes, but does not change original data.

        :param values: 2D DataArray of values for display/interaction.
        :type values: DataArray.

        :param draw: Re-draw the figure when done.
        :type draw; bool

        :param log_toggled: Default value of False resets 'j' hotkey binding.
        :type log_toggled; bool

        :param \**kw: Additional key word arguments passed to the DataArray plot method (modified pcolormesh).

        :return: The main 2d :class:`matplotlib.collections.QuadMesh` from pcolormesh

        """
        self._log_toggled = log_toggled
        self.values = values
        # mask values (allows for nan's)
        zim = nominal_values(values)
        zim = np.ma.masked_where(np.isnan(zim), zim)
        if isinstance(values[values.dims[0]].values[0], str):
            x0 = np.arange(len(values[values.dims[0]]))
        else:
            x0 = nominal_values(values[values.dims[0]])
        if isinstance(values[values.dims[1]].values[0], str):
            x1 = np.arange(len(values[values.dims[1]]))
        else:
            x1 = nominal_values(values[values.dims[1]])

        # limits
        xlim = (np.nanmin(x0), np.nanmax(x0))
        ylim = (np.nanmin(x1), np.nanmax(x1))
        vlim = (np.nanmin(zim), np.nanmax(zim))

        # default key words
        dkw = {}
        dkw.update(kw)

        # first call creates the base image from the original data
        if not hasattr(self, 'image'):
            if 1 in self.data.shape:
                raise ValueError("Must have 2D data to use View2D. This data is {:}x{:}".format(*self.data.shape))
            self.image = self.data.T.plot(ax=self.axm, add_colorbar=False, **dkw)

        # updated image
        self.image.set_array(zim.T.flatten())
        self.image.autoscale()
        for k, v in list(kw.items()):
            try:
                getattr(self.image, 'set_' + k)(v)
            except Exception:
                printe('Cannot reset {:}, change manually.'.format(k))

        # contour
        if hasattr(self, 'contour'):
            for c in self.contour.collections:
                if c in self.axm.collections:
                    self.axm.collections.remove(c)
        if not np.all(zim.T == zim.flat[0]) and self._contour_levels is not None:
            self.contour = self.axm.contour(x0, x1, zim.T, self._contour_levels, colors='k')

        # aesthetics
        self.axm.set_xlim(*xlim)
        self.axm.set_ylim(*ylim)
        self.axx.set_ylim(*vlim)
        self.axy.set_xlim(*vlim)

        # re-slice
        if hasattr(self, 'get_vslice_args') and hasattr(self, 'get_hslice_args'):
            self.vslice(*self.get_vslice_args(), draw=draw, force=True)
            self.hslice(*self.get_hslice_args(), draw=draw, force=True)
        else:
            self.vslice(*[np.nanmean(x0)] * 2, draw=draw, force=True)
            self.hslice(*[np.nanmean(x1)] * 2, draw=draw, force=True)

        # drawing is slow
        if draw:
            self.fig.canvas.draw()  # Why does this change the axm limits????

        return

    def set_data(self, data=None, **kw):
        """
        Set base data and axes, as well as displayed values.
        Call with no arguments re-sets to interactively displayed values (use after :func:`der`, or :func:`int`).

        :param data: 2D array of data.
        :type data: DataArray

        :return: The main 2d :class:`matplotlib.collections.QuadMesh` from pcolormesh
        """
        if not data is None:
            self.data = data

        # keep the radio selection
        self._radio_select(self.radio.selected)
        return

    def der(self, axis=0):
        """
        Set 2D values to derivative of data along specified axis.

        :param axis: Axis along which derivative is taken (0=horizontal, 1=vertical).
        :type axis: int

        :return: The main 2d :class:`matplotlib.collections.QuadMesh` from pcolormesh
        """
        if not isinstance(axis, int):
            axis = self.data.get_axis_num(axis)

        dx = np.gradient(nominal_values(self.data[self.data.dims[axis]])) + 0 * self.data[self.data.dims[axis]]
        dy = np.gradient(nominal_values(self.data), edge_order=2)[axis] + 0 * self.data
        data = dy / dx
        if np.allclose(nominal_values(self.values), nominal_values(data)):
            return
        self._set_values(data, **self.imag_options)

        # force action in linked views
        for v in self.links:
            v.der(axis=axis)

        return

    def int(self, axis=0):
        """
        Set 2D values to derivative of data along specified axis.

        :param axis: Axis along which integration is taken (0=horizontal, 1=vertical).
        :type axis: int

        :return: The main 2d :class:`matplotlib.collections.QuadMesh` from pcolormesh
        """
        if isinstance(axis, int):
            x = self.data[self.data.dims[axis]]
        else:
            x = self.data[axis]
        data = integrate.cumtrapz(np.nan_to_num(nominal_values(self.data)), x=x, axis=axis, initial=0) + 0 * self.data
        if np.allclose(nominal_values(self.values), nominal_values(data)):
            return
        self._set_values(data, **self.imag_options)

        # force action in linked views
        for v in self.links:
            v.int(axis=axis)

        return

    def toggle_log(self):
        """
        Toggle log/linear scaling of data in 2D plot.

        """
        if self._log_toggled:
            self._set_values(10 ** self.values, **self.imag_options)
            lbl = self.colorbar.ax.get_ylabel().lstrip('log ')
            self.colorbar.set_label(lbl)
            self.axx.set_ylabel(lbl)
            self.axy.set_xlabel(lbl)
            self.axx.set_yscale('linear')
            self.axy.set_xscale('linear')
            self._log_toggled = False
        else:
            self._set_values(np.log10(self.values), **self.imag_options)
            # relabel all axes
            lbl = 'log ' + self.colorbar.ax.get_ylabel()
            self.colorbar.set_label(lbl)
            self.axx.set_ylabel(lbl)
            self.axy.set_xlabel(lbl)
            # log scale line plots
            self.axx.set_yscale('log')
            self.axy.set_xscale('log')
            # robust log scale axes should not go to 0
            zim = nominal_values(self.values)
            zim = np.ma.masked_where(np.isnan(zim), zim)
            zim = np.ma.masked_where(zim <= 0, zim)
            vlim = (np.nanmin(zim), np.nanmax(zim))
            self.axx.set_ylim(*vlim)
            self.axy.set_xlim(*vlim)

            self._log_toggled = True

        return

    def vslice(self, xmin, xmax, std=False, draw=True, force=False, **kw):
        r"""
        Plot line collection of x slices.

        :param xmin: Lower bound of slices dispayed in line plot.
        :type xmin: float
        :param xmax: Upper bound of slices dispayed in line plot.
        :type xmax: float

        :param std: Display mean and standard deviation instead of individual slices.
        :type std: bool
        :param draw: Redraw the figure canvas
        :type draw: bool
        :param Force: Re-slice even if arguments are identical to last slice.
        :type draw: bool

        :param \**kw: Extra key words are passed to the 1D :func:`plot` function

        :return: Possibly modified (xmin,xmax,std)
        :rtype: tuple

        """
        # plot options
        self.plot_options.update(kw)
        # slices
        if isinstance(self.data[self.data.dims[0]].values[0], str):
            x0 = np.arange(len(self.data[self.data.dims[0]]))
        else:
            x0 = nominal_values(self.data[self.data.dims[0]])
        if isinstance(self.data[self.data.dims[1]].values[0], str):
            x1 = np.arange(len(self.data[self.data.dims[1]]))
        else:
            x1 = nominal_values(self.data[self.data.dims[1]])
        if isinstance(xmin, DataArray):
            xmin = xmin.values
        if isinstance(xmax, DataArray):
            xmax = xmax.values
        imin = np.abs(x0 - xmin).argmin()
        imax = np.abs(x0 - xmax).argmin()
        imax = max(imax, min(imin, len(x0) - 2))
        x = self.values[imin : imax + 1, :]
        y = self.data[self.data.dims[1]]
        limits = self.axm.axis()
        # Stop infinite loops
        if hasattr(self, 'get_vslice_args'):
            if not force and (x0[imin], x0[imax], std) == self.get_vslice_args():
                return self.get_vslice_args()

        self.get_vslice_args = lambda: (x0[imin], x0[imax], std)
        self.axy.containers = []
        self.axy.collections = []
        self.axy.lines = []
        xm, sd = np.mean(nominal_values(x), axis=0), np.std(nominal_values(x), axis=0)
        self._vslice_mean = xm
        self._vslice_std = sd
        self._vslice_xdata = y
        if std:
            (l,) = self.axy.plot(nominal_values(xm), nominal_values(y), color='r')
            self.axy.fill_betweenx(nominal_values(y), nominal_values(xm - sd), nominal_values(xm + sd), alpha=0.3, color='r')
        else:
            y = x1.repeat(x.shape[0]).reshape((len(x1), -1)).T
            lines = []
            for i, (xi, yi) in enumerate(zip(x, y)):
                if self._use_uband:
                    (l,) = uband(xi, yi, ax=self.axy, **self.plot_options)
                else:
                    (l,) = uerrorbar(xi, yi, ax=self.axy, **self.plot_options)
                if i == 0 or i == imax - imin:
                    l.set_label('{:}={:6.2g}'.format(self.axm.get_xlabel(), x0[imin + i]))
                lines.append(l)
            sm = set_linearray(lines[:], x0[imin : imax + 1], cmap=self.plot_cmap)
            # self.fig.colorbar(sm,cax=self.axy,orientation='horizontal',use_gridspec=True)
            # lc = plotslices(x,y,colorbar='None',axes=self.axy,cmap='autumn_r')
        self.axy.legend(numpoints=1, prop={'size': 'xx-small'}).draggable(True)
        # self.axy.texts = []
        # self.axy.text(0.02,0.95,'{:}=[{:.2},{:.2}]'.format(self.axm.get_xlabel(),*self.get_vslice_args()),
        #                    verticalalignment='top',transform=self.axy.transAxes)
        if hasattr(self.axm, '_vspan'):
            if self.axm._vspan in self.axm.patches:
                self.axm.patches.pop(self.axm.patches.index(self.axm._vspan))
        self.axm._vspan = self.axm.axvspan(x0[imin], x0[imax], facecolor='w', edgecolor='w', alpha=0.3)
        if draw:
            self.fig.canvas.draw()

        # force action in linked views
        for v in self.links:
            v.vslice(*self.get_vslice_args())

        return self.get_vslice_args()

    def hslice(self, ymin, ymax, std=False, draw=True, force=False, **kw):
        r"""
        Plot line collection of y slices.

        :param ymin: Lower bound of slices dispayed in line plot.
        :type ymin: float
        :param ymax: Upper bound of slices dispayed in line plot.
        :type ymax: float

        :param std: Display mean and standard deviation instead of individual slices.
        :type std: bool
        :param draw: Redraw the figure canvas
        :type draw: bool
        :param Force: Re-slice even if arguments are identical to last slice.
        :type draw: bool

        :param \**kw: Extra key words are passed to the 1D :func:`plot` function

        :return: Possibly modified (ymin,ymax,std)
        :rtype: tuple

        """
        # plot options
        self.plot_options.update(kw)
        # slices
        if isinstance(self.data[self.data.dims[0]].values[0], str):
            x0 = np.arange(len(self.data[self.data.dims[0]]))
        else:
            x0 = nominal_values(self.data[self.data.dims[0]])
        if isinstance(self.data[self.data.dims[1]].values[0], str):
            x1 = np.arange(len(self.data[self.data.dims[1]]))
        else:
            x1 = nominal_values(self.data[self.data.dims[1]])
        if isinstance(ymin, DataArray):
            ymin = ymin.values
        if isinstance(ymax, DataArray):
            ymax = ymax.values
        imin = np.abs(x1 - ymin).argmin()
        imax = np.abs(x1 - ymax).argmin()
        imax = max(imax, min(imin, len(x1) - 2))
        y = self.values[:, imin : imax + 1]
        x = self.data[self.data.dims[0]].values
        if isinstance(x[0], str):
            x = np.arange(len(x))
        # Prevent infinite loops
        if hasattr(self, 'get_hslice_args'):
            if not force and (x1[imin], x1[imax], std) == self.get_hslice_args():
                return self.get_hslice_args()

        self.get_hslice_args = lambda: (x1[imin], x1[imax], std)
        self.axx.containers = []
        self.axx.collections = []
        self.axx.lines = []
        ym, sd = np.mean(nominal_values(y), axis=1), np.std(nominal_values(y), axis=1)
        self._hslice_mean = ym
        self._hslice_std = sd
        self._hslice_xdata = x0
        if std:
            (l,) = self.axx.plot(x0, nominal_values(ym), color='b')
            self.axx.fill_between(nominal_values(x), nominal_values(ym - sd), nominal_values(ym + sd), alpha=0.3, color='b')
        else:
            lines = []
            for i, yi in enumerate(y.T):
                if self._use_uband:
                    (l,) = uband(x, yi.values, ax=self.axx, **self.plot_options)
                else:
                    (l,) = uerrorbar(x, yi.values, ax=self.axx, **self.plot_options)
                if i == 0 or i == imax - imin:
                    l.set_label('{:}={:6.2g}'.format(self.axm.get_ylabel(), x1[imin + i]))
                lines.append(l)
            sm = set_linearray(lines[:], x1[imin : imax + 1], cmap=self.plot_cmap)
        self.axx.legend(numpoints=1, prop={'size': 'xx-small'}).draggable(True)
        if hasattr(self.axm, '_hspan'):
            if self.axm._hspan in self.axm.patches:
                self.axm.patches.pop(self.axm.patches.index(self.axm._hspan))
        self.axm._hspan = self.axm.axhspan(x1[imin], x1[imax], facecolor='w', edgecolor='w', alpha=0.3)
        if draw:
            self.fig.canvas.draw()

        # force action in linked views
        for v in self.links:
            v.hslice(*self.get_hslice_args())

        return self.get_hslice_args()

    def line_select_callback(self, eclick, erelease=None):
        """
        Call vslice and hslice for the range of x and y spanned
        by the rectangle between mouse press and release.
        Called by RectangleSelector.

        :param eclick: Matplotlib mouse click.
        :type eclick: matplotlib Event
        :param erelease: Matplotlib mouse release.
        :type erelease: matplotlib Event
        :return: None

        """
        # do nothing if click not in main axes
        if eclick.inaxes != self.axm:
            return

        # special treatment for single click (no dragged box)
        eclick.button == rightClickMPLindex  # right click
        if erelease is None:
            x, y = self.axm.transData.inverted().transform([eclick.x, eclick.y])
            self.hslice(y, y, std=rightClickMPLindex)
            self.vslice(x, x, std=rightClickMPLindex)
            self.fig.canvas.draw_idle()
            return

        # check if box is new (prevent infinite loops)
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        xmin, xmax = sorted([x1, x2])
        ymin, ymax = sorted([y1, y2])
        if xmin == self.old_xmin and xmax == self.old_xmax and ymin == self.old_ymin and ymax == self.old_ymax:
            return
        self.old_xmin, self.old_xmax, self.old_ymin, self.old_ymax = xmin, xmax, ymin, ymax

        # print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
        # print(" The button you used were: %s %s" % (eclick.button, erelease.button))
        self.hslice(ymin, ymax, std=rightClickMPLindex)
        self.vslice(xmin, xmax, std=rightClickMPLindex)
        self.fig.canvas.draw_idle()

    def toggle_selector(self, event):
        """
        Connected to key press events to turn on (a) or off (q) selector.

        :param event: key press event.
        :type event: matplotlib event

        :return: None
        """
        if event is None or event.key is None:
            return
        if event.key.lower() in ['up', 'down', 'left', 'right']:
            self.key_navigate_cuts(event.key.lower())
        # if event.key.lower()=='f':
        #    self.scroll_event('','forward')
        if event.key in ['Q', 'q'] and self.RectangleSelector.active:
            print(' RectangleSelector deactivated.')
            self.RectangleSelector.set_active(False)
        if event.key in ['A', 'a'] and not self.RectangleSelector.active:
            print(' RectangleSelector activated.')
            self.RectangleSelector.set_active(True)
        if event.key == 'j':
            self.toggle_log()

    def _radio_select(self, label):
        """
        Radio button effect.
        """
        self.radio.selected = label
        if label == 'data':
            self._set_values(self.data, **self.imag_options)
        elif label == 'd/d-' + self.data.dims[0]:
            self.der(0)
        elif label == 'd/d-' + self.data.dims[1]:
            self.der(1)
        elif label == 'int-' + self.data.dims[0]:
            self.int(0)
        elif label == 'int-' + self.data.dims[1]:
            self.int(1)

        for view in self.links:
            # have to manually change the fill
            for l, c in zip(view.radio.labels, view.radio.circles):
                if l.get_text() == label:
                    c.set_facecolor(view.radio.activecolor)
                else:
                    c.set_facecolor(view.radio.ax.get_axis_bgcolor())
                view.radio.ax.draw_artist(c)
            view.fig.canvas.blit(view.radio.ax.bbox)

    def link(self, view):
        """
        Link all actions in this view to the given view.
        """
        self.links.append(view)
        return

    def unlink(self, view):
        """
        Unlink actions in this view from controlling the given view.
        """
        if view in self.links:
            self.links.remove(view)
        return


@_available_to_user_plot
class View3d(View2d):
    """
    View 3D data by scrolling through 3rd dimension in a View2d plot.

    """

    def __init__(
        self,
        data,
        coords=None,
        dims=None,
        name=None,
        axes=None,
        use_uband=False,
        quiet=False,
        contour_levels=0,
        imag_options={},
        plot_options={'marker': '', 'ls': '-'},
        **indexers,
    ):
        r"""

        :param data: DataArray or array-like
            2D or 3D data values to be viewed.
        :param coords: dict-like
            Dictionary of Coordinate objects that label values along each dimension.
        :param dims: tuple
            Dimension names associated with this array.
        :param name: string
            Label used in legend. Empty or begining with '_' produces no legend label.
        :param dim: string, DataArray
            Dimension plotted on x-axis. If DataArray, must have same dims as data.
        :param axes: Axes instance
            The axes plotting is done in.
        :param quiet: bool
            Suppress printed messages.
        :param use_uband: bool
            Use uband for 1D slice plots instead of uerrorbar.
        :param contour_levels: int or np.ndarray
            Number of or specific levels used to draw black contour lines over the 2D image.
        :param imag_options: dict
            Key word arguments passed to the DataArray plot method (modified pcolormesh).
        :param plot_options: dict
            Key word arguments passed to plot or uerrorbar/uband. Color will be determined by cmap variable.

        :param \**indexers: dict
            Dictionary with keys given by dimension names and values given by
            arrays of coordinate index values.

        """
        # check args and make Dataset if needed
        if isinstance(data, DataArray):
            if coords or dims:
                raise ValueError("View cannot re-assign coords/dims to data that is already a DataArray")
            if name:
                data.name = name
            elif not data.name:  # require name
                name = 'viewdata'
                data.name = name
            else:
                name = data.name
            data = data
        elif isinstance(data, Dataset):
            if coords or dims:
                raise ValueError("View cannot re-assign coords/dims to data that is already a Dataset")
            data = data[list(data.data_vars.keys())]
        else:
            if name is None:
                name = 'viewdata'
            # must be regular gridded data
            data = DataArray(data, coords=coords, dims=dims, name=name)

        # pass on key words
        self._use_uband = use_uband
        self.plot_options = plot_options
        self.plot_cmap = plot_options.get('cmap', None)
        self.imag_options = imag_options

        # store basic inputs
        self.data3d = data

        # adjust inputs
        self.step = max(1, int(len(data[data.dims[2]]) // 100))
        self._index = int(self.data3d.shape[-1] // 2)

        View2d.__init__(
            self,
            data[:, :, self._index],
            axes=axes,
            use_uband=use_uband,
            contour_levels=contour_levels,
            imag_options=imag_options,
            plot_options=plot_options,
            **indexers,
        )
        self.axm.set_title('')  # remove xarray label of 3rd dimension's slice (we have our own dynamically updated one)

        self._set_3d()

        self.alarm = None
        self.widget = AxesWidget(self.axm)
        self.widget.connect_event('scroll_event', self._scrollx)
        self.widget.active = True
        printi("Scroll over 2D plot to change " + data.dims[2])
        self.fig.canvas.draw()

    def _scrollx(self, event):
        """
        Update viewer2d axes to show new 3d slice.
        """
        key = self.data3d.dims[2]
        ilim = self.data3d[key].shape[0]
        # change index
        if event.button == 'up':
            # ignore if already at limit
            if self._index == ilim - 1:
                return
            self._index += self.step
            if self._index > ilim - 1:
                self._index = ilim - 1
        elif event.button == 'down':
            if self._index == 0:
                return
            self._index -= self.step
            if self._index < 0:
                self._index = 0
        else:
            return

        if self.alarm:
            OMFITaux['rootGUI'].after_cancel(self.alarm)
            self.alarm = None

        self.alarm = OMFITaux['rootGUI'].after(10, self._set_3d)

    def _set_3d(self):
        self.set_3d(self._index, index=True)
        for v in self.links:
            try:
                v._scrollx(event)
            except Exception:
                pass

    def set_3d(self, x2, index=False, draw=True):
        """
        Set third dimension of view to value nearest to slice.

        :param x2: Slice in third dimension.  Type depends on value of `index`.
        :type x2: float or int

        :param index: Set True if x2 is the integer index
        :type index: bool
        :param draw: If True, redraw the canvas
        :type draw: bool

        :return: None

        """
        # nearest index
        key = self.data3d.dims[2]
        if index:
            indx = x2
        else:
            indx = np.abs(self.data[key] - x2).argmin()
        # update the central 2D plot
        self.set_data(self.data3d[:, :, indx], draw=False)
        ax = self.axm
        ax.texts = []
        ax.text(0.02, 0.95, '{:}={:6.2g}'.format(key, float(self.data3d[key].values[self._index])), transform=ax.transAxes)
        if draw:
            self.fig.canvas.draw()


@_available_to_user_plot
class DragPoints(object):
    r"""
    This class is used to define matplotlib draggable arrays

    :param yArray: location in the OMFIT tree for the y array

    :param xArray: location in the OMFIT tree for the x array

    :param eyArray: location in the OMFIT tree for the x error array

    :param exArray: location in the OMFIT tree for the y error array

    :param editY: allow dragging of points along Y axis

    :param editX: allow dragging of points along X axis

    :param exDelta: increments of exArray

    :param eyDelta: increments of eyArray

    :param editX: allow dragging of points along X axis

    :param sorted: keep points sorted in x

    :param continuous: draw continuously even while user is dragging (may be good to disable if takes long time)

    :param showOriginal: show original points

    :param func: a function with signature like `func(x,y,motion,fargs=[])`.
                 where:
                 * x : x coordinate of control points

                 * y : y coordinate of control points

                 * motion : True if the user has dragged a point

                 This function must return x\_, y\_, x, y where:

                 * x\_ : interpolating points between x coordinate of control points

                 * y\_ : interpolating points between y coordinate of control points

                 * x : x coordinate of control points

                 * y : y coordinate of control points

    :param fargs: arguments to the function

    :param cyArray: location in the OMFIT tree for the y interpolation array

    :param cxArray: location in the OMFIT tree for the x interpolation array

    :param onMove: function handle to call whenever control point is moved

    :param resize: boolean to whether update axes size when drag point gets to an edge for the figure

    :param show_hints: bool. Show a cornernote with tips for interaction.

    :param ax: Axes. Axes in which to plot.

    All other key word arguments passed to the matplotlib plot function.

    :return:
    """

    epsilon = 5

    def __init__(
        self,
        yArray,
        xArray=None,
        eyArray=None,
        exArray=None,
        editY=True,
        editX=True,
        exDelta=1,
        eyDelta=1,
        sorted=False,
        continuous=True,
        showOriginal=False,
        func=None,
        fargs=[],
        cyArray=None,
        cxArray=None,
        onMove=None,
        resize=False,
        show_hints=True,
        ax=None,
        **kwargs,
    ):
        self.xArray = xArray
        self.yArray = yArray
        self.exArray = exArray
        self.eyArray = eyArray
        self.cxArray = cxArray
        self.cyArray = cyArray

        if ax is not None:
            pyplot.sca(ax)

        # enable any key words for lines
        kw = copy.deepcopy(kwargs)
        for k in ['animated', 'label']:  # these are set by this class
            kw.pop(k, None)
        ckw = copy.deepcopy(kw)
        kw['linestyle'] = ''  # the interpolation line gets the linestyle
        kw.setdefault('marker', kw.pop('m', 'o'))

        if func == 'nearest':

            def func(x, y, motion, *fargs, **fkw):
                if self.cxArray is not None:
                    x_ = eval(self.cxArray)
                else:
                    x_ = np.linspace(min(x), max(x), 1001)
                try:
                    return x_, interp1d(x, y, kind='nearest')(x_), x, y
                except ValueError as _excp:
                    printe(repr(_excp))

        elif func == 'linear':

            def func(x, y, motion, *fargs, **fkw):
                if self.cxArray is not None:
                    x_ = eval(self.cxArray)
                else:
                    x_ = np.linspace(min(x), max(x), 1001)
                try:
                    return x_, interpolate.InterpolatedUnivariateSpline(x, y, k=1, *fargs, **fkw)(x_), x, y
                except ValueError as _excp:
                    printe(repr(_excp))

        elif func == 'spline':

            def func(x, y, motion, *fargs, **fkw):
                if self.cxArray is not None:
                    x_ = eval(self.cxArray)
                else:
                    x_ = np.linspace(min(x), max(x), 1001)
                try:
                    return x_, interpolate.InterpolatedUnivariateSpline(x, y, *fargs, **fkw)(x_), x, y
                except ValueError as _excp:
                    printe(repr(_excp))

        elif func == 'pchip':

            def func(x, y, motion, *fargs, **fkw):
                if self.cxArray is not None:
                    x_ = eval(self.cxArray)
                else:
                    x_ = np.linspace(min(x), max(x), 1001)
                try:
                    return x_, interpolate.PchipInterpolator(x, y, *fargs, **fkw)(x_), x, y
                except ValueError as _excp:
                    printe(repr(_excp))

        elif func == 'circular':
            sorted = False

            def func(x, y, motion, *fargs, **fkw):
                x[-1] = x[0]
                y[-1] = y[0]

                x0 = np.mean(x)
                y0 = np.mean(y)
                xm = max(x) - min(x)
                ym = max(y) - min(y)

                t = np.unwrap(np.arctan2((y - y0) / ym, (x - x0) / xm))
                if t[0] > t[1]:
                    t = -t

                if self.cxArray is not None:
                    x_ = eval(self.cxArray)
                else:
                    x_ = np.linspace(min(x), max(x), 1001)

                if self.cyArray is not None:
                    y_ = eval(self.cyArray)
                else:
                    y_ = np.linspace(min(y), max(y), 1001)

                t_ = np.linspace(min(t), max(t), len(y_))

                tckp = interpolate.splrep(t, x, k=3, per=True)
                xi = interpolate.splev(t_, tckp, ext=0)
                tckp = interpolate.splrep(t, y, k=3, per=True)
                yi = interpolate.splev(t_, tckp, ext=0)

                return xi, yi, x, y

        self.func = func
        self.onMove = onMove
        self.fargs = fargs
        self.sorted = sorted
        self.continuous = continuous
        self.motion = False
        self.resize = resize

        self.editX = editX
        self.editY = editY

        self.exDelta = exDelta
        self.eyDelta = eyDelta

        self.ax = pyplot.gca()
        self.ax.dp = self
        self._ind = None
        self.canvas = pyplot.gcf().canvas

        y = eval(self.yArray)
        if self.xArray is None:
            x = np.array(list(range(y.size)))
            self.editX = False
        else:
            x = eval(self.xArray)
        if self.exArray is None:
            ex = y * 0
        else:
            ex = eval(self.exArray)
        if self.eyArray is None:
            ey = y * 0
        else:
            ey = eval(self.eyArray)
        if self.cxArray is None:
            cx = y * 0
        else:
            cx = eval(self.cxArray)
            self.ax.set_xlabel(self.cxArray)
        if self.cyArray is None:
            cy = y * 0
        else:
            cy = eval(self.cyArray)
            self.ax.set_ylabel(self.cyArray)

        if self.func is not None:

            argspec = inspect.getfullargspec(self.func)

            if len(argspec.args) > 2 and argspec.args[2] == 'motion':
                x_, y_ = self.func(x, y, False, *self.fargs)[:2]
            else:
                # backward compatibility
                x_, y_ = self.func(x, y, *self.fargs)[:2]

            self.cline, *_ = self.ax.plot(x_, y_, animated=True, **ckw)
            if self.cxArray is not None:
                self.cline.set_marker('.')
                self.cline.set_markerfacecolor('k')
        if showOriginal:
            okw = copy.deepcopy(kw)
            okw.pop('color', None)
            okw.pop('c', None)
            self.line_orig, *_ = self.ax.plot(x, y, animated=True, label='Original', color='grey', **okw)
        self.line, *_ = self.ax.plot(x, y, animated=True, label='Control point', **kw)

        if self.onMove is not None:
            self.onMove(self.cline._xy[:, 0], self.cline._xy[:, 1], self.line._xy[:, 0], self.line._xy[:, 1])

        self.orig = {}
        self.orig['xArray'] = copy.deepcopy(x)
        self.orig['yArray'] = copy.deepcopy(y)
        self.orig['cxArray'] = copy.deepcopy(cx)
        self.orig['cyArray'] = copy.deepcopy(cy)
        self.orig['exArray'] = copy.deepcopy(ex)
        self.orig['eyArray'] = copy.deepcopy(ey)

        self.canvas.mpl_connect('draw_event', self.draw_callback)
        self.canvas.mpl_connect('button_press_event', self.button_press_callback)
        self.canvas.mpl_connect('key_press_event', self.key_press_callback)
        self.canvas.mpl_connect('button_release_event', self.button_release_callback)
        self.canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)

        txt = '<u>: undo\n<i>: insert node\n<d>: delete node\n'
        if self.eyArray is not None:
            txt += '<=>: increment ey\n'
            txt += '<->: decrement ey\n'
        if self.exArray is not None:
            txt += '<+>: increment ex\n'
            txt += '<_>: decrement ex\n'
        if show_hints:
            cornernote('', txt.strip())
        self.inhibitFunc = True

    def draw_callback(self, event=None):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)

        if hasattr(self, 'line_orig'):
            self.ax.draw_artist(self.line_orig)

        if self.sorted:
            index = np.argsort(self.line._xy[:, 0])
            self.line._xy[:, 0] = self.line._xy[index, 0]
            self.line._xy[:, 1] = self.line._xy[index, 1]

        if self.func is not None:
            if not self.inhibitFunc or (event is not None and hasattr(event, 'key') and event.key == 'u' and self.cyArray is not None):
                x_ = self.cline._xy[:, 0]
                if self.cxArray is not None:
                    x_ = np.squeeze(eval(self.cxArray))
                y_ = self.cline._xy[:, 1]
                if self.cyArray is not None:
                    y_ = np.squeeze(eval(self.cyArray))
                x = self.line._xy[:, 0]
                y = self.line._xy[:, 1]
                self.ax.draw_artist(self.cline)
            else:
                argspec = inspect.getfullargspec(self.func)
                if len(argspec.args) > 2 and argspec.args[2] == 'motion':
                    try:
                        x_, y_, x, y = self.func(self.line._xy[:, 0], self.line._xy[:, 1], self.motion, *self.fargs)
                    except Exception as _excp:
                        return
                else:
                    # backward compatibility
                    try:
                        x_, y_, x, y = self.func(self.line._xy[:, 0], self.line._xy[:, 1], *self.fargs)
                    except Exception as _excp:
                        return
            self.motion = False
            self.cline.set_data(x_, y_)
            if self.cxArray is not None:
                exec('%s=np.reshape(x_,%s.shape)' % (self.cxArray, self.cxArray))
            if self.cyArray is not None:
                exec('%s=np.reshape(y_,%s.shape)' % (self.cyArray, self.cyArray))
            self.line._xy[:, 0] = np.squeeze(x)
            self.line._xy[:, 1] = np.squeeze(y)
            self.ax.draw_artist(self.cline)

        self.ax.draw_artist(self.line)

        self.canvas.blit(self.ax.bbox)

        if self.onMove is not None:
            self.onMove(self.cline._xy[:, 0], self.cline._xy[:, 1], self.line._xy[:, 0], self.line._xy[:, 1])

    def get_ind_under_point(self, event):
        xy = self.line._xy
        xyt = self.line.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = np.sqrt((xt - event.x) ** 2 + (yt - event.y) ** 2)
        indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
        ind = indseq[0]
        if d[ind] >= self.epsilon:
            ind = None
        return ind

    def button_press_callback(self, event):
        self.inhibitFunc = True
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        self._ind = self.get_ind_under_point(event)

    def key_press_callback(self, event=None):
        if event is not None and not event.inaxes:
            return

        if event is None or event.key == 'u':
            self.line.set_data(copy.deepcopy(self.orig['xArray']), copy.deepcopy(self.orig['yArray']))
            if self.xArray is not None:
                exec(self.xArray + "=copy.deepcopy(self.orig['xArray'])")
            if self.yArray is not None:
                exec(self.yArray + "=copy.deepcopy(self.orig['yArray'])")
            if self.cxArray is not None:
                exec(self.cxArray + "=copy.deepcopy(self.orig['cxArray'])")
            if self.cyArray is not None:
                exec(self.cyArray + "=copy.deepcopy(self.orig['cyArray'])")
            if self.exArray is not None:
                exec(self.exArray + "=copy.deepcopy(self.orig['exArray'])")
            if self.eyArray is not None:
                exec(self.eyArray + "=copy.deepcopy(self.orig['eyArray'])")

        elif event.key == 'd':
            ind = self.get_ind_under_point(event)
            if ind is not None:
                printd('Deleted point #' + str(ind), topic='figure')
                tmp = np.array([tup for i, tup in enumerate(self.line._xy) if i != ind])
                if not self.editX:
                    tmp.T[0] = np.array(list(range(tmp.T[0].size)))
                self.line.set_data(tmp.T[0], tmp.T[1])
                if self.xArray is not None:
                    exec(self.xArray + '=tmp.T[0]')
                if self.yArray is not None:
                    exec(self.yArray + '=tmp.T[1]')
                if self.exArray is not None:
                    tmp = np.squeeze(eval(self.exArray)).tolist()
                    del tmp[ind]
                    tmp = np.array(tmp)
                    exec(self.exArray + '=tmp')
                if self.eyArray is not None:
                    tmp = np.squeeze(eval(self.eyArray)).tolist()
                    del tmp[ind]
                    tmp = np.array(tmp)
                    exec(self.eyArray + '=tmp')

        elif event.key == 'i':
            xysl = self.line.get_transform().transform(self.line._xy)
            try:
                xys = self.cline.get_transform().transform(self.cline._xy)
            except Exception:
                xys = xysl

            p = event.x, event.y

            for i in range(len(xys) - 1):

                s0 = xys[i]
                s1 = xys[i + 1]
                d = point_to_line(p[0], p[1], s0[0], s0[1], s1[0], s1[1])
                new_point = (event.xdata, event.ydata)
                condition = True

                if d <= self.epsilon and condition:
                    tmp = np.array(list(self.line._xy[: i + 1]) + [new_point] + list(self.line._xy[i + 1 :]))
                    if not self.editX:
                        tmp.T[0] = np.array(list(range(tmp.T[0].size)))
                    self.line.set_data(tmp.T[0], tmp.T[1])

                    if self.xArray is not None:
                        exec(self.xArray + '=tmp.T[0]')
                    if self.yArray is not None:
                        exec(self.yArray + '=tmp.T[1]')
                    if self.exArray is not None:
                        ex = np.hstack(
                            (
                                np.squeeze(eval(self.exArray))[: i + 1],
                                (np.squeeze(eval(self.exArray))[i] + np.squeeze(eval(self.exArray))[i + 1]) * 0.5,
                                np.squeeze(eval(self.exArray))[i + 1 :],
                            )
                        )
                        exec(self.exArray + '=ex')
                    if self.eyArray is not None:
                        ey = np.hstack(
                            (
                                np.squeeze(eval(self.eyArray))[: i + 1],
                                (np.squeeze(eval(self.eyArray))[i] + np.squeeze(eval(self.eyArray))[i + 1]) * 0.5,
                                np.squeeze(eval(self.eyArray))[i + 1 :],
                            )
                        )
                        exec(self.eyArray + '=ey')

                    break

        elif event.key == '=' and self.eyArray is not None:
            ind = self.get_ind_under_point(event)
            if ind is not None:
                exec(self.eyArray + '[ind]+=self.eyDelta')
                print('figure: Increased ey point #%d to %3.3f' % (ind, np.squeeze(eval(self.eyArray))[ind]))

        elif event.key == '-' and self.eyArray is not None:
            ind = self.get_ind_under_point(event)
            if ind is not None:
                exec(self.eyArray + '[ind]-=self.eyDelta')
                print('figure: Decreased ey point #%d to %3.3f' % (ind, np.squeeze(eval(self.eyArray))[ind]))

        elif event.key == '+' and self.exArray is not None:
            ind = self.get_ind_under_point(event)
            if ind is not None:
                exec(self.exArray + '[ind]+=self.exDelta')
                print('figure: Increased ex point #%d to %3.3f' % (ind, np.squeeze(eval(self.eyArray))[ind]))

        elif event.key == '_' and self.exArray is not None:
            ind = self.get_ind_under_point(event)
            if ind is not None:
                exec(self.exArray + '[ind]-=self.exDelta')
                print('figure: Decreased ex point #%d to %3.3f' % (ind, np.squeeze(eval(self.eyArray))[ind]))

        elif event.key == 'x':
            self.editX = not self.editX
            printi('drag X:' + str(self.editX))

        elif event.key == 'y':
            self.editY = not self.editY
            printi('drag Y:' + str(self.editY))

        OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")

        if self.onMove is not None:
            self.onMove(self.cline._xy[:, 0], self.cline._xy[:, 1], self.line._xy[:, 0], self.line._xy[:, 1])

        self.canvas.draw_idle()
        self.canvas.restore_region(self.background)
        self.draw_callback(event)

    def button_release_callback(self, event):
        if event.button != 1:
            return
        self._ind = None
        self.inhibitFunc = False
        OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
        pyplot.draw()

    def motion_notify_callback(self, event):
        if self._ind is None:
            return
        if event.inaxes is None:
            return
        if event.button != 1:
            return

        x, y = event.xdata, event.ydata
        tmp = self.line._xy
        if self.editX:
            tmp[self._ind][0] = x
        if self.editY:
            tmp[self._ind][1] = y
        self.line.set_data(tmp.T[0], tmp.T[1])

        if self.editY:
            pyplot.sca(self.ax)
            dy = np.diff(pyplot.ylim())[0] / 20.0
            if self.resize and y > pyplot.ylim()[1] - dy:
                pyplot.ylim(np.array(pyplot.ylim()) + np.array([0, dy]))
            if self.resize and y < pyplot.ylim()[0] + dy:
                pyplot.ylim(np.array(pyplot.ylim()) + np.array([-dy, 0]))

        if self.editX:
            pyplot.sca(self.ax)
            dx = np.diff(pyplot.xlim())[0] / 20.0
            if self.resize and x > pyplot.xlim()[1] - dx:
                pyplot.xlim(np.array(pyplot.xlim()) + np.array([0, dx]))
            if self.resize and x < pyplot.xlim()[0] + dx:
                pyplot.xlim(np.array(pyplot.xlim()) + np.array([-dx, 0]))

        if self.xArray is not None:
            exec(self.xArray + '=tmp.T[0]')
        if self.yArray is not None:
            exec(self.yArray + '=tmp.T[1]')

        self.motion = True

        self.canvas.restore_region(self.background)
        if self.continuous:
            self.draw_callback()
        else:
            self.ax.draw_artist(self.line)
            self.canvas.blit(self.ax.bbox)


@_available_to_user_plot
def editProfile(yi, xi=None, n=None, showOriginal=True, func='spline', onMove=None):
    """
    This function opens an interactive figure for convenient editing of profiles via spline

    :param yi: string whose `eval` yields the y data

    :param xi: string whose `eval` yields the x data

    :param n: number of control points

    :param showOriginal: plot original data

    :param func: interpolation function used to interpolate between control points 'linear', 'spline', 'pchip', 'circular'

    :param onMove: function to call when moving of control points occurs

    :param resize: boolean to whether update axes size when drag point gets to an edge for the figure

    :return: DragPoints object
    """
    from omfit_classes.utils_fit import autoknot

    if n is None:
        n = int(len(np.squeeze(eval(yi))) // 5)
    n = max([4, n])
    n = min([n, int(len(np.squeeze(eval(yi))) // 2)])

    if xi is None:
        OMFIT['scratch']['x_' + str(id(yi))] = np.linspace(0, len(np.squeeze(eval(yi))) - 1, len(np.squeeze(eval(yi))))
        xi = "OMFIT['scratch']['x_" + str(id(yi)) + "']"
    if func == 'linear':
        x0, y0 = autoknot(np.squeeze(eval(xi)), np.squeeze(eval(yi)), n, s=1, allKnots=True)
    elif func == 'pchip':
        tmp = interpolate.PchipInterpolator(np.squeeze(eval(xi)), np.squeeze(eval(yi)))

        class pchip(object):
            def __init__(self, x, y):
                pass

            def __call__(self, x0):
                return tmp(x0)

        x0, y0 = autoknot(np.squeeze(eval(xi)), np.squeeze(eval(yi)), n, mindist=1e-6, allKnots=True, userFunc=pchip)
    elif func == 'nearest':
        tmp = interpolate.interp1d(np.squeeze(eval(xi)), np.squeeze(eval(yi)), kind='nearest', bounds_error=False)

        class nearest(object):
            def __init__(self, x, y):
                pass

            def __call__(self, x0):
                return tmp(x0)

        x0, y0 = autoknot(np.squeeze(eval(xi)), np.squeeze(eval(yi)), n, mindist=1e-6, allKnots=True, userFunc=nearest)
    elif func == 'spline':
        x0, y0 = autoknot(np.squeeze(eval(xi)), np.squeeze(eval(yi)), n, s=3, allKnots=True)
    elif func == 'circular':
        t = np.cumsum(np.sqrt(gradient(np.squeeze(eval(xi))) ** 2 + gradient(np.squeeze(eval(yi))) ** 2))
        te = np.linspace(min(t), max(t), 1001)
        xe = interp1e(t, np.squeeze(eval(xi)), kind=3)(te)
        ye = interp1e(t, np.squeeze(eval(yi)), kind=3)(te)
        xe0 = np.mean(xe)
        ye0 = np.mean(ye)
        xem = max(xe) - min(xe)
        yem = max(ye) - min(ye)
        tec = np.cumsum(np.sqrt(gradient((xe - xe0) / xem) ** 2 + gradient((ye - ye0) / yem) ** 2))

        t0, x0 = autoknot(tec, (xe - xe0) / xem, n + 1, mindist=1e-6, s=5, allKnots=True)
        t1, y0 = autoknot(tec, (ye - ye0) / yem, n + 1, mindist=1e-6, s=5, allKnots=True)
        t_ = (t0 + t1) / 2.0

        x0 = interp1e(tec, xe)(t_)
        y0 = interp1e(tec, ye)(t_)

    OMFIT['scratch']['x0_' + str(id(x0))] = x0
    OMFIT['scratch']['y0_' + str(id(y0))] = y0

    if showOriginal:
        pyplot.plot(np.squeeze(eval(xi)), np.squeeze(eval(yi)))
    tmp = DragPoints(
        "OMFIT['scratch']['y0_" + str(id(y0)) + "']",
        "OMFIT['scratch']['x0_" + str(id(x0)) + "']",
        func=func,
        sorted=True,
        cxArray=xi,
        cyArray=yi,
        onMove=onMove,
        resize=False,
    )
    if func == 'circular':
        tmp.ax.set_aspect('equal')
    return tmp


@_available_to_user_plot
def cornernote(
    text='', root=None, device=None, shot=None, time=None, ax=None, fontsize='small', clean=True, remove=False, remove_specific=False
):
    """
    Write text at the bottom right corner of a figure

    :param text: text to appear in the bottom left corner

    :param root: * if '' append nothing
                 * if None append shot/time as from `OMFIT['MainSettings']['EXPERIMENT']`
                 * if OMFITmodule append shot/time as from `root['SETTINGS']['EXPERIMENT']`

    :param device: override device string (does not print device at all if empty string)

    :param shot: override shot string (does not print shot at all if empty string)

    :param time: override time string (does not print time at all if empty string)

    :param ax: axis to plot on

    :param fontsize: str or float. Sets font size of the Axes annotate method.

    :param clean: delete existing cornernote(s) from current axes before drawing a new cornernote

    :param remove: delete existing cornernote(s) and return before drawing any new ones

    :param remove_specific: delete existing cornernote(s) from current axes only if text matches the text that would be printed by the current call to cornernote() (such as identical shot, time, etc.)

    :return: Matplotlib annotate object
    """
    if ax is None:
        ax = pyplot.gca()

    if root is None:
        root = eval('OMFIT')
    if root and not isinstance(root, str):
        for location in ['MainSettings', 'SETTINGS']:
            if device is None:
                try:
                    device = root[location]['EXPERIMENT']['device']
                except Exception:
                    pass
            if shot is None:
                try:
                    shot = root[location]['EXPERIMENT']['shot']
                except Exception:
                    pass
            if time is None:
                try:
                    time = root[location]['EXPERIMENT']['time']
                except Exception:
                    pass
        text_ = []
        if device is not None and len(str(device)):
            text_.append(str(device))
        if shot is not None and len(str(shot)):
            text_.append('#' + str(shot))
        if time is not None and len(str(time)):
            text_.append(str(time) + ' ms')
        if len(text):
            text = ' '.join(text_) + ' : ' + text
        else:
            text = ' '.join(text_)
    elif isinstance(root, str) and not len(text):
        text = root

    # cornernote deletion options
    if remove_specific:
        # delete existing cornernote only if the text that would be written by this call matches exactly with existing text
        for textObj in ax.texts:
            if textObj.get_text() == text and textObj.get_label() == 'cornernote' and np.all(textObj._get_xy_display() == [0.98, 0.02]):
                textObj.remove()
        return  # for the specific version only, return without writing a new cornernote (assume you want to delete just one specific note and not recreate it exactly)
    else:
        # if not trying to remove a specific note, then scrub all notes but don't return
        if clean or remove:
            for textObj in ax.texts:
                if textObj.get_label() == 'cornernote':
                    textObj.remove()
        if remove:
            return  # the remove keyword should leave the corner blank (no cornernote visible)
        else:
            pass  # no return after clean because we want the default behavior to be: clear all notes and then write a fresh one

    return ax.annotate(text, xy=(0.98, 0.02), xycoords='figure fraction', fontsize=fontsize, ha='right', va='bottom', label='cornernote')


# Diagonal line to go with axhline and axvline
class axdline(matplotlib.pyplot.Line2D):

    """
    Draw a line based on its slope and y-intercept. Additional arguments are
    passed to the <matplotlib.lines.Line2D> constructor.

    From stackoverflow anser by ali_m: http://stackoverflow.com/a/14348481/6605826
    Originally named ABLine2D
    """

    def __init__(self, slope=1, intercept=0, *args, **kwargs):

        # get current axes if user has not specified them
        if not 'axes' in kwargs:
            if 'ax' in kwargs:  # translate ax into axes
                kwargs.update({'axes': kwargs['ax']})
                del kwargs['ax']
            else:
                kwargs.update({'axes': pyplot.gca()})
        ax = kwargs['axes']

        # init the line, add it to the axes
        super().__init__([], [], *args, **kwargs)
        self._slope = slope
        self._intercept = intercept
        ax.add_line(self)

        # cache the renderer, draw the line for the first time
        ax.figure.canvas.draw()
        self._update_lim(None)

        # connect to axis callbacks
        self.axes.callbacks.connect('xlim_changed', self._update_lim)
        self.axes.callbacks.connect('ylim_changed', self._update_lim)

    def _update_lim(self, event):
        """called whenever axis x/y limits change"""
        x = np.array(self.axes.get_xbound())
        y = (self._slope * x) + self._intercept

        self.set_data(x, y)
        try:
            self.axes.draw_artist(self)
        except AttributeError:
            printw('WARNING: could not update axdline artist! Diagonal lines might not display correctly!')


def square_subplots(nplots, ncol_max=np.inf, flip=False, sparse_column=True, just_numbers=False, identify=False, fig=None, **kw):
    r"""
    Creates a set of subplots in an approximate square, with a few empty subplots if needed

    :param nplots: int
        Number of subplots desired

    :param ncol_max: int
        Maximum number of columns to allow

    :param flip: bool
        True: Puts row 0 at the bottom, so every plot on the bottom row can accept an X axis label
        False: Normal plot numbering with row 0 at the top. The bottom row may be sparsely populated.

    :param sparse_column: bool
        Controls the arrangement of empty subplots.
        True: the last column is sparse. That is, all the empty plots will be in the last column. There will be at most
            one plot missing from the last row, and potentially several from the last column. The advantage is this
            provides plenty of X axes on the bottom row to accept labels. To get natural numbering of flattened
            subplots, transpose before flattening: axs.T.flatten(), or just use the 1D axsf array that's returned.
        False: the last row is sparse. All the empty plots will be in the last row. The last column will be missing at
            most one plot, but the last row may be missing several. This arrangement goes more smoothly with the
            numbering of axes after flattening.

    :param just_numbers: bool
        Don't create any axes, but instead just return the number of rows, columns, and empty subplots in the array.

    :param identify: bool
        For debugging: write the number (as flattened) and [row, col] coordinates of each subplot on the plot itself.
        These go in the center, in black. In the top left corner in red is the naive flattened count, which will appear
        on empty plots as well to show how wrong it is. In the bottom right corner in blue is the proper flattened count
        based on axsf.

    :param fig: Figure instance [optional]

    :param \**kw: keywords passed to pyplot.subplots when creating axes (like sharex, etc.)

    :return: (axs, axsf) or (nr, nc, on, empty)
        axs: 2d array of Axes instances. It is flipped vertically relative to normal axes output by pyplot.subplots,
            so the 0th row is the bottom. This is so the bottom row will be populated and can receive x axis labels.
        axsf: 1d array of Axes instances, leaving out the empty ones (they might not be in order nicely)
        empty: int: number of empty cells in axs.
            The first empty, if there is one, is [-1, -1] (top right), then [-1, -2] (top row, 2nd from the right), etc.
        nr: int: number of rows
        nc: int: number of columns
        on: 2d bool array: flags indicating which axes should be on (True) and which should be hidden/off (False)
    """

    kw.setdefault('sharex', True)
    kw['squeeze'] = False

    # Find number of columns, rows, and empty plots
    nc = int(nplots ** 0.5)
    nc = int(np.ceil(np.min([nc, ncol_max])))
    nr = int(np.ceil(nplots / float(nc)))
    empty = nr * nc - nplots

    # Make a rule for hiding the unused subplots
    on = np.ones((nr, nc), bool)
    for j in range(empty):
        if sparse_column:
            on[-(1 + j), -1] = False
        else:
            on[-1, -(1 + j)] = False

    # Map 1D indices to 2D indices (the hidden axes make this harder than it should be)
    offset = 0
    coords = [None] * nplots
    for j in range(nplots):
        jeff = j + offset
        ir = jeff // nc
        ic = np.mod(jeff, nc)
        if sparse_column:
            # Skip empties by incrementing offset
            while not on[ir, ic]:
                offset += 1
                jeff = j + offset
                ir = jeff // nc  # Find which row we're on.
                ic = np.mod(jeff, nc)  # Find which column we're on
        coords[j] = (ir, ic)

    if just_numbers:
        return nr, nc, on, empty

    # Make the plot grid
    if fig is None:
        fig, axs = pyplot.subplots(nr, nc, **kw)  # Default to new figure instead of pyplot.gcf()
        if flip:
            axs = axs[::-1, :]
        for axx in axs.flatten()[~on.flatten()]:
            axx.axis('off')
        axsf = axs.flatten()[on.flatten()]
    else:
        axs = np.empty((nr, nc), object)
        axsf = np.empty(nplots, object)
        sharex = None
        sharey = None
        for j in range(nplots):
            ir, ic = coords[j]

            if flip:
                slot = (nr - 1 - ir) * nc + ic + 1
            else:
                slot = ir * nc + ic + 1
            axx = fig.add_subplot(nr, nc, slot, sharex=sharex, sharey=sharey)
            axs[ir, ic] = axx
            axsf[j] = axx
            if kw.get('sharex', False):
                if ((ir < (nr - 1)) and (not flip)) or ((ir > 0) and flip):
                    # This is not the last row, so tradition demands we hide the axis labels
                    for tick in axx.xaxis.get_ticklabels():
                        tick.set_visible(False)
                if sharex is None:
                    sharex = axx  # If sharex=True, catch the first axes as the ones to share with
            if kw.get('sharey', False):
                if ic > 0:
                    # This is not the first column, so tradition demands we hide the axis labels
                    for tick in axx.yaxis.get_ticklabels():
                        tick.set_visible(False)
                if sharey is None:
                    sharey = axx

    # Write numbers on the subplots to identify them
    if identify:
        for j in range(nplots):
            ir, ic = coords[j]
            axx = axs[ir, ic]  # Get a reference to the subplot we're working with
            label = '{} [{}, {}]'.format(j, ir, ic)
            axx.text(0.5, 0.5, label, transform=axx.transAxes, ha='center', va='center')
            axsf[j].text(0.95, 0.05, str(j), transform=axsf[j].transAxes, ha='right', va='bottom', color='blue')
            if on[ir, ic]:
                axx.text(0.75, 0.75, 'ON', transform=axx.transAxes, ha='center', va='center', color='blue')
            else:
                if axx is not None:
                    axx.text(0.75, 0.75, 'OFF', transform=axx.transAxes, ha='center', va='center', color='red')

        for j in range(nc * nr):
            ax1 = axs.flatten()[j]
            axt = axs.T.flatten()[j]
            if ax1 is not None:
                ax1.text(0.05, 0.95, str(j), transform=ax1.transAxes, ha='left', va='top', color='red')
            if axt is not None:
                axt.text(0.95, 0.95, 'T' + str(j), transform=axt.transAxes, ha='right', va='top', color='green')

    return axs, axsf


try:
    from matplotlib.widgets import TextBox as _TextBox
except ImportError:

    class _TextBox(AxesWidget):
        """
        A GUI neutral text input box.
        For the text box to remain responsive you must keep a reference to it.
        The following attributes are accessible:

          *ax*
            The :class:`matplotlib.axes.Axes` the button renders into.
          *label*
            A :class:`matplotlib.text.Text` instance.
          *color*
            The color of the text box when not hovering.
          *hovercolor*
            The color of the text box when hovering.

        Call :meth:`on_text_change` to be updated whenever the text changes.
        Call :meth:`on_submit` to be updated whenever the user hits enter or
        leaves the text entry field.

        Taken from
        https://github.com/QuadmasterXLII/matplotlib/blob/2734051ec04b73280dad6a27f2003d1697d11195/lib/matplotlib/widgets.py
        which is in a pull request to matplotlib
        https://github.com/matplotlib/matplotlib/pull/5375/files

        smithsp added the set_val method to be merged into that pull request with
        https://github.com/QuadmasterXLII/matplotlib/pull/1
        """

        def __init__(self, ax, label, initial='', color='.95', hovercolor='1', label_pad=0.01):
            """
            Parameters:

            ax : matplotlib.axes.Axes
                The :class:`matplotlib.axes.Axes` instance the button
                will be placed into.
            label : str
                Label for this text box. Accepts string.
            initial : str
                Initial value in the text box
            color : color
                The color of the box
            hovercolor : color
                The color of the box when the mouse is over it
            label_pad : float
                the distance between the label and the right side of the textbox
            """
            from matplotlib.widgets import AxesWidget

            AxesWidget.__init__(self, ax)

            self.DIST_FROM_LEFT = 0.05

            self.params_to_disable = []
            for key in list(rcParams.keys()):
                if u'keymap' in key:
                    self.params_to_disable += [key]

            self.text = initial
            self.label = ax.text(-label_pad, 0.5, label, verticalalignment='center', horizontalalignment='right', transform=ax.transAxes)
            self.text_disp = self._make_text_disp(self.text)

            self.cnt = 0
            self.change_observers = {}
            self.submit_observers = {}

            # If these lines are removed, the cursor won't appear the first
            # time the box is clicked:
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)

            self.cursor_index = 0

            # Because this is initialized, _render_cursor
            # can assume that cursor exists.
            self.cursor = self.ax.vlines(0, 0, 0)
            self.cursor.set_visible(False)

            self.connect_event('button_press_event', self._click)
            self.connect_event('button_release_event', self._release)
            self.connect_event('motion_notify_event', self._motion)
            self.connect_event('key_press_event', self._keypress)
            self.connect_event('resize_event', self._resize)
            ax.set_navigate(False)
            ax.set_axis_bgcolor(color)
            ax.set_xticks([])
            ax.set_yticks([])
            self.color = color
            self.hovercolor = hovercolor

            self._lastcolor = color

            self.capturekeystrokes = False

        def _make_text_disp(self, string):
            return self.ax.text(
                self.DIST_FROM_LEFT, 0.5, string, verticalalignment='center', horizontalalignment='left', transform=self.ax.transAxes
            )

        def _rendercursor(self):
            # this is a hack to figure out where the cursor should go.
            # we draw the text up to where the cursor should go, measure
            # and save its dimensions, draw the real text, then put the cursor
            # at the saved dimensions

            widthtext = self.text[: self.cursor_index]
            no_text = False
            if widthtext == "" or widthtext == " " or widthtext == "  ":
                no_text = widthtext == ""
                widthtext = ","

            wt_disp = self._make_text_disp(widthtext)

            self.ax.figure.canvas.draw()
            bb = wt_disp.get_window_extent()
            inv = self.ax.transData.inverted()
            bb = inv.transform(bb)
            wt_disp.set_visible(False)
            if no_text:
                bb[1, 0] = bb[0, 0]
            # hack done
            self.cursor.set_visible(False)

            self.cursor = self.ax.vlines(bb[1, 0], bb[0, 1], bb[1, 1])
            self.ax.figure.canvas.draw()

        def _notify_submit_observers(self):
            for cid, func in self.submit_observers.items():
                func(self.text)

        def _release(self, event):
            if self.ignore(event):
                return
            if event.canvas.mouse_grabber != self.ax:
                return
            event.canvas.release_mouse(self.ax)

        def _keypress(self, event):
            if self.ignore(event):
                return
            if self.capturekeystrokes:
                key = event.key

                if len(key) == 1:
                    self.text = self.text[: self.cursor_index] + key + self.text[self.cursor_index :]
                    self.cursor_index += 1
                elif key == "right":
                    if self.cursor_index != len(self.text):
                        self.cursor_index += 1
                elif key == "left":
                    if self.cursor_index != 0:
                        self.cursor_index -= 1
                elif key == "home":
                    self.cursor_index = 0
                elif key == "end":
                    self.cursor_index = len(self.text)
                elif key == "backspace":
                    if self.cursor_index != 0:
                        self.text = self.text[: self.cursor_index - 1] + self.text[self.cursor_index :]
                        self.cursor_index -= 1
                elif key == "delete":
                    if self.cursor_index != len(self.text):
                        self.text = self.text[: self.cursor_index] + self.text[self.cursor_index + 1 :]

                self.text_disp.set_text(self.text)
                self._rendercursor()
                self._notify_change_observers()
                if key == "enter":
                    self._notify_submit_observers()

        def set_val(self, val):
            newval = str(val)
            if self.text == newval:
                return
            self.text = newval
            self.text_disp.set_text(self.text)
            self._rendercursor()
            self._notify_change_observers()
            self._notify_submit_observers()

        def _notify_change_observers(self):
            for cid, func in self.change_observers.items():
                func(self.text)

        def begin_typing(self, x):
            self.capturekeystrokes = True
            # disable command keys so that the user can type without
            # command keys causing figure to be saved, etc
            self.reset_params = {}
            for key in self.params_to_disable:
                self.reset_params[key] = rcParams[key]
                rcParams[key] = []

        def stop_typing(self):
            notifysubmit = False
            # because _notify_submit_users might throw an error in the
            # user's code, we only want to call it once we've already done
            # our cleanup.
            if self.capturekeystrokes:
                # since the user is no longer typing,
                # reactivate the standard command keys
                for key in self.params_to_disable:
                    rcParams[key] = self.reset_params[key]
                notifysubmit = True
            self.capturekeystrokes = False
            self.cursor.set_visible(False)
            self.ax.figure.canvas.draw()
            if notifysubmit:
                self._notify_submit_observers()

        def position_cursor(self, x):
            # now, we have to figure out where the cursor goes.
            # approximate it based on assuming all characters the same length
            if len(self.text) == 0:
                self.cursor_index = 0
            else:
                bb = self.text_disp.get_window_extent()

                trans = self.ax.transData
                inv = self.ax.transData.inverted()
                bb = trans.transform(inv.transform(bb))

                text_start = bb[0, 0]
                text_end = bb[1, 0]

                ratio = (x - text_start) / (text_end - text_start)

                if ratio < 0:
                    ratio = 0
                if ratio > 1:
                    ratio = 1

                self.cursor_index = int(len(self.text) * ratio)

            self._rendercursor()

        def _click(self, event):
            if self.ignore(event):
                return
            if event.inaxes != self.ax:
                self.stop_typing()
                return
            if not self.eventson:
                return
            if event.canvas.mouse_grabber != self.ax:
                event.canvas.grab_mouse(self.ax)
            if not (self.capturekeystrokes):
                self.begin_typing(event.x)
            self.position_cursor(event.x)

        def _resize(self, event):
            self.stop_typing()

        def _motion(self, event):
            if self.ignore(event):
                return
            if event.inaxes == self.ax:
                c = self.hovercolor
            else:
                c = self.color
            if c != self._lastcolor:
                self.ax.set_axis_bgcolor(c)
                self._lastcolor = c
                if self.drawon:
                    self.ax.figure.canvas.draw()

        def on_text_change(self, func):
            """
            When the text changes, call this *func* with event.
            A connection id is returned which can be used to disconnect.
            """
            cid = self.cnt
            self.change_observers[cid] = func
            self.cnt += 1
            return cid

        def on_submit(self, func):
            """
            When the user hits enter or leaves the submision box, call this
            *func* with event.
            A connection id is returned which can be used to disconnect.
            """
            cid = self.cnt
            self.submit_observers[cid] = func
            self.cnt += 1
            return cid

        def disconnect(self, cid):
            """remove the observer with connection id *cid*"""
            try:
                del self.observers[cid]
            except KeyError:
                pass

    matplotlib.widgets.TextBox = _TextBox

if __name__ == '__main__':
    from pylab import figure, imshow
    import uncertainties

    x = np.linspace(0, 2 * np.pi, 20)
    y = np.linspace(0, 3 * np.pi, 20)
    s = np.sin(x)
    z = []
    for i in range(10):
        z.append(np.sin(x) + i)
    z = np.array(z)

    xx, yy = np.meshgrid(x, y)
    zz = np.sin(xx) * np.cos(yy)
    xerr = abs(0.1 * np.random.random(x.shape) * x)
    serr = abs(0.1 * np.random.random(x.shape) * s)
    X = uncertainties.unumpy.uarray(x, xerr)
    S = uncertainties.unumpy.uarray(s, serr)
    figure('sin')
    pyplot.plot(x, s)
    figure('multi-sin')
    plotc(x, z.T)
    ax = pyplot.gca()
    XKCDify(ax, xaxis_loc=0)
    draw()
    map_HBS_to_RGB(np.array([1]), np.array([2]), np.array([0]))
    paths = contourPaths(x, y, zz, [-0.75, 0, 0.75])
    fig = figure('pcolormesh')
    ax = fig.add_subplot(121)
    pcolor2(xx, yy, zz)
    ax2 = fig.add_subplot(122, sharey=ax, sharex=ax)
    im = blur_image(zz, 3)
    ax2.imshow(im, extent=(min(x), max(x), min(y), max(y)), origin='lower')
    set_fontsize(fontsize='+10')
    plot_equality_lims(ax=ax2)
    autofmt_sharey()
    hardcopy('/tmp/%s/test_hardcopy.pdf' % os.environ['USER'])
    fig = figure('uerrorbar')
    ax = fig.add_subplot(211)
    uerrorbar(X, S, ax=ax)
    ax2 = fig.add_subplot(212, sharex=ax)
    uerrorbar(X, S, ax=ax2)
    plot_equality(X, S, ax=ax2)
    autofmt_sharex()
    fig = figure('uband')
    uband(X, S)
