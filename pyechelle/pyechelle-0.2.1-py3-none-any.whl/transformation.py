import numpy as np
from numba import njit
from scipy.interpolate import CubicSpline


@njit(parallel=True, cache=True)
def calc_transformation(wl, lookup_wl, lookup_dwl, sx, sy, rot, shear, tx, ty):
    idx = np.floor((wl - lookup_wl[0]) // lookup_dwl).astype(np.int64)
    return sx[idx], sy[idx], rot[idx], shear[idx], tx[idx], ty[idx]


class AffineTransformation:
    def __init__(self, rot, sx, sy, shear, tx, ty, wl):
        """

        Args:
            rot:
            sx:
            sy:
            shear:
            tx:
            ty:
            wl:
        """
        self.sx = sx
        self.sy = sy
        self.rot = rot
        dif_rot = np.ediff1d(rot)
        # TODO: correct for jumps
        self.shear = shear
        self.tx = tx
        self.ty = ty
        self.wl = wl

        self.m0 = sx * np.cos(rot)
        self.m1 = -sy * np.sin(rot + shear)
        self.m2 = tx
        self.m3 = sx * np.sin(rot)
        self.m4 = sy * np.cos(rot + shear)
        self.m5 = ty

        self.lookup_table_m0 = self.m0
        self.lookup_table_m1 = self.m1
        self.lookup_table_m2 = self.m2
        self.lookup_table_m3 = self.m3
        self.lookup_table_m4 = self.m4
        self.lookup_table_m5 = self.m5

        self.spline_m0 = CubicSpline(self.wl, self.m0)
        self.spline_m1 = CubicSpline(self.wl, self.m1)
        self.spline_m2 = CubicSpline(self.wl, self.m2)
        self.spline_m3 = CubicSpline(self.wl, self.m3)
        self.spline_m4 = CubicSpline(self.wl, self.m4)
        self.spline_m5 = CubicSpline(self.wl, self.m5)

        self.lookup_table_sx = sx
        self.lookup_table_sy = sy
        self.lookup_table_rot = rot
        self.lookup_table_shear = shear
        self.lookup_table_tx = tx
        self.lookup_table_ty = ty
        self.lookup_table_wl = wl

        self.spline_sx = CubicSpline(self.wl, sx)
        self.spline_sy = CubicSpline(self.wl, sy)
        self.spline_rot = CubicSpline(self.wl, rot)
        self.spline_tx = CubicSpline(self.wl, tx)
        self.spline_ty = CubicSpline(self.wl, ty)
        self.spline_shear = CubicSpline(self.wl, shear)

        # length of lookup table. Will be overwritten when calling self.make_lookup_table
        self.lookup_table_n = len(sx)
        # wavelength step in the lookup table. will also be overwritten
        self.lookup_table_dwl = 1.
        # absolute wavelength in lookup table
        self.lookup_table_wl = wl

    def make_lookup_table(self, n=1000):
        self.lookup_table_n = n
        self.lookup_table_wl = np.linspace(np.min(self.wl), np.max(self.wl), n)
        self.lookup_table_dwl = (np.max(self.wl) - np.min(self.wl)) / n
        for f in ["sx", "sy", "rot", "shear", "tx", "ty"]:
            self.__setattr__(
                f"lookup_table_{f}", CubicSpline(self.wl, self.__getattribute__(f), )(self.lookup_table_wl)
            )
        for i in range(6):
            self.__setattr__(
                f"lookup_table_m{i}", CubicSpline(self.wl, self.__getattribute__(f'm{i}'), )(self.lookup_table_wl)
            )

    def get_matrices_lookup(self, wl):
        return calc_transformation(wl, self.lookup_table_wl, self.lookup_table_dwl, self.lookup_table_m0,
                                   self.lookup_table_m1, self.lookup_table_m2, self.lookup_table_m3,
                                   self.lookup_table_m4, self.lookup_table_m5)

    def get_transformations_lookup(self, wl):
        return calc_transformation(wl, self.lookup_table_wl, self.lookup_table_dwl, self.lookup_table_sx,
                                   self.lookup_table_sy, self.lookup_table_rot, self.lookup_table_shear,
                                   self.lookup_table_tx, self.lookup_table_ty)
        # idx = np.floor((wl - self.lookup_table_wl[0]) / self.lookup_table_dwl).astype(int)
        # return self.lookup_table_sx[idx], self.lookup_table_sy[idx], self.lookup_table_rot[idx], self.lookup_table_shear[idx], self.lookup_table_tx[idx], self.lookup_table_ty[idx]

    def get_transformations_spline(self, wl):
        return [self.__getattribute__(f'spline_{f}')(wl) for f in ["sx", "sy", "rot", "shear", "tx", "ty"]]

    def get_matrices_spline(self, wl):
        return [self.__getattribute__(f'spline_{f}')(wl) for f in ["m0", "m1", "m2", "m3", "m4", "m5"]]

    def min_wavelength(self):
        return self.wl[0]

    def max_wavelength(self):
        return self.wl[-1]
