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

from omfit_classes.omfit_ascii import OMFITascii

__all__ = ['OMFITfocusboundary', 'OMFITfocusharmonics']


class OMFITfocusboundary(SortedDict, OMFITascii):
    """
    OMFITobject used to interface with boundary ascii files used in FOCUS.

    :param filename: filename passed to OMFITascii class

    All additional key word arguments passed to OMFITascii

    """

    def __init__(self, filename, **kwargs):
        SortedDict.__init__(self)
        OMFITascii.__init__(self, filename, **kwargs)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        """Load the file and parse it into a sorted dictionary"""
        with open(self.filename, 'r') as f:
            lines = f.readlines()

        # allow class to be initialized with a new (empty) file
        if len(lines) == 0:
            return

        # remove any empty lines someone might have thought harmless
        lines = [l for l in lines if len(l.translate({ord(char): '' for char in ' \n\t\r'})) > 0]

        # first is a single line of defining parameters
        keys = ['bmn', 'bnfp', 'nbf']  # lines[0].replace('#', '').split()
        vals = list(map(int, lines[1].split()))
        for k, v in zip(keys, vals):
            self[k.lower()] = v

        # then comes the plasma boundary
        start, end = 4, 4 + self['bmn']
        keys = ['n', 'm', 'rbc', 'rbs', 'zbc', 'zbs']  # lines[start - 1].replace('#', '').split()
        vals = []
        for l in lines[start:end]:
            vals.append(list(map(np.float, l.split())))
        vals = np.array(vals).T
        self['boundary'] = SortedDict()
        for k, v in zip(keys, vals):
            if k in ('n', 'm'):
                self['boundary'][k.lower()] = v.astype(np.int)
            else:
                self['boundary'][k.lower()] = v

        # finally there is the bnormal coefficients
        start, end = end + 2, end + 2 + self['nbf']
        keys = ['n', 'm', 'bnc', 'bns']  # lines[start - 1].replace('#', '').split()
        vals = []
        for l in lines[start:end]:
            vals.append(list(map(np.float, l.split())))
        vals = np.array(vals).T
        self['bn'] = SortedDict()
        if self['nbf'] > 0:
            for k, v in zip(keys, vals):
                if k in ('n', 'm'):
                    self['bn'][k.lower()] = v.astype(np.int)
                else:
                    self['bn'][k.lower()] = v
        else:
            for k in keys:
                self['bn'][k] = np.array([])

        return

    @dynaSave
    def save(self):
        """Write the data in standard ascii format"""
        with open(self.filename, 'w') as f:
            # write the defining parameters
            f.write('#{:>11}{:>12}{:>12}\n'.format('bmn', 'bnfp', 'nbf'))
            f.write('{:12}{:12}{:12}\n'.format(self['bmn'], self['bnfp'], self['nbf']))

            # write the plasma boundary info
            f.write('#--------- plasma boundary --------\n')
            f.write('#{:>5}{:>6}{:>17}{:>17}{:>17}{:>17}\n'.format(*list(self['boundary'].keys())))
            for i in range(self['bmn']):
                f.write(
                    '{:6}{:6}{:17.9e}{:17.9e}{:17.9e}{:17.9e}\n'.format(
                        self['boundary']['n'][i],
                        self['boundary']['m'][i],
                        self['boundary']['rbc'][i],
                        self['boundary']['rbs'][i],
                        self['boundary']['zbc'][i],
                        self['boundary']['zbs'][i],
                    )
                )

            # write the normal field info
            f.write(' #--------- bn harmonics --------\n')
            f.write(' #{:>4}{:>6}{:>17}{:>17}\n'.format(*list(self['bn'].keys())))
            for i in range(self['nbf']):
                f.write(
                    '{:6}{:6}{:17.9e}{:17.9e}\n'.format(self['bn']['n'][i], self['bn']['m'][i], self['bn']['bnc'][i], self['bn']['bns'][i])
                )
        return

    @dynaLoad
    def plot(self, nd=3, ax=None, cmap='RdBu_r', vmin=None, vmax=None, colorbar=True, nzeta=60, ntheta=120, force_zeta=None, **kwargs):
        r"""
        Plot the normal field on the 3D boundary surface or as a contour by angle.

        :param nd: int. Choose 3 to plot a surface in 3D, and 2 to plot a contour in angle.

        :param ax: Axes. Axis into which the plot will be made.

        :param cmap: string. A valid matplolib color map name.

        :param vmin: float. Minimum of the color scaling.

        :param vmax: float. Maximum of the color scaling.

        :param colorbar: bool. Draw a colorbar.

        :param nzeta: int. Number of points in the toroidal angle.

        :param ntheta: int. Number of points in the poloidal angle (must be integer multiple of nzeta).

        :param force_zeta: list. Specific toroidal angle points (in degrees) used instead of nzeta grid. When nd=1, defaults to [0].

        :param \**kwargs: dict. All other key word arguments are passed to the mplot3d plot_trisurf function.

        :return: Figure.

        """
        if nd == 3:
            projection = '3d'
        else:
            projection = None
        if ax is None:
            # extra logic to handle OMFIT's auto-figure making when double-clicked in tree
            f = pyplot.gcf()
            if len(f.axes):
                # normal situation in which existing figures should be respected and left alone
                try:
                    f, ax = pyplot.subplots(subplot_kw={'aspect': 'equal', 'projection': projection})
                except NotImplementedError:
                    pyplot.close(pyplot.gcf())  # will have opened a figure than failed to set the aspect
                    f, ax = pyplot.subplots(subplot_kw={'projection': projection})
            else:
                # OMFIT (or the gcf needed to check OMFIT) made a empty figure for us
                try:
                    ax = f.add_subplot(111, aspect='equal', projection=projection)
                except NotImplementedError:
                    ax = f.add_subplot(111, projection=projection)
            # aesthetics
            if nd == 3:
                ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
                ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
                ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
                ax.set_xlabel('x (m)')
                ax.set_ylabel('y (m)')
                ax.set_zlabel('z (m)')
                ax.set_axis_off()
        else:
            f = ax.get_figure()

        # ensure multiples for trisurf
        if ntheta > nzeta:
            ntheta = int(np.round(float(ntheta) / nzeta)) * nzeta
        else:
            nzeta = int(np.round(float(nzeta) / ntheta)) * ntheta

        zeta = np.linspace(0, 2 * np.pi, nzeta, endpoint=(nd == 3)).reshape(1, nzeta)
        theta = np.linspace(-np.pi, np.pi, ntheta, endpoint=(nd == 3)).reshape(ntheta, 1)

        # use specific zeta values (usually for 1D plot)
        if nd == 1 and force_zeta is None:
            force_zeta = [0]
        if force_zeta is not None:
            force_zeta = np.deg2rad(np.atleast_1d(force_zeta))
            zeta = force_zeta.reshape(1, len(force_zeta))

        # inverse Fourier transform the boundary
        bo = self['boundary']
        r, z = 0, 0
        for i in range(self['bmn']):
            r += bo['rbc'][i] * np.cos(bo['m'][i] * theta - bo['n'][i] * zeta) + bo['rbs'][i] * np.sin(
                bo['m'][i] * theta - bo['n'][i] * zeta
            )
            z += bo['zbc'][i] * np.cos(bo['m'][i] * theta - bo['n'][i] * zeta) + bo['zbs'][i] * np.sin(
                bo['m'][i] * theta - bo['n'][i] * zeta
            )
        x = r * np.cos(zeta)
        y = r * np.sin(zeta)

        # inverse Fourier transform the normal field
        c = 0 * zeta * theta
        if 'bn' in self:
            bn = self['bn']
            for i in range(self['nbf']):
                c += bn['bnc'][i] * np.cos(bn['m'][i] * theta - bn['n'][i] * zeta) + bn['bns'][i] * np.sin(
                    bn['m'][i] * theta - bn['n'][i] * zeta
                )

        if nd == 3:
            # manually map values to colors
            norm = pyplot.Normalize(vmin=vmin, vmax=vmax)
            colors = getattr(pyplot.cm, cmap)(norm(c))
            # manually make a mappable object for the colorbar
            sm = pyplot.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array(c)

            # 3d colored surface plot
            # im = ax.plot_surface(x, y, z, rstride=1, cstride=1, facecolors=colors, linewidth=0,
            #                      antialiased=False, shade=True, **kwargs)
            # trisurf creates a smoother surface, but coloring it properly is harder
            # it is somehow much faster (3 times faster for 90 by 180)
            # it can mess up if the number of points is not a multiple of three
            x, y, z = [np.ravel(x) for x in (x, y, z)]
            colors = list(map(matplotlib.colors.rgb2hex, colors.reshape(-1, 4)))
            tri = matplotlib.tri.Triangulation(*list(map(np.ravel, np.meshgrid(theta.ravel(), zeta.ravel()))))
            im = ax.plot_trisurf(
                x,
                y,
                z,
                triangles=tri.triangles,
                linewidth=0,
                facecolors=colors,
                antialiased=False,
                shade=True,
                cmap=getattr(pyplot.cm, cmap),
                **kwargs,
            )
            # im.set_facecolors(colors)  # does not work
            colors = np.mean(np.ravel(c)[tri.triangles], axis=1)
            im.set_array(colors)
            # im.autoscale()

            if colorbar:
                cb = f.colorbar(sm, ax=ax, shrink=0.8)
                cb.set_label('Normal Field (T)')

            # force equal aspect
            bound = np.max(np.hstack((np.abs(x.ravel()), np.abs(y.ravel()), np.abs(z.ravel())))) * 0.6
            ax.set_xlim(-bound, bound)
            ax.set_ylim(-bound, bound)
            ax.set_zlim(-bound, bound)
            ax.auto_scale_xyz((-bound, bound), (-bound, bound), (-bound, bound))

        elif nd == 2:
            # "unraveled" contour plot
            im = ax.imshow(c, origin='lower', extent=[0, 360, -180, 180], interpolation='gaussian', cmap=cmap, vmin=vmin, vmax=vmax)
            if colorbar:
                cb = f.colorbar(im)
                cb.set_label('Normal Field (T)')
            ax.set_xlabel('zeta (deg.)')
            ax.set_ylabel('theta (deg.)')
        elif nd == 1:
            for i, zeta_i in enumerate(zeta[0, :]):
                xi, yi, zi, ci = [val[:, i] for val in (x, y, z, c)]
                ri = np.sqrt(xi ** 2 + yi ** 2)
                # connect the endpoints
                ri = np.hstack((ri, ri[:1]))
                zi = np.hstack((zi, zi[:1]))
                ci = np.hstack((ci, ci[:1]))
                # make a line with changing color (https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/multicolored_line.html)
                points = np.array([ri, zi]).T.reshape(-1, 1, 2)
                segments = np.concatenate([points[:-1], points[1:]], axis=1)
                norm = pyplot.Normalize(c.min(), c.max())
                lc = matplotlib.collections.LineCollection(segments, cmap=cmap, norm=norm)
                # Set the values used for colormapping
                lc.set_array(ci)
                lw = kwargs.get('linewidth', kwargs.get('lw', rcParams['lines.linewidth'] + 3))
                lc.set_linewidth(lw)
                (l,) = ax.plot(ri, zi, label=r'$\zeta$ = ' + '{:.0f}'.format(np.rad2deg(zeta_i)), lw=lw / 4)
                if not all(ci == 0):
                    im = ax.add_collection(lc)
                else:
                    colorbar = False
                    im = l
            ax.autoscale(tight=False)
            ax.legend(loc=0, frameon=False, hide_markers=True, text_same_color=True)
            if colorbar:
                cb = f.colorbar(im, ax=ax)
                cb.set_label('Normal Field (T)')
        else:
            raise ValueError("Key word argument 'nd' must be 1, 2, or 3.")

        return im


class OMFITfocusharmonics(SortedDict, OMFITascii):
    """
    OMFITobject used to interface with harmonics ascii files used in FOCUS.

    :param filename: filename passed to OMFITascii class

    All additional key word arguments passed to OMFITascii

    """

    def __init__(self, filename, **kwargs):
        SortedDict.__init__(self)
        OMFITascii.__init__(self, filename, **kwargs)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        """Load the file and parse it into a sorted dictionary"""
        with open(self.filename, 'r') as f:
            lines = f.readlines()

        # allow class to be initialized with a new (empty) file
        if len(lines) == 0:
            return

        # remove any empty lines someone might have thought harmless
        lines = [l for l in lines if len(l.translate({ord(char): '' for char in ' \n\t\r'})) > 0]

        # first is a single line of defining parameters
        self['nbf'] = int(lines[1])
        # rest is one big table
        vals = np.array([list(map(np.float, l.split())) for l in lines[3:]])
        self['n'] = vals[:, 0].astype(int)
        self['m'] = vals[:, 1].astype(int)
        self['bnc'] = vals[:, 2]
        self['bns'] = vals[:, 3]
        self['w'] = vals[:, 4]

    @dynaSave
    def save(self):
        """Write the data in standard ascii format"""
        with open(self.filename, 'w') as f:
            # write the defining parameters
            f.write('#{:>5}\n'.format('nbf'))
            f.write('{:12}\n'.format(self['nbf']))

            # write the normal field info
            f.write('#{:>5}{:>6}{:>17}{:>17}{:>17}\n'.format('n', 'm', 'bnc', 'bns', 'w'))
            for i in range(self['nbf']):
                f.write(
                    '{:6}{:6}{:17.9e}{:17.9e}{:17.9e}\n'.format(self['n'][i], self['m'][i], self['bnc'][i], self['bns'][i], self['w'][i])
                )
        return

    @dynaLoad
    def plot(self, axes=None, **kwargs):
        r"""
        Plot the normal field spectra and weighting.

        :param ax: list. 3 Axes into which the amplitude, phase, and weight plots will be made.

        :param \**kwargs: dict. All other key word arguments are passed to the plot function.

        :return: list. All the lines plotted.

        """
        if axes is None:
            # extra logic to handle OMFIT's auto-figure making when double-clicked in tree
            f = pyplot.gcf()
            if len(f.axes):
                # normal situation in which existing figures should be respected and left alone
                f, axes = pyplot.subplots(3, 1, sharex=True)
            else:
                # OMFIT (or the gcf needed to check OMFIT) made a empty figure for us
                ax = f.add_subplot(3, 1, 1)
                axes = np.array([ax, f.add_subplot(3, 1, 2, sharex=ax), f.add_subplot(3, 1, 3, sharex=ax)])
        else:
            f = axes[0].get_figure()

        c = self['bnc'] - 1j * self['bns']

        lines = []
        prefix = kwargs.pop('label', '')
        if prefix:
            prefix = prefix + ', '
        for n in sorted(set(self['n'])):
            lbl = prefix + 'n = {:}'.format(n)
            i = np.where(self['n'] == n)[0]
            lines += axes[0].plot(self['m'][i], np.abs(c[i]), label=lbl, **kwargs)
            lines += axes[1].plot(self['m'][i], np.angle(c[i], deg=True), label=lbl, **kwargs)
            lines += axes[2].plot(self['m'][i], self['w'], label=lbl, **kwargs)

        # aesthetics
        axes[0].set_ylabel('Amplitude (T)')
        axes[1].set_ylabel('Phase (deg.)')
        axes[2].set_ylabel('Weight')
        for a in axes:
            a.set_xlabel('m')
            a.legend(loc=0).draggable(True)

        return lines
