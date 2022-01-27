"""Tools that require the internet, and get asteroids"""
import os
import pickle
import warnings
from dataclasses import dataclass
from glob import glob
from typing import Optional

import astropy.units as u
import fitsio
import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tess_ephem as te
from astropy.stats import sigma_clip
from astropy.time import Time
from astropy.utils.exceptions import AstropyWarning
from matplotlib import patches
from scipy.interpolate import interp1d
from scipy.ndimage import label
from tqdm import tqdm

from . import PACKAGEDIR
from .scene import StarScene

sector_times = pickle.load(open(f"{PACKAGEDIR}/data/tess_sector_times.pkl", "rb"))


@dataclass
class AsteroidMetaCollection:
    name: str
    sectors: list
    cameras: list
    ccds: list
    aper: Optional = 7

    def __post_init__(self):
        self.asteroids = []
        last_sector = 0
        for sector, camera, ccd in zip(self.sectors, self.cameras, self.ccds):
            if sector not in sector_times.keys():
                continue
            if last_sector != sector:
                t = Time(sector_times[sector] + 2457000, format="jd")
                t += np.median(np.diff(t.value)) / 2
                asteroid = te.ephem(self.name, sector=sector, time=t, verbose=True)
                last_sector = sector
            k = (asteroid.camera == camera) & (asteroid.ccd == ccd)
            am = AsteroidMeta.from_dataframe(
                asteroid[k].join(pd.DataFrame(index=t), how="right"),
                name=self.name,
                aper=self.aper,
                sector=sector,
                camera=camera,
                ccd=ccd,
            )
            if am.mask.any():
                self.asteroids.append(am)
        if len(self.asteroids) == 0:
            raise ValueError(f"No valid asteroid data for sectors {self.sectors}")

    def __getitem__(self, key):
        return self.asteroids[key]

    def __len__(self):
        return len(self.asteroids)

    @staticmethod
    def from_name(name, sector=None, aper=7):
        if sector is not None:
            t = Time(sector_times[sector] + 2457000, format="jd")
            t += np.median(np.diff(t.value)) / 2
            ephem = te.ephem(name, time=t[::12])
        else:
            ephem = te.ephem(name, interpolation_step="6H")
        sectors, cameras, ccds = np.asarray(
            ephem.groupby(["sector", "camera", "ccd"])
            .first()
            .reset_index()[["sector", "camera", "ccd"]]
        ).T
        return AsteroidMetaCollection(name, sectors, cameras, ccds, aper=aper)

    def __repr__(self):
        return f"AsteroidMetaCollection: {self.name} ({len(self)} objects)"


@dataclass
class AsteroidMeta:
    row: list
    col: list
    vmag: list
    time: list
    name: Optional = None
    aper: Optional = 7
    sun_distance: Optional = None
    obs_distance: Optional = None
    phase_angle: Optional = None
    sector: Optional = None
    camera: Optional = None
    ccd: Optional = None

    def __repr__(self):
        repr = f"AsteroidMeta name:{self.name}"
        for key in ["sector", "camera", "ccd"]:
            if getattr(self, key) is not None:
                repr = f"{repr} {key}:{getattr(self, key)}"
        return repr

    @property
    def speed(self):
        if self.mask.any():
            return (
                np.abs(
                    np.gradient(
                        np.asarray(np.hypot(self.row, self.col))[self.mask],
                        self.time[self.mask],
                    )
                )
                * u.pixel
                / u.day
            )
        else:
            return np.atleast_1d(0) * u.pixel / u.day

    @property
    def lag(self):
        return (8 * u.pixel) / self.speed.min()

    @property
    def _fr(self):
        return interp1d(
            self.time[self.mask],
            np.asarray(self.row[self.mask]),
            bounds_error=False,
            fill_value="extrapolate",
        )

    @property
    def _fc(self):
        return interp1d(
            self.time[self.mask],
            np.asarray(self.col[self.mask]),
            bounds_error=False,
            fill_value="extrapolate",
        )

    def __post_init__(self):
        self.mask = (
            (self.row >= self.aper // 2)
            & (self.col >= self.aper // 2)
            & (self.row < (2048 - self.aper // 2))
            & (self.col < (2048 - self.aper // 2))
        )
        if not self.mask.any():
            self.xlag, self.x, self.xlead = (
                (self.row.astype(int), self.col.astype(int)),
                (self.row.astype(int), self.col.astype(int)),
                (self.row.astype(int), self.col.astype(int)),
            )
        else:
            self.xlag, self.x, self.xlead = [
                (
                    self._fr(self.time + l).astype(int),
                    self._fc(self.time + l).astype(int),
                )
                for l in [-self.lag.value, 0, self.lag.value]
            ]
            self.mask &= (
                (self.xlag[0] >= self.aper // 2)
                & (self.xlag[1] >= self.aper // 2)
                & (self.xlag[0] < (2048 - self.aper // 2))
                & (self.xlag[1] < (2048 - self.aper // 2))
            )
            self.mask &= (
                (self.xlead[0] >= self.aper // 2)
                & (self.xlead[1] >= self.aper // 2)
                & (self.xlead[0] < (2048 - self.aper // 2))
                & (self.xlead[1] < (2048 - self.aper // 2))
            )

    @staticmethod
    def from_dataframe(df, name=None, sector=None, camera=None, ccd=None, aper=7):
        return AsteroidMeta(
            row=np.asarray(df.row) - 0.5,
            col=np.asarray(df.column) - 45.5,
            vmag=np.asarray(df.vmag),
            sun_distance=np.asarray(df["sun_distance"]),
            obs_distance=np.asarray(df["obs_distance"]),
            phase_angle=np.asarray(df["phase_angle"]),
            time=np.asarray([i.jd for i in df.index]),
            sector=sector,
            camera=camera,
            ccd=ccd,
            aper=aper,
            name=name,
        )


@dataclass
class AsteroidExtractor:
    """Class to get asteroids out of tess data"""

    dir: str
    sector: int

    def __post_init__(self):
        """Class to get asteroids from TESS data

        Parameters
        ----------
        fnames: list of str
            Filenames of the TESS"""

        if not os.path.isdir(self.dir):
            raise ValueError("No such directory")
        if not os.path.isdir(f"{self.dir}/sector{self.sector:02}"):
            raise ValueError("No such sector")

        self.scenes, self.fnames = {}, {}
        for camera in np.arange(1, 5):
            for ccd in np.arange(1, 5):
                if StarScene.exists(self.sector, camera, ccd):
                    if camera not in self.scenes.keys():
                        self.scenes[camera] = {}
                    self.scenes[camera][ccd] = StarScene.from_disk(
                        self.sector, camera, ccd
                    )
                    if os.path.isdir(
                        f"{self.dir}/sector{self.sector:02}/camera{camera:02}/ccd{ccd:02}"
                    ):
                        if camera not in self.fnames.keys():
                            self.fnames[camera] = {}
                        self.fnames[camera][ccd] = np.sort(
                            glob(
                                f"{self.dir}/sector{self.sector:02}/camera{camera:02}/ccd{ccd:02}/*_ffic.fits"
                            )
                        )
                    else:
                        raise ValueError(
                            f"Please provide fits files for camera {camera} ccd {ccd}"
                        )
        self.time = (
            sector_times[self.sector]
            + np.median(np.diff(sector_times[self.sector])) / 2
        ) + 2457000

    def __repr__(self):
        return f"AsteroidExtractor Sector {self.sector}"

    def get_asteroid_arrays(self, ast, aper=21):
        fnames = self.fnames[ast.camera][ast.ccd]
        ar = np.zeros((len(fnames), aper, aper, 3)) * np.nan
        er = np.zeros((len(fnames), aper, aper, 3)) * np.nan
        for idx, x in enumerate([ast.xlag, ast.x, ast.xlead]):
            r, c = x
            for tdx in range(len(fnames)):
                if (
                    (r[tdx] >= aper // 2)
                    & (c[tdx] >= aper // 2)
                    & (r[tdx] < (2048 + aper // 2 + 1))
                    & (c[tdx] < (2048 + aper // 2 + 1))
                ):
                    ar[tdx, :, :, idx] = fitsio.FITS(fnames[tdx])[1][
                        r[tdx] - aper // 2 : r[tdx] + aper // 2 + 1,
                        44 + c[tdx] - aper // 2 : 44 + c[tdx] + aper // 2 + 1,
                    ]
                    er[tdx, :, :, idx] = fitsio.FITS(fnames[tdx])[2][
                        r[tdx] - aper // 2 : r[tdx] + aper // 2 + 1,
                        44 + c[tdx] - aper // 2 : 44 + c[tdx] + aper // 2 + 1,
                    ]
        return ar, er

    def get_asteroid_lightcurve(self, name, aper=21, plot=False, quality_mask=175):
        collection = AsteroidMetaCollection.from_name(
            name, sector=self.sector, aper=aper
        )
        R, C = np.mgrid[:aper, :aper]
        R -= aper // 2
        C -= aper // 2

        lcs = []
        for ast in collection:
            ast.mask &= (
                self.scenes[ast.camera][ast.ccd].quality.astype(int)
                & (8192 | quality_mask)
            ) == 0

            ar, er = self.get_asteroid_arrays(ast, aper=aper)

            model = np.zeros(ar.shape)
            for idx, x in enumerate([ast.xlag, ast.x, ast.xlead]):
                r, c = x
                row3d = np.zeros((r.shape[0], aper), int)
                row3d = (
                    np.asarray(r).astype(int)
                    + np.arange(-aper // 2 + 1, aper // 2 + 1)[:, None]
                ).T
                column3d = np.zeros((r.shape[0], aper), int)
                column3d = (
                    np.asarray(c).astype(int)
                    + np.arange(-aper // 2 + 1, aper // 2 + 1)[:, None]
                ).T
                model[:, :, :, idx] = self.scenes[ast.camera][ast.ccd].model_moving(
                    row3d, column3d, time_indices=np.where(ast.mask)[0]
                )

            # Get aperture
            aperture_mask = self._get_aperture_mask(
                ar[:, :, :, 1] - model[:, :, :, 1], er[:, :, :, 1]
            )

            bkg = (
                np.nanmedian(
                    ar[:, ~aperture_mask, :] - model[:, ~aperture_mask, :], axis=1
                )
            )[:, None, None, :]
            ar -= bkg
            # Get photometery
            flux = (ar[:, aperture_mask, 1] - model[:, aperture_mask, 1]).sum(axis=1)[
                ast.mask
            ]
            flux_err = (er[:, aperture_mask, 1] ** 2).sum(axis=1)[ast.mask] ** 0.5

            # Interpolate leading/lagging
            l1 = interp1d(
                ast.time[ast.mask] - ast.lag.value,
                (ar[:, aperture_mask, 0] - model[:, aperture_mask, 0]).sum(axis=1)[
                    ast.mask
                ],
                fill_value="extrapolate",
                bounds_error=False,
            )(ast.time[ast.mask])
            l2 = interp1d(
                ast.time[ast.mask] + ast.lag.value,
                (ar[:, aperture_mask, 2] - model[:, aperture_mask, 2]).sum(axis=1)[
                    ast.mask
                ],
                fill_value="extrapolate",
                bounds_error=False,
            )(ast.time[ast.mask])

            # Mask out bad cadences based on leading and lagging
            cadence_mask = np.ones(ast.mask.sum(), bool)
            k = np.isfinite(np.nansum(np.vstack([flux]), axis=0))

            for dat in [l1, l2, np.hypot(l1, l2), l1 / l2]:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=AstropyWarning)
                    m = sigma_clip(dat[k]).mask
                    m[~np.isfinite(dat[k])] = False
                    cadence_mask[k] &= ~m
                    m = sigma_clip(np.gradient(dat[k], ast.time[ast.mask][k])).mask
                    m[~np.isfinite(dat[k])] = False
                    cadence_mask[k] &= ~m

            # These might help users
            xcent = np.average(
                R[aperture_mask][None, :] * np.ones((ar.shape[0], 1)),
                weights=(ar[:, aperture_mask, 1] - model[:, aperture_mask, 1]),
                axis=1,
            )
            ycent = np.average(
                C[aperture_mask][None, :] * np.ones((ar.shape[0], 1)),
                weights=(ar[:, aperture_mask, 1] - model[:, aperture_mask, 1]),
                axis=1,
            )

            flux_corr = 10 ** (
                (ast.vmag[ast.mask] - np.median(ast.vmag[ast.mask])) * -0.4
            )

            # Package
            lc = lk.LightCurve(
                time=self.time[ast.mask][cadence_mask],
                flux=(flux / flux_corr)[cadence_mask],
                flux_err=flux_err[cadence_mask],
                targetid=ast.name,
                meta={
                    "LABEL": ast.name,
                    "MISSION": "TESS",
                    "TELESCOP": "TESS",
                    "SECTOR": ast.sector,
                    "TARGETID": ast.name,
                },
            )

            central_pixel = [aper // 2, aper // 2]
            lc["central_pixel"] = (
                ar[:, central_pixel[0], central_pixel[1], 1]
                - model[:, central_pixel[0], central_pixel[1], 1]
            )[ast.mask][cadence_mask]
            lc["xcentroid"] = xcent[ast.mask][cadence_mask]
            lc["ycentroid"] = ycent[ast.mask][cadence_mask]
            lc["ephem_row"] = ast.row[ast.mask][cadence_mask]
            lc["ephem_col"] = ast.col[ast.mask][cadence_mask]
            lc["vmag"] = ast.vmag[ast.mask][cadence_mask]
            lc["sun_distance"] = ast.sun_distance[ast.mask][cadence_mask]
            lc["obs_distance"] = ast.obs_distance[ast.mask][cadence_mask]
            lc["phase_angle"] = ast.phase_angle[ast.mask][cadence_mask]
            lc["flux_corr"] = flux_corr[cadence_mask]
            lc["camera"] = np.zeros(cadence_mask.sum(), dtype=int) + ast.camera
            lc["ccd"] = np.zeros(cadence_mask.sum(), dtype=int) + ast.ccd
            lc["l1"] = l1[cadence_mask]
            lc["l2"] = l2[cadence_mask]

            lcs.append(self._correct_lc(lc.remove_nans()))
        if len(lcs) == 0:
            return lk.LightCurve(time=[], flux=[])
        lc, thumb = (
            lk.LightCurveCollection(lcs).stitch(lambda x: x),
            (np.nanmedian(ar[:, :, :, 1] - model[:, :, :, 1], axis=0)),
        )
        if plot:
            ax = _plot_asteroid(lc, thumb, aperture_mask)
            return lc, ax
        # return (lc, thumb, aperture_mask, collection, model)
        return lc

    def _correct_lc(self, lc):

        # Remove outliers in the image centroids
        if len(lc.flux) > 10:
            r, c = lc.ephem_row.value % 1, lc.ephem_col.value % 1
            poly = np.vstack(
                [(lc.time.value - np.mean(lc.time.value)) ** idx for idx in range(4)]
            ).T
            A = np.hstack(
                [
                    poly,
                    r[:, None],
                    (r * c)[:, None],
                ]
            )
            xcent_corr = lc.xcentroid.value - A.dot(
                np.linalg.solve(A.T.dot(A), A.T.dot(lc.xcentroid.value))
            )
            A = np.hstack(
                [
                    poly,
                    c[:, None],
                    (r * c)[:, None],
                ]
            )
            ycent_corr = lc.ycentroid.value - A.dot(
                np.linalg.solve(A.T.dot(A), A.T.dot(lc.ycentroid.value))
            )
            cent_corr = np.hypot(
                xcent_corr - xcent_corr.min(), ycent_corr - ycent_corr.min()
            )
            nknots = int((lc.time.value[-1] - lc.time.value[0]) / 0.75)
            if nknots > 3:
                dm = lk.designmatrix.create_spline_matrix(
                    lc.time.value - np.mean(lc.time.value), n_knots=nknots
                )
            else:
                dm = lk.DesignMatrix(poly)
            r = lk.RegressionCorrector(
                lk.LightCurve(time=lc.time.value, flux=cent_corr, targetid="cent")
            )
            _ = r.correct(dm, sigma=3)
            outliers = r.outlier_mask
            outliers |= np.gradient(r.outlier_mask.astype(float)) != 0
            lc = lc[~outliers]
        return lc

    def _get_aperture_mask(self, ar, er, sigma=4):
        e = (np.nansum(er ** 2, axis=0) ** 0.5) / er.shape[0]
        thumb = np.nanmedian(ar, axis=0) / e
        aperture_mask = (
            thumb > np.hstack([thumb[thumb < 0], -thumb[thumb < 0]]).std() * sigma
        )
        if not aperture_mask[ar.shape[1] // 2, ar.shape[2] // 2]:
            raise ValueError("Can not find asteroid")

        # This is taken from lightkurve's create_threshold_mask
        labels = label(aperture_mask)[0]
        # For all pixels above threshold, compute distance to reference pixel:
        label_args = np.argwhere(labels > 0)
        distances = [
            np.hypot(crd[0], crd[1])
            for crd in label_args - np.array([ar.shape[1] // 2, ar.shape[2] // 2])
        ]
        # Which label corresponds to the closest pixel?
        closest_arg = label_args[np.argmin(distances)]
        closest_label = labels[closest_arg[0], closest_arg[1]]
        return labels == closest_label


def get_ffi_times():
    """Gets the times of all the FFI images from MAST by looking at all the file names."""
    from urllib.request import HTTPError

    """Get a dictionary of the times for each TESS FFI and save it as a pkl file"""
    time_dict = {}
    for sector in tqdm(np.arange(1, 300), total=300):
        try:
            df = pd.read_csv(
                f"https://archive.stsci.edu/missions/tess/download_scripts/sector/tesscurl_sector_{sector}_ffir.sh",
                skiprows=1,
                header=None,
            )
        except HTTPError:
            break
        df[["time", "camera", "ccd"]] = np.asarray(
            [
                (int(d[0][20:33]), int(d[0][40]), int(d[0][42]))
                for idx, d in df.iterrows()
            ]
        )
        time_dict[sector] = (
            Time.strptime(
                np.sort(df[(df.camera == 1) & (df.ccd == 1)].time).astype(str),
                "%Y%j%H%M%S",
            ).jd
            + 0.000809
            - 2457000
        )
    pickle.dump(time_dict, open(f"{PACKAGEDIR}/data/tess_sector_times.pkl", "wb"))


def _plot_asteroid(lc, thumbnail, aperture_mask):
    with plt.style.context("seaborn-white"):
        fig = plt.figure(figsize=(15, 3))
        ax = plt.subplot2grid((1, 4), (0, 0), colspan=3, fig=fig)
        lc.remove_outliers(10).errorbar(ax=ax, c="k", ls="-")
        ax.set(xlabel="Time [JD]", ylabel="Flux [counts]")
        ax = plt.subplot2grid((1, 4), (0, 3), fig=fig)
        ax.set(xticks=[], yticks=[], title=lc.label)
        std = np.hstack([thumbnail[thumbnail < 0], -thumbnail[thumbnail < 0]]).std()
        im = ax.imshow(thumbnail / std, vmin=0, vmax=10, cmap="viridis")
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Counts")
        # Overlay the aperture mask if given
        for i in range(thumbnail.shape[0]):
            for j in range(thumbnail.shape[1]):
                if aperture_mask[i, j]:
                    rect = patches.Rectangle(
                        xy=(j - 0.5, i - 0.5),
                        width=1,
                        height=1,
                        color="red",
                        fill=False,
                        hatch="/////",
                        alpha=0.3,
                    )
                    ax.add_patch(rect)
        return ax
