import numpy as np

from .constants import fp_eps, float_, C_0
from .utils.log import log_and_raise, Tidy3DError
from .utils.geom import inside_box_coords


class Grid(object):
    def __init__(self):
        """
        Parameters
        ----------
        span : np.ndarray of shape (3, 2)
            Defines (xmin, xmax), (ymin, ymax), (zmin, zmax) of the simulation
            region, in micron.
        """

        # Coordinates of the grid boundaries, dimension Nd + 1.
        self.coords = [np.zeros((1,)), np.zeros((1,)), np.zeros((1,))]
        # Coordinates of the grid centers, dimension Nd.
        self.mesh = [np.zeros((0,)), np.zeros((0,)), np.zeros((0,))]

        # Smallest mesh step in each direction
        self.mesh_step = np.zeros((3,), dtype=float_)


    # Grid span (array of shape (3, 2)).
    @property
    def span(self):
        return np.array([[self.coords[d][0], self.coords[d][-1]] for d in range(3)])


    # Grid size (number of cells in each direction).
    @property
    def Nx(self):
        return self.mesh[0].size

    
    @property
    def Ny(self):
        return self.mesh[1].size


    @property
    def Nz(self):
        return self.mesh[2].size


    @property
    def Nxyz(self):
        return [m.size for m in self.mesh]


    # Coordinates of the various Yee grid locations
    @property
    def mesh_ex(self):
        return (self.mesh[0], self.coords[1][:-1], self.coords[2][:-1])

    
    @property
    def mesh_ey(self):
        return (self.coords[0][:-1], self.mesh[1], self.coords[2][:-1])


    @property
    def mesh_ez(self):
        return (self.coords[0][:-1], self.coords[1][:-1], self.mesh[2])


    @property
    def mesh_hx(self):
        return (self.coords[0][:-1], self.mesh[1], self.mesh[2])


    @property
    def mesh_hy(self):
        return (self.mesh[0], self.coords[1][:-1], self.mesh[2])


    @property
    def mesh_hz(self):
        return (self.mesh[0], self.mesh[1], self.coords[2][:-1])


    @property
    def psteps(self):
        """ Primal grid steps. """

        pst = []
        for d, coords in enumerate(self.coords):
            if coords.size > 1:
                pst.append(coords[1:] - coords[:-1])
            else:
                pst.append(np.zeros((0,)))

        return pst


    @property
    def dsteps(self):
        """ Dual grid steps. """

        dst = []
        for d, coords in enumerate(self.coords):
            if coords.size > 1:
                ctmp = np.hstack((2 * coords[0] - coords[1], coords))
                dst.append((ctmp[2:] - ctmp[:-2]) / 2)
            else:
                dst.append(np.zeros((0,)))

        return dst
    

    def set_mesh_step(self, mesh_step):
        ms_tmp = np.array(mesh_step)
        if ms_tmp.size == 1:
            self.mesh_step = ms_tmp * np.ones((3,), dtype=float_)
        elif ms_tmp.size == 3:
            self.mesh_step = ms_tmp.astype(float_)
        else:
            log_and_raise("'mesh_step' must be a float or an array of 3 floats.", ValueError)


    def init_uniform(self, mesh_step, span, symmetries=(0, 0, 0), center=True):
        """Initialize coords and mesh based on a constant mesh step.
        """

        self.set_mesh_step(mesh_step)

        # Slightly increase span to assure pixels at the edges are included.
        _span = np.copy(span)
        _span[:, 0] -= fp_eps * (span[:, 1] - span[:, 0])
        _span[:, 1] += fp_eps * (span[:, 1] - span[:, 0])

        # Initialize mesh points in x, y and z
        Nxyz = [
            np.int64((_span[0][1] - _span[0][0]) / self.mesh_step[0]),
            np.int64((_span[1][1] - _span[1][0]) / self.mesh_step[1]),
            np.int64((_span[2][1] - _span[2][0]) / self.mesh_step[2]),
        ]

        # Always take an even number of points if symmetry required
        for dim in range(3):
            if symmetries[dim] != 0 and Nxyz[dim] % 2 == 1:
                Nxyz[dim] += 1
        Nx, Ny, Nz = Nxyz

        xcent = (_span[0, 1] + _span[0, 0]) / 2
        ycent = (_span[1, 1] + _span[1, 0]) / 2
        zcent = (_span[2, 1] + _span[2, 0]) / 2

        if center==True:
            # Make simulation center coincide with beginning of Yee cell if N
            # even and center of Yee cell if N odd
            xr = np.arange(-((Nx + 1)//2), Nx//2 + 1)
            xgrid = xcent + self.mesh_step[0]*(xr + 0.5*(Nx%2))
            yr = np.arange(-((Ny + 1)//2), Ny//2 + 1)
            ygrid = ycent + self.mesh_step[1]*(yr + 0.5*(Ny%2))
            zr = np.arange(-((Nz + 1)//2), Nz//2 + 1)
            zgrid = zcent + self.mesh_step[2]*(zr + 0.5*(Nz%2))
        else:
            xgrid = _span[0, 0] + np.arange(0, Nx + 1)
            ygrid = _span[1, 0] + np.arange(0, Ny + 1)
            zgrid = _span[2, 0] + np.arange(0, Nz + 1)

        for dim, grid in enumerate([xgrid, ygrid, zgrid]):
            self.coords[dim] = np.copy(grid).astype(float_)
            self.mesh[dim] = (self.coords[dim][1:] + self.coords[dim][:-1])/2


    def load_coords(self, coords, symmetries=[0, 0, 0]):
        """Load coords based on an externally-defined grid coordinates."""

        for dim in range(3):
            if symmetries[dim] != 0 and coords[dim].size % 2 != 1:
                log_and_raise("Number of grid cells along a dimension with symmetry must be "
                    "divisible by two.",
                    Tidy3DError
                )

            self.coords[dim] = coords[dim]
            self.mesh[dim] = (coords[dim][1:] + coords[dim][:-1])/2

            # Mesh step stores the smallest step in each direction
            if coords[dim].size > 1:
                self.mesh_step[dim] = np.amin(coords[dim][1:] - coords[dim][:-1])
            else:
                self.mesh_step[dim] = 0


    def moveaxis(self, source, destination):
        """Shuffle grid axes from tuple ``source`` to tuple ``destination``.
        """
        dest_inv = np.argsort(destination)
        perm = np.array(source)[dest_inv]
        self.mesh_step = self.mesh_step[perm]
        coords, mesh = [], []
        for d in perm:
            coords.append(np.copy(self.coords[d]))
            mesh.append(np.copy(self.mesh[d]))

        self.coords = coords
        self.mesh = mesh


    def pad(self, nxmin=0, nxmax=0, nymin=0, nymax=0, nzmin=0, nzmax=0):
        """Pad each of the six sides of the subgrid with a number of cells with
        a mesh step equal to the nearest mesh step in that direction."""

        def pad_dmin(d, n_pad):
            if n_pad <= 0: return
            dl = self.coords[d][1] - self.coords[d][0]
            dlg = np.arange(n_pad, 0, -1) * dl
            self.coords[d] = np.hstack((self.coords[d][0] - dlg, self.coords[d]))
            self.mesh[d] = np.hstack((self.mesh[d][0] - dlg, self.mesh[d]))

        def pad_dmax(d, n_pad):
            if n_pad <= 0: return
            dl = self.coords[d][-1] - self.coords[d][-2]
            dlg = np.arange(1, n_pad + 1) * dl
            self.coords[d] = np.hstack((self.coords[d], self.coords[d][-1] + dlg))
            self.mesh[d] = np.hstack((self.mesh[d], self.mesh[d][-1] + dlg))

        pad_dmin(0, nxmin)
        pad_dmax(0, nxmax)
        pad_dmin(1, nymin)
        pad_dmax(1, nymax)
        pad_dmin(2, nzmin)
        pad_dmax(2, nzmax)


class SubGrid(Grid):
    """ A Grid defined as a subspace of another Grid. It can also be padded
    such that only a subspace of the SubGrid matches a subspace of the Grid.
    """

    def __init__(self, grid, span_inds=None, span=None):
        """Construct. Either ``span`` or ``span_inds`` must be provided as an
        array of size ``(3, 2)`` defining the span of the subgrid.
        
        Parameters
        ----------
        grid : Grid
            The global grid that the current grid is subbing.
        span_inds : np.ndarray or None, optional
            Starting and stopping indexes of the global grid cells to be taken.
        span : np.ndarray or None, optional
            (micron) The span within the global grid to be taken. Only used if
            ``span_inds`` is ``None``.
        """

        self.grid = grid

        if span_inds is None:
            indsx, indsy, indsz = inside_box_coords(span, grid.coords)
            span_inds = np.array([[inds[0], inds[1]] for inds in (indsx, indsy, indsz)])

        super().__init__()
        coords = [grid.coords[d][span_inds[d, 0]:span_inds[d, 1] + 1] for d in range(3)]
        self.load_coords(coords)
        self.span_inds = np.array(span_inds).astype(np.int64)
        
        # Keep track of padding on each side 
        self.n_pad = np.zeros((3, 2), dtype=np.int64)


    def pad(self, nxmin=0, nxmax=0, nymin=0, nymax=0, nzmin=0, nzmax=0):
        """Regular pad, but also keep track of how many cells we've padded.
        """

        super().pad(nxmin, nxmax, nymin, nymax, nzmin, nzmax)
        self.n_pad += np.array([[nxmin, nxmax], [nymin, nymax], [nzmin, nzmax]])


    def sinds_in_overlap(self, sinds):
        """For an array ``sinds`` of shape (Np, 3) of cells indexes in the
        subgrid, return the ones that are in the overlap region.
        """

        # Indexing such that 0 is the beginning of the overlapping region
        inds = sinds - self.n_pad[:, 0]

        Nd = self.span_inds[:, 1] - self.span_inds[:, 0]
        inds_in = np.prod(inds >= 0, axis=1).astype(bool)
        inds_in *= np.prod(inds < Nd, axis=1).astype(bool)

        return sinds[inds_in], inds_in


    def ginds_in_overlap(self, ginds):
        """For an array ``ginds`` of shape (Np, 3) of cells indexes in the
        global grid, return the ones that are in the overlap region.
        """

        inds_in = np.prod(ginds >= self.span_inds[:, 0], axis=1).astype(bool)
        inds_in *= np.prod(ginds < self.span_inds[:, 1], axis=1).astype(bool)

        return ginds[inds_in], inds_in


    def sinds2ginds(self, sinds, truncate=True):
        """For an array  ``sinds`` of shape (Np, 3) of cells indexes in the
        subgrid, return an array of cell indexes in the global grid. If 
        truncate == True and any indexes are in the padding of the subgrid,
        they are excluded.
        """

        inds = np.copy(sinds)
        if truncate == True:
            # Truncate to overlapping region
            inds, _ = self.sinds_in_overlap(inds)

        return inds + self.span_inds[:, 0] - self.n_pad[:, 0]


    def ginds2sinds(self, ginds, truncate=True):
        """For an array ``ginds`` of shape (Np, 3) of cells indexes in the
        global grid, return an array of cell indexes in the subgrid. If any
        indexes are outside the overlapping region, they are excluded.
        """

        inds = np.copy(ginds)
        if truncate == True:
            # Truncate to overlapping region
            inds, _ = self.ginds_in_overlap(inds)

        return inds - self.span_inds[:, 0] + self.n_pad[:, 0]

