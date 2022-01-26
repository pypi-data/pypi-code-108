import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from ..constants import xyz_dict, xyz_list
from ..utils import listify, log_and_raise
from ..monitor import TimeMonitor, FreqMonitor
from .structure import _plot_eps_interp


def _monitor_slice(
    sim,
    mnt_data,
    sind=None,
    normal=None,
    normal_ind=0,
    field="E",
    val="re",
    comp="z",
    eps_freq=None,
):

    # Get normal if not provided
    if normal is None:
        dmin = np.argmin(mnt_data.inds_end - mnt_data.inds_beg)
        normal = ["x", "y", "z"][dmin]

    # Field component and which field (E/H/S)
    inds = {"x": 0, "y": 1, "z": 2}
    comp_ind = inds[comp]
    if field.lower() == "e":
        ftmp = mnt_data.E[:, :, :, :, sind]
        ftit = "E"
    elif field.lower() == "h":
        ftmp = mnt_data.H[:, :, :, :, sind]
        ftit = "H"
    elif field.lower() == "s":
        ftmp = mnt_data.S[:, :, :, :, sind]
        ftit = "S"

    # Time or frequency monitor dependent stuff
    if isinstance(mnt_data.monitor, TimeMonitor):
        tit_string = "t=" + "%1.2e" % (mnt_data.tmesh[sind] * 1e12) + "fs"
    elif isinstance(mnt_data.monitor, FreqMonitor):
        tit_string = "f=" + "%1.2e" % (mnt_data.freqs[sind] * 1e-12) + "THz"
        if eps_freq is None and isinstance(mnt_data.monitor, FreqMonitor):
            eps_freq = mnt_data.freqs[sind]

    # Colormap for epsilon overlay
    if val == "re" or val == "im":
        cmap_eps = "Greys"
    else:
        cmap_eps = "Greys_r"

    # Coordinates and position along normal direction
    mbeg = mnt_data.inds_beg
    mend = mnt_data.inds_end

    grid_dict = {
        "x": (1, 2, 0, "y", "z"),
        "y": (0, 2, 1, "x", "z"),
        "z": (0, 1, 2, "x", "y"),
    }
    (d1, d2, dn, x_lab, y_lab) = grid_dict[normal]
    norm_pos = sim.grid.mesh[dn][mbeg[dn] + normal_ind]
    mesh = [m[mbeg[i] : mend[i]] for (i, m) in enumerate(sim.grid.mesh)]
    mesh[dn] = np.array([norm_pos])

    # Coordinates in the 2D plotting plane
    coords_mnt = [c[mbeg[i] : mend[i] + 1] for i, c in enumerate(sim.grid.coords)]
    coords = [coords_mnt[d1], coords_mnt[d2]]

    # Field values to plot
    if val == "int":
        fvals = np.sum(np.abs(ftmp) ** 2, axis=0)
        ax_tit = "||%s||^2" % ftit
    else:
        fvals = ftmp[comp_ind, :, :, :]
        ax_tit = val + "(" + ftit + comp + ")"
    fvals = np.take(fvals, normal_ind, axis=dn)

    xlabel = x_lab + " (um)"
    ylabel = y_lab + " (um)"
    ax_title = f"Monitor {mnt_data.name}, {normal} = {norm_pos:1.2e}um\n{ax_tit}, {tit_string}"

    return (fvals, coords, normal, norm_pos, cmap_eps, eps_freq, xlabel, ylabel, ax_title)


def _plot_field_2D(fvals, coords, val="re", ax=None, cbar=False, clim=None):

    # Colormap
    cmap = "RdBu"
    bg_color = "w"
    if val == "re":
        fvals = np.real(fvals)
    elif val == "im":
        fvals = np.imag(fvals)
    else:
        cmap = "magma"
        fvals = np.abs(fvals)
        bg_color = "k"

    # Color limits
    fmax = np.amax(np.abs(fvals))
    if clim is None:
        if cmap == "RdBu":
            clim = (-fmax, fmax)
        else:
            clim = (0, fmax)

    ax.set_aspect("equal")
    ax.set_facecolor(bg_color)
    ax.set_xlim(coords[0][0], coords[0][-1])
    ax.set_ylim(coords[1][0], coords[1][-1])

    im = ax.pcolormesh(
        coords[0], coords[1], fvals.T, cmap=cmap, vmin=clim[0], vmax=clim[1], edgecolor=None, lw=0
    )

    if cbar == True:
        plt.colorbar(im, ax=ax, shrink=0.8)

    return im


def _plot_field_1D(fvals, xlim, ylim, val, ax):

    if val == "re":
        fvals = np.real(fvals)
    elif val == "im":
        fvals = np.imag(fvals)
    else:
        fvals = np.abs(fvals)

    fmax = np.amax(np.abs(fvals))
    if ylim is None:
        if cmap == "RdBu":
            ylim = (-fmax, fmax)
        else:
            ylim = (0, fmax)

    if ax is None:
        fig, ax = plt.subplots(1, constrained_layout=True)

    xs = xlim[0] + np.arange(fvals.size) * (xlim[1] - xlim[0]) / fvals.size
    im = ax.plot(xs, fvals)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    return im


def _check_monitor(mnt_data, field):
    if field.lower() == "e":
        if mnt_data.E.size == 0:
            log_and_raise("Monitor has no stored E-field values.", RuntimeError)
    elif field.lower() == "h":
        if mnt_data.H.size == 0:
            log_and_raise("Monitor has no stored H-field values.", RuntimeError)
    elif field.lower() == "s":
        if mnt_data.S.size == 0:
            log_and_raise(
                "Monitor has no stored S-field values. Run the simulation and "
                "use Simulation.poynting(Monitor) to compute S.",
                RuntimeError,
            )
    else:
        log_and_raise("'field' can be 'E' or 'H'.", ValueError)


def viz_field_2D(
    self,
    monitor,
    sample_ind=0,
    normal=None,
    normal_ind=0,
    field="E",
    val="re",
    comp="z",
    ax=None,
    cbar=False,
    clim=None,
    cmap=None,
    eps_alpha=0.3,
    eps_freq=None,
):
    """Plot a 2D cross-section of a field stored in a :class:`.Monitor`.

    Parameters
    ----------
    monitor : Monitor
        The monitor to be queried.
    sample_ind : int, optional
        Index of the frequency in a :class:`.FreqMonitor` or the time step in
        a :class:`.TimeMonitor`.
    normal : None, optional
        Axis normal to the 2D plane of plotting. If ``None``, the shortest
        dimension is taken as the normal.
    normal_ind : int, optional
        Spatial index along the normal dimension, for 3D monitors.
    field : {'E', 'H', 'S'}, optional
        Which field to plot.
    val : {'re', 'im', 'abs', 'int'}, optional
        Plot the real part (default), or the imaginary part, or the
        absolute value of a field component, or the total field intensity.
    comp : {'x', 'y', 'z'}, optional
        Component of the field to plot. If ``val`` is ``'int'``, this
        parameter has no effect.
    ax : Matplotlib axis object, optional
        If None, a new figure is created.
    cbar : bool, optional
        Add a colorbar to the plot.
    clim : List[float], optional
        Matplotlib color limit to use for plot.
    cmap : Matplotlib colormap object
        Optional colormap to use, passed as ``image.set_cmap(cmap)``.
    eps_alpha : float, optional
        If larger than zero, overlay the underlying relative permittivity
        distribution, with opacity defined by ``eps_alpha``.
    eps_freq : float or None, optional
        (Hz) frequency at which to query the permittivity. Should only be used
        for time monitors - for frequency monitors, the monitor frequency is
        used by default.

    Returns
    -------
    Matplotlib image object
    """

    mnt_data = self._mnt_data(monitor)
    _check_monitor(mnt_data, field)

    if ax is None:
        fig, ax = plt.subplots(1, constrained_layout=True)

    (fvals, coords, normal, norm_pos, cmap_eps, eps_freq, xlab, ylab, title) = _monitor_slice(
        self, mnt_data, sample_ind, normal, normal_ind, field, val, comp, eps_freq
    )

    im = _plot_field_2D(fvals, coords, val=val, ax=ax, cbar=cbar, clim=clim)
    zorder = im.get_zorder() + 1
    if eps_alpha > 0:
        _plot_eps_interp(
            self,
            normal,
            norm_pos,
            coords,
            frequency=eps_freq,
            ax=ax,
            cmap=cmap_eps,
            alpha=min(eps_alpha, 1),
            zorder=zorder,
        )

    # Override the colormap if provided
    if cmap is not None:
        im.set_cmap(cmap)

    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(title)

    return im


def _fmonitors_png(self, folder_path, val="int", comp="z"):
    """
    Export png images of 2D cross-sections for all frequency monitors in a
    given simulation. For 3D monitors, all 2D slices along the shortest
    dimension are exported.

    Parameters
    ----------
    folder_path : string
        Path in which the images will be exported.
    val : str, optional
        ``val`` supplied to :meth:`.viz_field_2D`.
    comp : str, optional
        ``comp`` suplied to :meth:`.viz_field_2D`.
    """

    fig = plt.figure(constrained_layout=True)

    for (ip, monitor) in enumerate(self.monitors):

        # Only export frequency monitors
        if isinstance(monitor, TimeMonitor):
            continue

        mnt_data = self._mnt_data(monitor)
        mdims = mnt_data.inds_end - mnt_data.inds_beg
        min_dir = np.argmin(mdims)
        normal = xyz_list[min_dir]

        for normal_ind in range(mdims[min_dir]):
            for (find, _) in enumerate(mnt_data.freqs):
                try:
                    ax = fig.add_subplot(111)
                    self.viz_field_2D(
                        monitor,
                        sample_ind=find,
                        normal=normal,
                        normal_ind=normal_ind,
                        val=val,
                        comp=comp,
                        ax=ax,
                        cbar=True,
                    )
                    fname = mnt_data.name
                    fname += "_find%d_nind%d.png" % (find, normal_ind)
                    plt.savefig(folder_path + fname)
                    plt.clf()
                except:
                    print(
                        "Could not export image for monitor index %d" % ip
                        + ", normal index %d, frequency index %d." % (normal_ind, find)
                    )

    plt.close(fig)
