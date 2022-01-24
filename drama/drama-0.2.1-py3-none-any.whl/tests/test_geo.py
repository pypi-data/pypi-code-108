import unittest
from datetime import datetime

import numpy as np
from astropy.time import Time

import drama.geo.geometry as d_geo
from drama.constants import r_polar, r_equatorial


class TestECI(unittest.TestCase):
    def test_eci_to_ecef(self):
        # Test values from Matlab documentation on eci2ecef
        t0_utc = datetime(2019, 1, 4, 12)
        # t0_utc = Time(t0_utc, format="datetime", scale="utc")
        # epoch = t0_utc.jd
        eci = [-2981784, 5207055, 3161595]
        ecef = d_geo.eci_to_ecef(eci, t0_utc)
        np.testing.assert_allclose(ecef, [-5.7627e6, -1.6827e6, 3.1560e6], rtol=0.02)

    def test_eci_to_ecef2(self):
        """
        Notes
        -----
        Test scenario taken from Vallado_[1] Example 3-15: Performing IAU-76/FK5 reduction.
        The example shows that for
        UTC epoch = April 6, 2004, 07:51:28.386009

        References
        ----------
        ..[1] Vallado, D. A.; McClain, W. D. Fundamentals of Astrodynamics and Applications, 4th ed.; Space Technology Library; Microcosm Press: Hawthorne, CA, 2013.
        """
        t0_utc = datetime(2004, 4, 6, 7, 51, 28)
        eci = [5102.50895790e3, 6123.01140070e3, 6378.13692820e3]
        ecef = d_geo.eci_to_ecef(eci, t0_utc)
        np.testing.assert_allclose(
            ecef, [-1033.4793830e3, 7901.2952754e3, 6380.3565958e3], rtol=0.02
        )

    def test_eci_to_ecef_array(self):
        to_utc = np.array((datetime(2019, 1, 4, 12), datetime(2004, 4, 6, 7, 51, 28)))
        eci = np.array(
            [
                (-2981784, 5207055, 3161595),
                (5102.50895790e3, 6123.01140070e3, 6378.13692820e3),
            ]
        )
        expected = np.array(
            [
                (-5.7627e6, -1.6827e6, 3.1560e6),
                (-1033.4793830e3, 7901.2952754e3, 6380.3565958e3),
            ]
        )
        ecef = d_geo.eci_to_ecef(eci, to_utc)
        np.testing.assert_allclose(ecef, expected, rtol=0.02)


class TestECEF(unittest.TestCase):
    def test_ecef_to_geodetic(self):
        ecef = np.array([4201, 172.46, 4780.1]) * 1e3
        expected_llh = np.array([48.8562, 2.3508, 0.0674e3])
        llh = d_geo.ecef_to_geodetic(ecef)
        np.testing.assert_allclose(llh, expected_llh, rtol=1e3)

    def test_ecef_to_geodetic2(self):
        ecef = np.array([6524.834, 6862.875, 6448.296]) * 1e3
        expected_llh = np.array([34.352496, 46.4464, 5085.22e3])
        llh = d_geo.ecef_to_geodetic(ecef)
        np.testing.assert_allclose(llh, expected_llh, rtol=1e3)

    def test_ecef_to_geodetic_array(self):
        ecef_1 = np.array([4201, 172.46, 4780.1]) * 1e3
        ecef_2 = np.array([6524.834, 6862.875, 6448.296]) * 1e3
        ecef = np.array([ecef_1, ecef_2])
        llh_1 = np.array([48.8562, 2.3508, 0.0674e3])
        llh_2 = np.array([34.352496, 46.4464, 5085.22e3])
        expected_llh = np.array([llh_1, llh_2])
        llh = d_geo.ecef_to_geodetic(ecef)
        np.testing.assert_allclose(llh, expected_llh, rtol=1e3)

    def test_ecef_to_geodetic_north_pole(self):
        r0 = r_equatorial["wgs84"]
        z = r0 + 10
        llh = d_geo.ecef_to_geodetic(np.array([0, 0, z]))
        expected_llh = np.array([90, 0, z - r_polar["wgs84"]])
        np.testing.assert_allclose(llh, expected_llh, rtol=1e-5)

    def test_ecef_to_geodetic_south_pole(self):
        r0 = r_equatorial["wgs84"]
        z = -r0 + 10
        llh = d_geo.ecef_to_geodetic(np.array([0, 0, z]))
        expected_llh = np.array([-90, 0, -z - r_polar["wgs84"]])
        np.testing.assert_allclose(llh, expected_llh, rtol=1e-5)


if __name__ == "__main__":
    unittest.main()
