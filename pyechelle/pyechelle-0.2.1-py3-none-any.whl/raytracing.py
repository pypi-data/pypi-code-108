import math
import random

import numba.cuda
import numpy as np

from pyechelle.CCD import CCD
from pyechelle.randomgen import make_alias_sampling_arrays, unravel_index
from pyechelle.slit import simple_slit, octagonal_slit, hexagonal_slit, round_slit
from pyechelle.sources import Source
from pyechelle.spectrograph import ZEMAX
from pyechelle.telescope import Telescope


@numba.njit(cache=True, parallel=False, nogil=True)
def raytrace(spectrum_wl, spectrum_q, spectrum_j, transformations, trans_wl, trans_wld, transf_deriv,
             psfs_q, psfs_j, psf_wl, psf_wld, psf_shape, psf_sampling, ccd, pixelsize, slitfun, nphotons):
    max_y, max_x = ccd.shape

    for _ in range(nphotons):
        # sample from spectrum
        k = int(math.floor(random.random() * len(spectrum_j)))
        wl = spectrum_wl[k] if random.random() < spectrum_q[k] else spectrum_wl[spectrum_j[k]]

        # find index for transformation
        idx_trans_float = (wl - trans_wl[0]) / trans_wld
        idx_trans = math.floor(idx_trans_float)
        r = (idx_trans_float - idx_trans)

        # do linear interpolation of transformation matrices
        m0, m1, m2, m3, m4, m5 = transformations[:, idx_trans] + r * transf_deriv[:, idx_trans]

        # random start points in slit
        x, y = slitfun(random.random(), random.random())
        # transform
        xt = m0 * x + m1 * y + m2
        yt = m3 * x + m4 * y + m5

        # apply PSF
        idx_psf = int((wl - psf_wl[0]) / psf_wld)  # find psf index
        # next 3 lines implement drawing random number via alias sampling
        k = int(math.floor(random.random() * len(psfs_j[idx_psf])))
        if not random.random() < psfs_q[idx_psf][k]:
            k = psfs_j[idx_psf][k]

        dx, dy = unravel_index(k, psf_shape)
        xt += (dx - psf_shape[1] / 2.) * psf_sampling / pixelsize
        yt += (dy - psf_shape[0] / 2.) * psf_sampling / pixelsize
        x_int = math.floor(xt)
        y_int = math.floor(yt)

        if (0 <= x_int < max_x) and (0 <= y_int < max_y):
            ccd[y_int, x_int] += 1


def raytrace_order_cpu(o, spec: ZEMAX, source: Source, telescope: Telescope, rv: float, t, ccd: CCD, efficiency=None,
                       n_cpu=1):
    wavelength = np.linspace(*spec.get_wavelength_range(o), num=100000)

    # get spectral density per order
    spectral_density = source.get_spectral_density_rv(wavelength, rv)
    # if source returns own wavelength vector, use that for further calculations instead of default grid
    if isinstance(spectral_density, tuple):
        wavelength, spectral_density = spectral_density

    # for stellar targets calculate collected flux by telescope area
    if source.stellar_target:
        spectral_density *= telescope.area

    # get efficiency per order
    if efficiency is not None:
        eff = efficiency.get_efficiency_per_order(wavelength=wavelength, order=o)
        effective_density = eff * spectral_density
    else:
        effective_density = spectral_density

    # calculate photon flux
    if source.flux_in_photons:
        flux = effective_density
    else:
        ch_factor = 5.03E12  # convert microwatts / micrometer to photons / s per wavelength interval
        wl_diffs = np.ediff1d(wavelength, wavelength[-1] - wavelength[-2])
        flux = effective_density * wavelength * wl_diffs * ch_factor

    flux_photons = flux * t
    total_photons = int(np.sum(flux_photons))
    print(f'Order {o:3d}:    {(np.min(wavelength) * 1000.):7.1f} - {(np.max(wavelength) * 1000.):7.1f} nm.     '
          f'Number of photons: {total_photons}')

    minwl, maxwl = spec.get_wavelength_range(o)
    trans_wl, trans_wld = np.linspace(minwl, maxwl, 10000, retstep=True)
    transformations = np.array(spec.transformations[f'order{o}'].get_matrices_spline(trans_wl))
    # derivatives for simple linear interpolation
    trans_deriv = np.array([np.ediff1d(t, t[-1] - t[-2]) for t in transformations])

    psf_sampler_qj = np.array(
        [make_alias_sampling_arrays(p.T.ravel()) for p in spec.psfs[f"psf_order_{o}"].psfs])

    psfs_wl = spec.psfs[f"psf_order_{o}"].wl
    psfs_wld = np.ediff1d(psfs_wl, psfs_wl[-1] - psfs_wl[-2])
    psf_shape = spec.psfs[f"psf_order_{o}"].psfs[0].shape

    if spec.field_shape == "rectangular":
        slitfunc = simple_slit
    elif spec.field_shape == "octagonal":
        slitfunc = octagonal_slit
    elif spec.field_shape == "hexagonal":
        slitfunc = hexagonal_slit
    elif spec.field_shape == "circular":
        slitfunc = round_slit
    else:
        raise NotImplementedError(f"Field shape {spec.field_shape} is not implemented.")

    spectrum_sampler_q, spectrum_sampler_j = make_alias_sampling_arrays(np.asarray(flux_photons / np.sum(flux_photons),
                                                                                   dtype=np.float32))

    psf_sampling = spec.psfs[f"psf_order_{o}"].sampling
    if n_cpu > 1:
        ccd_new = np.zeros_like(ccd.data, dtype=np.uint32)
        raytrace(wavelength, spectrum_sampler_q, spectrum_sampler_j,
                 transformations, trans_wl, trans_wld, trans_deriv,
                 psf_sampler_qj[:, 0], psf_sampler_qj[:, 1], psfs_wl, psfs_wld[0], psf_shape, psf_sampling[0],
                 ccd_new, float(ccd.pixelsize), slitfunc, total_photons)

        return ccd_new, total_photons
    else:
        raytrace(wavelength, spectrum_sampler_q, spectrum_sampler_j,
                 transformations, trans_wl, trans_wld, trans_deriv,
                 psf_sampler_qj[:, 0], psf_sampler_qj[:, 1], psfs_wl, psfs_wld[0], psf_shape, psf_sampling[0],
                 ccd.data, float(ccd.pixelsize), slitfunc, total_photons)
        return total_photons
