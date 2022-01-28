"""Detectors for capturing images, slices and single pixels of a beam.

The camera types are split into two categories (CCDs and ComplexCameras) based on the
mathematical implementation shown in :ref:`camera_equations`.
"""

import logging
from abc import ABC
import numbers

import numpy as np

from .general import MaskedDetector
from .compute import (
    field_pixel_output,
    ccd_pixel_output,
    field_line_output,
    ccd_line_output,
    field_camera_output,
    ccd_output,
)
from .compute.camera import (
    CameraWorkspace,
    CCDWorkspace,
    CCDLineWorkspace,
    FieldCameraWorkspace,
    FieldLineWorkspace,
    FieldPixelWorkspace,
)
from ..env import warn
from ..parameter import float_parameter
from ..utilities.misc import find_nearest, is_iterable


LOGGER = logging.getLogger(__name__)


class Camera(MaskedDetector, ABC):
    """Base camera class.

    Parameters
    ----------
    name : str
        Unique name of the camera.

    node : :class:`.OpticalNode`
        Node at which to detect.

    w0_scaled : bool
        Flag indicating whether the :math:`x`, :math:`y` axes
        should be scaled to the waist-size of the beam parameter
        at `node`.

    dtype : :class:`numpy.dtype` or str
        The data-type of the pixels.

    shape : tuple
        Dimensions of the camera image.
    """

    def __init__(self, name, node, w0_scaled, dtype, shape, **kwargs):
        MaskedDetector.__init__(self, name, node, dtype=dtype, shape=shape, **kwargs)
        self.__w0_scaled = w0_scaled in (True, 1, "True", "true", "Y", "y")
        self._nr = self.node.space.nr if self.node.space is not None else 1.0
        self._changing_check = set()

    @property
    def needs_trace(self):
        return True

    @property
    def w0_scaled(self):
        """Flag for whether the x and y co-ordinates have been scaled by the waist-size
        of the beam parameter at the detection node.

        :getter: Returns `True` if x and y have been scaled by the beam waist, `False` otherwise.
        """
        return self.__w0_scaled

    @property
    def scaled_xdata(self):
        """Coordinate data in the x-axis scaled to metres.

        Equivalent to ``xdata`` if :attr:`.Camera.w0_scaled` is False. Otherwise this is
        ``xdata`` multiplied by the tangential waist size as measured at the node.
        """
        x = self.xdata
        if not self.w0_scaled:
            return x

        qx = self._model.beam_trace()[self.node].qx
        return x * qx.w0

    @property
    def scaled_ydata(self):
        """Coordinate data in the y-axis scaled to metres.

        Equivalent to ``ydata`` if :attr:`.Camera.w0_scaled` is False. Otherwise this is
        ``ydata`` multiplied by the sagittal waist size as measured at the node.
        """
        y = self.ydata
        if not self.w0_scaled:
            return y

        qy = self._model.beam_trace()[self.node].qy
        return y * qy.w0

    def _set_plotting_variables(self, trace_info):
        trace_info["w0_scaled"] = self.w0_scaled


class Image:
    r"""Data structure representation of an image.

    Parameters
    ----------
    xlim : sequence or scalar
        Limits of the x-dimension of the image. If a single number is given then
        this will be computed as :math:`x_{\mathrm{lim}} = [-|x|, +|x|]`.

    ylim : sequence or scalar
        Limits of the y-dimension of the image. If a single number is given then
        this will be computed as :math:`y_{\mathrm{lim}} = [-|y|, +|y|]`.

    npts : int
        Number of points for both the x and y axes.

    dtype : str or dtype
        Data type of the image to pass to NumPy for array creation.
    """

    def __init__(self, xlim, ylim, npts, dtype):
        xl, xu = _check_limits(xlim)
        yl, yu = _check_limits(ylim)

        self.__set_x_space(npts, lower=xl, upper=xu)
        self.__set_y_space(npts, lower=yl, upper=yu)

        self.__set_out_grid(dtype)

    def __set_x_space(self, npts, lower=None, upper=None):
        npts = int(npts)
        if not npts > 0:
            raise ValueError("Number of points must be a positive integer.")

        if lower is None:
            lower = self._x[0]
        if upper is None:
            upper = self._x[-1]

        self._x = np.linspace(lower, upper, npts, dtype=np.float64)

    def __set_y_space(self, npts, lower=None, upper=None):
        npts = int(npts)
        if not npts > 0:
            raise ValueError("Number of points must be a positive integer.")

        if lower is None:
            lower = self._y[0]
        if upper is None:
            upper = self._y[-1]

        self._y = np.linspace(lower, upper, npts, dtype=np.float64)

    def __set_out_grid(self, dtype=None):
        if dtype is None:
            dtype = self._out.dtype

        self._out = np.zeros(self.resolution, dtype=dtype)

    @property
    def xlim(self):
        """The limits of the x coordinate data.

        :getter: Returns a tuple of ``(xmin, xmax)``.
        :setter: Sets the x-axis limits.
        """
        return self._x[0], self._x[-1]

    @xlim.setter
    def xlim(self, value):
        xl, xu = _check_limits(value)
        self.__set_x_space(self.npts, xl, xu)

    @property
    def ylim(self):
        """The limits of the y coordinate data.

        :getter: Returns a tuple of ``(ymin, ymax)``.
        :setter: Sets the y-axis limits.
        """
        return self._y[0], self._y[-1]

    @ylim.setter
    def ylim(self, value):
        yl, yu = _check_limits(value)
        self.__set_y_space(self.npts, yl, yu)

    @property
    def xdata(self):
        """The array of data points for the x-axis.

        :getter: Returns a copy of the :class:`numpy.ndarray` containing the x-axis points.
        """
        return self._x.copy()

    @property
    def ydata(self):
        """The array of data points for the y-axis.

        :getter: Returns a copy of the :class:`numpy.ndarray` containing the y-axis points.
        """
        return self._y.copy()

    @property
    def npts(self):
        """Number of pixels in each axis.

        :getter: Returns the number of pixels in each axis.
        :setter: Sets the number of pixels in each axis.
        """
        return self._x.shape[0]

    @npts.setter
    def npts(self, value):
        self.__set_x_space(value)
        self.__set_y_space(value)
        self.__set_out_grid()

    @property
    def resolution(self):
        """The resolution of the image.

        Currently this is always square (i.e. number of points in both axes
        always equal).

        :getter: Returns the tuple ``(xpts, ypts)``.
        """
        return self.npts, self.npts

    def at(self, x=None, y=None):
        """Retrieves a slice or single pixel of the output image.

        Parameters
        ----------
        x : scalar, optional
            Value indicating where to take a y-slice of the image or,
            if used in conjunction with `y`, which pixel to return. Defaults
            to `None`.

        y : scalar, optional
            Value indicating where to take a x-slice of the image or,
            if used in conjunction with `x`, which pixel to return. Defaults
            to `None`.

        magnitude : bool, optional
            Returns the amplitude of the detected field if `True`. Otherwise
            returns the full complex description.

        Returns
        -------
        out : :class:`numpy.ndarray` or float
            Either a slice of the image or a single pixel at the specified co-ordinates.
        """
        if x is None and y is None:
            return self._out.copy()

        if x is None:
            nearest_idx = find_nearest(self._y, y, index=True)
            values = self._out[nearest_idx][:]
            return values.copy()

        if y is None:
            nearest_idx = find_nearest(self._x, x, index=True)
            values = self._out[:, nearest_idx]
            return values.copy()

        nearest_indices = (
            find_nearest(self._x, x, index=True),
            find_nearest(self._y, y, index=True),
        )
        values = self._out[nearest_indices]
        return values.copy()

    def _set_plotting_variables(self, trace_info):
        trace_info["xlim"] = self.xlim
        trace_info["ylim"] = self.ylim


class ScanLine:
    r"""Data structure representation of a slice of an image.

    Parameters
    ----------
    x : scalar or None
        The x coordinate of the slice.

    y : scalar or None
        The y coordinate of the slice.

    xlim : scalar or size two sequence
        The limits of the x-axis scan lines. A single number gives
        :math:`x_{\mathrm{axis}} \in [-|x|, +|x|]`, or a tuple of size two gives
        :math:`x_{\mathrm{axis}} \in [x[0], x[1]]`.

    ylim : scalar or array-like
        The limits of the y-axis scan lines. A single number gives
        :math:`y_{\mathrm{axis}} \in [-|y|, +|y|]`, or a tuple of size two gives
        :math:`y_{\mathrm{axis}} \in [y[0], y[1]]`.

    npts : int
        Number of points in slice axis.

    dtype : str or dtype
        Data type of the slice to pass to NumPy for array creation.
    """

    def __init__(self, npts, dtype, x=None, y=None, xlim=None, ylim=None):
        if xlim is not None and ylim is not None:
            raise ValueError("Both xlim and ylim cannot be specified.")

        if xlim is not None:
            self.__direction = "x"
        elif ylim is not None:
            self.__direction = "y"
        else:
            raise ValueError("One of xlim or ylim must be specified.")

        if self.direction == "x":
            xl, xu = _check_limits(xlim)
            self._x = np.linspace(xl, xu, npts, dtype=np.float64)

            if x is not None:
                warn(
                    f"Ignoring x = {repr(x)} argument passed to ScanLine as xlim "
                    f"has been specified."
                )

            if y is None:
                self._y = 0
            else:
                self._y = y
        else:
            yl, yu = _check_limits(ylim)
            self._y = np.linspace(yl, yu, npts, dtype=np.float64)

            if y is not None:
                warn(
                    f"Ignoring y = {repr(y)} argument passed to ScanLine as ylim "
                    f"has been specified."
                )

            if x is None:
                self._x = 0
            else:
                self._x = x

        self._out = np.zeros(npts, dtype=dtype)

    def __set_ax_space(self, npts, lower=None, upper=None):
        npts = int(npts)
        if not npts > 0:
            raise ValueError("Number of points must be a positive integer.")

        if self.direction == "x":
            ax = self._x
        else:
            ax = self._y

        if lower is None:
            lower = ax[0]
        if upper is None:
            upper = ax[-1]

        ax = np.linspace(lower, upper, npts, dtype=np.float64)
        if self.direction == "x":
            self._x = ax
        else:
            self._y = ax

    def __set_out_line(self, dtype=None):
        if dtype is None:
            dtype = self._out.dtype

        self._out = np.zeros(self.npts, dtype=dtype)

    @property
    def direction(self):
        """The slice axis - i.e. 'x' for x-axis, 'y' for y-axis.

        :getter: Returns a string determining the slice axis (read-only).
        """
        return self.__direction

    @property
    def x(self):
        """The x co-ordinate of the slice.

        If :attr:`.ScanLine.direction` is 'x' then this will return ``None``.

        :getter: Returns the x coordinate of the slice.
        :setter: Sets the x coordinate of the slice.
        """
        if self.direction == "x":
            return None

        return self._x

    @x.setter
    def x(self, value):
        if self.direction == "x":
            raise RuntimeError(
                "Cannot set x-position of scan line when the slice is in the x-axis."
            )

        self._x = float(value)

    @property
    def y(self):
        """The y co-ordinate of the slice.

        If :attr:`ScanLine.direction` is 'y' then this will return ``None``.

        :getter: Returns the y coordinate of the slice.
        :setter: Sets the y coordinate of the slice.
        """
        if self.direction == "y":
            return None

        return self._y

    @y.setter
    def y(self, value):
        if self.direction == "y":
            raise RuntimeError(
                "Cannot set y-position of scan line when the slice is in the y-axis."
            )

        self._y = float(value)

    @property
    def xlim(self):
        """The limits of the slice in the x-axis.

        If :attr:`ScanLine.direction` is 'y' then this will return ``None``.

        :getter: Returns a tuple of ``(xmin, xmax)``.
        :setter: Sets the x-axis limits.
        """
        if self.direction == "y":
            return None

        return self._x[0], self._x[-1]

    @xlim.setter
    def xlim(self, value):
        if self.direction == "y":
            raise RuntimeError("Cannot set x-axis limits for scan line in the y-axis.")

        xl, xu = _check_limits(value)
        self.__set_ax_space(self.npts, xl, xu)

    @property
    def ylim(self):
        """The limits of the slice in the y-axis.

        If :attr:`ScanLine.direction` is 'x' then this will return ``None``.

        :getter: Returns a tuple of ``(ymin, ymax)``.
        :setter: Sets the y-axis limits.
        """
        if self.direction == "x":
            return None

        return self._y[0], self._y[-1]

    @ylim.setter
    def ylim(self, value):
        if self.direction == "x":
            raise RuntimeError("Cannot set y-axis limits for scan line in the x-axis.")

        yl, yu = _check_limits(value)
        self.__set_ax_space(self.npts, yl, yu)

    @property
    def xdata(self):
        """The numeric value(s) of the x coordinate.

        If :attr:`ScanLine.direction` is 'x' then this will be a copy of the array of
        values, otherwise it is a single value equivalent to :attr:`.ScanLine.x`.

        :getter: The x coordinate value(s). Read-only.
        """
        if self.direction == "x":
            return self._x.copy()

        return self._x

    @property
    def ydata(self):
        """The numeric value(s) of the y coordinate.

        If :attr:`ScanLine.direction` is 'y' then this will be a copy of the array of
        values, otherwise it is a single value equivalent to :attr:`.ScanLine.y`.

        :getter: The y coordinate value(s). Read-only.
        """
        if self.direction == "y":
            return self._y.copy()

        return self._y

    @property
    def npts(self):
        """Number of pixels in the scanning axis.

        :getter: Returns the number of pixels in the slice axis.
        :setter: Sets the number of pixels in the slice axis.
        """
        if self.direction == "x":
            return self._x.shape[0]

        return self._y.shape[0]

    @npts.setter
    def npts(self, value):
        self.__set_ax_space(value)
        self.__set_out_line()

    def _set_plotting_variables(self, trace_info):
        trace_info["xlim"] = self.xlim
        trace_info["ylim"] = self.ylim
        trace_info["xdata"] = self.xdata
        trace_info["ydata"] = self.ydata
        trace_info["direction"] = self.direction


class Pixel:
    r"""Data structure representation of a pixel of an image.

    Parameters
    ----------
    x : scalar
        The x co-ordinate of the pixel.

    y : scalar
        The y co-ordinate of the pixel.

    dtype : str or dtype
        Data type of the pixel.
    """

    def __init__(self, x, y, dtype):
        self.x = x
        self.y = y

        if dtype == np.complex128:
            self._out = complex(0, 0)
        else:
            self._out = 0.0

    @property
    def x(self):
        """The x coordinate of the pixel.

        :getter: Returns the x coordinate of the pixel.
        :setter: Sets the x coordinate of the pixel.
        """
        return self._x

    @x.setter
    def x(self, value):
        self._x = float(value)

    @property
    def xdata(self):
        """Equivalent to :attr:`.Pixel.x`.

        :getter: Returns the x coordinate of the pixel. Read-only version.
        """
        return self._x

    @property
    def y(self):
        """The y coordinate of the pixel.

        :getter: Returns the y coordinate of the pixel.
        :setter: Sets the y coordinate of the pixel.
        """
        return self._y

    @y.setter
    def y(self, value):
        self._y = float(value)

    @property
    def ydata(self):
        """Equivalent to :attr:`.Pixel.y`.

        :getter: Returns the y coordinate of the pixel. Read-only version.
        """
        return self._y

    def _set_plotting_variables(self, trace_info):
        trace_info["xdata"] = self.xdata
        trace_info["ydata"] = self.ydata


class CCDCamera(Camera, ABC):
    """Abstract type for cameras which detect pixel intensity.

    Parameters
    ----------
    name : str
        Unique name of the camera.

    node : :class:`.OpticalNode`
        Node at which to detect.

    w0_scaled : bool, optional; default: True
        Flag indicating whether the :math:`x`, :math:`y` axes
        should be scaled to the waist-size of the beam parameter
        at `node`.
    """

    def __init__(self, name, node, w0_scaled=True, **kwargs):
        if isinstance(self, Image):
            shape = self._x.shape[0], self._y.shape[0]
        elif isinstance(self, ScanLine):
            if self.direction == "x":
                shape = self._x.shape
            else:
                shape = self._y.shape
        elif isinstance(self, Pixel):
            shape = None
        else:
            raise TypeError(
                "Bug detected! CCDCamera does not derive from Image, "
                "ScanLine or Pixel."
            )

        Camera.__init__(self, name, node, w0_scaled, np.float64, shape, **kwargs)


class CCD(CCDCamera, Image):
    r"""Camera for detecting the full image of the beam in terms of the intensity.

    Get the unscaled x and y coordinate data via :attr:`.Image.xdata` and :attr:`.Image.ydata`,
    respectively.

    Parameters
    ----------
    name : str
        Unique name of the camera.

    node : :class:`.OpticalNode`
        Node at which to detect.

    xlim : sequence or scalar
        Limits of the x-dimension of the image. If a single number is given then
        this will be computed as :math:`x_{\mathrm{lim}} = [-|x|, +|x|]`.

    ylim : sequence or scalar
        Limits of the y-dimension of the image. If a single number is given then
        this will be computed as :math:`y_{\mathrm{lim}} = [-|y|, +|y|]`.

    npts : int
        Number of points in both axes.

    w0_scaled : bool, optional; default: True
        Flag indicating whether the :math:`x`, :math:`y` axes
        should be scaled to the waist-size of the beam parameter
        at `node`.
    """

    def __init__(self, name, node, xlim, ylim, npts, w0_scaled=True):
        Image.__init__(self, xlim, ylim, npts, dtype=np.float64)
        CCDCamera.__init__(self, name, node, w0_scaled)

    @property
    def npts(self):
        return super().npts

    @npts.setter
    def npts(self, value):
        super(CCD, self.__class__).npts.fset(self, value)
        self._update_dtype_shape(self.resolution)

    def _get_workspace(self, sim):
        ws = CCDWorkspace(self, sim, self._out)
        ws.set_output_fn(ccd_output)
        return ws

    def _set_plotting_variables(self, trace_info):
        CCDCamera._set_plotting_variables(self, trace_info)
        Image._set_plotting_variables(self, trace_info)


class CCDScanLine(CCDCamera, ScanLine):
    r"""Camera for detecting a slice of the beam in terms of the intensity.

    The :attr:`.ScanLine.direction` (i.e. axis of slice) is determined
    from which of `xlim` or `ylim` is specified.

    Get the unscaled x and y coordinate data via :attr:`.ScanLine.xdata` and
    :attr:`.ScanLine.ydata`, respectively.

    Parameters
    ----------
    name : str
        Unique name of the camera.

    node : :class:`.OpticalNode`
        Node at which to detect.

    npts : int
        Number of points in slice axis.

    x : scalar or None; default: None
        The x coordinate of the slice. If ylim is given and this is
        not specified then defaults to zero. If xlim is given and
        this is also specified then it is ignored.

    y : scalar or None; default: None
        The y coordinate of the slice. If xlim is given and this is
        not specified then defaults to zero. If ylim is given and
        this is also specified then it is ignored.

    xlim : scalar or size two sequence; default: None
        The limits of the x-axis scan lines. A single number gives
        :math:`x_{\mathrm{axis}} \in [-|x|, +|x|]`, or a tuple of size two gives
        :math:`x_{\mathrm{axis}} \in [x[0], x[1]]`.

    ylim : scalar or array-like; default: None
        The limits of the y-axis scan lines. A single number gives
        :math:`y_{\mathrm{axis}} \in [-|y|, +|y|]`, or a tuple of size two gives
        :math:`y_{\mathrm{axis}} \in [y[0], y[1]]`.

    w0_scaled : bool, optional; default: True
        Flag indicating whether the :math:`x`, :math:`y` axes
        should be scaled to the waist-size of the beam parameter
        at `node`.
    """

    def __init__(
        self, name, node, npts, x=None, y=None, xlim=None, ylim=None, w0_scaled=True
    ):
        label = "Pixel intensity"
        unit = r"W m$^{-2}$"

        ScanLine.__init__(
            self, x=x, y=y, xlim=xlim, ylim=ylim, npts=npts, dtype=np.float64
        )
        CCDCamera.__init__(self, name, node, w0_scaled, label=label, unit=unit)

    @property
    def npts(self):
        return super().npts

    @npts.setter
    def npts(self, value):
        super(CCDScanLine, self.__class__).npts.fset(self, value)
        self._update_dtype_shape(self.npts)

    def _get_workspace(self, sim):
        ws = CCDLineWorkspace(self, sim, self._out)
        ws.set_output_fn(ccd_line_output)
        return ws

    def _set_plotting_variables(self, trace_info):
        CCDCamera._set_plotting_variables(self, trace_info)
        ScanLine._set_plotting_variables(self, trace_info)


class CCDPixel(CCDCamera, Pixel):
    """Camera for detecting a single pixel of the beam in terms of the intensity.

    Get the unscaled x and y coordinate data via :attr:`.Pixel.xdata` and
    :attr:`.Pixel.ydata`, respectively.

    Parameters
    ----------
    name : str
        Unique name of the camera.

    node : :class:`.OpticalNode`
        Node at which to detect.

    x : scalar, optional; default: 0
        The x co-ordinate of the pixel.

    y : scalar, optional; default: 0
        The y co-ordinate of the pixel.

    w0_scaled : bool, optional; default: True
        Flag indicating whether the :math:`x`, :math:`y` axes
        should be scaled to the waist-size of the beam parameter
        at `node`.
    """

    def __init__(self, name, node, x=0, y=0, w0_scaled=True):
        label = "Pixel intensity"
        unit = r"W m$^{-2}$"
        Pixel.__init__(self, x, y, dtype=np.float64)
        CCDCamera.__init__(self, name, node, w0_scaled, label=label, unit=unit)

    def _get_workspace(self, sim):
        ws = CameraWorkspace(self, sim)
        ws.set_output_fn(ccd_pixel_output)
        return ws

    def _set_plotting_variables(self, trace_info):
        CCDCamera._set_plotting_variables(self, trace_info)
        Pixel._set_plotting_variables(self, trace_info)


@float_parameter("f", "Frequency", units="Hz")
class ComplexCamera(Camera, ABC):
    """Abstract type for cameras which detect pixel amplitude and phase.

    Parameters
    ----------
    name : str
        Unique name of the camera.

    node : :class:`.OpticalNode`
        Node at which to detect.

    f : scalar, optional; default: 0
        Field frequency offset from the carrier to detect.

    w0_scaled : bool, optional; default: True
        Flag indicating whether the :math:`x`, :math:`y` axes
        should be scaled to the waist-size of the beam parameter
        at `node`.
    """

    def __init__(self, name, node, f=0, w0_scaled=True):
        if isinstance(self, Image):
            shape = self._x.shape[0], self._y.shape[0]
        elif isinstance(self, ScanLine):
            if self.direction == "x":
                shape = self._x.shape
            else:
                shape = self._y.shape
        elif isinstance(self, Pixel):
            shape = None
        else:
            raise TypeError(
                "Bug detected! ComplexCamera does not derive from Image, "
                "ScanLine or Pixel."
            )

        Camera.__init__(self, name, node, w0_scaled, dtype=np.complex128, shape=shape)

        self.f = f
        self._changing_check = set((self.f,))


@float_parameter("f", "Frequency", units="Hz")
class FieldCamera(ComplexCamera, Image):
    r"""Camera for detecting the full image of the beam in terms of amplitude and phase.

    Get the unscaled x and y coordinate data via :attr:`.Image.xdata` and :attr:`.Image.ydata`,
    respectively.

    Parameters
    ----------
    name : str
        Unique name of the camera.

    node : :class:`.OpticalNode`
        Node at which to detect.

    xlim : sequence or scalar
        Limits of the x-dimension of the image. If a single number is given then
        this will be computed as :math:`x_{\mathrm{lim}} = [-|x|, +|x|]`.

    ylim : sequence or scalar
        Limits of the y-dimension of the image. If a single number is given then
        this will be computed as :math:`y_{\mathrm{lim}} = [-|y|, +|y|]`.

    npts : int
        Number of points in both axes.

    f : scalar, optional; default: 0
        Field frequency offset from the carrier to detect.

    w0_scaled : bool, optional; default: True
        Flag indicating whether the :math:`x`, :math:`y` axes
        should be scaled to the waist-size of the beam parameter
        at `node`.
    """

    def __init__(self, name, node, xlim, ylim, npts, f=0, w0_scaled=True):
        Image.__init__(self, xlim, ylim, npts, dtype=np.complex128)
        ComplexCamera.__init__(self, name, node, f=f, w0_scaled=w0_scaled)

    @property
    def npts(self):
        return super().npts

    @npts.setter
    def npts(self, value):
        super(FieldCamera, self.__class__).npts.fset(self, value)
        self._update_dtype_shape(self.resolution)

    def _get_workspace(self, sim):
        ws = FieldCameraWorkspace(self, sim, self._out)
        ws.set_output_fn(field_camera_output)
        return ws

    def _set_plotting_variables(self, trace_info):
        Image._set_plotting_variables(self, trace_info)
        ComplexCamera._set_plotting_variables(self, trace_info)


@float_parameter("f", "Frequency", units="Hz")
class FieldScanLine(ComplexCamera, ScanLine):
    r"""Camera for detecting a slice of the beam in terms of amplitude and phase.

    The :attr:`.ScanLine.direction` (i.e. axis of slice) is determined
    from which of `xlim` or `ylim` is specified.

    Get the unscaled x and y coordinate data via :attr:`.ScanLine.xdata` and
    :attr:`.ScanLine.ydata`, respectively.

    Parameters
    ----------
    name : str
        Unique name of the camera.

    node : :class:`.OpticalNode`
        Node at which to detect.

    npts : int
        Number of points in slice axis.

    x : scalar or None; default: None
        The x coordinate of the slice. If ylim is given and this is
        not specified then defaults to zero. If xlim is given and
        this is also specified then it is ignored.

    y : scalar or None; default: None
        The y coordinate of the slice. If xlim is given and this is
        not specified then defaults to zero. If ylim is given and
        this is also specified then it is ignored.

    xlim : scalar or size two sequence; default: None
        The limits of the x-axis scan lines. A single number gives
        :math:`x_{\mathrm{axis}} \in [-|x|, +|x|]`, or a tuple of size two gives
        :math:`x_{\mathrm{axis}} \in [x[0], x[1]]`.

    ylim : scalar or array-like; default: None
        The limits of the y-axis scan lines. A single number gives
        :math:`y_{\mathrm{axis}} \in [-|y|, +|y|]`, or a tuple of size two gives
        :math:`y_{\mathrm{axis}} \in [y[0], y[1]]`.

    f : scalar, optional; default: 0
        Field frequency offset from the carrier to detect.

    w0_scaled : bool, optional; default: True
        Flag indicating whether the :math:`x`, :math:`y` axes
        should be scaled to the waist-size of the beam parameter
        at `node`.
    """

    def __init__(
        self,
        name,
        node,
        npts,
        x=None,
        y=None,
        xlim=None,
        ylim=None,
        f=0,
        w0_scaled=True,
    ):
        ScanLine.__init__(
            self, x=x, y=y, xlim=xlim, ylim=ylim, npts=npts, dtype=np.complex128
        )
        ComplexCamera.__init__(self, name, node, f=f, w0_scaled=w0_scaled)

    @property
    def npts(self):
        return super().npts

    @npts.setter
    def npts(self, value):
        super(FieldScanLine, self.__class__).npts.fset(self, value)
        self._update_dtype_shape(self.npts)

    def _get_workspace(self, sim):
        ws = FieldLineWorkspace(self, sim, self._out)
        ws.set_output_fn(field_line_output)
        return ws

    def _set_plotting_variables(self, trace_info):
        ComplexCamera._set_plotting_variables(self, trace_info)
        ScanLine._set_plotting_variables(self, trace_info)


@float_parameter("f", "Frequency", units="Hz")
class FieldPixel(ComplexCamera, Pixel):
    """Camera for detecting a single pixel of the beam in terms of the amplitude and
    phase.

    Get the unscaled x and y coordinate data via :attr:`.Pixel.xdata` and
    :attr:`.Pixel.ydata`, respectively.

    Parameters
    ----------
    name : str
        Unique name of the camera.

    node : :class:`.OpticalNode`
        Node at which to detect.

    x : scalar, optional; default: 0
        The x co-ordinate of the pixel.

    y : scalar, optional; default: 0
        The y co-ordinate of the pixel.

    f : scalar, optional; default: 0
        Field frequency offset from the carrier to detect.

    w0_scaled : bool, optional; default: True
        Flag indicating whether the :math:`x`, :math:`y` axes
        should be scaled to the waist-size of the beam parameter
        at `node`.
    """

    def __init__(self, name, node, x=0, y=0, f=0, w0_scaled=True):
        Pixel.__init__(self, x, y, dtype=np.complex128)
        ComplexCamera.__init__(self, name, node, f=f, w0_scaled=w0_scaled)

    def _get_workspace(self, sim):
        ws = FieldPixelWorkspace(self, sim)
        ws.set_output_fn(field_pixel_output)
        return ws

    def _set_plotting_variables(self, trace_info):
        ComplexCamera._set_plotting_variables(self, trace_info)
        Pixel._set_plotting_variables(self, trace_info)


def _check_limits(value):
    if isinstance(value, numbers.Number):
        value = [-abs(value), abs(value)]

    elif isinstance(value, np.ndarray):
        value = [value.min(), value.max()]

    elif is_iterable(value):
        if len(value) != 2:
            raise TypeError(
                "Expected limit to be a single number or sequence of size 2 "
                f"but got a sequence of size: {len(value)}"
            )

    else:
        raise TypeError("Unrecognised type for limit value.")

    return value
