print('External imports...')

from omfit_classes import unix_os as os
import sys

# the OMFITsrc variable stores the directory where OMFIT is running from
OMFITsrc = os.path.abspath(os.path.dirname(__file__) + os.sep + '..')

# load base utilities
from omfit_classes.utils_base import *

# this defines the command line that is shown when OMFIT is used at terminal
# Note that setting ps1 is also required to avoid crashing with Matplotlib v1.4 (matplotlib bug)
sys.ps1 = 'OMFIT >>> '

# monkey patching of np `array`, `asarray` and `asanyarray` to fix array behavior with OMFIT dynamic expressions
from numpy.core.multiarray import array as _array


def array(object, dtype=None, copy=True, order=None, subok=False, ndmin=0):
    object = evalExpr(object)
    return _array(object, dtype=dtype, copy=copy, order=order, subok=subok, ndmin=ndmin)


array.__doc__ = _array.__doc__

from numpy.core.fromnumeric import asarray as _asarray


def asarray(a, dtype=None, order=None):
    a = evalExpr(a)
    return _asarray(a, dtype=dtype, order=order)


asarray.__doc__ = _asarray.__doc__

from numpy.core.fromnumeric import asanyarray as _asanyarray


def asanyarray(a, dtype=None, order=None):
    a = evalExpr(a)
    return _asanyarray(a, dtype=dtype, order=order)


asanyarray.__doc__ = _asanyarray.__doc__

from numpy.core import multiarray as _multiarray

_multiarray.array = array
_multiarray.asarray = asarray
_multiarray.asanyarray = asanyarray

from numpy.core import fromnumeric as _fromnumeric

_fromnumeric.array = array
_fromnumeric.asarray = asarray
_fromnumeric.asanyarray = asanyarray

from numpy.core import shape_base as _shape_base

_shape_base.array = array
_shape_base.asarray = asarray
_shape_base.asanyarray = asanyarray

# Monkey patch gradient so it doesn't complain about 0-d arrays as not being scalars
import numpy.lib.function_base
from numpy.lib.function_base import gradient as _gradient


def gradient(f, *args, **kwargs):
    return _gradient(f, *[x * 1.0 for x in args], **kwargs)


gradient.__doc__ = _gradient.__doc__
numpy.lib.function_base._gradient = _gradient
numpy.lib.function_base.gradient = gradient

import numpy as np
from numpy.lib.recfunctions import *
import bisect

warnings.simplefilter('ignore', np.RankWarning)
np.array = array
np.asarray = asarray
np.asanyarray = asanyarray
np.gradient = gradient

# matplotlib (if matplotlib module was already loaded, keep the same rc parameters)
if 'matplotlib' in sys.modules:
    if 'matplotlib.pyplot' in sys.modules:
        raise ImportError('Because OMFIT monkey patches matplotlib figure and ' 'axes, you must import OMFIT before pyplot')
    _rc_updates = copy.deepcopy(sys.modules['matplotlib'].rcParams)
    import matplotlib

else:
    import matplotlib

    _rc_updates = {
        'figure.facecolor': 'white',
        'axes.formatter.use_mathtext': True,
        'legend.labelspacing': 0.2,
        'legend.fontsize': 'medium',
        'savefig.format': 'pdf',
        'pdf.fonttype': 42,
        'ps.useafm': True,
        'axes.formatter.limits': [-3, 3],
        'axes.formatter.useoffset': False,
        'keymap.fullscreen': 'f',
        'keymap.home': 'h',
        'keymap.back': '',
        'keymap.forward': '',
        'keymap.pan': 'p',
        'keymap.zoom': 'z',
        'keymap.save': 's',
        'keymap.grid': 'g',
        'keymap.yscale': 'l',
        'keymap.xscale': 'L',
        'mathtext.default': 'regular',
        'savefig.transparent': True,
    }

if hasattr(matplotlib, 'get_data_path'):
    _mpl_font_path = os.sep.join([matplotlib.get_data_path(), 'fonts', 'ttf'])
else:
    _mpl_font_path = os.sep.join([matplotlib.rcParams['datapath'], 'fonts', 'ttf'])
if not os.path.exists(os.sep.join([_mpl_font_path, 'Muli.ttf'])) and os.access(_mpl_font_path, os.W_OK):
    _font_path = os.sep.join([OMFITsrc, 'extras', 'graphics', 'fonts'])
    for _f in os.listdir(_font_path):
        _mpl_fname = os.sep.join([_mpl_font_path, _f])
        if not os.path.exists(_mpl_fname):
            os.system('cp %s %s' % (os.sep.join([_font_path, _f]), _mpl_fname))

# remove fontCache file if produced before Muli got installed (previous lines added)
import matplotlib.font_manager

_fontcachefn = getattr(matplotlib.font_manager, '_fmcache', '')
if os.path.exists(_fontcachefn) and os.path.getmtime(_fontcachefn) < 1586983275:
    print('Removing font cache to get updated fonts')
    os.unlink(_fontcachefn)
if os.environ.get('OMFIT_NO_GUI', '0') == '1' or not os.environ.get("DISPLAY"):
    matplotlib.use('agg')
else:
    matplotlib.use('TkAgg')
# ===========================
import matplotlib.axes


def _imag_arg(arg):
    if np.any(np.iscomplex(arg)):
        return np.imag(arg)
    else:
        return arg


def _real_arg(arg):
    if np.any(np.iscomplex(arg)):
        return np.real(arg)
    else:
        return arg


class dummyLegend(object):
    def draggable(*args, **kw):
        pass

    def set_draggable(*args, **kw):
        pass


# Avoid red text in console
import logging

with quiet_environment():
    logging.getLogger('matplotlib.legend').warning('')

_orig_matplotlib_axes_Axes = matplotlib.axes.Axes


class Axes(_orig_matplotlib_axes_Axes):
    def plot(self, *args, **kw):
        linestyles = list(matplotlib.lines.lineStyles.keys())
        newargs = list(map(_real_arg, args))
        lines1 = _orig_matplotlib_axes_Axes.plot(self, *newargs, **kw)
        lines2 = []
        if np.any([np.any(np.iscomplex(arg).flat) for arg in args]):
            newargs = list(map(_imag_arg, args))
            lines2 = _orig_matplotlib_axes_Axes.plot(self, *newargs, **kw)
            for l1, l2 in zip(lines1, lines2):
                l2.set_color(l1.get_color())
                ils = linestyles.index(l1.get_linestyle())
                l2.set_linestyle(linestyles[ils + 1])
                l2.set_label(r'$\Im$ ' + l1.get_label())
                l1.set_label(r'$\Re$ ' + l1.get_label())
            pyplot.gca().legend(ncol=max(1, len(self.lines) // 6))
        self.callbacks.connect('xlim_changed', self.axes_downsample)
        return lines1 + lines2

    def legend(self, *args, **kw):
        r"""
        Modified matplotlib legend method.

        :param handles: list of artists
            Artists (lines, patches) to be added to the legend

        :param labels: list of strings
            Label to use in the legend

        :param no_duplicates: bool
            Keeps only one of each unique legend label and deletes the others

        :param alpha_reset: float (optional)
            If not None, sets transparency of legend items to specific value.
            alpha_reset=1.0 is useful if there are many transparent symbols
            but you want one full opacity symbol to represent the group.

        :param extra_note: string
            Add text to the bottom of the legend with no marker

        :param text_same_color: bool
            Change the color of the text to match the plot object.

        :param hide_markers: bool
            Hide legend markers or lines and just show legend text.

        :param draggable: bool
            Make the legend draggable.

        :param \**kw: keyword arguments passed to original matplotlib legend method

        :return: legend object

        Original legend docstring:
        """
        kwargs = kw
        no_duplicates = kw.pop('no_duplicates', False)
        alpha_reset = kw.pop('alpha_reset', None)
        extra_note = kw.pop('extra_note', None)
        text_same_color = kw.pop('text_same_color', False)
        hide_markers = kw.pop('hide_markers', False)
        draggable = kw.pop('draggable', True)

        import matplotlib.legend as mleg

        logging.getLogger("matplotlib").setLevel(logging.CRITICAL)  # Prevent sub-critical warnings from displaying
        if hasattr(mleg, '_parse_legend_args'):
            handles, labels, extra_args, kwargs = mleg._parse_legend_args([self], *args)
            if not handles:
                return dummyLegend()
        else:
            # Begin copy from matplotlib.axes._axes.legend
            handlers = kwargs.get('handler_map', {}) or {}

            # Support handles and labels being passed as keywords.
            handles = kwargs.pop('handles', None)
            labels = kwargs.pop('labels', None)

            if (handles is not None or labels is not None) and len(args):
                warnings.warn("You have mixed positional and keyword arguments; some input will be discarded.")

            # If got both handles and labels as kwargs, make same length
            if handles and labels:
                handles, labels = list(zip(*list(zip(handles, labels))))

            elif handles is not None and labels is None:
                labels = [handle.get_label() for handle in handles]
                for label, handle in zip(labels[:], handles[:]):
                    if label.startswith('_'):
                        warnings.warn(
                            'The handle {!r} has a label of {!r} '
                            'which cannot be automatically added to the legend.'.format(handle, label)
                        )
                        labels.remove(label)
                        handles.remove(handle)

            elif labels is not None and handles is None:
                # Get as many handles as there are labels.
                handles = [handle for handle, label in zip(self._get_legend_handles(handlers), labels)]

            # No arguments - automatically detect labels and handles.
            elif len(args) == 0:
                handles, labels = self.get_legend_handles_labels(handlers)
                if not handles:
                    return dummyLegend()

            # One argument. User defined labels - automatic handle detection.
            elif len(args) == 1:
                (labels,) = args
                # Get as many handles as there are labels.
                handles = [handle for handle, label in zip(self._get_legend_handles(handlers), labels)]

            # Two arguments:
            #   * user defined handles and labels
            elif len(args) == 2:
                handles, labels = args

            else:
                raise TypeError('Invalid arguments to legend.')
            # End copy from matplotlib.axes._axes.legend

        # Modify list of handles and labels in legend to prevent duplicate entries
        if no_duplicates:
            i = np.arange(len(labels))
            legend_idxs = np.array([])
            unique_labels = tolist(set(labels))
            for ul in unique_labels:
                legend_idxs = np.append(legend_idxs, [i[np.array(labels) == ul][0]])
            handles = [handles[int(idx)] for idx in legend_idxs]
            labels = [labels[int(idx)] for idx in legend_idxs]

        # Add extra note
        if extra_note is not None:
            for note in tolist(extra_note):
                handles += [matplotlib.patches.Patch(alpha=0)]
                labels += [note]

        # Reset alpha (opacity) value of legend markers to a specified value
        if alpha_reset is not None:
            # Because deepcopy doesn't work on legend handles, we have to:
            # 1. Go through all the handles on the plot, backup the original alpha value, and set the new one
            # 2. Draw the legend
            # 3. Restore all the alpha values on the plot to their original value
            alphass = [None] * len(handles)  # Make a list to hold lists of saved alpha values
            for k, handle in enumerate(handles):  # Loop through the legend entries
                try:  # If handle was a simple list of parts, then this will work
                    alphass[k] = handle.get_alpha()  # This probably only works for a plot with a few simple line plots
                    handle.set_alpha(alpha_reset)
                except AttributeError:
                    alphas = [None] * len(handle)  # Make a list to hold the alphas of the pieces of this legend entry
                    for i, h in enumerate(handle):
                        # Loop through the pieces of this legend entry (there could be a line and a marker, for example)
                        try:  # If handle was a simple list of parts, then this will work
                            alphas[i] = h.get_alpha()
                            h.set_alpha(alpha_reset)
                        except AttributeError:
                            # If handle was a list of parts which themselves were made up of smaller sub-components,
                            # then we must go one level deeper still. This was needed for the output of errorbar() and
                            # may not be needed for simpler plot objects
                            alph = [None] * len(h)
                            for j, hh in enumerate(h):
                                alph[j] = hh.get_alpha()
                                hh.set_alpha(alpha_reset)
                            alphas[i] = alph  # Save the list of alpha values for the sub-components of this piece of
                            #                   this legend entry
                    alphass[k] = alphas  # Save the list of alpha values for the pieces of this legend entry

        if len(handles):
            kw['labels'] = labels
            if hide_markers:
                # Make invisible dummy handles to replace the real legend handles
                kw['handles'] = [matplotlib.patches.Patch(alpha=0)] * len(handles)
                kw['handlelength'] = 0
                kw['handletextpad'] = 0
            else:
                kw['handles'] = handles
            the_legend = _orig_matplotlib_axes_Axes.legend(self, **kw)
        else:
            the_legend = None

        if the_legend is None:
            # if plot is empty, legend() returns `None`
            # This hack prevents raising an error if one does:
            # >> legend().draggable(True)
            printd('legend monkey match returning dummyLegend')
            return dummyLegend()

        if hide_markers:
            for item in the_legend.legendHandles:
                item.set_visible(False)

        if text_same_color:
            for handle, leg_text in zip(handles, the_legend.get_texts()):
                h0 = tolist(handle)[0]
                if hasattr(h0, 'get_color'):
                    handle_color = h0.get_color()  # Works for lines, errorbars, ubands, etc.
                elif hasattr(h0, 'get_facecolor'):
                    handle_color = h0.get_facecolor()  # Works for scatter
                elif hasattr(h0, 'get_edgecolor'):
                    handle_color = h0.get_edgecolor()
                else:
                    handle_color = None  # Give up and leave it alone.
                if handle_color is not None:
                    # Handle color needs to be sanitized because some objects return things like [[1, 0, 0, 1]]
                    if isinstance(handle_color, str):
                        pass  # Already good
                    elif isinstance(handle_color[0], str):
                        handle_color = handle_color[0]
                    else:
                        handle_color = np.squeeze(handle_color)
                    leg_text.set_color(handle_color)

        if alpha_reset is not None:
            # Now we have to restore the original alpha values
            for k, handle in enumerate(handles):  # Loop through legend items to restore original alphas on the plot
                try:
                    handle.set_alpha(alphass[k])
                except AttributeError:
                    for i, h in enumerate(handle):  # Loop through pieces of this legend item to restore alpha values
                        try:
                            h.set_alpha(alphass[k][i])
                        except AttributeError:
                            for j, hh in enumerate(h):
                                # Loop through sub-components of this piece of this legend item to restore alpha values
                                hh.set_alpha(alphass[k][i][j])

        if draggable and the_legend:
            try:
                if hasattr(the_legend, 'set_draggable'):
                    the_legend.set_draggable(True)
                else:
                    the_legend.draggable(True)
            except Exception:
                pass

        return the_legend

    legend.__doc__ += _orig_matplotlib_axes_Axes.legend.__doc__

    def set_downsampling(self, npts):
        """
        Set the minimum number of points before downsampling

        :param npts: If plotting more than npts points in a given curve, then downsample the line
        """
        self.npts = npts

    def axes_downsample(self, ax):
        """
        Down-sample original data in each Line2D object in lines
        (either x or y must be numerical and monotonically increasing)
        """
        npts = getattr(self, 'npts', 1e4)
        for line in ax.lines:
            if not isinstance(line.get_xdata(), np.ndarray):
                continue  # odd bug with xdata just a float in uerrorbar
            if ((not hasattr(line, '_xinit') and len(line.get_xdata()) > npts)) or (hasattr(line, '_xinit') and line._xinit is not None):
                # do not downsample arrays that are strings, boolean, or object type
                for check in [np.asarray(line.get_xdata()).dtype.name, np.asarray(line.get_ydata()).dtype.name]:
                    if 'string' in check or check == 'object' or check == 'bool':
                        line._xinit = None
                        return
                if not hasattr(line, '_xinit'):
                    tmpx = np.sign(np.diff(line.get_xdata()))
                    tmpy = np.sign(np.diff(line.get_ydata()))
                    if np.all(tmpx == tmpx[0]) or np.all(tmpy == tmpy[0]):
                        line.downsample(npts)
                else:
                    line.downsample(npts)

    def format_xydata(self, xy, theaxis):
        """
        Override default matplotlib data formatter to make fixed-width cursor coordinates in the toolbar

        Changing the length of the cursor's message box causes the size of the figure window to change,
        which is distracting. The figure itself may try to stay centered in the window, so it might jump
        around, or it might change size as the cursor moves.

        Formats using "g" give a consistent number of sig-figs, not a consistent string length, hence the
        if/else business with "f" and "e" format codes.
        """

        isdate = isinstance(theaxis.get_major_formatter(), matplotlib.dates.AutoDateFormatter)
        if isdate:
            # return (default_formatter or theaxis.get_major_formatter().format_data_short)(xy)
            return matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S')(xy)
        elif (abs(xy) >= 1e5) or ((xy != 0) and (abs(xy) <= 1e-3)):
            return f'{xy:+12.5e}'
        else:
            return f'{xy:+12.5f}'

    def format_xdata(self, x):
        return self.format_xydata(x, self.xaxis)

    def format_ydata(self, y):
        return self.format_xydata(y, self.yaxis)

    def format_coord(self, x, y):
        """
        Modified message in toolbar to alert users when a plot is interactive.
        """
        prefix = ''
        if hasattr(self, 'is_interactive') and self.is_interactive:
            prefix = 'Interactive, '
        return prefix + _orig_matplotlib_axes_Axes.format_coord(self, x, y)


_orig_matplotlib_legend_Legend = matplotlib.legend.Legend
if hasattr(_orig_matplotlib_legend_Legend, 'set_draggable'):
    orig_draggable = _orig_matplotlib_legend_Legend.set_draggable
else:
    orig_draggable = _orig_matplotlib_legend_Legend.draggable


def draggable(self, state=True, use_blit=False, update="loc"):
    # This monkey patch changes the default value of state from None (toggle) to True (turn on draggability).
    return orig_draggable(self, state=state, use_blit=use_blit, update=update)


_orig_matplotlib_legend_Legend.draggable = draggable
matplotlib.axes.Axes = Axes

if compare_version(matplotlib.__version__, '3.0') > 0:
    # retain matplotlib ability to add an axes using the same arguments
    # as a previous axes currently reuses the earlier instance.
    from matplotlib.figure import AxesStack
    import matplotlib.cbook as cbook

    def _get(self, key):
        """
        Return the Axes instance that was added with *key*.
        If it is not present, return *None*.
        """
        item = dict(self._elements).get(key)
        if item is None:
            return None
        return item[1]

    def _add(self, key, a):
        """
        Add Axes *a*, with key *key*, to the stack, and return the stack.

        If *key* is unhashable, replace it by a unique, arbitrary object.

        If *a* is already on the stack, don't add it again, but
        return *None*.
        """
        # All the error checking may be unnecessary; but this method
        # is called so seldom that the overhead is negligible.
        if not isinstance(a, Axes):
            raise ValueError("second argument, {!r}, is not an Axes".format(a))
        try:
            hash(key)
        except TypeError:
            key = object()

        a_existing = self.get(key)
        if a_existing is not None:
            cbook.Stack.remove(self, (key, a_existing))
            cbook._warn_external("key {!r} already existed; Axes is being replaced".format(key))
            # I don't think the above should ever happen.

        if a in self:
            return None
        self._ind += 1
        return cbook.Stack.push(self, (key, (self._ind, a)))

    AxesStack.add = _add
    AxesStack.get = _get

# ===========================
from matplotlib import pyplot

matplotlib.style.use('classic')
matplotlib.rcParams.update(_rc_updates)
matplotlib.rcParams['interactive'] = True
matplotlib.rcParams['tk.window_focus'] = True

import colorsys

from numpy import nan, NaN
import pylab
import scipy

try:
    import dask.array  # Need to do this before monkeypatching np
except ImportError:
    pass
from scipy.interpolate import *

# patch interp1d so that it can handle a single data point
_interp1d = interp1d


class interp1d(_interp1d):
    __doc__ = _interp1d.__doc__

    def __init__(self, x, y, kind='linear', axis=-1, copy=True, bounds_error=None, fill_value=np.nan, assume_sorted=False, **kw):
        if np.atleast_1d(x).size == 1:
            x = np.atleast_1d(x)
            x = np.array([x[0] - np.finfo(float).epsneg, x[0], x[0] + np.finfo(float).eps])
            y = np.atleast_1d(y)
            y = np.array([y[0], y[0], y[0]])
        _interp1d.__init__(
            self, x, y, kind=kind, axis=axis, copy=copy, bounds_error=bounds_error, fill_value=fill_value, assume_sorted=assume_sorted, **kw
        )


_Interpolator1D = interp1d
interpolate.interp1d = interp1d
scipy.interpolate.interp1d = interp1d
scipy.interpolate.polyint._Interpolator1D = interp1d

from scipy import interpolate
from scipy import integrate
from scipy import optimize
from scipy import ndimage
import scipy.io.netcdf as netcdf
from scipy import constants

# --------------
import uncertainties
import uncertainties.unumpy as unumpy
from uncertainties.unumpy import nominal_values, std_devs, uarray
from uncertainties import ufloat, ufloat_fromstr

_isnan = np.isnan


def isnan(x, *args):
    try:
        return _isnan(x, *args)
    except TypeError:
        return unumpy.isnan(x, *args)


isnan.__doc__ = _isnan.__doc__
np.isnan = isnan
pylab.isnan = isnan
scipy.isnan = isnan

_isinf = np.isinf


def isinf(x, *args):
    try:
        return _isinf(x, *args)
    except TypeError:
        return unumpy.isinf(x, *args)


isinf.__doc__ = _isinf.__doc__
np.isinf = isinf
pylab.isinf = isinf
scipy.isinf = isinf

_isfinite = np.isfinite


def isfinite(x, *args):
    try:
        return _isfinite(x, *args)
    except TypeError:
        if np.iterable(x):
            return np.reshape(list(map(bool, 1 - (isinf(x.flat) | np.isnan(x.flat)))), x.shape)
        else:
            return bool(1 - (isinf(x) | np.isnan(x)))


isfinite.__doc__ = _isfinite.__doc__
np.isfinite = isfinite
pylab.isfinite = isfinite
scipy.isfinite = isfinite

# ------------------------------------
# data
if os.environ['USER'] in ['eldond']:
    warnings.filterwarnings('ignore', category=ImportWarning)
    warnings.filterwarnings('always', category=UserWarning, message='.*ModuleNotFoundError.*')
import netCDF4
import csv
import fortranformat

import zipfile
import collections

# strings
import re
import fnmatch
import string
import textwrap
import ast
import difflib

# exec
import subprocess
import multiprocessing

# system
import platform
import signal
import atexit
import shutil
import glob
import struct
import stat
import filecmp

# python
import weakref
import types
import copy
import itertools
import functools
import gc
import importlib
import unittest

# remote
import socket

# time
import datetime
import dateutil
import time

# buffers
import ctypes

import io

# introspection
import inspect
import traceback
import pydoc

# web
import requests
import json

if os.name == 'nt':
    try:
        import wexpect as pexpect
    except Exception as _excp:
        pexpect = None
        warnings.warn('No `wexepect` support: ' + repr(_excp))
else:
    try:
        import pexpect
    except Exception as _excp:
        pexpect = None
        warnings.warn('No `pexepect` support: ' + repr(_excp))

try:
    import pidly
except Exception as _excp:
    pidly = None
    warnings.warn('No `pidly` support: ' + repr(_excp))

try:
    with warnings.catch_warnings(record=True) as w:
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        import boto3
        from boto3.dynamodb.conditions import Attr
        import decimal
except Exception as _excp:
    boto3 = None
    warnings.warn('No `boto3` support: ' + repr(_excp))

try:
    import pandas

    warnings.filterwarnings('ignore', message="Pandas doesn't allow columns to be created via a new attribute name*")
except Exception as _excp:
    pandas = None
    warnings.warn('No `pandas` support! DataArray and Dataset not will not be available : ' + repr(_excp))

try:
    with warnings.catch_warnings(record=True) as w:
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        warnings.filterwarnings('ignore', category=FutureWarning)
        import xarray
except Exception as _excp:
    try:
        import xray as xarray

        warnings.warn("Package `xray` is deprecated. Please upgrade to `xarray`")
    except Exception:
        xarray = None
        warnings.warn('No `xarray` support! DataArray and Dataset not will not be available : ' + repr(_excp))

try:
    import lmfit
except Exception as _excp:
    lmfit = None
    warnings.warn('No `lmfit` support: ' + repr(_excp))

try:
    import gpr1dfusion
except Exception as _excp:
    gpr1dfusion = None
    warnings.warn('No `gpr1dfusion` support! Corresponding Gaussian Process functions will not be available : ' + repr(_excp))
try:
    import jedi
except Exception as _excp:
    jedi = None
    warnings.warn('No jedi support')
else:
    try:
        jedi.preload_module('numpy', 'pylab')
    except Exception:
        # purge jedi cache directory if failing to load cache files
        if os.path.exists(jedi.settings.cache_directory):
            shutil.rmtree(jedi.settings.cache_directory, ignore_errors=True)
        jedi.preload_module('numpy', 'pylab')

from omfit_classes.utils_base import summarize_installed_packages

print('Sanity check Python packages required by OMFIT')
_rc, _ = summarize_installed_packages(required=True, optional=False, verbose=False)
if _rc:
    summarize_installed_packages(required=True, optional=False, verbose=True)
    print(
        '''
Some Python package required by OMFIT is missing. You could:
1. Update the python environment following these instructions: https://omfit.io/install.html
2. Run an older version of OMFIT that does not have this requirement
'''
    )
    exit(_rc)
