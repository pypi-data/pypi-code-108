import numpy as np

import drama.constants as cnst
from drama.geo import geometry as sargeo


__author__ = "Paco Lopez Dekker"
__email__ = "F.LopezDekker@tudeft.nl"


class Baseline:
    """A class to convert between baselines

    Parameters
    ----------
    b :
        Baseline: if it is a two element list then first element is
        the horizontal baseline, and the second is the vertical
        (radial) one. Else, it is the perpendicular baseline, defaults
        to False
    theta_i :
        incident angle or array of incident angles, in degrees
    h_orb :
        height of sensor, in m.
    f0 :
        reasonant frequency, defaults to 5.4 GHz

    Returns
    -------

    """

    def __init__(self, b, theta_i, h_orb, bistatic=False, f0=5.4e9):
        """Initialise Baseline.
        """

        # Look angle
        self.sargeo = sargeo.QuickRadarGeometry(h_orb)
        self.theta_i = np.radians(theta_i)
        self.theta_l = self.sargeo.inc_to_look(self.theta_i)
        self.h_orb = h_orb
        self.f0 = f0
        if type(b) is tuple:
            self.b_h = b[0]
            self.b_r = b[1]
            self.b_p = self.b_h * np.cos(self.theta_l) + self.b_r * np.sin(
                self.b_r
            )
        else:
            self.b_p = b
            self.b_h = None
            self.b_r = None

        self.sr = self.sargeo.look_to_sr(self.theta_l)
        self.bistfact = 1 if bistatic else 2

    def kz(self, delta_grg=0):
        """

        Parameters
        ----------
        delta_grg :
            Shift of target in ground range, useful for ice (Default value = 0)

        Returns
        -------

        """
        # phase_int = phase_m - phase_s = -2 k0 (R_m - R_s) = 2 k0 (R_s-R_m)
        # positive phase means R_s > R_m -> lower height
        k0 = 2 * np.pi * self.f0 / cnst.c
        # Modify the effective baseline. Here we take a coordinate system with the vertical direction
        # perpendicular to the surface
        d_b_p = -delta_grg * np.cos(self.theta_i)
        b_p = self.b_p + d_b_p
        kz = -self.bistfact * k0 * b_p / self.sr / np.sin(self.theta_i)
        return kz

    def dkz(self, delta_grg=0):
        """

        Parameters
        ----------
        delta_grg :
            Shift of target in ground range, useful for ice (Default value = 0)

        Returns
        -------

        """
        # phase_int = phase_m - phase_s = -2 k0 (R_m - R_s) = 2 k0 (R_s-R_m)
        # positive phase means R_s > R_m -> lower height
        k0 = 2 * np.pi * self.f0 / cnst.c
        # Modify the effective baseline. Here we take a coordinate system with the vertical direction
        # perpendicular to the surface
        d_b_p = -delta_grg * np.cos(self.theta_i)
        dkz = -self.bistfact * k0 * d_b_p / self.sr / np.sin(self.theta_i)
        return dkz

    def set_kz(self, kz):
        """

        Parameters
        ----------
        kz :


        Returns
        -------

        """
        k0 = 2 * np.pi * self.f0 / cnst.c
        self.b_p = -kz * self.sr * np.sin(self.theta_i) / self.bistfact / k0
