import unittest
from datetime import datetime

import numpy as np
from numpy import deg2rad

import drama.orbits.two_body as d_two_body
from drama.constants import r_polar, r_equatorial, gm_earth


class TestKepler(unittest.TestCase):
    def setUp(self):
        self.r_eci_atol = 3e-2
        self.v_eci_atol = 5e-3

        self.semi_latus_vd = 11067.790e3
        self.e_vd = 0.83285
        self.a_vd = self.semi_latus_vd / (1 - self.e_vd ** 2)
        self.i_vd = deg2rad(87.87)
        self.raan_vd = deg2rad(227.89)
        self.arg_p_vd = deg2rad(53.38)
        self.true_anomaly_vd = deg2rad(92.335)

        self.h_curtis = 80000 * 1e6  # m^2/s
        self.e_curtis = 1.4
        self.semi_latus_curtis = self.h_curtis ** 2 / gm_earth
        self.a_curtis = self.semi_latus_curtis / (1 - self.e_curtis ** 2)
        self.i_curtis = deg2rad(30)
        self.raan_curtis = deg2rad(40)
        self.arg_p_curtis = deg2rad(60)
        self.true_anomaly_curtis = deg2rad(30)

        self.r_eci_expected_vd = np.array([6525.344, 6861.535, 6449.125])
        self.v_eci_expected_vd = np.array([4.902276, 5.533124, -1.975709])

        self.r_eci_expected_curtis = np.array([-4040, 4815, 3629])
        self.v_eci_expected_curtis = np.array([-10.39, -4.772, 1.744])

    def test_orbital_elements_to_rv(self):
        """Determine the position and velocity vectors from the classical orbital elements.

        The orbital elements are:
        p = 11,067.790 km, e = 0.832_85, i = 87.87°, Ω = 227.89°, ω = 53.38°, ν = 92.335°

        The position and velocity in cartesian coordinates (ECI):
        r = 6525.344     i + 6861.535     j + 6449.125     k km
        v =    4.902_276 i +    5.533_124 j –    1.975_709 k km/s

        Notes
        _____
        The values are taken from Example 2-6 - Finding Position and Velocity Vectors (COE2RV Test Case) of Vallado_[1]
        References
        ----------
        ..[1] Vallado, D. A.; McClain, W. D. Fundamentals of Astrodynamics and Applications, 4th ed.; Space Technology Library; Microcosm Press: Hawthorne, CA, 2013.
        """
        r_eci, v_eci = d_two_body.orbital_elements_to_rv(
            self.a_vd,
            self.e_vd,
            self.i_vd,
            self.raan_vd,
            self.arg_p_vd,
            self.true_anomaly_vd,
        )
        r_eci_expected = np.array([6525.344, 6861.535, 6449.125])
        np.testing.assert_allclose(r_eci / 1e3, r_eci_expected, atol=self.r_eci_atol)
        v_eci_expected = np.array([4.902276, 5.533124, -1.975709])
        np.testing.assert_allclose(v_eci / 1e3, v_eci_expected, atol=self.v_eci_atol)

    def test_orbital_elements_to_rv_curtis(self):
        """Determine the position and velocity vectors from the classical orbital elements.

        The orbital elements are:
        h = 80_000 km^2/s, e = 1.4, i = 30°, Ω = 40°, ω = 60°, ν = 30°

        The position and velocity in cartesian coordinates (ECI):
        r = -4040 i    + 4815     j + 3629     k km
        v = -  10.39 i -    4.772 j –    1.744 k km/s

        Notes
        _____
        The values are taken from Example 4.7 of Curtis_[2]

        References
        ----------
        ..[2] Curtis, H. D. (2013). Orbital mechanics for engineering students. Butterworth-Heinemann.
        """
        r_eci, v_eci = d_two_body.orbital_elements_to_rv(
            self.a_curtis,
            self.e_curtis,
            self.i_curtis,
            self.raan_curtis,
            self.arg_p_curtis,
            self.true_anomaly_curtis,
        )
        r_eci_expected = np.array([-4040, 4815, 3629])
        np.testing.assert_allclose(r_eci / 1e3, r_eci_expected, atol=1)
        v_eci_expected = np.array([-10.39, -4.772, 1.744])
        np.testing.assert_allclose(v_eci / 1e3, v_eci_expected, atol=self.v_eci_atol)

    def test_orbital_elements_to_rv_array(self):
        """Pass a numpy array instead of a scalar for each of the argument of orbital_elements_to_rv.

        The inputs are arrays holding the values of the previous two tests.
        """
        a = np.array([self.a_vd, self.a_curtis])
        e = np.array([self.e_vd, self.e_curtis])
        i = np.array([self.i_vd, self.i_curtis])
        raan = np.array([self.raan_vd, self.raan_curtis])
        arg_p = np.array([self.arg_p_vd, self.arg_p_curtis])
        true_anomaly = np.array([self.true_anomaly_vd, self.true_anomaly_curtis])
        r_eci, v_eci = d_two_body.orbital_elements_to_rv(
            a, e, i, raan, arg_p, true_anomaly
        )

        r_expected = np.array([self.r_eci_expected_vd, self.r_eci_expected_curtis])
        v_expected = np.array([self.v_eci_expected_vd, self.v_eci_expected_curtis])
        np.testing.assert_allclose(r_eci / 1e3, r_expected, atol=1)
        np.testing.assert_allclose(v_eci / 1e3, v_expected, atol=self.v_eci_atol)


class TestJ2_Kepler(unittest.TestCase):
    def setUp(self):
        self.r_eci_atol = 3e-2
        self.v_eci_atol = 5e-3

        self.a = 7073.8962e3
        self.e = 0.000136
        self.i = np.deg2rad(98.181)
        self.raan = np.deg2rad(45.8182)
        self.arg_p = np.deg2rad(83.1844)
        self.true_anomaly = np.deg2rad(276.9353)

        self.r_3h = np.array([1.503903, 2.855701, -6.295605]) * 1e3  # in km
        self.v_3h = np.array([5.028346, 4.523710, 3.253772])  # in km/s
        self.r_2h = np.array([1.7821499, 0.427812104, 6.83135273]) * 1e3  # in km
        self.v_2h = np.array([-4.93016221, -5.42345787, 1.62571156])  # in km/s

    def test_j2_kepler_3h(self):
        """Position and velocity using pertubations to the classical orbital elements up to the seond zonal term.

        The orbital elements are:
        a = 7073.8962 km, e = 0.000136, i = 98.181°, Ω = 45.8182°, ω = 83.1844°, ν = 276.9353°

        After Δt = 3 * 3600 s.
        The position and velocity in cartesian coordinates (ECI):
        r = 1.503903e6 i + 2.855701e6 j - 6.295605e6 k m
        v = 5.028346e3 i + 4.523710e3 j + 3.253772e3 k m/s

        Notes
        -----
        The values were obtained using a J2 propagator in SatelliteToolbox.jl_[1]

        References
        ----------
        ..[1] Chagas RA, de Sousa FL, Louro AC, dos Santos WG. Modeling and design of a multidisciplinary simulator of the concept of operations for space mission pre-phase A studies. Concurrent Engineering. 2019;27(1):28-39. doi:10.1177/1063293X18804006
        """
        delta_t = 3 * 3600  # 3 hours
        ((r_eci, v_eci), _) = d_two_body.j2_kepler(
            delta_t, self.a, self.e, self.i, self.raan, self.arg_p, self.true_anomaly
        )

        r_eci_expected = self.r_3h  # in km
        v_eci_expected = self.v_3h  # in km/s
        np.testing.assert_allclose(r_eci / 1e3, r_eci_expected, atol=self.r_eci_atol)
        np.testing.assert_allclose(v_eci / 1e3, v_eci_expected, atol=self.v_eci_atol)

    def test_j2_kepler_2h(self):
        """Position and velocity using pertubations to the classical orbital elements up to the seond zonal term.

        The orbital elements are:
        a = 7073.8962 km, e = 0.000136, i = 98.181°, Ω = 45.8182°, ω = 83.1844°, ν = 276.9353°

        After Δt = 2 * 3600 s.
        The position and velocity in cartesian coordinates (ECI):
        r = 1.503903e6 i + 2.855701e6 j - 6.295605e6 k m
        v = 5.028346e3 i + 4.523710e3 j + 3.253772e3 k m/s

        Notes
        -----
        The values were obtained using a J2 propagator in SatelliteToolbox.jl_[1]

        References
        ----------
        ..[1] Chagas RA, de Sousa FL, Louro AC, dos Santos WG. Modeling and design of a multidisciplinary simulator of the concept of operations for space mission pre-phase A studies. Concurrent Engineering. 2019;27(1):28-39. doi:10.1177/1063293X18804006
        """
        true_anomaly = np.deg2rad(276.9353)
        delta_t = 2 * 3600  # 4 hours
        ((r_eci, v_eci), _) = d_two_body.j2_kepler(
            delta_t, self.a, self.e, self.i, self.raan, self.arg_p, self.true_anomaly
        )

        r_eci_expected = self.r_2h  # in km
        v_eci_expected = self.v_2h  # in km/s
        np.testing.assert_allclose(r_eci / 1e3, r_eci_expected, atol=self.r_eci_atol)
        np.testing.assert_allclose(v_eci / 1e3, v_eci_expected, atol=self.v_eci_atol)

    def test_j2_kepler_array(self):
        """Pass a numpy array instead of a scalar for each of the argument of j2_kepler.

        The inputs of the orbital parameters are the same as the 2h and 3h test but an array with both 2h and 3h is passed as delta_t.
        """
        delta_t = np.array([2, 3]) * 3600
        ((r_eci, v_eci), _) = d_two_body.j2_kepler(
            delta_t, self.a, self.e, self.i, self.raan, self.arg_p, self.true_anomaly
        )

        r_eci_expected = np.array([self.r_2h, self.r_3h])
        np.testing.assert_allclose(r_eci / 1e3, r_eci_expected, atol=self.r_eci_atol)

    def test_OrbitalParameters_indexing(self):
        """Test the indexing of the OrbitalParameters instance returned by j2_keppler.
        """
        delta_t = np.array([2, 3]) * 3600
        _, orb_p = d_two_body.j2_kepler(
            delta_t, self.a, self.e, self.i, self.raan, self.arg_p, self.true_anomaly
        )
        _, orb_p_at_2h = d_two_body.j2_kepler(
            delta_t[0], self.a, self.e, self.i, self.raan, self.arg_p, self.true_anomaly
        )
        np.testing.assert_allclose(orb_p[0].arg_p, orb_p_at_2h.arg_p, atol=self.r_eci_atol)
