import math

import numba
import numba.cuda
import numpy as np
from numba import cuda
from numba.cuda.random import create_xoroshiro128p_states, xoroshiro128p_uniform_float64

from pyechelle.randomgen import make_alias_sampling_arrays
from pyechelle.sources import Source
from pyechelle.spectrograph import ZEMAX
from pyechelle.telescope import Telescope


@cuda.jit()
def cuda_raytrace_rectangularslit(spectrum_wl, spectrum_q, spectrum_j, transformations, trans_wl, trans_wld,
                                  transf_deriv, psfs_q, psfs_j, psf_wl, psf_wld, psf_shape, psf_sampling, ccd,
                                  pixelsize, rng_states, nphotons):
    max_y, max_x = ccd.shape
    thread_id = cuda.grid(1)

    for _ in range(thread_id, nphotons, cuda.gridDim.x * cuda.blockDim.x):
        # sample from spectrum
        k = int(math.floor(xoroshiro128p_uniform_float64(rng_states, thread_id) * len(spectrum_j)))
        wl = spectrum_wl[k] if xoroshiro128p_uniform_float64(rng_states, thread_id) < spectrum_q[k] else spectrum_wl[
            spectrum_j[k]]

        # find index for transformation
        idx_trans_float = (wl - trans_wl[0]) / trans_wld
        idx_trans = int(math.floor(idx_trans_float))
        r = (idx_trans_float - idx_trans)

        # do linear interpolation of transformation matrices
        # m0, m1, m2, m3, m4, m5 = transformations[:, idx_trans] + r * transf_deriv[:, idx_trans]
        m0, m1, m2, m3, m4, m5 = transformations[:, idx_trans]
        dm0, dm1, dm2, dm3, dm4, dm5 = transf_deriv[:, idx_trans]
        m0 += r * dm0
        m1 += r * dm1
        m2 += r * dm2
        m3 += r * dm3
        m4 += r * dm4
        m5 += r * dm5

        # random start points in slit
        x = xoroshiro128p_uniform_float64(rng_states, thread_id)
        y = xoroshiro128p_uniform_float64(rng_states, thread_id)
        # transform
        xt = m0 * x + m1 * y + m2
        yt = m3 * x + m4 * y + m5

        # apply PSF
        idx_psf = int((wl - psf_wl[0]) / psf_wld)  # find psf index
        # next 3 lines implement drawing random number via alias sampling
        k = int(math.floor(xoroshiro128p_uniform_float64(rng_states, thread_id) * len(psfs_j[idx_psf])))
        if not xoroshiro128p_uniform_float64(rng_states, thread_id) < psfs_q[idx_psf][k]:
            k = psfs_j[idx_psf][k]

        # unravel 2d index
        dy = k % psf_shape[1]
        k = k // psf_shape[1]
        dx = k % psf_shape[0]

        # dx, dy = unravel_index(k, psf_shape)
        xt += (dx - psf_shape[1] / 2.) * psf_sampling / pixelsize
        yt += (dy - psf_shape[0] / 2.) * psf_sampling / pixelsize
        x_int = int(math.floor(xt))
        y_int = int(math.floor(yt))

        if (0 <= x_int < max_x) and (0 <= y_int < max_y):
            numba.cuda.atomic.inc(ccd, (y_int, x_int), 4294967295)


@cuda.jit()
def cuda_raytrace_roundslit(spectrum_wl, spectrum_q, spectrum_j, transformations, trans_wl, trans_wld, transf_deriv,
                            psfs_q, psfs_j, psf_wl, psf_wld, psf_shape, psf_sampling, ccd, pixelsize, rng_states,
                            nphotons):
    max_y, max_x = ccd.shape
    thread_id = cuda.grid(1)

    for _ in range(thread_id, nphotons, cuda.gridDim.x * cuda.blockDim.x):
        # sample from spectrum
        k = int(math.floor(xoroshiro128p_uniform_float64(rng_states, thread_id) * len(spectrum_j)))
        wl = spectrum_wl[k] if xoroshiro128p_uniform_float64(rng_states, thread_id) < spectrum_q[k] else spectrum_wl[
            spectrum_j[k]]

        # find index for transformation
        idx_trans_float = (wl - trans_wl[0]) / trans_wld
        idx_trans = int(math.floor(idx_trans_float))
        r = (idx_trans_float - idx_trans)

        # do linear interpolation of transformation matrices
        # m0, m1, m2, m3, m4, m5 = transformations[:, idx_trans] + r * transf_deriv[:, idx_trans]
        m0, m1, m2, m3, m4, m5 = transformations[:, idx_trans]
        dm0, dm1, dm2, dm3, dm4, dm5 = transf_deriv[:, idx_trans]
        m0 += r * dm0
        m1 += r * dm1
        m2 += r * dm2
        m3 += r * dm3
        m4 += r * dm4
        m5 += r * dm5

        # random starting point in slit
        x = xoroshiro128p_uniform_float64(rng_states, thread_id)
        y = xoroshiro128p_uniform_float64(rng_states, thread_id)
        r = math.sqrt(x) / 2.
        phi = y * math.pi * 2
        x = r * math.cos(phi) + 0.5
        y = r * math.sin(phi) + 0.5

        # transform
        xt = m0 * x + m1 * y + m2
        yt = m3 * x + m4 * y + m5

        # apply PSF
        idx_psf = int((wl - psf_wl[0]) / psf_wld)  # find psf index
        # next 3 lines implement drawing random number via alias sampling
        k = int(math.floor(xoroshiro128p_uniform_float64(rng_states, thread_id) * len(psfs_j[idx_psf])))
        if not xoroshiro128p_uniform_float64(rng_states, thread_id) < psfs_q[idx_psf][k]:
            k = psfs_j[idx_psf][k]

        # unravel 2d index
        dy = k % psf_shape[1]
        k = k // psf_shape[1]
        dx = k % psf_shape[0]

        # dx, dy = unravel_index(k, psf_shape)
        xt += (dx - psf_shape[1] / 2.) * psf_sampling / pixelsize
        yt += (dy - psf_shape[0] / 2.) * psf_sampling / pixelsize
        x_int = int(math.floor(xt))
        y_int = int(math.floor(yt))

        if (0 <= x_int < max_x) and (0 <= y_int < max_y):
            numba.cuda.atomic.inc(ccd, (y_int, x_int), 4294967295)


@cuda.jit()
def cuda_raytrace_octagonalslit(spectrum_wl, spectrum_q, spectrum_j, transformations, trans_wl, trans_wld, transf_deriv,
                                psfs_q, psfs_j, psf_wl, psf_wld, psf_shape, psf_sampling, ccd, pixelsize, rng_states,
                                nphotons):
    max_y, max_x = ccd.shape
    thread_id = cuda.grid(1)

    for _ in range(thread_id, nphotons, cuda.gridDim.x * cuda.blockDim.x):
        # sample from spectrum
        k = int(math.floor(xoroshiro128p_uniform_float64(rng_states, thread_id) * len(spectrum_j)))
        wl = spectrum_wl[k] if xoroshiro128p_uniform_float64(rng_states, thread_id) < spectrum_q[k] else spectrum_wl[
            spectrum_j[k]]

        # find index for transformation
        idx_trans_float = (wl - trans_wl[0]) / trans_wld
        idx_trans = int(math.floor(idx_trans_float))
        r = (idx_trans_float - idx_trans)

        # do linear interpolation of transformation matrices
        # m0, m1, m2, m3, m4, m5 = transformations[:, idx_trans] + r * transf_deriv[:, idx_trans]
        m0, m1, m2, m3, m4, m5 = transformations[:, idx_trans]
        dm0, dm1, dm2, dm3, dm4, dm5 = transf_deriv[:, idx_trans]
        m0 += r * dm0
        m1 += r * dm1
        m2 += r * dm2
        m3 += r * dm3
        m4 += r * dm4
        m5 += r * dm5

        # random starting point in slit
        r1 = xoroshiro128p_uniform_float64(rng_states, thread_id)
        r2 = xoroshiro128p_uniform_float64(rng_states, thread_id)
        phi = 0.
        s1 = math.sqrt(r1)
        phi_segment = 2. * math.pi / 8.

        b = (1., 0.)
        c = (math.cos(phi_segment), math.sin(phi_segment))
        xx = b[0] * (1.0 - r2) * s1 + c[0] * r2 * s1
        yy = b[1] * (1.0 - r2) * s1 + c[1] * r2 * s1

        segments = math.floor(xoroshiro128p_uniform_float64(rng_states, thread_id) * 8.)
        arg_values = phi_segment * segments + phi
        cos_values = math.cos(arg_values)
        sin_values = math.sin(arg_values)
        x = (xx * cos_values - yy * sin_values) / 2. + 0.5
        y = (xx * sin_values + yy * cos_values) / 2. + 0.5

        # transform
        xt = m0 * x + m1 * y + m2
        yt = m3 * x + m4 * y + m5

        # apply PSF
        idx_psf = int((wl - psf_wl[0]) / psf_wld)  # find psf index
        # next 3 lines implement drawing random number via alias sampling
        k = int(math.floor(xoroshiro128p_uniform_float64(rng_states, thread_id) * len(psfs_j[idx_psf])))
        if not xoroshiro128p_uniform_float64(rng_states, thread_id) < psfs_q[idx_psf][k]:
            k = psfs_j[idx_psf][k]

        # unravel 2d index
        dy = k % psf_shape[1]
        k = k // psf_shape[1]
        dx = k % psf_shape[0]

        # dx, dy = unravel_index(k, psf_shape)
        xt += (dx - psf_shape[1] / 2.) * psf_sampling / pixelsize
        yt += (dy - psf_shape[0] / 2.) * psf_sampling / pixelsize
        x_int = int(math.floor(xt))
        y_int = int(math.floor(yt))

        if (0 <= x_int < max_x) and (0 <= y_int < max_y):
            numba.cuda.atomic.inc(ccd, (y_int, x_int), 4294967295)


@cuda.jit()
def cuda_raytrace_hexagonalslit(spectrum_wl, spectrum_q, spectrum_j, transformations, trans_wl, trans_wld, transf_deriv,
                                psfs_q, psfs_j, psf_wl, psf_wld, psf_shape, psf_sampling, ccd, pixelsize, rng_states,
                                nphotons):
    max_y, max_x = ccd.shape
    thread_id = cuda.grid(1)

    for _ in range(thread_id, nphotons, cuda.gridDim.x * cuda.blockDim.x):
        # sample from spectrum
        k = int(math.floor(xoroshiro128p_uniform_float64(rng_states, thread_id) * len(spectrum_j)))
        wl = spectrum_wl[k] if xoroshiro128p_uniform_float64(rng_states, thread_id) < spectrum_q[k] else spectrum_wl[
            spectrum_j[k]]

        # find index for transformation
        idx_trans_float = (wl - trans_wl[0]) / trans_wld
        idx_trans = int(math.floor(idx_trans_float))
        r = (idx_trans_float - idx_trans)

        # do linear interpolation of transformation matrices
        # m0, m1, m2, m3, m4, m5 = transformations[:, idx_trans] + r * transf_deriv[:, idx_trans]
        m0, m1, m2, m3, m4, m5 = transformations[:, idx_trans]
        dm0, dm1, dm2, dm3, dm4, dm5 = transf_deriv[:, idx_trans]
        m0 += r * dm0
        m1 += r * dm1
        m2 += r * dm2
        m3 += r * dm3
        m4 += r * dm4
        m5 += r * dm5

        # random starting point in slit
        r1 = xoroshiro128p_uniform_float64(rng_states, thread_id)
        r2 = xoroshiro128p_uniform_float64(rng_states, thread_id)
        phi = 0.
        s1 = math.sqrt(r1)
        phi_segment = 2. * math.pi / 6.

        b = (1., 0.)
        c = (math.cos(phi_segment), math.sin(phi_segment))
        xx = b[0] * (1.0 - r2) * s1 + c[0] * r2 * s1
        yy = b[1] * (1.0 - r2) * s1 + c[1] * r2 * s1

        segments = math.floor(xoroshiro128p_uniform_float64(rng_states, thread_id) * 6.)
        arg_values = phi_segment * segments + phi
        cos_values = math.cos(arg_values)
        sin_values = math.sin(arg_values)
        x = (xx * cos_values - yy * sin_values) / 2. + 0.5
        y = (xx * sin_values + yy * cos_values) / 2. + 0.5

        # transform
        xt = m0 * x + m1 * y + m2
        yt = m3 * x + m4 * y + m5

        # apply PSF
        idx_psf = int((wl - psf_wl[0]) / psf_wld)  # find psf index
        # next 3 lines implement drawing random number via alias sampling
        k = int(math.floor(xoroshiro128p_uniform_float64(rng_states, thread_id) * len(psfs_j[idx_psf])))
        if not xoroshiro128p_uniform_float64(rng_states, thread_id) < psfs_q[idx_psf][k]:
            k = psfs_j[idx_psf][k]

        # unravel 2d index
        dy = k % psf_shape[1]
        k = k // psf_shape[1]
        dx = k % psf_shape[0]

        # dx, dy = unravel_index(k, psf_shape)
        xt += (dx - psf_shape[1] / 2.) * psf_sampling / pixelsize
        yt += (dy - psf_shape[0] / 2.) * psf_sampling / pixelsize
        x_int = int(math.floor(xt))
        y_int = int(math.floor(yt))

        if (0 <= x_int < max_x) and (0 <= y_int < max_y):
            numba.cuda.atomic.inc(ccd, (y_int, x_int), 4294967295)


def raytrace_order_cuda(o, spec: ZEMAX, source: Source, telescope: Telescope, rv: float, t, ccd, ps, efficiency=None,
                        seed=-1):
    wavelength = np.linspace(*spec.get_wavelength_range(o), num=100000)
    if seed < 0:
        seed = np.random.randint(0, np.iinfo(np.int64).max)
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

    spectrum_sampler_q, spectrum_sampler_j = make_alias_sampling_arrays(np.asarray(flux_photons / np.sum(flux_photons),
                                                                                   dtype=np.float32))

    psf_sampling = spec.psfs[f"psf_order_{o}"].sampling

    threads_per_block = 128
    blocks = 64
    rng_states = create_xoroshiro128p_states(threads_per_block * blocks, seed=seed)

    if spec.field_shape == "rectangular":
        cuda_raytrace = cuda_raytrace_rectangularslit
    elif spec.field_shape == "octagonal":
        cuda_raytrace = cuda_raytrace_octagonalslit
    elif spec.field_shape == "hexagonal":
        cuda_raytrace = cuda_raytrace_hexagonalslit
    elif spec.field_shape == "circular":
        cuda_raytrace = cuda_raytrace_roundslit
    else:
        raise NotImplementedError(f"Field shape {spec.field_shape} is not implemented.")

    cuda_raytrace[threads_per_block, blocks](np.ascontiguousarray(wavelength), np.ascontiguousarray(spectrum_sampler_q),
                                             np.ascontiguousarray(spectrum_sampler_j),
                                             np.ascontiguousarray(transformations), np.ascontiguousarray(trans_wl),
                                             trans_wld, np.ascontiguousarray(trans_deriv),
                                             np.ascontiguousarray(psf_sampler_qj[:, 0]),
                                             np.ascontiguousarray(psf_sampler_qj[:, 1]), np.ascontiguousarray(psfs_wl),
                                             psfs_wld[0],
                                             np.ascontiguousarray(psf_shape), psf_sampling[0],
                                             ccd, float(ps), rng_states,
                                             total_photons)
    return total_photons
