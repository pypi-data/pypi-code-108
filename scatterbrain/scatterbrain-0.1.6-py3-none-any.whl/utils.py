"""basic utility functions"""
import logging
import warnings

import fitsio
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.convolution import Gaussian1DKernel, convolve
from astropy.stats import sigma_clip, sigma_clipped_stats
from astropy.time import Time
from astropy.utils.exceptions import AstropyWarning
from fbpca import pca
from matplotlib import animation
from scipy.signal import medfilt
from tqdm import tqdm

from . import PACKAGEDIR
from .cupy_numpy_imports import load_image, xp

log = logging.getLogger(__name__)


def _align_with_tpf(object, tpf):
    """Returns indicies to align a BackDrop object with a tpf

    Parameters
    ----------
    object: scatterbrain.ScatteredLightBackground or scatterbrain.StarScene
        BackDrop object to align
    tpf : lightkurve.TargetPixelFile
        TPF object to align

    Returns
    -------
    indices: xp.ndarray
        Array of indices in the BackDrop that are in the TPF
    tpf_indices: xp.ndarray
        Array of indices in the TPF that are in the BackDrop
    """
    idxs, jdxs = [], []
    for idx, t in enumerate(tpf.time.value):
        k = (object.tstart - t) < 0
        k &= (object.tstop - t) > 0
        if k.sum() == 1:
            idxs.append(idx)
            jdxs.append(np.where(k)[0][0])
    return np.asarray(jdxs), np.asarray(idxs)


def _spline_basis_vector(x, degree, i, knots):
    """Recursive function to create a single spline basis vector for an ixput x,
    for the ith knot.
    See https://en.wikipedia.org/wiki/B-spline for a definition of B-spline
    basis vectors

    NOTE: This is lifted out of the funcs I wrote for lightkurve

    Parameters
    ----------
    x : cp.ndarray
        Ixput x
    degree : int
        Degree of spline to calculate basis for
    i : int
        The index of the knot to calculate the basis for
    knots : cp.ndarray
        Array of all knots
    Returns
    -------
    B : cp.ndarray
        A vector of same length as x containing the spline basis for the ith knot
    """
    if degree == 0:
        B = xp.zeros(len(x))
        B[(x >= knots[i]) & (x <= knots[i + 1])] = 1
    else:
        da = knots[degree + i] - knots[i]
        db = knots[i + degree + 1] - knots[i + 1]
        if (knots[degree + i] - knots[i]) != 0:
            alpha1 = (x - knots[i]) / da
        else:
            alpha1 = xp.zeros(len(x))
        if (knots[i + degree + 1] - knots[i + 1]) != 0:
            alpha2 = (knots[i + degree + 1] - x) / db
        else:
            alpha2 = xp.zeros(len(x))
        B = (_spline_basis_vector(x, (degree - 1), i, knots)) * (alpha1) + (
            _spline_basis_vector(x, (degree - 1), (i + 1), knots)
        ) * (alpha2)
    return B


def get_star_mask(f):
    """False where stars are. Keep in mind this might be a bad
    set of hard coded parameters for some TESS images!"""
    # This removes pixels where there is a steep flux gradient
    star_mask = (xp.hypot(*xp.gradient(f)) < 30) & (f < 9e4)
    # This broadens that mask by one pixel on all sides
    star_mask = (
        ~(xp.asarray(xp.gradient(star_mask.astype(float))) != 0).any(axis=0) & star_mask
    )
    return star_mask


def _find_saturation_column_centers(mask):
    """
    Finds the center point of saturation columns.
    Parameters
    ----------
    mask : xp.ndarray of bools
        Mask where True indicates a pixel is saturated
    Returns
    -------
    centers : xp.ndarray
        Array of the centers in XY space for all the bleed columns
    """
    centers = []
    radii = []
    idxs = xp.where(mask.any(axis=0))[0]
    for idx in idxs:
        line = mask[:, idx]
        seq = []
        val = line[0]
        jdx = 0
        while jdx <= len(line):
            while line[jdx] == val:
                jdx += 1
                if jdx >= len(line):
                    break
            if jdx >= len(line):
                break
            seq.append(jdx)
            val = line[jdx]
        w = xp.array_split(line, seq)
        v = xp.array_split(xp.arange(len(line)), seq)
        coords = [(idx, v1.mean().astype(int)) for v1, w1 in zip(v, w) if w1.all()]
        rads = [len(v1) / 2 for v1, w1 in zip(v, w) if w1.all()]
        for coord, rad in zip(coords, rads):
            centers.append(coord)
            radii.append(rad)
    centers = xp.asarray(centers)
    radii = xp.asarray(radii)
    return centers, radii


def get_sat_mask(f):
    """False where saturation spikes are. Keep in mind this might be a bad
    set of hard coded parameters for some TESS images!"""
    sat = f > 9e4
    l, r = _find_saturation_column_centers(sat)
    col, row = xp.mgrid[: f.shape[0], : f.shape[1]]
    l, r = l[r > 1], r[r > 1]
    for idx in range(len(r)):
        sat |= (xp.hypot(row - l[idx, 0], col - l[idx, 1]) < (r[idx] * 2)) & (
            xp.abs(col - l[idx, 1]) < xp.ceil(xp.min([r[idx] * 0.5, 7]))
        )
        sat |= xp.hypot(row - l[idx, 0], col - l[idx, 1]) < (r[idx] * 0.75)

    return ~sat


def _package_pca_comps(backdrop, xpca_components=20, split_time_domain=False):
    """Packages the jitter terms into detrending vectors similar to CBVs.
    If `split_time_domain` then splits the jitter into timescales of:
        - t < 0.5 days
        - t > 0.5 days
    Parameters
    ----------
    backdrop: tess_backdrop.FullBackDrop
        Ixput backdrop to package
    xpca_components : int
        Number of pca components to compress into. Default 20, which will result
        in an ntimes x 40 matrix if `split_time_domain`.
    split_time_domain: bool
        If True will split into two different time scales. Otherwise will take a PCA.

    Returns
    -------
    matrix : xp.ndarray
        The packaged jitter matrix will contains the top principle components
        of the jitter matrix.
    """

    for label in ["jitter", "bkg"]:
        comp = getattr(backdrop, label)
        comp = xp.asarray(comp)
        finite = np.isfinite(comp).all(axis=1)
        # If there aren't enough components, just return them.
        if comp.shape[0] < 40:
            setattr(backdrop, label + "_pack", comp)
            continue
        if finite.sum() < 50:
            setattr(backdrop, label + "_pack", comp)
            continue

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=AstropyWarning)
            if label == "jitter":
                sigma = 2
            else:
                sigma = 5
            perc = np.diff(np.nanpercentile(comp, [90, 10], axis=0), axis=0)[0]
            m = ~sigma_clip(perc, sigma=sigma).mask
            comp = comp[:, m]

        # We split at data downlinks where there is a gap of at least 0.2 days
        breaks = xp.where(xp.diff(backdrop.tstart[finite]) > 0.2)[0] + 1
        breaks = xp.hstack([0, breaks, len(backdrop.tstart[finite])])

        comp_short = comp[finite].copy()

        if split_time_domain:
            nb = int(0.5 / xp.median(xp.diff(backdrop.tstart)))
            nb = [nb if (nb % 2) == 1 else nb + 1][0]

            def smooth(x):
                return xp.asarray([medfilt(x[:, tdx], nb) for tdx in range(x.shape[1])])

            comp_medium = xp.hstack(
                [smooth(comp[finite][x1:x2]) for x1, x2 in zip(breaks[:-1], breaks[1:])]
            ).T

            U1, s, V = pca(
                comp_short - comp_medium, xpca_components, n_iter=10, raw=True
            )
            U2, s, V = pca(comp_medium, xpca_components, n_iter=10, raw=True)

            X = xp.hstack(
                [
                    U1,
                    U2,
                ]
            )
            X = xp.hstack(
                [X[:, idx::xpca_components] for idx in range(xpca_components)]
            )
            Xall = np.zeros((backdrop.tstart.shape[0], X.shape[1]))
            Xall[finite] = X
        else:
            X, s, V = pca(comp_short, xpca_components, n_iter=10, raw=True)
            Xall = np.zeros((backdrop.tstart.shape[0], X.shape[1]))
            Xall[finite] = X
        setattr(backdrop, label + "_pack", Xall)
    return


def movie(data, out="out.mp4", scale="linear", title="", **kwargs):
    fig, ax = plt.subplots(1, 1, figsize=(4.5, 4.5))
    ax.set_facecolor("#ecf0f1")
    im = ax.imshow(data[0], origin="lower", **kwargs)
    xlims, ylims = ax.get_xlim(), ax.get_ylim()

    ax.set(xlim=xlims, ylim=ylims)
    ax.set_xticks([])
    ax.set_yticks([])

    def animate(i):
        im.set_array(data[i])
        return im

    anim = animation.FuncAnimation(fig, animate, frames=len(data), interval=30)
    anim.save(out, dpi=150)


def test_strip(fname, value=False):
    """Test whether any of the CCD strips are saturated"""
    f = np.median(
        np.abs(fitsio.FITS(fname)[1][:10, 44 : 2048 + 44].mean(axis=0)).reshape(
            (4, 512)
        ),
        axis=1,
    )
    if value:
        return f
    return f > 10000


def identify_bad_frames(fnames):
    test = np.asarray([test_strip(fname, value=True) for fname in fnames])
    s = sigma_clipped_stats(test.std(axis=1))
    return convolve(((test.std(axis=1) - s[1]) / s[2]) > 8, Gaussian1DKernel(2)) != 0


def minmax(x, shape=2048):
    return np.min(
        [np.max([x, np.zeros_like(x)], axis=0), np.zeros_like(x) + shape - 1], axis=0
    ).astype(int)


def _validate_inputs(fnames, sector, camera, ccd):
    if not isinstance(fnames, (list, xp.ndarray)):
        raise ValueError("Pass an array of file names")
    if not isinstance(fnames[0], (str)):
        raise ValueError("Pass an array of strings")
    if sector is None:
        try:
            sector = int(fnames[0].split("-s")[1].split("-")[0])
        except ValueError:
            raise ValueError("Can not parse file name for sector number")
    if camera is None:
        try:
            camera = fitsio.read_header(fnames[0], ext=1)["CAMERA"]
        except ValueError:
            raise ValueError("Can not find a camera number")
    if ccd is None:
        try:
            ccd = fitsio.read_header(fnames[0], ext=1)["CCD"]
        except ValueError:
            raise ValueError("Can not find a CCD number")
    log.debug(f"Validated inputs for sector{sector}, camera{camera}, ccd{ccd}")
    return fnames, sector, camera, ccd


def get_asteroid_files(catalog_fname, sectors, magnitude_limit=18):
    """Get files for each sector containing asteroid locations in the image."""
    import os
    import pickle

    import tess_ephem as te

    sector_times = pickle.load(open(f"{PACKAGEDIR}/data/tess_sector_times.pkl", "rb"))

    df_raw = pd.read_csv(catalog_fname, low_memory=False)
    for sector in np.atleast_1d(sectors):
        df = (
            df_raw[
                (df_raw.max_Vmag != 0)
                & (df_raw.sector == sector)
                & (df_raw.max_Vmag <= magnitude_limit)
            ]
            .drop_duplicates("pdes")
            .reset_index(drop=True)
        )
        t = Time(sector_times[sector] + 2457000, format="jd")
        t += np.median(np.diff(t.value)) / 2

        asteroid_df = pd.DataFrame(
            columns=np.hstack(
                [
                    "camera",
                    "ccd",
                    "vmag",
                    [f"{i}r" for i in np.arange(len(t))],
                    [f"{i}c" for i in np.arange(len(t))],
                ]
            ),
            dtype=np.int16,
        )
        names = []
        jdx = 0
        for idx, d in tqdm(df.iterrows(), total=len(df), desc=f"Sector {sector}"):
            ast = te.ephem(
                d.pdes, interpolation_step="6H", time=t, sector=sector, verbose=True
            )[["sector", "camera", "ccd", "column", "row", "vmag"]]

            ast.replace(np.nan, -1, inplace=True)
            for camera in ast.camera.unique():
                for ccd in ast[ast.camera == camera].ccd.unique():
                    j = np.asarray((ast.camera == camera) & (ast.ccd == ccd))
                    k = np.in1d(t.jd, [i.jd for i in ast[j].index])
                    row, col = np.zeros((2, k.shape[0])) - 1
                    row[k] = ast[j].row
                    col[k] = ast[j].column
                    names.append(d.pdes)
                    if (ast["vmag"] > 0).sum() == 0:
                        vmagmean = -99
                    else:
                        vmagmean = np.round(ast["vmag"][ast["vmag"] > 0].mean())
                    asteroid_df.loc[jdx] = np.hstack(
                        [camera, ccd, vmagmean, row, col]
                    ).astype(np.int16)
                    jdx += 1
        path = f"{PACKAGEDIR}/data/sector{sector:03}/"
        if not os.path.isdir(path):
            os.mkdir(path)
        if os.path.isfile(f"{path}bright_asteroids.hdf"):
            os.remove(f"{path}bright_asteroids.hdf")
        asteroid_df.to_hdf(
            f"{path}bright_asteroids.hdf",
            **{"key": f"asteroid_sector{sector}", "format": "fixed", "complevel": 9},
        )


def get_asteroid_locations(sector=1, camera=1, ccd=1, times=None):
    """Get the row and column positions of asteroids in sector, camera, ccd

    Returns
    -------

    row:

    col:
    """
    import pickle

    sector_times = pickle.load(open(f"{PACKAGEDIR}/data/tess_sector_times.pkl", "rb"))

    df = pd.read_hdf(f"{PACKAGEDIR}/data/sector{sector:03}/bright_asteroids.hdf")
    df = df[(df.camera == camera) & (df.ccd == ccd)].reset_index(drop=True)

    vmag = np.asarray(df["vmag"])
    row = (
        np.asarray(df)[:, 2:][:, np.asarray([d.endswith("r") for d in df.columns[2:]])]
        - 0.5
    )
    col = (
        np.asarray(df)[:, 2:][:, np.asarray([d.endswith("c") for d in df.columns[2:]])]
        - 45.5
    )
    if times is None:
        time_mask = np.ones(row.shape[1], bool)
    else:
        time_mask = np.any(
            [np.isclose(sector_times[sector], t, atol=1e-6) for t in times], axis=0
        )

    return vmag, row[:, time_mask], col[:, time_mask]


def get_asteroid_mask(sector=1, camera=1, ccd=1, cutout_size=2048, times=None):
    """Load a saved bright asteroid file as a 2048x2048 pixel mask.

    Use time mask to specify which times to use.
    """

    mask = np.zeros((cutout_size, cutout_size), bool)

    vmag, row, col = get_asteroid_locations(
        sector=sector, camera=camera, ccd=ccd, times=times
    )

    def func(row, col, ap=3):
        X, Y = np.mgrid[-ap : ap + 1, -ap : ap + 1]
        aper = np.hypot(X, Y) <= ap
        aper_locs = np.asarray(np.where(aper)).T - ap
        for idx in range(row.shape[0]):
            k = (
                (row[idx] >= 0)
                & (col[idx] > 0)
                & (row[idx] < cutout_size)
                & (col[idx] < cutout_size)
            )
            for loc in aper_locs:
                l1 = minmax(row[idx, k] + loc[0], shape=cutout_size)
                l2 = minmax(col[idx, k] + loc[1], shape=cutout_size)
                mask[l1, l2] = True

    func(row[vmag >= 14], col[vmag >= 14], ap=5)
    func(row[(vmag < 14) & (vmag >= 11)], col[(vmag < 14) & (vmag >= 11)], ap=7)
    func(row[(vmag < 11)], col[(vmag < 11)], ap=9)
    return mask


def get_locs(im_size=2048, batch_size=512):
    """Get an array of the corners of an image if split into batches

    Parameters
    ----------
    im_size : int
        Size of the image to split
    batch_size: int
        Size of the desired batches

    Returns
    -------
    locs: list of list of tuples
        List of batches. Length number of batches. Each element is a list, of tuples
        which describes the corner of the batch.
    """
    locs = []
    nbatches = im_size // batch_size
    if im_size % batch_size != 0:
        nbatches += 1
    for bdx1 in range(nbatches):
        for bdx2 in range(nbatches):
            locs.append(
                [
                    (batch_size * bdx1, np.min([im_size, batch_size * (bdx1 + 1)])),
                    (batch_size * bdx2, np.min([im_size, batch_size * (bdx2 + 1)])),
                ]
            )
    return locs


def get_min_image_from_filenames(fnames, cutout_size=2048):
    """Find the minimum image in a list of file names.

    Breaks image into batches and loads segments of the image so as not to
    fill up memory.

    Parameters
    ----------
    fnames : list of str
        List of filenames
    cutout_size: int, Optional
        Optional size of the image to cut out.
    Returns
    -------
    ar : np.ndarray
        2D image that is the minimum image in the stack.
    """
    batch_size = np.max([512, int(2 ** (np.log2(cutout_size) - 2))])
    f = np.zeros((cutout_size, cutout_size))
    for loc in get_locs(cutout_size, batch_size):
        f[loc[0][0] : loc[0][1], loc[1][0] : loc[1][1]] = np.min(
            [load_image(fname, loc=loc) for fname in fnames],
            axis=0,
        )
    return f
