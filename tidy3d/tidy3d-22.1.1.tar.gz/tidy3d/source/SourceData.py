import numpy as np
import logging

from ..utils.geom import axes_handed, rotate3D
from ..utils.log import log_and_raise, SourceError
from ..constants import int_, float_, complex_, fp_eps, ETA_0, C_0, pec_viz
from ..mode import Mode, ModePlane, dot_product
from .Source import VolumeSource, Field2DSource, ModeSource, PlaneWave, PlaneSource, GaussianBeam
from .utils import paraxial_gaussian_beam, pol_vectors

class SourceData(object):
    """Class used internally to store data related to a Source added in a 
    specific Simulation.
    """

    def __init__(self, source):

        # Reference to the source that the data corresponds to
        self.source = source

        # To be set by Simulation
        self.name = None

        # Mesh normalization, set by Simulation
        self.mesh_norm = np.ones((6,))

        # Phase offset between J and M currents; nonzero in Field2DSource
        self.phaseMJ = 0

        # Extra variables specific to Field2DSource
        if isinstance(source, Field2DSource):
            # Variables to store the mode plane, mode, and mode index
            self.mode_plane = ModePlane(source.span, source.norm_ind)
            self.mode = None

            # Extra variables specific to ModeSource, set using Simulation.set_mode()
            if isinstance(source, Field2DSource):
                # Nmodes and target_neff can be used to find the desired mode
                self.Nmodes = 1
                self.target_neff = None
                self.mode_ind = None
                self.pml_layers = (0, 0)
                self.bend_radius = None
                self.bend_axis = None
                self.angle_theta = source.angle_theta
                self.angle_phi = source.angle_phi


    def _mesh_norm(self, grid):
        """Normalize source by the mesh step in a given direction, if the span 
        of the source in that direction is zero. This is to avoid changes in 
        radiated power when the spatial discretization is changed.
        """

        coords = grid.coords
        self.mesh_norm = np.ones((6,))
        for dim in range(3):
            if np.abs(self.source.span[dim, 1] - self.source.span[dim, 0]) < fp_eps:
                cind = np.nonzero(self.source.span[dim, 0] < coords[dim])[0]
                if cind.size == 0:
                    continue
                else:
                    cind = cind[0] - 1
                if cind < 0:
                    continue

                # Primal and dual step at the source coordinate
                pstep = grid.psteps[dim][cind]
                dstep = grid.dsteps[dim][cind]
                # Indexes orthogonal to current dimension
                cross_inds = [0, 1, 2]
                cross_inds.pop(dim)
                cross_inds = np.array(cross_inds)

                # Electric current normalization
                self.mesh_norm[dim] /= pstep
                self.mesh_norm[cross_inds] /= dstep

                # Magnetic current normalization
                self.mesh_norm[3 + dim] /= dstep
                self.mesh_norm[3 + cross_inds] /= pstep

    def _currents(self, src_inds):
        """Source currents (Jx, Jy, Jz, Mx, My, Mz) at grid locations 
        specified by the global grid indexes ``src_inds``.
        """

        if src_inds.size==0:
            return np.zeros((0, 6), dtype=complex_)

        if isinstance(self.source, VolumeSource):
            src_amps = np.zeros((src_inds.shape[0], 6), dtype=float_)
            src_amps[:, self.source.components==1] = self.source.amplitude
            src_amps *= self.mesh_norm

        elif isinstance(self.source, Field2DSource):
            """ Currents for the 2D field source are defined through the 
            the equivalence principle. Only tangential currents are used. 
            ``src_inds`` are the indexes in 
            the global grid, so to get the indexing in the 2D plane, we use 
            ``mode_plane.span_inds``, which gives the beginning and end 
            indexes of the plane in the global grid.
            """

            src_amps = np.zeros((src_inds.shape[0], 6), dtype=complex_)
            mplane = self.mode_plane

            # Indexing in the 2D plane. 
            inds1 = src_inds[:, mplane.new_ax[0]] - mplane.span_inds[mplane.new_ax[0], 0]
            inds2 = src_inds[:, mplane.new_ax[1]] - mplane.span_inds[mplane.new_ax[1], 0]

            # Electric current sources from magnetic field of the eigenmode.
            src_amps[:, mplane.new_ax[0]] = self.mode.H[1, inds1, inds2].ravel()
            src_amps[:, mplane.new_ax[1]] = -self.mode.H[0, inds1, inds2].ravel()

            # Magnetic current sources from electric field of the eigenmode.
            src_amps[:, 3 + mplane.new_ax[0]] = -self.mode.E[1, inds1, inds2].ravel()
            src_amps[:, 3 + mplane.new_ax[1]] = self.mode.E[0, inds1, inds2].ravel()
            
            # +/-1 depending on handedness of mode_plane axes
            ax_fact = axes_handed(mplane.new_ax)
            # dir_ind is +/-1 for positive/negative direction
            src_amps[:, 3:] *= ax_fact*self.source.dir_ind
            # Overall source amplitude
            src_amps *= self.source.amplitude * self.mesh_norm
            # Extra correction because J and M are not co-localized
            src_amps /= np.sqrt(np.abs(np.cos(self.phaseMJ)))

        return src_amps

    def _set_mode(self):
        """ Compute 2D injection fields for a Field2DSource that is not ModeSource.
        """

        if isinstance(self.source, PlaneWave):
            self._set_mode_plane_wave()
        elif isinstance(self.source, PlaneSource):
            self._set_mode_plane_source()
        elif isinstance(self.source, GaussianBeam):
            self._set_mode_gaussian_beam()


    def _set_mode_phases(self):
        """ Set the J and M phase offset for an eigenmode source.
        This should perhaps be replaced by just computing the E and H fields 
        at the correct location along the propagation direction.
        """

        mplane = self.mode_plane

        # Spatial offset phase
        zH = (mplane.grid.coords[2][1] - mplane.grid.coords[2][0]) / 2
        self.phaseMJ = -self.mode.kvector[2] * zH


    def _set_mode_plane_wave(self):
        """Compute normal incidence plane wave."""

        source = self.source
        mplane = self.mode_plane
        eps = np.stack([e[0].real for e in [mplane.eps_ex, mplane.eps_ey, mplane.eps_ez]])

        for dim in range(3):
            eps_d = eps[dim, :, :]
            if np.amax(eps_d) - np.amin(eps_d) > 1e-5 and np.amin(eps_d) > pec_viz:
                log_and_raise(
                    "'PlaneWave' is intended to be placed entirealy in a homogeneous material.",
                    SourceError
                )

        frequency = source.source_time.frequency

        """ Mode fields are defined w.r.t. ModePlane axes, which are 
        [cross_ind1, cross_ind2, norm_ind]. """
        N1, N2 = eps.shape[1:]
        neff = np.sqrt(np.amax(eps[2, :, :]))
        E = np.zeros((3, N1, N2))
        H = np.zeros((3, N1, N2))
        if source.epol_ind < source.hpol_ind:
            # E is polarized along first cross-index
            E[0, :, :] = 1
            H[1, :, :] = neff/ETA_0
        else:
            # E is polarized along second cross-index
            E[1, :, :] = 1
            H[0, :, :] = -neff/ETA_0

        mode = Mode(E, H, neff, keff=0)
        flux = dot_product((E, H), (E, H), mplane.grid.coords)
        mode.E /= np.sqrt(flux)
        mode.H /= np.sqrt(flux)
        mode.kvector = np.array([0, 0, source.dir_ind * mode.neff])
        mode.kvector *= 2 * np.pi * source.source_time.frequency / C_0
        self.mode = mode
        self._set_mode_phases()


    def _set_mode_plane_source(self):
        """ Compute (oblique) wave mode without matrix diagonalization.
        """

        source = self.source
        mplane = self.mode_plane
        eps = np.stack([e[0].real for e in [mplane.eps_ex, mplane.eps_ey, mplane.eps_ez]])

        for dim in range(3):
            eps_d = eps[dim, :, :]
            if np.amax(eps_d) - np.amin(eps_d) > 1e-5 and np.amin(eps_d) > pec_viz:
                log_and_raise(
                    "'PlaneSource' is intended to be placed entirealy in a homogeneous material.",
                    SourceError
                )

        frequency = source.source_time.frequency

        """ Mode fields are defined w.r.t. ModePlane axes, which are 
        [cross_ind1, cross_ind2, norm_ind]. """
        N1, N2 = eps.shape[1:]
        neff = np.sqrt(np.amax(eps[2, :, :]))
        E = np.zeros((3, N1, N2), dtype=complex_)
        H = np.zeros((3, N1, N2), dtype=complex_)

        # kvector in units of effective index, based on diffraction order
        d1 = mplane.grid.span[0, 1] - mplane.grid.span[0, 0]
        d2 = mplane.grid.span[1, 1] - mplane.grid.span[1, 0]
        k1 = source.diff_order[0] * 2*np.pi / d1 
        k2 = source.diff_order[1] * 2*np.pi / d2 
        k0 = 2 * np.pi * neff * frequency / C_0
        if k0 ** 2 <= k1**2 + k2**2:
            raise ValueError("Diffraction order [%d, %d] not available"%(
                            source.diff_order[0], source.diff_order[1]) +\
                            "for PlaneSource size and frequency.")
        kn = np.sqrt(k0**2 - k1**2 - k2**2)
        # Unit vector along the propagation axis
        dir_vec = np.array([k1, k2, kn])/k0
        # k-vector in 1/micron
        kvector = source.dir_ind * k0 * dir_vec
        # Polarization unit vectors
        if np.linalg.norm(source.polarization) < fp_eps:
            E_vec, H_vec = pol_vectors(dir_vec, source.pol_angle)
        else:
            E_vec = source.polarization[mplane.new_ax]
            E_vec -= np.dot(E_vec, dir_vec) * dir_vec
            E_vec /= np.sqrt(E_vec.dot(E_vec))
            H_vec = np.cross(dir_vec, E_vec)
            H_vec /= np.sqrt(H_vec.dot(H_vec))

        # Add impedence
        H_vec *= neff/ETA_0

        """ Finally need to account for the Yee grid locations of each component
        through mplane.grid. E[0] and H[1] are co-locallized in the 
        cross-section plane, and same for E[1] and H[0]. The offset in the 
        normal direction is taken into account later. """
        xg, yg = np.meshgrid(mplane.grid.mesh_ex[0],
                             mplane.grid.mesh_ex[1])
        E[0, :, :] = E_vec[0]*np.exp(1j*(xg*kvector[0] + yg*kvector[1])).T
        H[1, :, :] = H_vec[1]*np.exp(1j*(xg*kvector[0] + yg*kvector[1])).T
        xg, yg = np.meshgrid(mplane.grid.mesh_ey[0],
                             mplane.grid.mesh_ey[1])
        E[1, :, :] = E_vec[1]*np.exp(1j*(xg*kvector[0] + yg*kvector[1])).T
        H[0, :, :] = H_vec[0]*np.exp(1j*(xg*kvector[0] + yg*kvector[1])).T

        mode = Mode(E, H, neff, keff=0)
        flux = dot_product((E, H), (E, H), mplane.grid.coords)
        mode.E /= np.sqrt(flux)
        mode.H /= np.sqrt(flux)
        mode.kvector = kvector
        self.mode = mode
        self._set_mode_phases()


    def _set_mode_gaussian_beam(self):
        """ Compute Gaussian beam mode without matrix diagonalization.
        """

        source = self.source
        mplane = self.mode_plane
        eps = np.stack([e[0].real for e in [mplane.eps_ex, mplane.eps_ey, mplane.eps_ez]])

        frequency = source.source_time.frequency

        """ Mode fields are defined w.r.t. ModePlane axes, which are 
        [cross_ind1, cross_ind2, norm_ind]. """
        N1, N2 = eps.shape[1:]
        neff = np.sqrt(np.amax(eps[2, :, :]))
        E = np.zeros((3, N1, N2), dtype=complex_)
        H = np.zeros((3, N1, N2), dtype=complex_)

        k0 = 2 * np.pi * neff * frequency / C_0
        kn = k0 * np.cos(source.angle_theta)
        k1 = k0 * np.sin(source.angle_theta) * np.cos(source.angle_phi)
        k2 = k0 * np.sin(source.angle_theta) * np.sin(source.angle_phi)

        # Unit vector along the propagation axis
        dir_vec = np.array([k1, k2, kn])/k0
        # k-vector in 1/micron
        kvector = source.dir_ind * k0 * dir_vec
        # Polarization unit vectors
        E_vec, H_vec = pol_vectors(dir_vec, source.pol_angle)
        # Add impedence
        H_vec *= neff/ETA_0

        """ Finally need to account for the Yee grid locations of each 
        component through mplane.grid. E[0] and H[1] are co-locallized in the 
        cross-section plane, and same for E[1] and H[0]. In the normal
        direction, H is one half-step away from E. """

        w0 = source.waist_radius
        zE = source.waist_distance * np.cos(source.angle_theta)
        zH = zE + (mplane.grid.coords[2][1] - mplane.grid.coords[2][0])/2
        xy_offset = source.waist_distance * np.sin(source.angle_theta)
        x_center = source.center[mplane.new_ax[0]] - xy_offset * np.cos(source.angle_phi)
        y_center = source.center[mplane.new_ax[1]] - xy_offset * np.sin(source.angle_phi)

        # In-plane grid for E[0] and H[1]
        xg, yg = [m.T for m in np.meshgrid(mplane.grid.mesh_ex[0], mplane.grid.mesh_ex[1])]
        xg -= x_center
        yg -= y_center
        # Rotate coordinates to a frame where the beam direction is along z
        xr, yr, zr = self._propagation_axes(xg, yg, zE*np.ones_like(xg))
        GE = paraxial_gaussian_beam(xr, yr, zr, w0, k0*source.dir_ind)
        xr, yr, zr = self._propagation_axes(xg, yg, zH*np.ones_like(xg))
        GH = paraxial_gaussian_beam(xr, yr, zr, w0, k0*source.dir_ind)
        E[0, :, :] = E_vec[0] * GE
        H[1, :, :] = H_vec[1] * GH

        # In-plane grid for E[1] and H[0]
        xg, yg = [m.T for m in np.meshgrid(mplane.grid.mesh_ey[0], mplane.grid.mesh_ey[1])]
        xg -= x_center
        yg -= y_center
        # Rotate coordinates to a frame where the beam direction is along z
        xr, yr, zr = self._propagation_axes(xg, yg, zE*np.ones_like(xg))
        GE = paraxial_gaussian_beam(xr, yr, zr, w0, k0*source.dir_ind)
        xr, yr, zr = self._propagation_axes(xg, yg, zH*np.ones_like(xg))
        GH = paraxial_gaussian_beam(xr, yr, zr, w0, k0*source.dir_ind)
        E[1, :, :] = E_vec[1] * GE
        H[0, :, :] = H_vec[0] * GH

        mode = Mode(E, H, neff, keff=0)
        fields_cent = mode.fields_to_center()
        flux = dot_product(fields_cent, fields_cent, mplane.grid.coords)
        mode.E /= np.sqrt(flux)
        mode.H /= np.sqrt(flux)
        mode.kvector = kvector

        """ Here, we do not set the spatial phaseMJ offset since the Gaussian 
        beam source is more complicated and intrinsically requires complex 
        fields, as set above. """

        self.mode = mode


    def _propagation_axes(self, x, y, z):
        """Rotate the points x, y, z (same shape arrays) from the ModePlane
        coordinate frame into the coordinate frame defined by the source
        propagation direction angles.
        """

        xr, yr, zr = rotate3D(x, y, z, 0, 0, -self.source.angle_phi)
        xr, yr, zr = rotate3D(xr, yr, zr, 0, -self.source.angle_theta, 0)

        return xr, yr, zr
