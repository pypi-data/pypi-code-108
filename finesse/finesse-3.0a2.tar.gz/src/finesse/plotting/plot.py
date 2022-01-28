import collections.abc
import logging

import numpy as np

from .. import detectors as fd, BeamParam
from ..env import warn
from ..plotting.tools import add_colorbar
from ..utilities.units import get_SI_value
from ..cymath.homs import HGModes

LOGGER = logging.getLogger(__name__)


def get_2d_field(modes, amplitudes, qs, x=None, y=None, samples=100, scale=3):
    """Computes the 2D optical field for a given set of modes, modal amplitudes, and
    beam parameters.

    x and y dimensions can be specified if required, otherwise it
    will return an area of `scale` times the spot sizes. When `x` and
    `y` are provided `scale` and `samples` will not do anything.

    Parameters
    ----------
    modes : array_like
        Pairs of modes (n,m). Can be an 2xN array or a
        list or tuple of modes.
    amplitudes : array_like
        Array of complex amplitudes for each mode
    qs : BeamParam or Tuple(BeamParam, BeamParam)
        Compex beam parameter object for x and y planes.
        If singular value give, qx = qy.
    x : array_like, optional
        x points
    y : array_like, optional
        y points
    samples : int, optional
        Number of sample points to use in x and y
    scale : float, optional
        Number of sample points to use in x and y

    Returns
    -------
    x : double[::1]
        x points
    y : double[::1]
        y points
    field : complex[:, ::1]
        Complex optical field of size samples x samples
    """
    # Try and extract the q values
    try:
        qx, qy = qs
    except TypeError:
        qx = qy = qs

    HGs = HGModes((qx, qy), np.array(modes).astype(np.int32))
    if x is None:
        x = np.linspace(-scale * qx.w, scale * qx.w, samples)
    if y is None:
        y = np.linspace(-scale * qy.w, scale * qy.w, samples)
    Unm = HGs.compute_2d_modes(x, y)
    return x, y, (Unm.T * np.array(amplitudes)).T.sum(0)


def z_w0_mismatch_contourf(qref, ax=None, N=100, **kwargs):
    """For a given Matplotlib axis this will produce a mode-mismatch filled contour
    background. The axes are assumed to be z in the x and w0 in y. Limits are
    automatically taken from the current axes limits.

    Parameters
    ----------
    qref : complex, BeamParam
        Reference beamparameter to generate contours
        with respect to.
    ax : Axes, optional
        Axes to plot on, if None plt.gca() is called
    N : int, optional
        Number of samples in each axis to use
    **kwargs
        Values are passed to plt.contourf function.
    """
    import matplotlib.pyplot as plt

    if ax is None:
        ax = plt.gca()
    X, Y = np.meshgrid(
        np.linspace(*ax.get_xlim(), N),
        np.linspace(*ax.get_ylim(), N),
    )
    q = BeamParam(z=X, w0=Y)
    plt.contourf(X[0, :], Y[:, 0], 100 * BeamParam.mismatch(q, qref), **kwargs)
    plt.colorbar(label="Mismatch [%]")
    plt.xlabel("z [m]")
    plt.ylabel("w0 [m]")


def plot_field(
    modes,
    amplitudes,
    qs,
    *,
    x=None,
    y=None,
    samples=100,
    scale=3,
    ax=None,
    colorbar=True,
    **kwargs,
):
    """Plots a 2D optical field for a given set of modes, modal amplitudes, and beam
    parameters.

    x and y dimensions can be specified if required, otherwise it
    will return an area of `scale` times the spot sizes. When `x` and
    `y` are provided `scale` and `samples` will not do anything.

    Parameters
    ----------
    modes : array_like
        Pairs of modes (n,m). Can be an 2xN array or a
        list or tuple of modes.
    amplitudes : array_like
        Array of complex amplitudes for each mode
    qs : BeamParam or Tuple(BeamParam, BeamParam)
        Compex beam parameter object for x and y planes.
        If singular value give, qx = qy.
    x, y : ndarray, optional
        Specify x and y coordinates to plot beam
    samples : int, optional
        Number of sample points to use in x and y
    scale : float, optional
        Number of sample points to use in x and y
    ax : Axis, optional
        A Matplotlib axis to put the image on. If None,
        a new figure will be made.
    colorbar : bool
        When True the colorbar will be added
    **kwargs
        Extra keyword arguments will be passed to the
        pcolormesh plotting function.
    """
    import matplotlib.pyplot as plt

    if ax is None:
        fig, ax = plt.subplots(1, 1)
    if "shading" not in kwargs:
        kwargs["shading"] = "auto"
    x, y, E = get_2d_field(
        modes, amplitudes, qs, x=x, y=y, samples=samples, scale=scale
    )
    p = ax.pcolormesh(x, y, (E * E.conj()).real, **kwargs)
    p.set_rasterized(True)
    ax.set_aspect("equal")
    if colorbar:
        plt.colorbar(p, ax=ax, label=r"Intensity [$\mathrm{W}\mathrm{m}^{-2}$]")


def bode(f, *Y, axs=None, return_axes=True, figsize=(6, 6), **kwargs):
    """Create a Bode plot for a complex array.

    Parameters
    ----------
    f : array_like
        Frequencies
    *Y : array_like
        Complex valued transfer functions evaluated at frequencies `f`
    axs : Axes, optional
        Axes to use to plot transfer functions on. Magnitude plotted on axs[0]
        and phase on axs[1].
    figsize : tuple
        Figure size
    **kwargs
        Additional arguments are passed to the semilog calls

    Examples
    --------
    >>> axs = bode(f, CLG, label='CLG')
    >>> bode(f, CHR, axs=axs, label='CHR')
    """

    import matplotlib.pyplot as plt

    if axs is None:
        fig, axs = plt.subplots(2, 1, sharex=True, figsize=figsize)

    axs[0].set_ylabel("Magnitude [dB]")
    axs[1].set_xlabel("Frequency [Hz]")
    axs[1].set_ylabel("Phase [Deg]")

    for y in Y:
        mag = 20.0 * np.log10(abs(y))
        phase = np.unwrap(np.arctan2(y.imag, y.real)) * 180.0 / np.pi
        axs[0].semilogx(f, mag, **kwargs)
        axs[1].semilogx(f, phase, **kwargs)

    if "label" in kwargs:
        axs[0].legend()
        axs[1].legend()

    if return_axes:
        return axs


def ws_phase_space(
    W,
    S,
    OL,
    cmap="bone",
    levels=None,
    wscale="mm",
    sscale="m",
    contour_kwargs=None,
    clabel_kwargs=None,
    show=True,
    fig=None,
    ax=None,
):
    """Plots the overlap contours for WS phase space data.

    The return values of :func:`.ws_overlap_grid` correspond to the first three
    arguments of this function.

    Parameters
    ----------
    W : :class:`numpy.ndarray`
        The W space (as a 2D grid).

    S : :class:`numpy.ndarray`
        The S space (as a 2D grid).

    OL : :class:`numpy.ndarray`
        The overlap as a function of the WS phase space (as a 2D grid).

    cmap : str or colormap, optional; default: "bone"
        A matplotlib colormap, or its name.

    levels : list, optional; default: None
        List of contour levels to pass to contour plotting explicitly.

    wscale : str, optional; default: "mm"
        Units for W-axis (i.e. beam size units).

    sscale : str, optional; default: "m"
        Reciprocal units for S-axis (i.e. defocus units).

    contour_kwargs : dict, optional
        Dictionary of keyword arguments to pass to matplotlib contour function. If not
        specified then the following defaults are used:

        - "colors": "k"
        - "linestyles": "--"
        - "linewidths": 0.5

    clabel_kwargs : dict, optional
        Dictionary of keyword arguments to pass to matplotlib clabel function. If not
        specified then the following defaults are used:

        - "colors": same as `contour_kwargs`
        - "inline": True

    show : bool, optional; default: True
        Whether to show the figure immediately.

    fig : :class:`~matplotlib.figure.Figure`, optional, default: None
        The figure object to use. If not specified a new figure will be drawn.

    ax : :class:`~matplotlib.axes.Axes`, optional, default: None
        The axes to use. If not specified the first pair will be used, or created.
        Ignored if `fig` is None.

    Returns
    -------
    fig : :class:`~matplotlib.figure.Figure`
        Handle to the matplotlib Figure.

    ax : :class:`~matplotlib.axes.Axes`
        Handle to the matplotlib Axis.

    See Also
    --------
    :class:`~finesse.gaussian.ws_overlap_grid`
    """
    import matplotlib.pyplot as plt

    if fig is None:
        fig = plt.figure()
        if ax is not None:
            warn("Ignoring axes specified without figure")
            ax = None

    if ax is None:
        if len(fig.axes) == 0:
            ax = fig.add_subplot()
        else:
            warn("Axes not specified; using first pair.")
            ax = fig.axes[0]

    if contour_kwargs is None:
        contour_kwargs = {}
    if clabel_kwargs is None:
        clabel_kwargs = {}

    # Set some sensible defaults for the overlap contour line properties
    contour_kwargs.setdefault("colors", "k")
    contour_kwargs.setdefault("linestyles", "--")
    contour_kwargs.setdefault("linewidths", 0.5)

    # And some defaults for the overlap contour label properties
    clabel_kwargs.setdefault("inline", True)
    clabel_kwargs.setdefault("colors", contour_kwargs["colors"])

    CS = ax.contourf(W, S, OL, cmap=plt.cm.get_cmap(cmap), levels=levels)
    CS2 = ax.contour(W, S, OL, levels=CS.levels, **contour_kwargs)
    ax.clabel(CS2, **clabel_kwargs)

    if len(wscale) == 2:
        wsv = get_SI_value(wscale[0])
        ax.set_xticklabels(f"{(x / wsv):.2f}" for x in ax.get_xticks())
    if len(sscale) == 2:
        ssv = get_SI_value(sscale[0])
        ax.set_yticklabels(f"{(y / ssv):.2f}" for y in ax.get_yticks())

    ax.set_xlabel(f"Gaussian mode size $W$ [{wscale}]")
    ax.set_ylabel(f"Gaussian defocus $S$ [1/{sscale}]")

    if show:
        plt.show()

    return fig, ax


class Plotter:
    """Handler for plotting outputs from a simulation."""

    import matplotlib.pyplot as plt
    import matplotlib.colors as colors
    import matplotlib.animation as animation

    def __init__(self, solution):
        self.out = solution
        # figure size scaling and layout
        self.scale = 1
        self.tight_layout = True

        # animation attributes
        self.repeat = True
        self.repeat_delay = None
        self.interval = 50
        self.blit = True

    def __do_scaling_and_layout(self, figures):
        done = set()
        for figs_t in figures.values():
            if isinstance(figs_t, dict):
                figs = list(figs_t.values())
                if figs and isinstance(figs[0], list):
                    figs = figs[0]
            elif isinstance(figs_t, list):
                figs = figs_t
            else:
                figs = [figs_t]

            for fig in figs:
                if fig in done:
                    continue

                fig.set_size_inches(self.scale * fig.get_size_inches())

                if self.tight_layout:
                    fig.tight_layout()

                done.add(fig)

    def parameter_axis_label(self, param, axis="x", ax=None):
        info = self.out.axis_info[param]
        if ax is not None:
            if axis == "x":
                func = ax.set_xlabel
            else:
                func = ax.set_ylabel
        else:
            if axis == "x":
                func = Plotter.plt.xlabel
            else:
                func = Plotter.plt.ylabel

        label = f"{info['name']}"
        if info["unit"]:
            label += f" [{info['unit']}]"

        func(label)

    def output_axis_label(self, obj, ax=None):
        info = self.out.trace_info[obj]
        if ax is not None:
            func = ax.set_ylabel
        else:
            func = Plotter.plt.ylabel

        if info["label"] is None:
            label = ""
            warn(
                f"Detector {repr(info['name'])} has no label, unable to set output "
                f"axis label for this detector."
            )

        label = f"{info['label']}"

        if info["unit"]:
            label += f" [{info['unit']}]"

        func(label)

    @staticmethod
    def choose_plot_func(logx, logy, magnitude_axis=None):
        if magnitude_axis is not None:
            obj = magnitude_axis
        else:
            obj = Plotter.plt

        if logx and logy:
            return obj.loglog
        if logx:
            return obj.semilogx
        if logy:
            return obj.semilogy

        return obj.plot

    @staticmethod
    def select_detector_cmap(cmaps, det):
        det_type = type(det)

        if isinstance(cmaps, dict):
            if det in cmaps:
                cmap = cmaps[det]
            elif det_type in cmaps:
                cmap = cmaps[det_type]
            else:
                LOGGER.info(
                    "No entry for %s or %s in specified cmap dictionary, "
                    "using default colormap",
                    det,
                    det_type,
                )
                cmap = Plotter.plt.get_cmap()
        else:
            cmap = cmaps

        return cmap

    @staticmethod
    def make_text_handle(
        text_former, units, x, y, index=0, color="white", fig=None, ax=None
    ):
        units_txt = f"\n[{units}]" if units else ""

        if ax is None:
            if fig is None:
                raise RuntimeError()

            txt_func = Plotter.plt.text
            transform = fig.axes[0].transAxes
        else:
            txt_func = ax.text
            transform = ax.transAxes

        return txt_func(
            x,
            y,
            text_former(index) + units_txt,
            ha="center",
            va="center",
            transform=transform,
            color=color,
        )

    def make_images(
        self,
        fig,
        extent,
        z,
        cmap,
        det,
        log,
        anim_axis,
        aspect="auto",
        cbar_label=None,
        transpose=False,
    ):
        x, p = anim_axis

        norm = None
        if log:
            norm = Plotter.colors.LogNorm(z.min(), z.max())

        if transpose:
            z0 = z[0].T
        else:
            z0 = z[0]

        initial_im = Plotter.plt.imshow(
            z0,
            norm=norm,
            extent=extent,
            cmap=cmap,
            aspect=aspect,
            animated=True,
        )
        if cbar_label is None:
            cbar_label = f"{self.out.trace_info[det]['label']}"
            if self.out.trace_info[det]["unit"]:
                cbar_label += f" [{self.out.trace_info[det]['unit']}]"
            cbar_label += f" ({det})"

        add_colorbar(initial_im, label=cbar_label)

        def form_txt(idx):
            cname = self.out.axis_info[p]["component"]
            name = self.out.axis_info[p]["name"]
            return f"{cname} {name} = {x[idx]:.3g}"

        txt_handle = Plotter.make_text_handle(
            form_txt, self.out.axis_info[p]["unit"], x=0.8, y=0.9, fig=fig
        )

        images = [[initial_im, txt_handle]]
        for i in np.arange(1, x.size):
            if transpose:
                zi = z[i].T
            else:
                zi = z[i]

            im = Plotter.plt.imshow(
                zi,
                norm=norm,
                extent=extent,
                cmap=cmap,
                aspect=aspect,
                animated=True,
            )
            txt_handle = Plotter.make_text_handle(
                form_txt,
                self.out.axis_info[p]["unit"],
                x=0.8,
                y=0.9,
                index=i,
                fig=fig,
            )

            images.append([im, txt_handle])

        return images

    def make_amp_phase_images(
        self,
        ax1,
        ax2,
        extent,
        z1,
        z2,
        cmap,
        degrees,
        det,
        log,
        anim_axis,
        aspect="auto",
        transpose=False,
    ):
        x, p = anim_axis

        norm = None
        if log:
            norm = Plotter.colors.LogNorm(z1.min(), z1.max())

        if transpose:
            z10 = z1[0].T
            z20 = z2[0].T
        else:
            z10 = z1[0]
            z20 = z2[0]

        initial_amp_im = ax1.imshow(
            z10,
            norm=norm,
            extent=extent,
            cmap=cmap,
            aspect=aspect,
            animated=True,
        )
        add_colorbar(initial_amp_im, label=r"Amplitude [$\sqrt{{W}}$" + f" ({det})")

        initial_phase_im = ax2.imshow(
            z20,
            extent=extent,
            cmap=cmap,
            aspect=aspect,
            animated=True,
        )
        add_colorbar(
            initial_phase_im,
            label=f"Phase [{'deg' if degrees else 'rad'}] ({det})",
        )

        def form_txt(idx):
            cname = self.out.axis_info[p]["component"]
            name = self.out.axis_info[p]["name"]
            return f"{cname} {name} = {x[idx]:.3g}"

        amp_txt_handle = Plotter.make_text_handle(
            form_txt, self.out.axis_info[p]["unit"], x=0.8, y=0.9, ax=ax1
        )
        phase_txt_handle = Plotter.make_text_handle(
            form_txt, self.out.axis_info[p]["unit"], x=0.8, y=0.9, ax=ax2
        )

        images = [[initial_amp_im, initial_phase_im, amp_txt_handle, phase_txt_handle]]

        for i in np.arange(1, x.size):
            if transpose:
                z1i = z1[i].T
                z2i = z2[i].T
            else:
                z1i = z1[i]
                z2i = z2[i]

            amp_im = ax1.imshow(
                z1i,
                norm=norm,
                extent=extent,
                cmap=cmap,
                aspect=aspect,
                animated=True,
            )
            phase_im = ax2.imshow(
                z2i,
                extent=extent,
                cmap=cmap,
                aspect=aspect,
                animated=True,
            )

            amp_txt_handle = Plotter.make_text_handle(
                form_txt,
                self.out.axis_info[p]["unit"],
                x=0.8,
                y=0.9,
                index=i,
                ax=ax1,
            )

            phase_txt_handle = Plotter.make_text_handle(
                form_txt,
                self.out.axis_info[p]["unit"],
                x=0.8,
                y=0.9,
                index=i,
                ax=ax2,
            )

            images.append([amp_im, phase_im, amp_txt_handle, phase_txt_handle])

        return images

    @staticmethod
    def _set_fig_at_detname(figures: dict, dets, fig):
        if not hasattr(dets, "__getitem__"):
            dets = [dets]

        figures.update(dict.fromkeys(dets, fig))

    def __handle_beam_property_plotting(
        self, bp_detector_map, cmaps, figures, animations, logx, logy, log, degrees
    ):
        if bp_detector_map:
            sub_figs = figures[fd.BeamPropertyDetector] = {}

        for det_prop, dets in bp_detector_map.items():
            if det_prop == fd.BeamProperty.Q:
                continue

            if self.out.axes == 1:
                self.__plot_1D(det_prop, dets, logx, logy, degrees, sub_figs, figures)
            elif self.out.axes == 2:
                self.__plot_2D(det_prop, dets, log, degrees, cmaps, sub_figs, figures)
            elif self.out.axes == 3:
                self.__plot_2D_animated(
                    det_prop, dets, log, degrees, cmaps, sub_figs, animations, figures
                )

    def __handle_cavity_property_plotting(
        self, cp_detector_map, cmaps, figures, animations, logx, logy, log, degrees
    ):
        if cp_detector_map:
            sub_figs = figures[fd.CavityPropertyDetector] = {}

        for det_prop, dets in cp_detector_map.items():
            if det_prop == fd.CavityProperty.EIGENMODE:
                continue

            if self.out.axes == 1:
                self.__plot_1D(det_prop, dets, logx, logy, degrees, sub_figs, figures)
            elif self.out.axes == 2:
                self.__plot_2D(det_prop, dets, log, degrees, cmaps, sub_figs, figures)
            elif self.out.axes == 3:
                self.__plot_2D_animated(
                    det_prop, dets, log, degrees, cmaps, sub_figs, animations, figures
                )

    def __handle_detector_plotting(
        self,
        detector_type_map,
        cmaps,
        figures,
        animations,
        logx,
        logy,
        log,
        degrees,
    ):
        for det_type, dets in detector_type_map.items():
            if det_type == fd.CCD:
                self.__plot_CCDs(dets, log, cmaps, figures, animations)
            elif det_type == fd.FieldCamera:
                self.__plot_field_cameras(
                    dets, log, degrees, cmaps, figures, animations
                )
            elif det_type == fd.CCDScanLine:
                self.__plot_ccd_scan_lines(dets, log, cmaps, figures, animations)
            elif det_type == fd.FieldScanLine:
                self.__plot_field_scan_lines(
                    dets, log, degrees, cmaps, figures, animations
                )
            else:
                if not self.out.axes:
                    warn(
                        f"No x-axes have been defined, unable to plot the "
                        f"outputs of any detectors of type {repr(det_type)}"
                    )
                    continue

                if self.out.axes == 1:
                    self.__plot_1D(det_type, dets, logx, logy, degrees, figures)
                elif self.out.axes == 2:
                    self.__plot_2D(det_type, dets, log, degrees, cmaps, figures)
                elif self.out.axes == 3:
                    self.__plot_2D_animated(
                        det_type, dets, log, degrees, cmaps, figures, animations
                    )
                else:
                    LOGGER.error(
                        "Unable to produce plots of %d-dimensional data", self.out.axes
                    )

    def __plot_1D(self, det_type, dets, logx, logy, degrees, figures, allfigs=None):
        fig = figures.get(det_type)
        if fig is None:
            fig = Plotter.plt.figure()
        else:
            Plotter.plt.figure(fig.number)

        mag_and_phase = (
            allfigs is None
            and issubclass(det_type, fd.Detector)
            and any(self.out.trace_info[det]["dtype"] == np.complex128 for det in dets)
        )
        if mag_and_phase:
            mag_ax = fig.add_subplot(211)
            phase_ax = fig.add_subplot(212, sharex=mag_ax)
        else:
            mag_ax = None

        plot_func = Plotter.choose_plot_func(logx, logy, mag_ax)

        for det in dets:
            data = self.out[det]

            if mag_and_phase:
                amplitude = np.abs(data)
                plot_func(self.out.x1, amplitude, label=det + " (abs)")
                mag_ax.set_ylabel(r"Amplitude [$\sqrt{W}$]")
                mag_ax.legend()

                phase = np.angle(data, degrees)

                phase_ax.plot(self.out.x1, phase, label=det + " (phase)")
                phase_ax.set_ylabel(f"Phase [{'deg' if degrees else 'rad'}]")
            else:
                plot_func(self.out.x1, data, label=det)

        if not mag_and_phase and dets:
            self.output_axis_label(dets[0])
            Plotter.plt.legend()

        self.parameter_axis_label(self.out.p1)

        figures[det_type] = fig

        if allfigs is None:
            Plotter._set_fig_at_detname(figures, dets, fig)
        else:
            Plotter._set_fig_at_detname(allfigs, dets, fig)

    def __plot_2D(self, det_type, dets, log, degrees, cmaps, figures, allfigs=None):
        x1 = self.out.x1
        x2 = self.out.x2
        extent = [x1.min(), x1.max(), x2.min(), x2.max()]

        for det in dets:
            fig = Plotter.plt.figure()

            data = self.out[det].T
            cmap = Plotter.select_detector_cmap(cmaps, det)

            mag_and_phase = self.out.trace_info[det]["dtype"] == np.complex128
            if mag_and_phase:
                mag_ax = fig.add_subplot(211)
                phase_ax = fig.add_subplot(212)

                amplitude = np.abs(data)

                norm = None
                if log:
                    norm = Plotter.colors.LogNorm(amplitude.min(), amplitude.max())

                mag_im = mag_ax.imshow(
                    amplitude,
                    extent=extent,
                    norm=norm,
                    cmap=cmap,
                    aspect="auto",
                )
                add_colorbar(mag_im, label=r"Amplitude [$\sqrt{{W}}$]" + f" ({det})")

                phase = np.angle(data, degrees)
                phase_im = phase_ax.imshow(
                    phase,
                    extent=extent,
                    cmap=cmap,
                    aspect="auto",
                )
                add_colorbar(
                    phase_im,
                    label=f"Phase [{'deg' if degrees else 'rad'}] ({det})",
                )
                for ax in (mag_ax, phase_ax):
                    self.parameter_axis_label(self.out.p1, ax=ax)
                    self.parameter_axis_label(self.out.p2, axis="y", ax=ax)

            else:
                norm = None
                if log:
                    norm = Plotter.colors.LogNorm(data.min(), data.max())

                im = Plotter.plt.imshow(
                    data,
                    extent=extent,
                    norm=norm,
                    cmap=cmap,
                    aspect="auto",
                )
                add_colorbar(
                    im,
                    label=f"{self.out.trace_info[det]['label']} [{self.out.trace_info[det]['unit']}] ({det})",
                )

                self.parameter_axis_label(self.out.p1)
                self.parameter_axis_label(self.out.p2, axis="y")

            if det_type in figures:
                figures[det_type].append(fig)
            else:
                figures[det_type] = [fig]

            if allfigs is None:
                Plotter._set_fig_at_detname(figures, det, fig)
            else:
                Plotter._set_fig_at_detname(allfigs, det, fig)

    def __plot_2D_animated(
        self,
        det_type,
        dets,
        log,
        degrees,
        cmaps,
        figures,
        animations,
        allfigs=None,
    ):
        x1 = self.out.x1
        x2 = self.out.x2
        extent = [x1.min(), x1.max(), x2.min(), x2.max()]

        for det in dets:
            fig = Plotter.plt.figure()

            data = self.out[det]
            cmap = Plotter.select_detector_cmap(cmaps, det)

            mag_and_phase = self.out.trace_info[det]["dtype"] == np.complex128
            if mag_and_phase:
                mag_ax = fig.add_subplot(211)
                phase_ax = fig.add_subplot(212)

                amplitude = np.abs(data)
                phase = np.angle(data, degrees)

                images = self.make_amp_phase_images(
                    mag_ax,
                    phase_ax,
                    extent,
                    amplitude,
                    phase,
                    cmap,
                    degrees,
                    det,
                    log,
                    (self.out.x3, self.out.p3),
                    transpose=True,
                )

                for ax in (mag_ax, phase_ax):
                    self.parameter_axis_label(self.out.p1, ax=ax)
                    self.parameter_axis_label(self.out.p2, axis="y", ax=ax)
            else:
                images = self.make_images(
                    fig,
                    extent,
                    data,
                    cmap,
                    det,
                    log,
                    (self.out.x3, self.out.p3),
                    transpose=True,
                )

                self.parameter_axis_label(self.out.p1)
                self.parameter_axis_label(self.out.p2, axis="y")

            animations[det] = Plotter.animation.ArtistAnimation(
                fig,
                images,
                interval=self.interval,
                repeat=self.repeat,
                repeat_delay=self.repeat_delay,
                blit=self.blit,
            )

            if det_type in figures:
                figures[det_type].append(fig)
            else:
                figures[det_type] = [fig]

            if allfigs is None:
                Plotter._set_fig_at_detname(figures, det, fig)
            else:
                Plotter._set_fig_at_detname(allfigs, det, fig)

    def __plot_CCDs(self, dets, log, cmaps, figures, animations):
        if self.out.axes > 1:
            warn("Skipping CCD plots as multiple axes have been defined")
            return

        for det in dets:
            fig = Plotter.plt.figure()

            data = self.out[det]
            norm = None
            if log:
                norm = Plotter.colors.LogNorm(data.min(), data.max())
            w0_scaled = self.out.trace_info[det]["w0_scaled"]

            cmap = Plotter.select_detector_cmap(cmaps, det)

            extent = [
                *self.out.trace_info[det]["xlim"],
                *self.out.trace_info[det]["ylim"],
            ]

            cb_label = r"Intensity [W m$^{-2}$ px]" + f" ({det})"

            if not self.out.axes:  # single image
                im = Plotter.plt.imshow(
                    data.T,
                    norm=norm,
                    extent=extent,
                    cmap=cmap,
                    aspect="equal",
                )
                add_colorbar(im, label=cb_label)

            else:
                images = self.make_images(
                    fig,
                    extent,
                    data,
                    cmap,
                    det,
                    log,
                    (self.out.x1, self.out.p1),
                    aspect="equal",
                    cbar_label=cb_label,
                    transpose=True,
                )

                animations[det] = Plotter.animation.ArtistAnimation(
                    fig,
                    images,
                    interval=self.interval,
                    repeat=self.repeat,
                    repeat_delay=self.repeat_delay,
                    blit=self.blit,
                )

            Plotter.plt.xlabel(r"$\mathrm{x}$ [$\mathrm{w}_0$]" if w0_scaled else "[m]")
            Plotter.plt.ylabel(r"$\mathrm{y}$ [$\mathrm{w}_0$]" if w0_scaled else "[m]")

            if fd.CCD in figures:
                figures[fd.CCD].append(fig)
            else:
                figures[fd.CCD] = [fig]

            Plotter._set_fig_at_detname(figures, det, fig)

    def __plot_field_cameras(self, dets, log, degrees, cmaps, figures, animations):
        if self.out.axes > 1:
            warn("Skipping ComplexCamera plots as multiple axes have been defined")
            return

        for det in dets:
            fig = Plotter.plt.figure()

            data = self.out[det]
            norm = None
            if log:
                norm = Plotter.colors.LogNorm(data.min(), data.max())
            w0_scaled = self.out.trace_info[det]["w0_scaled"]

            cmap = Plotter.select_detector_cmap(cmaps, det)

            extent = [
                *self.out.trace_info[det]["xlim"],
                *self.out.trace_info[det]["ylim"],
            ]

            mag_ax = fig.add_subplot(211)
            phase_ax = fig.add_subplot(212)

            amplitude = np.abs(data)
            phase = np.angle(data, degrees)
            if not self.out.axes:  # single image
                mag_im = mag_ax.imshow(
                    amplitude.T,
                    norm=norm,
                    extent=extent,
                    cmap=cmap,
                    aspect="equal",
                )
                add_colorbar(mag_im, label=det + r" Amplitude [$\sqrt{W}$ px]")

                phase_im = phase_ax.imshow(
                    phase.T,
                    extent=extent,
                    cmap=cmap,
                    aspect="equal",
                )
                add_colorbar(
                    phase_im, label=det + f" Phase [{'deg' if degrees else 'rad'}]"
                )

            else:
                images = self.make_amp_phase_images(
                    mag_ax,
                    phase_ax,
                    extent,
                    amplitude,
                    phase,
                    cmap,
                    degrees,
                    det,
                    log,
                    (self.out.x1, self.out.p1),
                    aspect="equal",
                    transpose=True,
                )

                animations[det] = Plotter.animation.ArtistAnimation(
                    fig,
                    images,
                    interval=self.interval,
                    repeat=self.repeat,
                    repeat_delay=self.repeat_delay,
                    blit=self.blit,
                )

            for ax in (mag_ax, phase_ax):
                ax.set_xlabel(r"$\mathrm{x}$ [$\mathrm{w}_0$]" if w0_scaled else "[m]")
                ax.set_ylabel(r"$\mathrm{y}$ [$\mathrm{w}_0$]" if w0_scaled else "[m]")

            if fd.FieldCamera in figures:
                figures[fd.FieldCamera].append(fig)
            else:
                figures[fd.FieldCamera] = [fig]

            Plotter._set_fig_at_detname(figures, det, fig)

    def __plot_ccd_scan_lines(
        self,
        dets,
        log,
        cmap,
        figures,
        animations,
    ):
        if self.out.axes > 2:
            warn("Skipping CCDScanLine plots as more than two axes have been defined")
            return

        if not self.out.axes:
            fig = Plotter.plt.figure()

        for det in dets:
            if self.out.axes:
                fig = Plotter.plt.figure()

            data = self.out[det]
            if self.out.trace_info[det]["direction"] == "x":
                x = self.out.trace_info[det]["xdata"]
            else:
                x = self.out.trace_info[det]["ydata"]
            w0_scaled = self.out.trace_info[det]["w0_scaled"]

            if not self.out.axes:
                plot_func = Plotter.choose_plot_func(log, log)

                plot_func(x, data, label=det)
            else:
                extent = [x.min(), x.max(), self.out.x1.min(), self.out.x1.max()]

                if self.out.axes == 1:
                    norm = None
                    if log:
                        norm = Plotter.colors.LogNorm(data.min(), data.max())

                    im = Plotter.plt.imshow(
                        data.T,
                        extent=extent,
                        norm=norm,
                        cmap=cmap,
                        aspect="auto",
                    )
                    add_colorbar(
                        im,
                        label=f"{self.out.trace_info[det]['label']} [{self.out.trace_info[det]['unit']}] ({det})",
                    )
                else:
                    images = self.make_images(
                        fig,
                        extent,
                        data,
                        cmap,
                        det,
                        log,
                        (self.out.x2, self.out.p2),
                        transpose=True,
                    )

                    animations[det] = Plotter.animation.ArtistAnimation(
                        fig,
                        images,
                        interval=self.interval,
                        repeat=self.repeat,
                        repeat_delay=self.repeat_delay,
                        blit=self.blit,
                    )

                self.parameter_axis_label(self.out.p1, axis="y")

                if fd.FieldScanLine in figures:
                    figures[fd.FieldScanLine].append(fig)
                else:
                    figures[fd.FieldScanLine] = [fig]

                Plotter._set_fig_at_detname(figures, det, fig)

            Plotter.plt.xlabel(
                r"$\mathrm{"
                + self.out.trace_info[det]["direction"]
                + r"}$ [$\mathrm{w}_0$]"
                if w0_scaled
                else "[m]"
            )

        if not self.out.axes:
            self.output_axis_label(dets[0])
            Plotter.plt.legend()

            figures[fd.FieldScanLine] = fig
            Plotter._set_fig_at_detname(figures, dets, fig)

    def __plot_field_scan_lines(
        self,
        dets,
        log,
        degrees,
        cmap,
        figures,
        animations,
    ):
        if self.out.axes > 2:
            warn("Skipping FieldScanLine plots as more than two axes have been defined")
            return

        if not self.out.axes:
            fig = Plotter.plt.figure()

        for det in dets:
            if self.out.axes:
                fig = Plotter.plt.figure()

            mag_ax = fig.add_subplot(211)
            phase_ax = fig.add_subplot(212)

            if self.out.trace_info[det]["direction"] == "x":
                x = self.out.trace_info[det]["xdata"]
            else:
                x = self.out.trace_info[det]["ydata"]
            w0_scaled = self.out.trace_info[det]["w0_scaled"]

            amplitude = np.abs(self.out[det])
            phase = np.angle(self.out[det], degrees)

            if not self.out.axes:
                plot_func = Plotter.choose_plot_func(log, log, mag_ax)

                plot_func(x, amplitude, label=det)
                mag_ax.set_ylabel(r"Amplitude [$\sqrt{W}$ px]")
                mag_ax.legend()

                phase_ax.plot(x, phase, label=det)
                phase_ax.set_ylabel(f"Phase [{'deg' if degrees else 'rad'}]")
                phase_ax.legend()
            else:
                extent = [x.min(), x.max(), self.out.x1.min(), self.out.x1.max()]

                if self.out.axes == 1:
                    norm = None
                    if log:
                        norm = Plotter.colors.LogNorm(amplitude.min(), amplitude.max())

                    mag_im = mag_ax.imshow(
                        amplitude.T,
                        norm=norm,
                        extent=extent,
                        cmap=cmap,
                        aspect="auto",
                    )
                    add_colorbar(mag_im, label=r"Ampltide [$\sqrt{W}$ px]")

                    phase_im = phase_ax.imshow(
                        phase.T,
                        extent=extent,
                        cmap=cmap,
                        aspect="auto",
                    )
                    add_colorbar(
                        phase_im, label=f"Phase [{'deg' if degrees else 'rad'}]"
                    )

                else:
                    images = self.make_amp_phase_images(
                        mag_ax,
                        phase_ax,
                        extent,
                        amplitude,
                        phase,
                        cmap,
                        degrees,
                        det,
                        log,
                        (self.out.x2, self.out.p2),
                        aspect="equal",
                        transpose=True,
                    )

                    animations[det] = Plotter.animation.ArtistAnimation(
                        fig,
                        images,
                        interval=self.interval,
                        repeat=self.repeat,
                        repeat_delay=self.repeat_delay,
                        blit=self.blit,
                    )

                for ax in (mag_ax, phase_ax):
                    self.parameter_axis_label(self.out.p1, axis="y", ax=ax)

                if fd.FieldScanLine in figures:
                    figures[fd.FieldScanLine].append(fig)
                else:
                    figures[fd.FieldScanLine] = [fig]

                Plotter._set_fig_at_detname(figures, det, fig)

            for ax in (mag_ax, phase_ax):
                ax.set_xlabel(
                    r"$\mathrm{"
                    + self.out.trace_info[det]["direction"]
                    + r"}$ "
                    + r"[$\mathrm{w}_0$]"
                    if w0_scaled
                    else "[m]"
                )

        if not self.out.axes:
            figures[fd.FieldScanLine] = fig
            Plotter._set_fig_at_detname(figures, dets, fig)

    def plot(
        self,
        *detectors,
        log=False,
        logx=None,
        logy=None,
        degrees=True,
        cmap=None,
        show=True,
        separate=True,
        _test_fig_handles=None,
    ):
        r"""Plots the outputs from the specified `detectors` of a given solution `out`, or all
        detectors in the executed model if `detectors` is `None`.

        Detectors are sorted by their type and the outputs of each are plotted on their own figure
        accordingly - i.e. all amplitude detector outputs are plotted on one figure, all power
        detector outputs on another figure etc.

        .. note::

            It is recommended to use this function with :func:`finesse.plotting.tools.init`. This
            then means that all figures produced by this function will use matplotlib rcParams
            corresponding to the style selected.

            For example::

                import finesse
                finesse.plotting.init()

                model = finesse.parse(\"""
                l L0 P=1

                s s0 L0.p1 ITM.p1

                m ITM R=0.99 T=0.01 Rc=inf
                s CAV ITM.p2 ETM.p1 L=1
                m ETM R=0.99 T=0.01 Rc=10

                modes maxtem=4

                gauss L0.p1.o q=(-0.4+2j)
                cav FP ITM.p2.o ITM.p2.i

                xaxis L0.f (-100M) 100M 1000 lin

                ad ad00 ETM.p1.i f=&L0.f n=0 m=0
                ad ad02 ETM.p1.i f=&L0.f n=0 m=2

                pd C ETM.p1.i
                \""")
                model.run().plot(logy=True, figsize_scale=2)

            will produce two figures (one for the power-detector output and another for the
            amplitude detectors) which use rcParams from the `default` style-sheet. Using
            `figsize_scale` here then scales these figures whilst keeping the proportions
            defined in this style-sheet constant.

        .. rubric:: Multi-dimensional scan plotting behaviour

        If multiple parameters have been scanned in the underlying model associated
        with this solution object, then the form of the resulting plots produced here
        will depend on a number of options:

        - If two parameters have been scanned then all non-CCD detector ouputs will be plotted
            on separate image plot figures. All CCD plots will be ignored.
        - If a single parameter has been scanned and `index` is not specified then all CCD detector
            outputs will be plotted on separate animated figures. Or if `index` is specified, then
            all CCD detector outputs will be plotted on separate image plot figures *at the
            specified index of the scanned axis*.

        Parameters
        ----------
        detectors : sequence or str or type or :class:`.Detector`, optional
            An iterable (or singular) of strings (corresponding to detector names),
            :class:`.Detector` instances or detector types. Defaults to `None` so that all detector
            outputs are plotted.

        log : bool, optional
            Use log-log scale. Also applies to image plots so that colours are normalised
            on a log-scale between limits of image data. Defaults to `False`.

        logx : bool, optional
            Use log-scale on x-axis if appropriate, defaults to the
            value of `log`.

        logy : bool, optional
            Use log-scale on y-axis if appropriate, defaults to the
            value of `log`.

        degrees : bool, optional
            Plots angle and phase outputs in degrees, defaults to `True`.

        show : bool, optional
            Shows all the produced figures if true, defaults to `True`.

        separate : bool, optional
            Plots the output of different detector types on different
            axes if true, defaults to `True`.

        Returns
        -------
        figures : dict
            A dictionary mapping `type(detector)` and detector names to corresponding
            :class:`~matplotlib.figure.Figure` objects. Note that some keys, i.e. those of each
            `type(detector)` and the names of the detectors of that type, share the same values.

        animations : dict
            A dictionary of `detector.name : animation` mappings.
        """
        # handle case where detectors are given as some iterable list/tuple
        if (
            len(detectors) == 1
            and isinstance(detectors[0], collections.abc.Iterable)
            and not isinstance(detectors[0], str)
        ):
            detectors = detectors[0]

        if logx is None:
            logx = log
        if logy is None:
            logy = log

        # Convert from any objects to names
        if len(detectors) == 0:
            detectors = self.out.detectors
        else:
            detectors = tuple(x if isinstance(x, str) else x.name for x in detectors)

        detector_type_map = {}
        bp_detector_map = {}
        cp_detector_map = {}

        plot_infos = tuple(self.out.trace_info[det] for det in detectors)

        for info in plot_infos:
            if info["detector_type"] is fd.BeamPropertyDetector:
                if info["detecting"] in bp_detector_map:
                    bp_detector_map[info["detecting"]].append(info["name"])
                else:
                    bp_detector_map[info["detecting"]] = [info["name"]]
            elif info["detector_type"] is fd.CavityPropertyDetector:
                if info["detecting"] in cp_detector_map:
                    cp_detector_map[info["detecting"]].append(info["name"])
                else:
                    cp_detector_map[info["detecting"]] = [info["name"]]
            else:
                if separate:
                    key = info["detector_type"]
                else:
                    key = type(fd.Detector)
                if key in detector_type_map:
                    detector_type_map[key].append(info["name"])
                else:
                    detector_type_map[key] = [info["name"]]

        if cmap is None:
            cmap = Plotter.plt.get_cmap()

        figures = _test_fig_handles or {}
        animations = {}

        self.__handle_beam_property_plotting(
            bp_detector_map,
            cmap,
            figures,
            animations,
            logx,
            logy,
            log,
            degrees,
        )
        self.__handle_cavity_property_plotting(
            cp_detector_map,
            cmap,
            figures,
            animations,
            logx,
            logy,
            log,
            degrees,
        )
        self.__handle_detector_plotting(
            detector_type_map,
            cmap,
            figures,
            animations,
            logx,
            logy,
            log,
            degrees,
        )

        self.__do_scaling_and_layout(figures)

        if show:
            Plotter.plt.show()

        if not animations:
            return figures

        return figures, animations
