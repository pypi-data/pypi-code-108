import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import logging

from ..constants import xyz_dict, xyz_list, fp_eps, pec_viz, pmc_viz, inf
from ..utils import log_and_raise
from ..material import PEC, PMC


def _eps_cmap(eps_r, alpha=1, cmap=None, clim=None):

    if cmap == None:
        cmap = "Greys"
    cm = mpl.cm.get_cmap(cmap, 256)

    # New map based on cmap with 256 colors and alpha as specified
    newmap = cm(np.linspace(0, 1, 256))
    newmap[:, 3] = alpha

    if clim is None:
        epsmax = np.amax(eps_r)
        # Get the minimum value that's larger than the PEC value
        cmin = np.amin(eps_r[eps_r > pec_viz], initial=epsmax)
        cl = [cmin, epsmax + 256 * fp_eps]
    else:
        cl = list(clim)

    # Make sure we're larger than the PEC value
    # PMC and PEC colors are appended below
    cl[0] = max(cl[0], pec_viz)

    bounds = np.hstack(
        (pmc_viz - 1, pec_viz - 1, pec_viz + 1, np.linspace(cl[0], cl[1], 256))
    )
    eps_cmap = np.vstack(([0, 0, 1, 1], [1, 0, 0, 1], newmap))

    if cl[0] <= 1.0 and cl[1] >= 1.0 and alpha < 1.:
        # Make eps = 1 completely transparent
        ind1 = int(np.argwhere(bounds < 1 - fp_eps)[-1])
        ind2 = int(np.argwhere(bounds <= 1 + fp_eps)[-1])

        if ind1 != ind2:
            bounds = np.delete(bounds, ind2)
            eps_cmap = np.delete(eps_cmap, [ind2], 0)

        c_insert = np.vstack((np.zeros((4,)), eps_cmap[ind2, :]))
        around_one = np.array([1 - fp_eps, 1 + fp_eps])
        bounds = np.insert(bounds, ind1 + 1, around_one)
        eps_cmap = np.insert(eps_cmap, [ind1 + 1], c_insert, 0)

    ncolors = bounds.shape[0] - 1
    norm = mpl.colors.BoundaryNorm(boundaries=bounds, ncolors=ncolors)

    return mpl.colors.ListedColormap(eps_cmap), norm, bounds


def _eps_patches(
    sim,
    normal,
    position,
    frequency=None
):

    str_epses = []
    str_patches = []
    disp_warning = False
    for struct in (sim.structures + sim._structures_sym):
        ps = struct._intersect_patches(axis=normal, position=position)
        if len(ps) > 0:
            if len(struct.material.poles) > 0 and frequency == None:
                disp_warning = True
            eps = np.real(struct.material.epsilon(freqs=frequency))[0]
            str_epses.append(eps)
            str_patches.append(ps)

    if disp_warning:
        logging.warning(
            "Permittivity value of dispersive materials taken "
            "as epsilon_infty. Consider providing 'frequency' for "
            "the plotting, or using 'viz_mat_2D' instead."
        )

    patches = []
    epses = []
    for eps, str_ps in zip(str_epses, str_patches):
        for patch in str_ps:
            epses.append(eps)
            patches.append(mpl.patches.Polygon(patch))

    return patches, epses


def _plot_eps(
    sim,
    normal,
    position,
    frequency=None,
    cmap=None,
    clim=None,
    ax=None,
    cbar=False,
    alpha=1.,
):
    """Plot the permittivity distribution in a cross-sectional plane at
    'position' along axis 'normal', using matplotlib patches.""" 

    patches, epses = _eps_patches(sim, normal, position, frequency)

    # Always include the background epsilon (1.) in the colormap
    epses_cm = np.array(epses + [1.])
    cmplot, norm, bounds = _eps_cmap(epses_cm, alpha=alpha, cmap=cmap, clim=clim)

    p = mpl.collections.PatchCollection(patches, norm=norm, cmap=cmplot)
    p.set_array(np.array(epses))
    ax.add_collection(p)

    if cbar:
        plt.colorbar(p, ax=ax, boundaries=bounds[3:])

    return p


def _plot_eps_interp(
    sim,
    normal,
    position,
    coords,
    frequency=None,
    cmap=None,
    clim=None,
    ax=None,
    cbar=False,
    alpha=1.,
    zorder=2,
):
    """Plot the permittivity distribution in a cross-sectional plane at
    'position' along axis 'normal', using imshow after interpolating
    on a discretized grid based on 'coords'. The smallest grid step in
    'coords' along a given dimension is used to make a uniform mesh along
    that dimension.""" 

    patches, epses = _eps_patches(sim, normal, position, frequency)

    # Always include the background epsilon in the colormap
    eps_bg = 1.
    epses_cm = np.array(epses + [eps_bg])
    cmplot, norm, bounds = _eps_cmap(epses_cm, alpha=alpha, cmap=cmap, clim=clim)

    xy_interp = []
    for c in coords:
        dl = np.amin(c[1:] - c[:-1])
        cbeg = (c[0] + c[1])/2 - fp_eps
        cend = (c[-2] + c[-1])/2 + fp_eps
        # Refine dl if needed to get at least 600 pixels
        npix = (cend - cbeg) // dl
        dl /= np.ceil(600 / npix)
        xy_interp.append(np.arange(cbeg, cend, dl))

    meshgrid = np.meshgrid(*xy_interp)
    Nx, Ny = meshgrid[0].shape
    eps_interp = eps_bg * np.ones((Nx, Ny))
    xy = np.stack((meshgrid[0].ravel(), meshgrid[1].ravel()), axis=1)

    for patch, eps in zip(patches, epses):
        # if np.abs(eps - eps_bg) < fp_eps:
        #     continue

        pts_in = patch.contains_points(xy).reshape(Nx, Ny)
        eps_interp[pts_in==True] = eps

    extent = [coords[0][0], coords[0][-1], coords[1][0], coords[1][-1]]
    im = ax.imshow(eps_interp, norm=norm, cmap=cmplot, extent=extent, origin='lower', zorder=zorder)

    if cbar:
        plt.colorbar(im, ax=ax, boundaries=bounds[3:])

    return im


def _mat_cmap(alpha=1., cmap=None):

    if cmap == None:
        # Define a custom colormap by picking colors not used for other stuff
        m0 = mpl.cm.get_cmap("tab20")(np.linspace(0, 1, 20))
        m1 = mpl.cm.get_cmap("tab20b")(np.linspace(0, 1, 20))
        m2 = mpl.cm.get_cmap("tab20c")(np.linspace(0, 1, 20))
        mc = np.vstack((m0, m1, m2))
        pick_c = [20, 32, 36, 28, 56, 22, 34, 38, 29, 58, 21, 33, 37, 10, 57]
        pick_c += [23, 35, 39, 11, 59]
        newmap = mc[pick_c, :]

        # ncl colors total, repeating if more materials present
        ncl = newmap.shape[0]
        newmap = np.tile(newmap, (200 // ncl + 1, 1))
        newmap = newmap[:200, :]
    else:
        cm = mpl.cm.get_cmap(cmap)
        # New map based on cmap for up to 200 materials
        newmap = cm(np.linspace(0, 1, 200))
        newmap[:, 3] = alpha

    bounds = np.hstack(
        (pmc_viz - 1, pec_viz - 1, -1.5, np.arange(0, 200) - 0.5)
    )
    mat_cmap = np.vstack(([0, 0, 1, 1], [1, 0, 0, 1], [0, 0, 0, 0], newmap))
    norm = mpl.colors.BoundaryNorm(boundaries=bounds, ncolors=203)

    return mpl.colors.ListedColormap(mat_cmap), norm, bounds, newmap


def _plot_mat(
    sim,
    normal,
    position,
    cmap=None,
    ax=None,
    extent=None,
    cbar=False,
    legend=False,
    alpha=1.,
):

    mat_names = []
    mat_inds = []
    str_patches = []
    for (istr, struct) in enumerate(sim.structures + sim._structures_sym):
        ps = struct._intersect_patches(axis=normal, position=position)
        if len(ps) > 0:
            if isinstance(struct.material, PEC):
                mat_inds.append(pec_viz)
            elif isinstance(struct.material, PMC):
                mat_inds.append(pmc_viz)
            else:
                mat_ind = sim._mat_inds[istr]
                mat_inds.append(mat_ind)
                mat_names.append(sim._mat_names[mat_ind])
            str_patches.append(ps)

    cmplot, norm, bounds, newmap = _mat_cmap(alpha=alpha, cmap=cmap)
    patches = []
    colors = []
    for mat_ind, str_ps in zip(mat_inds, str_patches):
        for patch in str_ps:
            colors.append(mat_ind)
            patches.append(mpl.patches.Polygon(patch))
    p = mpl.collections.PatchCollection(patches, norm=norm, cmap=cmplot)
    p.set_array(np.array(colors))
    ax.add_collection(p)

    if cbar:
        plt.colorbar(p, ax=ax, boundaries=bounds[2:])

    if legend == True:
        labels = []
        for imat, mat in enumerate(mat_names):
            ax.plot(extent[1] + 1, extent[3] + 1, "s", color=newmap[imat, :])
            labels.append(mat)

        ax.legend(labels, borderaxespad=0.0, bbox_to_anchor=(1.02, 1))

    return p


def _get_inside(objects, coords, min_pts=1):
    """Get a mask defining points inside a list of objects.

    Parameters
    ----------
    objects : list of Source or Monitor objects
    coords : tuple of 3 1D arrays

    Returns
    -------
    mask : np.ndarray
        Array indicating if the centers of the ``coords`` are inside any of the
        Sources or Monitors in the list.
    """

    Nx, Ny, Nz = [c.size - 1 for c in coords]

    mask = np.zeros((Nx, Ny, Nz))
    for obj in objects:
        mtmp = obj._inside(coords)
        mask[mtmp > 0] = 1

    return mask


def _plot_structures(
    sim,
    val="eps",
    normal="x",
    position=0.0,
    ax=None,
    cbar=False,
    clim=None,
    source_alpha=0.3,
    monitor_alpha=0.3,
    pml_alpha=0.2,
    frequency=None,
    legend=False,
):
    """Plot either the real part of the permittivity (val=='eps') or the
    material index of the structures (val=='mat')."""

    grid = sim.grid
    position = float(position)

    if ax is None:
        fig, ax = plt.subplots(1, constrained_layout=True)

    ax.set_aspect('equal')

    # Get normal and cross-section axes indexes
    norm = xyz_dict[normal]
    cross = [0, 1, 2]
    cross.pop(norm)

    """ Get mesh for permittivity discretization.
    Use ``coords`` for the source/monitor plotting to ensure that 
    zero-size dimensions are taken to be in the same Yee cell as ``position``.
    We always break the symmetry such that if an object center is 
    sitting exactly on a coord, it will be taken to the right. """
    coords = [[], [], []]
    cnorm = grid.coords[norm] - fp_eps
    ind = np.nonzero((position >= cnorm[:-1]) * (position < cnorm[1:]))[0]
    if ind.size == 0:
        log_and_raise(
            "Plane position outside of simulation domain.", RuntimeError
        )
    else:
        ind = ind[0]

    coords[norm] = np.array([cnorm[ind], cnorm[ind + 1]])
    for cind in cross:
        coords[cind] = grid.coords[cind]

    # Set axes xlim and ylim
    sim_xlim = (grid.mesh[cross[0]][0], grid.mesh[cross[0]][-1])
    sim_ylim = (grid.mesh[cross[1]][0], grid.mesh[cross[1]][-1])

    # Define axes extent, labels and title
    extent = list(sim_xlim) + list(sim_ylim)
    x_lab = xyz_list[cross[0]]
    y_lab = xyz_list[cross[1]]
    ax_tit = x_lab + y_lab
    ax_tit += "-plane at " + xyz_list[norm] + "=%1.2eum" % position

    # Transparent color
    transp = (0, 0, 0, 0)
    # Colors for monitors, sources, pml, and border
    mnt_color = (236 / 255, 203 / 255, 32 / 255)
    src_color = (78 / 255, 145 / 255, 78 / 255)
    pml_color = (229 / 255, 127 / 255, 25 / 255)
    pbc_color = (75 / 255, 0, 130 / 255)

    if val == "eps":
        _plot_eps(sim, normal, position, frequency, clim=clim, ax=ax, cbar=cbar, alpha=1.)

    elif val == "mat":
        _plot_mat(sim, normal, position, ax=ax, extent=extent, legend=legend, cbar=cbar)
 
    ax.set_xlabel(x_lab + " (um)")
    ax.set_ylabel(y_lab + " (um)")
    ax.set_title(ax_tit)

    # Plot simulation domain borders depending on boundaries
    npml = sim.Npml[[cross[0], cross[1]], :]
    # In order of bottom, right, top, left
    border_pmls = [npml[1, 0], npml[0, 1], npml[1, 1], npml[0, 0]]
    x_border = [extent[0], extent[1], extent[1], extent[0], extent[0]]
    y_border = [extent[2], extent[2], extent[3], extent[3], extent[2]]
    for ib, bpml in enumerate(border_pmls):
        if bpml > 0:
            border_color = pml_color
        else:
            border_color = pbc_color
        ax.plot(
            [x_border[ib], x_border[ib + 1]],
            [y_border[ib], y_border[ib + 1]],
            color=border_color,
        )

    def squeeze_mask(mask, axis):
        inds = [slice(None), slice(None), slice(None)]
        inds[axis] = 0
        return np.squeeze(mask[tuple(inds)])

    if monitor_alpha > 0:
        mnt_alpha = min(monitor_alpha, 1)
        mnt_c = list(mnt_color)
        mnt_c.append(mnt_alpha)
        for monitor in sim.monitors:
            if np.any(monitor._inside(coords)):
                xy = [monitor.span[cross[0], 0], monitor.span[cross[1], 0]]
                width = monitor.span[cross[0], 1] - monitor.span[cross[0], 0]
                height = monitor.span[cross[1], 1] - monitor.span[cross[1], 0]
                if width==0 and height==0:
                    # special treatment for 0D
                    xy[0] -= sim.grid.mesh_step[cross[0]]/2
                    xy[1] -= sim.grid.mesh_step[cross[1]]/2
                    width = sim.grid.mesh_step[cross[0]]
                    height = sim.grid.mesh_step[cross[1]]

                rect = mpl.patches.Rectangle(
                    xy, width, height, ec=mnt_c, fc=mnt_c, lw=3
                )
                ax.add_patch(rect)

    if source_alpha > 0:
        src_alpha = min(source_alpha, 1)
        src_c = list(src_color)
        src_c.append(src_alpha)
        for source in sim.sources:
            if np.any(source._inside(coords)):
                xy = [source.span[cross[0], 0], source.span[cross[1], 0]]
                width = source.span[cross[0], 1] - source.span[cross[0], 0]
                height = source.span[cross[1], 1] - source.span[cross[1], 0]
                if width==0 and height==0:
                    # special treatment for 0D
                    xy[0] -= sim.grid.mesh_step[cross[0]]/2
                    xy[1] -= sim.grid.mesh_step[cross[1]]/2
                    width = sim.grid.mesh_step[cross[0]]
                    height = sim.grid.mesh_step[cross[1]]

                rect = mpl.patches.Rectangle(
                    xy, width, height, ec=src_c, fc=src_c, lw=3
                )
                ax.add_patch(rect)

    if pml_alpha > 0:
        pml_alpha = min(pml_alpha, 1)
        pml_c = list(pml_color)
        pml_c.append(pml_alpha)

        w1 = sim.span_in[cross[0], 0] - sim.span[cross[0], 0]
        w2 = sim.span[cross[0], 1] - sim.span[cross[0], 0]
        h1 = sim.span_in[cross[1], 0] - sim.span[cross[1], 0]
        h2 = sim.span[cross[1], 1] - sim.span[cross[1], 0]

        xy = (sim.span[cross[0], 0], sim.span[cross[1], 0])
        rect = mpl.patches.Rectangle(xy, w1, h2, ec=None, fc=pml_c)
        ax.add_patch(rect)

        xy = (sim.span_in[cross[0], 1], sim.span[cross[1], 0])
        rect = mpl.patches.Rectangle(xy, w1, h2, ec=None, fc=pml_c)
        ax.add_patch(rect)

        xy = (sim.span[cross[0], 0], sim.span[cross[1], 0])
        rect = mpl.patches.Rectangle(xy, w2, h1, ec=None, fc=pml_c)
        ax.add_patch(rect)

        xy = (sim.span[cross[0], 0], sim.span_in[cross[1], 1])
        rect = mpl.patches.Rectangle(xy, w2, h1, ec=None, fc=pml_c)
        ax.add_patch(rect)

    ax.set_xlim((extent[0], extent[1]))
    ax.set_ylim((extent[2], extent[3]))

    return ax


def viz_eps_2D(
    self,
    normal="x",
    position=0.0,
    ax=None,
    cbar=False,
    clim=None,
    source_alpha=0.3,
    monitor_alpha=0.3,
    pml_alpha=0.2,
    frequency=None,
):
    """Plot the real part of the relative permittivity distribution of a
    2D cross-section of the simulation.

    Parameters
    ----------
    normal : {'x', 'y', 'z'}
        Axis normal to the cross-section plane.
    position : float, optional
        Position offset along the normal axis.
    ax : Matplotlib axis object, optional
        If ``None``, a new figure is created.
    cbar : bool, optional
        Add a colorbar to the plot.
    clim : List[float], optional
        Matplotlib color limit to use for plot.
    source_alpha : float, optional
        If larger than zero, overlay all sources in the simulation,
        with opacity defined by ``source_alpha``.
    monitor_alpha : float, optional
        If larger than zero, overlay all monitors in the simulation,
        with opacity defined by ``monitor_alpha``.
    pml_alpha : float, optional
        If larger than zero, overlay the PML boundaries of the simulation,
        with opacity defined by ``pml_alpha``.
    frequency : float or None, optional
        (Hz) frequency at which to query the permittivity. If
        ``None``, the instantaneous :math:`\\epsilon_\\infty` is used.

    Returns
    -------
    Matplotlib axis object

    Note
    ----
    The plotting is discretized at the center positions of the Yee grid and
    is for illustrative purposes only. It does not exactly match the
    discretization used in the solver.
    """

    return _plot_structures(
        self,
        "eps",
        normal=normal,
        position=position,
        ax=ax,
        cbar=cbar,
        clim=clim,
        source_alpha=source_alpha,
        monitor_alpha=monitor_alpha,
        pml_alpha=pml_alpha,
        frequency=frequency,
    )


def viz_mat_2D(
    self,
    normal="x",
    position=0.0,
    ax=None,
    source_alpha=0.3,
    monitor_alpha=0.3,
    pml_alpha=0.2,
    legend=False,
):
    """Visualize the structures in a 2D cross-section of the simulation
    using a fake-color coding based on material index in the list of materials.

    Parameters
    ----------
    normal : {'x', 'y', 'z'}
        Axis normal to the cross-section plane.
    position : float, optional
        Position offset along the normal axis.
    ax : Matplotlib axis object, optional
        If ``None``, a new figure is created.
    source_alpha : float, optional
        If larger than zero, overlay all sources in the simulation,
        with opacity defined by ``source_alpha``.
    monitor_alpha : float, optional
        If larger than zero, overlay all monitors in the simulation,
        with opacity defined by ``monitor_alpha``.
    pml_alpha : float, optional
        If larger than zero, overlay the PML boundaries of the simulation,
        with opacity defined by ``pml_alpha``.
    legend : bool, optional
        If ``True``, a legend with the material names is shown.

    Returns
    -------
    Matplotlib axis object

    Note
    ----
    The plotting is discretized at the center positions of the Yee grid and
    is for illustrative purposes only. It does not exactly match the
    discretization used in the solver.
    """

    return _plot_structures(
        self,
        "mat",
        normal=normal,
        position=position,
        ax=ax,
        source_alpha=source_alpha,
        monitor_alpha=monitor_alpha,
        pml_alpha=pml_alpha,
        legend=legend,
    )


def _structure_png(self, folder_path, val="mat", aspect_ratio=None):
    """
    Export png images of 2D cross-sections of the simulation at the domain
    center in x, y, and z.

    Parameters
    ----------
    folder_path : string
        Path in which the images will be exported.
    val : str, optional
        'eps' or 'mat', whether to plot based on permittivity or material.
    aspect_ratio : float or None
        Fix the width/height image ratio. If ``None``, the smallest aspect
        ratio of the three plots is used in all.
    """

    figs = [
        plt.figure(0, constrained_layout=True),
        plt.figure(1, constrained_layout=True),
        plt.figure(2, constrained_layout=True),
    ]
    ims = []
    clims = []
    norm_ims = []  # stores the indexes for successfully plotted images

    if not aspect_ratio:
        # Take the smallest aspect ratio
        sim_ars = [
            self.size[1] / self.size[2],
            self.size[0] / self.size[2],
            self.size[0] / self.size[1],
        ]
        aspect_ratio = np.min(sim_ars)

    for norm_ind, normal in enumerate(["x", "y", "z"]):
        cinds = [0, 1, 2]
        cinds.pop(norm_ind)
        ax = figs[norm_ind].add_subplot(111)
        sim_width = self.size[cinds[0]]
        sim_height = self.size[cinds[1]]
        sim_aspect = sim_width / sim_height
        if sim_aspect > aspect_ratio:
            new_height = sim_width / aspect_ratio
            ax.set_ylim(-new_height / 2, new_height / 2)
        elif sim_aspect < aspect_ratio:
            new_width = sim_height * aspect_ratio
            ax.set_xlim(-new_width / 2, new_width / 2)
        try:
            if val == "eps":
                im = self.viz_eps_2D(normal, self.center[norm_ind], ax)
                eps_r = np.array(im.get_array())
                epsmax = np.amax(eps_r)
                epsmin = np.amin(eps_r[eps_r > pec_viz], initial=epsmax)
                clims.append([epsmin, epsmax])
            elif val == "mat":
                im = self.viz_mat_2D(normal, self.center[norm_ind], ax)
            ims.append(im)
            norm_ims.append(norm_ind)
        except:
            logging.warning(f"Could not export image for normal {normal}!")

    if val == "eps":
        # Set the same clims in all plots
        clims = np.array(clims)
        clim_glob = [np.amin(clims[:, 0]), np.amax(clims[:, 1])]
        # Get a new color norm based on the global clims. eps_r is irrelevant.
        _, norm, _ = _eps_cmap(eps_r, clim=clim_glob)

    # Set new clims and save figures
    for norm_ind, normal in enumerate(["x", "y", "z"]):
        fname = "simulation_%scent.png" % normal
        plt.figure(norm_ind)
        if norm_ind in norm_ims:
            # if val == "eps":
            #     ims[norm_ims.index(norm_ind)].set_norm(norm)
            plt.savefig(folder_path + fname, dpi=150)
        plt.close(figs[norm_ind])
