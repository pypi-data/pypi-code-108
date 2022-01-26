import numpy as np
import h5py

from ..constants import float_, pec_val, xyz_dict
from ..utils import inside_box_coords, listify, log_and_raise
from ..utils.log import Tidy3DError
from ..utils.em import fix_pec
from ..grid import SubGrid
from .solver import compute_modes as get_modes
from .dot_product import dot_product

class ModePlane(object):
    """2D plane for computation of modes used in ModeSource and ModeMonitor.
    The coordinate system of the ModePlane.grid is rotated such that the 
    z-axis is normal to the plane.
    """
    def __init__(self, span, norm_ind):
        """Construct.
        
        Parameters
        ----------
        span : np.ndarray of shape (3, 2)
            (micron) Defines (xmin, xmax), (ymin, ymax), (zmin, zmax) of the 
            mode plane.
        norm_ind : int
            Specifies the normal direction. We must then also have 
            ``span[mode_ind, 0] = span[mode_ind, 1]``.
        """
        self.span = span
        self.norm_ind = norm_ind
        
        """ Everything is stored in axes oriented as 
        (in_plane1, in_plane2, normal). Array self.new_ax defines how to do the
        switching between simulation axes and ModePlane axes:
            sim_axes[self.new_ax] -> ModePlane axes
            mpl_axes[self.old_ax] -> Simulation axes
        """
        self.new_ax = [0, 1, 2]
        self.new_ax.pop(self.norm_ind)
        self.new_ax.append(self.norm_ind)
        self.old_ax = np.argsort(self.new_ax).tolist()

        # Grid is to be set later based on a Simulation.
        self.grid = None

        # Permittivity at the Yee grid locations
        self.eps_ex = None
        self.eps_ey = None
        self.eps_ez = None

        """List of modes, set by a call to ``compute_modes()``. The first list 
        dimension is equal to the number of sampling frequencies, while the 
        second dimension is the number of computed modes. Each mode is given by 
        a dictionary with the fields and propagation constants."""
        self.modes = [[]]
        self.freqs = []

    def _set_sim(self, sim, freqs):
        """ Set the grid of the ModePlane based on a global simulation grid.
        The ModePlane grid is rotated such that ``z`` is the normal direction.
        Also set the ModePlane frequencies and the ``modes`` attribute as a
        list of Nfreqs empty lists.
        """
        self.freqs = listify(freqs)
        self.modes = [[] for i in range(len(self.freqs))]
        indsx, indsy, indsz = inside_box_coords(self.span, sim.grid.coords)
        if np.any([inds[0]==inds[1] for inds in (indsx, indsy, indsz)]):
            raise Tidy3DError("Mode plane position is outside simulation domain.")

        """Array of shape (3, 2) of int defining the starting and stopping 
        index in the global simulation grid of the ModePlane span."""
        self.span_inds = np.array([[inds[0], inds[1]] for inds in (indsx, indsy, indsz)])

        # Cut the mode plane span if symmetries are applied
        self.symmetries = [0, 0]
        for i, d in enumerate(self.new_ax[:2]):
            Nd = sim.grid.Nxyz[d]
            if self.span_inds[d, 0] < Nd / 2 and sim.symmetries[d] != 0:
                self.symmetries[i] = sim.symmetries[d]
                self.span_inds[d, 0] = int(Nd / 2)

        # Space and time resolution from global grid.
        self.time_step = sim.dt

        self.grid = SubGrid(sim.grid, span_inds=self.span_inds)
        self.grid.moveaxis(self.new_ax, (0, 1, 2))


    def _get_eps_cent(self, sim, freq):
        """Get the (non-averaged) permittivity at the center of the Yee cells,
        in ModePlane axes, at a given frequency. Used for plotting.
        """

        sim_mesh = [self.grid.mesh[a] for a in self.old_ax]
        eps = sim._get_eps(sim_mesh, edges='in', freq=freq)
        eps = np.squeeze(eps, axis=self.norm_ind)

        # Return as shape (N_cross_ind1, N_cross_ind2)
        return eps


    def _set_yee_sim(self, sim):
        """Set the permittivity at the Yee grid positions by passing the 
        simulation in which the mode plane is embedded.
        """

        meshes = [self.grid.mesh_ex, self.grid.mesh_ey, self.grid.mesh_ez]
        # Meshes and components in simulation axes
        meshes_sim = [[meshes[a1][a2] for a2 in self.old_ax] for a1 in self.old_ax]
        comps_sim = ['xx', 'yy', 'zz']

        epses = []
        for freq in self.freqs:
            eps_tmp = []
            for im, mesh in enumerate(meshes_sim):
                eps = sim._get_eps(mesh, edges='in', freq=freq, syms=False,
                    pec_val=pec_val, component=comps_sim[im])
                eps_tmp.append(eps)
            eps_tmp = np.stack(eps_tmp, axis=0)
            epses.append(fix_pec(eps_tmp, pec_val))

        epses = np.stack(epses, axis=0)

        # Rotate back to mode plane axes
        epses = np.moveaxis(epses, 1, -1)
        self._set_yee_arr(epses)


    def _set_yee_arr(self, eps_yee):
        """Set the permittivity at the Yee grid positions by passing an 
        array of shape (Nfreqs, Nx, Ny, Nz, 3) in Simulation axes. The 
        dimension in the direction normal to the ModePlane must be of size 1.
        """

        eps_new = np.moveaxis(eps_yee, 1 + np.array(self.new_ax), [1, 2, 3])
        self.eps_ex = eps_new[:, :, :, 0, self.new_ax[0]]
        self.eps_ey = eps_new[:, :, :, 0, self.new_ax[1]]
        self.eps_ez = eps_new[:, :, :, 0, self.new_ax[2]]


    def compute_modes(self, Nmodes, target_neff=None, pml_layers=(0, 0), bend_radius=None,
        bend_axis=None, angle_theta=0., angle_phi=0.):
        """ Compute the ``Nmodes`` eigenmodes in decreasing order of 
        propagation constant at every frequency in the list ``freqs``.
        """

        for (ifreq, freq) in enumerate(self.freqs):
            modes = self._compute_modes_ifreq(
                ifreq, Nmodes, target_neff, pml_layers, bend_radius, bend_axis, angle_theta,
                angle_phi)
            self.modes[ifreq] = modes 

    def _compute_modes_ifreq(self, ifreq, Nmodes, target_neff=None, pml_layers=[0, 0],
        bend_radius=None, bend_axis=None, angle_theta=0., angle_phi=0.):
        """ Compute the ``Nmodes`` eigenmodes in decreasing order of 
        propagation constant for frequency index ``ifreq``.
        """

        if self.grid is None:
            raise Tidy3DError("Mode plane has not been added to a simulation yet.")

        if bend_radius is not None:
            if bend_axis is None:
                raise Tidy3DError("'bend_axis' is required if 'bend_radius is provided.")
            bend_axis_sim_ind = xyz_dict[bend_axis]
            if bend_axis_sim_ind == self.norm_ind:
                raise Tidy3DError("'bend axis' must be normal to the mode plane axis.")
            bend_axis_ind = self.old_ax[bend_axis_sim_ind]
            transform_ind = 0 if bend_axis_ind == 1 else 1
            coords_t = self.grid.coords[transform_ind]
            if coords_t[(coords_t.size - 1)//2] - coords_t[0] >= np.abs(bend_radius):
                raise Tidy3DError("The bend center must be outside of the mode plane.")
        else:
            bend_axis_ind = None

        freq = self.freqs[ifreq]
        # Get permittivity. Slightly break the c1-c2 symmetry to avoid 
        # complex-valued degenerate modes.
        epses = [self.eps_ex[ifreq],
                 self.eps_ey[ifreq] + 1e-6,
                 self.eps_ez[ifreq]]

        # Get modes
        modes = get_modes(
            epses,
            freq,
            mesh_step=self.grid.mesh_step,
            pml_layers=pml_layers,
            num_modes=Nmodes,
            target_neff=target_neff,
            symmetries=self.symmetries,
            coords=self.grid.coords[:2],
            bend_radius=bend_radius,
            bend_axis_ind=bend_axis_ind,
            angle_theta=angle_theta,
            angle_phi=angle_phi)
        
        for mode in modes:
            # Make largest E-component real            
            mode.fix_efield_phase()
            # Normalize to unit power flux
            fields_cent = mode.fields_to_center()
            flux = dot_product(fields_cent, fields_cent, self.grid.coords)
            flux *= 2**np.sum([sym != 0 for sym in self.symmetries])
            mode.E /= np.sqrt(flux)
            mode.H /= np.sqrt(flux)

        return modes