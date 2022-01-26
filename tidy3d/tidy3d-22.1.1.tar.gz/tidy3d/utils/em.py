import os
import numpy as np
import h5py

from . import log_and_raise, subprocess_cmd
from ..constants import fp_eps, pec_val


def poynting_avg(E, H):
    """Compute the time-averaged Poynting vector that gives the energy
    flow per unit area per unit time at every point. ``E`` and ``H`` are
    assumed to be arrays of the same shape, as returned by frequency
    monitors. The first dimension is the field polarization (x, y, z), and
    must have size 3. The last dimension is the number of frequencies.
    """

    if E.shape != H.shape:
        log_and_raise("E and H must have the same dimension.", ValueError)
    if E.shape[0] != 3:
        log_and_raise("First dimension of fields must have size 3.", ValueError)

    return 1 / 2 * np.real(np.cross(E, np.conj(H), axis=0)).astype(np.float64)


def poynting_insta(E, H):
    """Compute the instantaneous Poynting vector that gives the energy
    flow per unit area per unit time at every point in space and time.
    ``E`` and ``H`` are assumed to be arrays of the same shape, as returned by
    time monitors. The first dimension is the field polarization (x, y, z),
    and must have size 3. The last dimension is the number of time steps.
    """

    if E.shape != H.shape:
        log_and_raise("E and H must have the same dimension.", ValueError)
    if E.shape[0] != 3:
        log_and_raise("First dimension of fields must have size 3.", ValueError)

    return np.cross(E, H, axis=0)


def dft_spectrum(time_series, dt, freqs):
    """Computes the frequency spectrum associated to a time series directly
    using the discrete fourier transform.

    Note
    ----
    The DFT spectrum can be computed over an arbitrary list of frequencies,
    but is much more inefficient than FFT. Use sparingly.

    Parameters
    ----------
    time_series: array_like
        1D array of time-dependent data.
    dt : float, optional
        Step in time over which the time series is recorded.
    freqs : array_like
        Array of frequencies to sample the spectrum at.

    Returns
    -------
    spectrum : array_like
        Array of same size as ``freqs`` giving the complex-valued spectrum.
    """

    frs = np.array(freqs)
    tdep = np.array(time_series)
    tmesh = np.arange(tdep.size) * dt
    spectrum = np.sum(
        tdep[:, np.newaxis] * np.exp(2j * np.pi * frs[np.newaxis, :] * tmesh[:, np.newaxis]),
        0,
    ).ravel()

    return dt / np.sqrt(2 * np.pi) * spectrum


def x_to_center(Ex):
    """Interpolate Ex positions to the center of a Yee lattice"""
    return (Ex + np.roll(Ex, -1, 1) + np.roll(Ex, -1, 2) + np.roll(np.roll(Ex, -1, 1), -1, 2)) / 4


def y_to_center(Ey):
    """Interpolate Ey positions to the center of a Yee lattice"""
    return (Ey + np.roll(Ey, -1, 0) + np.roll(Ey, -1, 2) + np.roll(np.roll(Ey, -1, 0), -1, 2)) / 4


def z_to_center(Ez):
    """Interpolate Ez positions to the center of a Yee lattice"""
    return (Ez + np.roll(Ez, -1, 0) + np.roll(Ez, -1, 1) + np.roll(np.roll(Ez, -1, 0), -1, 1)) / 4


def E_to_center(E):
    """Interpolate an E-field array of shape (3, Nx, Ny, Nz, ...) to the
    center of the Yee grid. Returns array of same shape."""

    Ex_interp = x_to_center(E[0, ...])
    Ey_interp = y_to_center(E[1, ...])
    Ez_interp = z_to_center(E[2, ...])

    return np.stack((Ex_interp, Ey_interp, Ez_interp), axis=0)


def H_to_center(H):
    """Interpolate an H-field array of shape (3, Nx, Ny, Nz, ...) to the
    center of the Yee grid. Returns array of same shape."""

    Hx_interp = (H[0, ...] + np.roll(H[0, ...], -1, 1)) / 2
    Hy_interp = (H[1, ...] + np.roll(H[1, ...], -1, 2)) / 2
    Hz_interp = (H[2, ...] + np.roll(H[2, ...], -1, 3)) / 2

    return np.stack((Hx_interp, Hy_interp, Hz_interp), axis=0)


def eps_to_center(eps_xx, eps_yy, eps_zz):
    """Interpolate eps_r to the center of the Yee lattice."""

    # # Simple averaging of one x, y, z values per cell.
    # return (eps_xx + eps_yy + eps_zz)/3

    # Average all 4 eps_xx, 4 eps_yy, and 4 eps_zz values around the
    # cell center, similar to the monitor field recording.
    return (x_to_center(eps_xx) + y_to_center(eps_yy) + z_to_center(eps_zz)) / 3


def expand_syms(sim, span_inds, E, H, eps, interpolate=True):
    """Expand E field based on simulation symmetries, if touching a symmetry
    plane.

    Parameters
    ----------
    sim : Simulation
        Simulation to which the field relates.
    span_inds : np.ndarray
        Indexes in the simulation grid within which the field lies, starting
        from the symmetry plane if present.
    E : np.ndarray
        Shape (3, Nx, Ny, Nz, Ns).
    H : np.ndarray
        Shape (3, Nx, Ny, Nz, Ns).
    eps : np.ndarray
        Shape (3, Nx, Ny, Nz, Ns).
    """

    inds_beg = span_inds[:, 0]
    inds_end = span_inds[:, 1]
    Nxyz = sim.grid.Nxyz

    # Auxiliary variable for slicing along a given axis
    slices = (slice(None),) * 5

    """If symmetries are present, we need to offset the stored fields 
    by half the simulation size in the symmetry direction. Also, if a 
    monitor starts at the symmetry axis, we double its size and 
    pad it with the fields with the correct symmetry eigenvalues. """
    for dim, sym in enumerate(sim.symmetries):

        if sym == 0 or (span_inds[dim, 1] - span_inds[dim, 0]) == 1:
            continue

        # Auxiliary variable for symmetry eigenvalue along current axis
        svals = np.ones((3, 1, 1, 1, 1))
        svals[dim] = -1
        if sym == 1:
            svals *= -1

        if span_inds[dim, 0] == Nxyz[dim] // 2:

            inds_beg[dim] -= span_inds[dim, 1] - span_inds[dim, 0]

            if interpolate == True:
                sl = list(slices)
                sl[dim + 1] = slice(-1, None, -1)

                # Stack fields
                if E.size > 0:
                    E = np.concatenate((-svals * E[tuple(sl)], E), axis=dim + 1)
                if H.size > 0:
                    H = np.concatenate((svals * H[tuple(sl)], H), axis=dim + 1)
                if eps.size > 0:
                    eps = np.concatenate((eps[tuple(sl)], eps), axis=dim + 1)

            else:
                inds_beg[dim] += 1
                # Slicing for fields at the beginning of Yee cells along the symmetry direction
                sl_beg = list(slices)
                sl_beg[dim + 1] = slice(-1, 0, -1)
                # Slicing for fields at the center of Yee cells along the symmetry direction
                sl_cen = list(slices)
                sl_cen[dim + 1] = slice(-2, None, -1)

                # tangential indexes for E components
                cross_dims = [0, 1, 2]
                cross_dims.pop(dim)

                # Stack fields
                if E.shape[dim + 1] > 0:
                    shape_pad = list(E.shape)
                    shape_pad[dim + 1] -= 1
                    Epad = np.zeros(shape_pad, dtype=np.complex64)
                    Epad[cross_dims] = -svals[cross_dims] * E[tuple([cross_dims] + sl_beg[1:])]
                    Epad[dim] = -svals[dim] * E[tuple([dim] + sl_cen[1:])]
                    E = np.concatenate((Epad, E), axis=dim + 1)
                if H.shape[dim + 1] > 0:
                    shape_pad = list(H.shape)
                    shape_pad[dim + 1] -= 1
                    Hpad = np.zeros(shape_pad, dtype=np.complex64)
                    Hpad[cross_dims] = svals[cross_dims] * H[tuple([cross_dims] + sl_cen[1:])]
                    Hpad[dim] = svals[dim] * H[tuple([dim] + sl_beg[1:])]
                    H = np.concatenate((Hpad, H), axis=dim + 1)
                if eps.shape[dim + 1] > 0:
                    shape_pad = list(eps.shape)
                    shape_pad[dim + 1] -= 1
                    eps_pad = np.zeros(shape_pad, dtype=np.complex64)
                    eps_pad[cross_dims] = eps[tuple([cross_dims] + sl_beg[1:])]
                    eps_pad[dim] = eps[tuple([dim] + sl_cen[1:])]
                    eps = np.concatenate((eps_pad, eps), axis=dim + 1)

    return (np.stack((inds_beg, inds_end), axis=1), E, H, eps)


def nk_to_eps(n, k):
    """Convert refractive index (n, k) to complex permittivity.
    """
    return (n + 1j * k) ** 2


def eps_to_nk(eps):
    """Convert complex permittivity to refractive index (n, k).
    """

    nk_complex = np.sqrt(eps)
    return nk_complex.real, nk_complex.imag


def eps_pole_residue(poles, freqs):
    """The pole-residue contribution to the permittivity at a set of
    frequencies. We use the convention exp(-1j w t) and so positive imaginary
    part of eps(w) means loss. This is opposite from the original definition
    in Han et al., IEEE MICROWAVE AND WIRELESS COMPONENTS LETTERS (2006).
    """

    w = 2*np.pi*np.array(freqs)
    eps = np.zeros_like(w, dtype=np.complex128)
    for (a, c) in poles:
        eps -= c/(1j*w + a)
        eps -= c.conjugate()/(1j*w + a.conjugate())

    return eps


def get_eps_yee(sim, fjson, fdtd_path, span_inds, freqs, file_in, file_out, dset_name):
    """Get the permittivity of a mode_plane using a call to the C++
    solver that applies subpixel averaging as in the time stepping.
    """

    mfile = h5py.File(file_in, "w")
    if "subdomains" not in mfile.keys():
        grp = mfile.create_group("subdomains")
    if "grid" not in mfile.keys():
        grp = mfile.create_group("grid")
        dimname = ("x", "y", "z")
        for dim in range(3):
            coords = sim.grid.coords[dim]
            grp.create_dataset(dimname[dim], data=coords)

    grp = mfile.create_group("subdomains/" + dset_name)
    grp.create_dataset("span_inds", data=span_inds)
    grp.create_dataset("freqs", data=freqs)
    mfile.close()

    gencoeffs_args = f"{fjson} {file_in} {file_out}"
    subprocess_cmd(f"{fdtd_path}/solver/gencoeffs {gencoeffs_args}")

    with h5py.File(file_out, "r") as mfile:
        eps_sub = np.array(mfile[dset_name]['eps'])

    return eps_sub


def set_eps_yee(mode_plane, sim, fjson, fdtd_path, file_in, file_out, dset_name):
    """Set the permittivity of a mode_plane using a call to the C++ solver.
    """

    span_inds = mode_plane.span_inds
    freqs = np.array([mode_plane.freqs])
    eps_sub = get_eps_yee(sim, fjson, fdtd_path, span_inds, freqs, file_in, file_out, dset_name)
    mode_plane._set_yee_arr(eps_sub)


def eps_python_cpp(sim, mplane, fdtd_path, subpixel=False):
    """Compute the epsilon distribution in a ModePlane in a Simulation
    using the python code and the C++ solver.

    This alters sim, so should only be used in self-contained tests!
    Generally it's assumed it's run in the test folder (tmp folder is created).
    """

    sim.subpixel = subpixel
    os.makedirs('tmp', exist_ok=True)
    fjson = 'tmp/fdtd3d.json'
    sim.export_json('tmp/fdtd3d.json')
    mplane._set_yee_sim(sim)
    eps_sim = np.stack([mplane.eps_ex, mplane.eps_ey, mplane.eps_ez])
    set_eps_yee(mplane, sim, fjson, fdtd_path, "tmp/mplane_in.hdf5", "tmp/mplane_ou.hdf5", "test")
    eps_cpp = np.stack([mplane.eps_ex, mplane.eps_ey, mplane.eps_ez])

    return eps_sim, eps_cpp


def fix_pec(eps, pec_val=pec_val):
    """Fix the PEC staircasing by removing "hanging" components which do not
    connect to at least one tangential component on each side.
    
    Parameters
    ----------
    eps : array_like
        Shape (3, Nx, Ny, Nz).
    """

    _, Nx, Ny, Nz = eps.shape
    Nxyz = (Nx, Ny, Nz)

    eps_fix = np.copy(eps)

    for dim in range(3):
        cinds = [0, 1, 2]
        cinds.pop(dim)

        # Epsilon of normal component at current, previous, and next locations
        eps_n = eps[dim, :, :, :]
        eps_n_prev = np.take(eps_n, np.arange(-1, Nxyz[dim]-1), axis=dim, mode='wrap')
        eps_n_next = np.take(eps_n, np.arange(1, Nxyz[dim]+1), axis=dim, mode='wrap')
        # Epsilon of tangential components at current location
        eps_c1 = eps[cinds[0], :, :, :]
        eps_c2 = eps[cinds[1], :, :, :]

        # Previous tangential components pec checks
        c1_prev1 = np.take(eps_c1, np.arange(-1, Nxyz[cinds[0]]-1), axis=cinds[0], mode='wrap')
        pec_c1_prev1 = np.abs(c1_prev1 - pec_val) < fp_eps
        c2_prev1 = np.take(eps_c2, np.arange(-1, Nxyz[cinds[1]]-1), axis=cinds[1], mode='wrap')
        pec_c2_prev1 = np.abs(c2_prev1 - pec_val) < fp_eps

        pec_c1_prev2 = np.abs(eps_c1 - pec_val) < fp_eps
        pec_c2_prev2 = np.abs(eps_c2 - pec_val) < fp_eps

        # Next tangential components
        c1_next1 = np.take(c1_prev1, np.arange(1, Nxyz[dim]+1), axis=dim, mode='wrap')
        pec_c1_next1 = np.abs(c1_next1 - pec_val) < fp_eps
        c2_next1 = np.take(c2_prev1, np.arange(1, Nxyz[dim]+1), axis=dim, mode='wrap')
        pec_c2_next1 = np.abs(c2_next1 - pec_val) < fp_eps

        c1_next2 = np.take(eps_c1, np.arange(1, Nxyz[dim]+1), axis=dim, mode='wrap')
        pec_c1_next2 = np.abs(c1_next2 - pec_val) < fp_eps
        c2_next2 = np.take(eps_c2, np.arange(1, Nxyz[dim]+1), axis=dim, mode='wrap')
        pec_c2_next2 = np.abs(c2_next2 - pec_val) < fp_eps

        # Check if any of the previous tangential components is PEC
        pec_prev = pec_c1_prev1 | pec_c2_prev1 | pec_c1_prev2 | pec_c2_prev2
        # Check if any of the next tangential components is PEC
        pec_next = pec_c1_next1 | pec_c2_next1 | pec_c1_next2 | pec_c2_next2

        # Fix epsilon if no connecting previous tangential components 
        pec = np.abs(eps_n - pec_val) < fp_eps
        bad_pec = pec & np.invert(pec_prev)
        eps_fix[dim, bad_pec==True] = eps_n_prev[bad_pec==True]

        # Fix epsilon if no connecting next tangential components 
        pec = np.abs(eps_n - pec_val) < fp_eps
        bad_pec = pec & np.invert(pec_next)
        eps_fix[dim, bad_pec==True] = eps_n_next[bad_pec==True]

    return eps_fix