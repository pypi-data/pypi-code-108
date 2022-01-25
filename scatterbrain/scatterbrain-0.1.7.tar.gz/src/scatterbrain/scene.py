import logging
import os
from copy import deepcopy
from dataclasses import dataclass
from typing import Optional

import fitsio
import numpy as np
from astropy.io import fits
from astropy.stats import sigma_clip
from tqdm import tqdm

from . import PACKAGEDIR
from .background import ScatteredLightBackground
from .cupy_numpy_imports import load_image, xp
from .utils import (
    _align_with_tpf,
    _spline_basis_vector,
    _validate_inputs,
    get_asteroid_locations,
    get_locs,
    minmax,
)
from .version import __version__

log = logging.getLogger(__name__)


@dataclass
class StarScene:
    """Class to remove stars and jitter noise from TESS images.

    This class will take a stack of TESS FFIs, and will use the ScatteredLightBackground
    class to remove scattered light from the images. The ScatteredLightBackground also
    provides an estimate of the "jitter" in pixels as the top principal components of
    bright pixels in the dataset, and the average image. StarScene takes these components
    and fits each individual pixel time series



    Parameters
    ----------
    sector : int
        TESS sector number
    camera: int
        TESS camera number
    ccd : int
        TESS CCD number
    batch_size: int
        This will process the fits images in "batches". The larger the batch_size,
        the more memory fitting will take. 512 is a sane default.
    spline: bool
        Whether to correct time with a spline. If False, will use a 2nd order polynomial.
        If True, will use a 40 knot spline for every pixel.
    ncomps: int
        Number of components from the background model to use. Default is 15. Maximum is 20.
    """

    sector: int
    camera: int
    ccd: int
    row: Optional = None
    column: Optional = None
    batch_size: int = 512
    spline: bool = False
    ncomps: int = 10
    dir: Optional = None

    def __post_init__(self):
        if (self.row is None) | (self.column is None):
            self.row = np.arange(2048)
            self.column = np.arange(2048)
        else:
            self.row = np.atleast_1d(self.row)
            self.column = np.atleast_1d(self.column)

        self.ncomps = np.min([self.ncomps, 20])
        log.debug("Loading ScatteredLightBackground")
        self.background = ScatteredLightBackground.from_disk(
            sector=self.sector,
            camera=self.camera,
            ccd=self.ccd,
            row=np.asarray([1]),
            column=np.asarray([1]),
            dir=self.dir,
        )
        log.debug("Loaded ScatteredLightBackground")
        self.break_point = np.where(
            (
                np.diff(self.background.tstart)
                / np.median(np.diff(self.background.tstart))
            )
            > 10
        )[0][0]
        self.orbit_masks = [
            np.arange(len(self.background.tstart)) <= self.break_point,
            np.arange(len(self.background.tstart)) > self.break_point,
        ]
        log.debug("Building design matrices")
        if self.spline:
            self.Xs = [
                self._get_spline_design_matrix(
                    self.orbit_masks[0], bounds=(-0.5, 0), ncomps=self.ncomps
                ),
                self._get_spline_design_matrix(
                    self.orbit_masks[1], bounds=(0, 0.5), ncomps=self.ncomps
                ),
            ]
        else:
            self.Xs = [
                self._get_design_matrix(self.orbit_masks[0], ncomps=self.ncomps),
                self._get_design_matrix(self.orbit_masks[1], ncomps=self.ncomps),
            ]
        log.debug("Built")

        self.weights = [
            np.zeros(
                (self.Xs[0].shape[1], self.row.shape[0], self.column.shape[0]),
                np.float32,
            ),
            np.zeros(
                (self.Xs[0].shape[1], self.row.shape[0], self.column.shape[0]),
                np.float32,
            ),
        ]

        self.bad_pixels = [
            np.zeros(
                (self.row.shape[0], self.column.shape[0]),
                bool,
            ),
            np.zeros(
                (self.row.shape[0], self.column.shape[0]),
                bool,
            ),
        ]
        self.tstart = self.background.tstart
        self.tstop = self.background.tstop
        self.quality = self.background.quality
        return

    def quality_mask(self, quality_bitmask=175):
        return (self.quality.astype(int) & (8192 | quality_bitmask)) == 0

    @property
    def empty(self):
        return (self.weights[0] == 0).all() & (self.weights[1] == 0).all()

    @property
    def shape(self):
        return (len(self.tstart), self.row.shape[0], self.column.shape[0])

    def _load_background(self, row, column):
        try:
            self.background = ScatteredLightBackground.from_disk(
                sector=self.sector,
                camera=self.camera,
                ccd=self.ccd,
                row=row,
                column=column,
                dir=self.dir,
            )
        except ValueError:
            raise ValueError("No background solutions exist on disk.")

    def __repr__(self):
        return f"StarScene {self.shape}, Sector {self.sector}, Camera {self.camera}, CCD {self.ccd}"

    @property
    def path(self):
        return (
            f"{PACKAGEDIR}/data/sector{self.sector:03}/camera{self.camera:02}/ccd{self.ccd:02}/"
            f"tessstarscene_sector{self.sector}_camera{self.camera}_ccd{self.ccd}.fits.gz"
        )

    def __getitem__(self, key):
        """Set indexing"""
        if self.tstart is None:
            raise ValueError("Can not slice an object with no `tstart` array.")
        attrs = [
            item
            for item in self.__dir__()
            if not item.startswith("_")
            and isinstance(getattr(self, item), (xp.ndarray, list))
            and (xp.asarray(getattr(self, item)).shape[0] == len(self.tstart))
        ]
        copy = deepcopy(self)
        for attr in attrs:
            setattr(copy, attr, np.asarray(getattr(self, attr))[key])
            if isinstance(getattr(self, attr), list):
                setattr(copy, attr, list(getattr(copy, attr)))
        return copy

    def _get_spline_design_matrix(
        self, mask=None, ncomps=20, degree=2, nknots=20, bounds=(-0.5, 0.5)
    ):
        """Construct a design matrix from the ScatteredLightBackground object"""
        if mask is None:
            mask = np.ones(self.background.tstart.shape[0], bool)
        t = (self.background.tstart[mask] - self.background.tstart.mean()) / (
            self.background.tstart[-1] - self.background.tstart[0]
        )
        knots = (
            xp.linspace(*bounds, nknots + 2)[1:-1] + 1e-10
        )  # This stops numerical instabilities where x==knot value
        knots_wbounds = xp.append(
            xp.append([knots[0]] * (degree - 1), knots), [knots[-1]] * (degree + 2)
        )

        # 2D sparse matrix, for 2048 pixels
        As = xp.vstack(
            [
                _spline_basis_vector(t, degree, i, knots_wbounds)
                for i in xp.arange(-1, len(knots_wbounds) - degree - 3)
            ]
        ).T

        bkg = self.background.jitter_pack[mask, :ncomps]
        jitter = self.background.jitter_pack[mask, :ncomps]

        X = np.hstack(
            [
                bkg,
                jitter,
                # np.vstack([t ** 0, t, t ** 2]).T,
                As,
            ]
        )
        return X

    def _get_design_matrix(self, mask=None, ncomps=10):
        """Construct a design matrix from the ScatteredLightBackground object"""
        if mask is None:
            mask = np.ones(self.background.tstart.shape[0], bool)
        t = (self.background.tstart[mask] - self.background.tstart.mean()) / (
            self.background.tstart[-1] - self.background.tstart[0]
        )
        bkg = self.background.jitter_pack[mask, :ncomps]
        jitter = self.background.jitter_pack[mask, :ncomps]

        X = np.hstack(
            [
                bkg,
                jitter,
                np.vstack([t ** 0, t, t ** 2]).T,
            ]
        )
        return X

    @staticmethod
    def exists(sector=None, camera=None, ccd=None, dir=None):
        for type in ["backdrop", "starscene"]:
            fname = f"tess{type}_sector{sector}_camera{camera}_ccd{ccd}.fits.gz"
            if dir is None:
                dir = f"{PACKAGEDIR}/data/sector{sector:03}/camera{camera:02}/ccd{ccd:02}/"
            if dir != "":
                if not os.path.isdir(dir):
                    return False
            if not os.path.isfile(dir + fname):
                return False
        return True

    @staticmethod
    def from_tess_images(
        fnames, sector=None, camera=None, ccd=None, batch_size=512, plot=False, dir=None
    ):
        """Class to remove stars from TESS images

        Parameters
        ----------
        fnames : list of str
            File names to use to build the object
        sector : int
            TESS sector number
        camera: int
            TESS camera number
        ccd : int
            TESS CCD number
        batch_size: int
            This will process the fits images in "cutouts". The larger the cutout,
            the more memory fitting will take. 512 is a sane default.
        """
        log.debug("Building StarScene from TESS images")
        fnames, sector, camera, ccd = _validate_inputs(fnames, sector, camera, ccd)
        self = StarScene(
            sector=sector, camera=camera, ccd=ccd, batch_size=batch_size, dir=dir
        )
        log.debug("Fitting StarScene model")
        self.fit_model(fnames=fnames, batch_size=batch_size)
        if plot:
            fig = self.diagnose(fnames)
            return self, fig
        return self

    def diagnose(self, fnames, npix=512, ntimes=6):
        import matplotlib.pyplot as plt

        row = np.arange(1024 - npix // 2, 1024 + npix // 2)
        column = np.arange(1024 - npix // 2, 1024 + npix // 2)
        tdxs = np.linspace(0, self.shape[0], ntimes + 2, dtype=int)[1:-1]
        fig, ax = plt.subplots(ntimes, 3, figsize=(4 * 3, 4 * ntimes))
        for jdx, tdx in enumerate(tdxs):
            while self.quality[tdx] != 0:
                tdx += 1
            dat = load_image(fnames[tdx])
            v = np.nanpercentile(dat, (5, 95))
            ax[jdx, 0].imshow(dat[row][:, column], vmin=v[0], vmax=v[1])
            ax[jdx, 0].set_ylabel(f"{self.tstart[tdx]} BTJD")
            ax[jdx, 1].imshow(
                self.model(row, column, time_indices=tdx)[0], vmin=v[0], vmax=v[1]
            )
            ax[jdx, 2].imshow(
                dat[row][:, column] - self.model(row, column, time_indices=tdx)[0],
                vmin=-5,
                vmax=5,
            )
            for idx, title in enumerate(["Data", "Model", "Residuals"]):
                if jdx == 0:
                    ax[jdx, idx].set(title=title)
                ax[jdx, idx].set(xticks=[], yticks=[])
        plt.tight_layout()
        return fig

    @property
    def locs(self):
        """The locations of each of the cutouts. List of lists. Format is

        [[mininmum row, maxmimum row], [minimum column, maximum column]]
        """
        return get_locs(2048, 512)

    def load(self, input, dir=None):
        """
        Load a model fit from the data directory.

        Parameters
        ----------
        input: tuple or string
            Either pass a tuple with `(sector, camera, ccd)` or pass
            a file name in `dir` to load
        dir : str
            Optional tring with the directory name

        Returns
        -------
        self: `scatterbrain.StarScene` object
        """
        if isinstance(input, tuple):
            if len(input) == 3:
                sector, camera, ccd = input
                fname = f"tessstarscene_sector{sector}_camera{camera}_ccd{ccd}.fits"
            else:
                raise ValueError("Please pass tuple as `(sector, camera, ccd)`")
        elif isinstance(input, str):
            fname = input
        else:
            raise ValueError("Can not parse input")
        if dir is None:
            dir = f"{PACKAGEDIR}/data/sector{sector:03}/camera{camera:02}/ccd{ccd:02}/"
        if dir != "":
            if not os.path.isdir(dir):
                raise ValueError("No solutions exist")
        log.debug(f"Loading StarScene from {dir+fname}")
        with fits.open(dir + fname, lazy_load_hdus=True) as hdu:
            for key in [
                "sector",
                "camera",
                "ccd",
            ]:
                setattr(self, key, hdu[0].header[key])
            setattr(self, "batch_size", hdu[0].header["BATSIZE"])
            if "NCOMPS" in hdu[0].header:
                setattr(self, "ncomps", hdu[0].header["NCOMPS"])
            else:
                setattr(self, "ncomps", 15)

        self.weight_row = np.arange(self.row[0], self.row[-1] + 1)
        self.weight_column = np.arange(self.column[0], self.column[-1] + 1)
        self.weights = [
            fitsio.FITS(dir + fname)[1][
                :, self.row[0] : self.row[-1] + 1, self.column[0] : self.column[-1] + 1
            ],
            fitsio.FITS(dir + fname)[2][
                :, self.row[0] : self.row[-1] + 1, self.column[0] : self.column[-1] + 1
            ],
        ]
        self.bad_pixels = [
            fitsio.FITS(dir + fname)[3][
                self.row[0] : self.row[-1] + 1, self.column[0] : self.column[-1] + 1
            ].astype(bool),
            fitsio.FITS(dir + fname)[4][
                self.row[0] : self.row[-1] + 1, self.column[0] : self.column[-1] + 1
            ].astype(bool),
        ]
        return self

    @staticmethod
    def from_disk(sector, camera, ccd, dir=None, row=None, column=None):
        return StarScene(
            sector=sector,
            camera=camera,
            ccd=ccd,
            batch_size=512,
            row=row,
            column=column,
        ).load((sector, camera, ccd), dir=dir)

    def _package_weights_hdulist(self):
        hdu0 = self.hdu0
        hdu1 = fits.ImageHDU(np.asarray(self.weights[0]), name="ORBIT1")
        hdu2 = fits.ImageHDU(np.asarray(self.weights[1]), name="ORBIT2")
        hdu3 = fits.ImageHDU(self.bad_pixels[0].astype(int), name="BADPIX1")
        hdu4 = fits.ImageHDU(self.bad_pixels[1].astype(int), name="BADPIX2")
        hdul = fits.HDUList([hdu0, hdu1, hdu2, hdu3, hdu4])
        return hdul

    def save(self, output_dir=None, overwrite=False):
        """Save a StarScene"""
        log.debug("Packaging data for save")
        self.hdu0 = fits.PrimaryHDU()
        self.hdu0.header["ORIGIN"] = "scatterbrain"
        self.hdu0.header["AUTHOR"] = "christina.l.hedges@nasa.gov"
        self.hdu0.header["VERSION"] = __version__
        for key in ["sector", "camera", "ccd"]:
            self.hdu0.header[key] = getattr(self, key)
        self.hdu0.header["BATSIZE"] = getattr(self, "batch_size")
        self.hdu0.header["NCOMPS"] = getattr(self, "ncomps")

        if output_dir is None:
            output_dir = f"{PACKAGEDIR}/data/sector{self.sector:03}/camera{self.camera:02}/ccd{self.ccd:02}/"
            if output_dir != "":
                if not os.path.isdir(output_dir):
                    os.makedirs(output_dir)

        hdul = self._package_weights_hdulist()
        fname = (
            f"tessstarscene_sector{self.sector}_camera{self.camera}_ccd{self.ccd}.fits"
        )
        log.debug(f"Saving to {fname}")
        hdul.writeto(output_dir + fname, overwrite=overwrite)
        log.debug("Saved")
        if os.path.isfile(output_dir + fname + ".gz"):
            os.remove(f"{output_dir + fname}.gz")
        os.system(f"gzip {output_dir + fname}")
        log.debug("Compressed")
        return

    def get_images(self, fnames, loc, orbit=1):
        """Load the TESS FFIs, remove the best fitting scattered light model, and
        the best "average" frame, and return as an array.


        Parameters
        ----------
        fnames : list of str
            File names to use to build the object
        loc : list of lists
            Location of the cut out in format [[min row, max row], [min col, max col]]
        orbit: int, [1 or 2]
            Which orbit to get
        """
        if loc != [
            [self.background.row[0], self.background.row[-1] + 1],
            [self.background.column[0], self.background.column[-1] + 1],
        ]:
            self._load_background(row=np.arange(*loc[0]), column=np.arange(*loc[1]))
        y = np.zeros(
            (
                (self.background.quality[self.orbit_masks[orbit - 1]] == 0).sum(),
                *np.diff(loc).ravel(),
            )
        )
        idx = 0
        for tdx in np.where(self.orbit_masks[orbit - 1])[0]:
            if self.background.quality[tdx] != 0:
                continue
            y[idx] = (
                load_image(np.asarray(fnames)[tdx], loc=loc)
                - self.background.model(tdx)
                - self.background.average_frame
            )
            idx += 1
        return y

    def _mask_asteroids(self, flux_cube, loc, orbit):
        """Zero out any asteroids in a flux cube.

        Parameters
        ----------
        flux_cube : np.ndarray
            3D flux object, with shape [time, row, column]
        loc : list of lists
            Location of the cut out in format [[min row, max row], [min col, max col]]
        orbit: int, [1 or 2]
            Which orbit you are processing
        """
        tmask = (self.background.quality == 0) & self.orbit_masks[orbit - 1]
        vmag, row, col = get_asteroid_locations(
            self.sector, self.camera, self.ccd, times=self.tstart[tmask]
        )
        t = np.arange(row.shape[1])

        aps = {"faint": 3, "middle": 3, "bright": 5}
        tests = {
            "faint": lambda x: x > 14,
            "middle": lambda x: (x <= 14) & (x > 11),
            "bright": lambda x: x <= 11,
        }
        for idx in np.arange(row.shape[0]):
            ap = [aps[key] for key, item in tests.items() if item(vmag[idx])][0]
            k = (
                (row[idx] >= loc[0][0])
                & (row[idx] < loc[0][1])
                & (col[idx] >= loc[1][0])
                & (col[idx] < loc[1][1])
            )
            if not k.any():
                continue
            rdx, cdx = row[idx][k] - loc[0][0], col[idx][k] - loc[1][0]
            RDX, CDX = np.array_split(
                np.vstack(
                    [
                        minmax(v + offset, flux_cube.shape[1])
                        for v in [rdx, cdx]
                        for offset in np.arange(-ap, ap + 1)
                    ]
                ),
                2,
            )
            bad_pix = [np.vstack([r, c]) for r in RDX for c in CDX]
            for bdx in range(len(bad_pix)):
                flux_cube[t[k], bad_pix[bdx][0], bad_pix[bdx][1]] = 0

    def _fill_weights_block(self, fnames, loc, iter=False):
        """Process a cutout of the TESS FFIs. Will process the `loc` cutout.

        Parameters
        ----------
        fnames : list of str
            File names to use to build the object
        loc : list of lists
            Location of the cut out in format [[min row, max row], [min col, max col]]
        iter: bool
            Whether to iterate the fit. If True, will repeat the fit, masking
            the largest values in each pixel time series.
        """
        log.debug("Filling weight block")
        for orbit in [1, 2]:
            log.debug(f"Orbit {orbit}: loading images")
            y = self.get_images(fnames, loc, orbit=orbit)

            log.debug(f"Orbit {orbit}: masking asteroids")
            self._mask_asteroids(y, loc=loc, orbit=orbit)
            s = (y.shape[0], np.product(y.shape[1:]))
            X = self.Xs[orbit - 1][
                self.background.quality[self.orbit_masks[orbit - 1]] == 0
            ]
            prior_sigma = np.ones(X.shape[1]) * 1e8
            ws = np.linalg.solve(
                X.T.dot(X) + np.diag(1 / prior_sigma ** 2), X.T.dot(y.reshape(s))
            )
            res = y - X.dot(ws).reshape(y.shape)
            m = sigma_clip(res, sigma_upper=4, sigma_lower=1e10, axis=(1, 2)).mask
            self.bad_pixels[orbit - 1][loc[0][0] : loc[0][1], loc[1][0] : loc[1][1]] = (
                m.sum(axis=0) / y.shape[0]
            ) >= 0.05

            log.debug(f"Orbit {orbit}: fitting model")
            if iter:
                # res[
                #     sigma_clip(
                #         np.abs(res).sum(axis=(1, 2)), sigma_upper=5, sigma_lower=1e10
                #     ).mask
                # ] = 0
                res[
                    self.bad_pixels[orbit - 1][
                        loc[0][0] : loc[0][1], loc[1][0] : loc[1][1]
                    ]
                ] = 0
                for idx in range(5):
                    k = res == np.max(res, axis=0)
                    k = (
                        k
                        | np.vstack([k[1:], k[0][None, :, :]])
                        | np.vstack([k[-1][None, :, :], k[:-1]])
                    )
                    res[k] = 0
                ws2 = np.linalg.solve(X.T.dot(X), X.T.dot((y * (res != 0)).reshape(s)))
                self.weights[orbit - 1][
                    :, loc[0][0] : loc[0][1], loc[1][0] : loc[1][1]
                ] = ws2.reshape((ws.shape[0], *y.shape[1:])).astype(np.float32)
            else:
                self.weights[orbit - 1][
                    :, loc[0][0] : loc[0][1], loc[1][0] : loc[1][1]
                ] = ws.reshape((ws.shape[0], *y.shape[1:])).astype(np.float32)

    def fit_model(self, fnames, batch_size=512):
        """Fit a StarScene model to a set of TESS filenames"""
        for loc in tqdm(self.locs, desc=f"{self.sector}, {self.camera}, {self.ccd} "):
            self._fill_weights_block(fnames=fnames, loc=loc)
        log.debug("Inflating bad pixels")
        for idx in range(2):
            self.bad_pixels[idx] |= (
                np.asarray(np.gradient(self.bad_pixels[idx].astype(float))) != 0
            ).any(axis=0)

    def model(
        self, row=None, column=None, time_indices=None, mask_bad_pixels=True, trend=True
    ):
        """Returns a model for a given row and column.

        Parameters
        ----------
        row: np.ndarray
            Row to evaluate at
        column: np.ndarray
            Column to evaluate at
        time_indices: None, int, list of int
            Which indices to evaluate the model at. If None will use all.

        Returns
        -------
        model : np.ndarray
            Array of shape (time_indices, row, column) which has the full scene
            model, including scattered light.
        """
        if (row is None) | (column is None):
            row, column = self.row, self.column
        if time_indices is None:
            time_indices = np.arange(self.shape[0])
        single_frame = False
        if isinstance(time_indices, int):
            time_indices = [time_indices]
            single_frame = True
        if (len(row) != len(self.background.row)) | (
            len(column) != len(self.background.column)
        ):
            self._load_background(row=row, column=column)
        else:
            if not (
                (self.background.row == row).all()
                and (self.background.column == column).all()
            ):
                self._load_background(row=row, column=column)
        # r = np.where(np.in1d(self.weight_row, row))[0]
        # c = np.where(np.in1d(self.weight_column, column))[0]
        r, c = row - row[0], column - column[0]
        w1 = self.weights[0][:, r][:, :, c].reshape(
            (self.weights[0].shape[0], row.shape[0] * column.shape[0])
        )
        w2 = self.weights[1][:, r][:, :, c].reshape(
            (self.weights[1].shape[0], row.shape[0] * column.shape[0])
        )
        xmask1 = np.in1d(np.where(self.orbit_masks[0])[0], time_indices)
        xmask2 = np.in1d(np.where(self.orbit_masks[1])[0], time_indices)
        if trend:
            m1, m2 = self.Xs[0][xmask1].dot(w1), self.Xs[1][xmask2].dot(w2)
        else:
            m1, m2 = self.Xs[0][:, : self.ncomps * 2][xmask1].dot(
                w1[: self.ncomps * 2]
            ), self.Xs[1][:, : self.ncomps * 2][xmask2].dot(w2[: self.ncomps * 2])
        if mask_bad_pixels:
            bp1 = self.bad_pixels[0][r][:, c].reshape((row.shape[0] * column.shape[0]))
            bp2 = self.bad_pixels[1][r][:, c].reshape((row.shape[0] * column.shape[0]))
            m1[:, bp1] = np.nan
            m2[:, bp2] = np.nan
        model = np.vstack([m1, m2])
        model = model.reshape((model.shape[0], row.shape[0], column.shape[0]))
        background = self.background.model(time_indices)
        if single_frame:
            return model[0] + self.background.average_frame + background[0]
        return model + self.background.average_frame + background

    def model_moving(self, row3d, column3d, star_model=True, time_indices=None):
        if time_indices is None:
            time_indices = np.arange(self.shape[0])
        if (row3d.shape[0] != self.shape[0]) | (column3d.shape[0] != self.shape[0]):
            raise ValueError("Pass Row and Column positions for all times. ")
        model = np.zeros((row3d.shape[0], row3d.shape[1], column3d.shape[1])) * np.nan
        for orbit in [0, 1]:
            # mask = self.orbit_masks[orbit]
            mask = self.orbit_masks[orbit] & np.in1d(
                np.arange(self.shape[0]), time_indices
            )
            if mask.sum() == 0:
                continue
            s = (self.weights[orbit].shape[0], row3d.shape[1] * column3d.shape[1])
            r1, r2 = row3d[mask].min(), row3d[mask].max() + 1
            c1, c2 = column3d[mask].min(), column3d[mask].max() + 1

            self._load_background(np.arange(r1, r2), np.arange(c1, c2))
            background = self.background.model(np.where(mask)[0])
            for idx, tdx, row, column in zip(
                np.arange(mask.sum()), np.where(mask)[0], row3d[mask], column3d[mask]
            ):

                model[tdx] = (
                    +background[idx][row - r1][:, column - c1]
                    + self.background.average_frame[row - r1][:, column - c1]
                )
                if star_model:
                    w1 = self.weights[orbit][:, row][:, :, column].reshape(s)
                    model[tdx] += (
                        self.Xs[orbit][idx]
                        .dot(w1)
                        .reshape((row.shape[0], column.shape[0]))
                    )
                    model[tdx][self.bad_pixels[orbit][row][:, column]] = np.nan
        return model

    @staticmethod
    def from_tpf(tpf, dir=None):
        scene = StarScene(
            sector=tpf.sector,
            camera=tpf.camera,
            ccd=tpf.ccd,
            row=np.arange(tpf.shape[1]) + tpf.row - 1,
            column=np.arange(tpf.shape[2]) + tpf.column - 44 - 1,
        ).load((tpf.sector, tpf.camera, tpf.ccd), dir=dir)
        idx, jdx = _align_with_tpf(scene, tpf)
        return scene[idx]

    def get_tpf_mask(self, tpf):
        idx, jdx = _align_with_tpf(self, tpf)
        return jdx
