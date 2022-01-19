from unittest import TestCase
import numpy as np
from dkist_processing_pac.CUModel import CalibrationSequence
from dkist_processing_pac import Data

class TestInit(TestCase):

    def test_numsteps(self):

        psteps = rsteps = np.arange(4)
        pin = rin = din = np.array([1,1,0,0], dtype=np.bool)
        times = np.arange(4) * 1e4 + 1e4

        CS = CalibrationSequence(psteps, rsteps, pin, rin, din, times)
        self.assertEqual(CS.numsteps, 4)
        self.assertEqual(CS.sequence_nums, [4])

    def test_delta_t(self):

        psteps = rsteps = np.arange(4)
        pin = rin = din = np.array([1,1,0,0], dtype=np.bool)
        times = np.arange(4) * 1e3 + 4e4

        CS = CalibrationSequence(psteps, rsteps, pin, rin, din, times)
        np.testing.assert_array_equal(CS.delta_t, np.arange(4) * 1e3)

    def test_angle_conversion(self):

        psteps = rsteps = np.array([0, 60, 45, 90])
        pin = rin = din = np.array([1,1,0,0], dtype=np.bool)
        times = np.arange(4) * 1e3 + 4e4

        CS = CalibrationSequence(psteps, rsteps, pin, rin, din, times)
        np.testing.assert_array_equal(CS.theta_ret_steps, np.array([0, np.pi/3, np.pi/4, np.pi/2.]))
        np.testing.assert_array_equal(CS.theta_pol_steps, np.array([0, np.pi/3, np.pi/4, np.pi/2.]))

    def test_unequal_lengths(self):

        psteps = np.arange(4)
        rsteps = np.arange(5)
        pin = rin = din = np.array([1,1,1,0,0,0], dtype=np.bool)
        times = np.arange(4) * 1e3 + 1e4

        with self.assertRaises(ValueError):
            CS = CalibrationSequence(psteps, rsteps, pin, rin, din, times)

    def test_kwargs_conversion(self):

        psteps = rsteps = np.arange(4)
        pin = rin = din = np.array([1,1,0,0], dtype=np.bool)
        times = np.arange(4) * 1e4 + 1e4

        CS = CalibrationSequence(psteps, rsteps, pin, rin, din, times, ret_0_h=1, dret_h=3, ret_0_45=10., dret_45=30., ret_0_r=0.1, dret_r=0.3)
        np.testing.assert_array_equal(CS.ret_0_h, np.array([1.], dtype=np.float64))
        np.testing.assert_array_equal(CS.dret_h, np.array([3.], dtype=np.float64))
        np.testing.assert_array_equal(CS.ret_0_45, np.array([10.], dtype=np.float64))
        np.testing.assert_array_equal(CS.dret_45, np.array([30.], dtype=np.float64))
        np.testing.assert_array_equal(CS.ret_0_r, np.array([0.1], dtype=np.float64))
        np.testing.assert_array_equal(CS.dret_r, np.array([0.3], dtype=np.float64))

class TestAddition(TestCase):

    def test_concatenation(self):

        CS1 = CalibrationSequence(np.array([0,45]), np.array([90,0]), np.array([True, True]), np.array([False, True]),
                                  np.array([False, True]), np.array([50000, 60000]))
        CS2 = CalibrationSequence(np.array([90,180]), np.array([-90,180]), np.array([False, True]), np.array([True, True]),
                                  np.array([True, False]), np.array([55000, 65000]))
        CS = CS1 + CS2
        np.testing.assert_array_equal(CS.theta_pol_steps, np.array([0,45,90,180]) * np.pi / 180)
        np.testing.assert_array_equal(CS.theta_ret_steps, np.array([90,0,-90,180]) * np.pi / 180)
        np.testing.assert_array_equal(CS.pol_in, np.array([True, True, False, True]))
        np.testing.assert_array_equal(CS.ret_in, np.array([False, True, True, True]))
        np.testing.assert_array_equal(CS.delta_t, np.array([0, 10000, 0, 10000]))
        np.testing.assert_array_equal(CS.dark_in, np.array([False, True, True, False]))

    def test_kwargs(self):

        CS1 = CalibrationSequence(np.array([0,45]), np.array([90,0]), np.array([True, True]), np.array([False, True]),
                                  np.array([False, True]), np.array([50000, 60000]), ret_0_h=1, dret_h=10)
        CS2 = CalibrationSequence(np.array([90,180]), np.array([-90,180]), np.array([False, True]), np.array([True, True]),
                                  np.array([True, False]), np.array([55000, 65000]), ret_0_h=2, dret_h=11)
        CS = CS1 + CS2
        np.testing.assert_array_equal(CS.ret_0_h, np.array([1,2]))
        np.testing.assert_array_equal(CS.dret_h, np.array([10,11]))
        self.assertEqual(CS.sequence_nums, [2,2])

    def test_new_object(self):

        CS1 = CalibrationSequence(np.array([0,45]), np.array([90,0]), np.array([True, True]), np.array([False, True]),
                                  np.array([False, True]), np.array([50000, 60000]))
        CS2 = CalibrationSequence(np.array([90,180]), np.array([-90,180]), np.array([False, True]), np.array([True, True]),
                                  np.array([True, False]), np.array([55000, 65000]))
        CS = CS1 + CS2
        self.assertIsNot(CS, CS1)
        self.assertIsNot(CS, CS2)

class TestComponents(TestCase):

    def test_single_ret(self):

        psteps = rsteps = np.arange(5)
        pin = rin = din = np.array([1,1,0,0,1], dtype=np.bool)
        times = np.arange(5) * 1e3 + 4e4

        CS = CalibrationSequence(psteps, rsteps, pin, rin, din, times, ret_0_h=4, dret_h=1, ret_0_45=1, dret_45=2, ret_0_r=1, dret_r=-1)
        np.testing.assert_array_equal(CS.ret_h, np.arange(5) * 1e3 * 1 + 4)
        np.testing.assert_array_equal(CS.ret_45, np.arange(5) * 1e3 * 2 + 1)
        np.testing.assert_array_equal(CS.ret_r, np.arange(5) * 1e3 * -1 + 1)

    def test_multi_ret(self):

        CS1 = CalibrationSequence(np.array([0,45]), np.array([90,0]), np.array([True, True]), np.array([False, True]),
                                  np.array([False, True]), np.array([50000, 60000]), ret_0_h=1, dret_h=10, ret_0_45=10, dret_45=1, ret_0_r=1, dret_r=1)
        CS2 = CalibrationSequence(np.array([90,180]), np.array([-90,180]), np.array([False, True]), np.array([True, True]),
                                  np.array([True, False]), np.array([55000, 65000]), ret_0_h=2, dret_h=11, ret_0_45=20, dret_45=1, ret_0_r=2, dret_r=22)
        CS = CS1 + CS2
        np.testing.assert_array_equal(CS.ret_h, np.array([1, 100001, 2, 110002]))
        np.testing.assert_array_equal(CS.ret_45, np.array([10, 10010, 20, 10020]))
        np.testing.assert_array_equal(CS.ret_r, np.array([1, 10001, 2, 220002]))

    def test_pol_mat(self):

        CS = CalibrationSequence(np.array([0,45,90]), np.array([90,0,0]), np.array([True, False,True]),
                                 np.array([False, False, False]), np.array([False, False, False]),
                                 np.array([50000, 60000, 70000]))

        truth1 = Data.polarizer(1, 0)
        truth2 = np.diag(np.ones(4))
        truth3 = Data.rotation(-np.pi / 2) @ Data.polarizer(1, 0) @ Data.rotation(np.pi / 2)

        self.assertEqual(CS.pol_mat.shape, (3,4,4))
        np.testing.assert_array_equal(CS.pol_mat[0], truth1)
        np.testing.assert_array_equal(CS.pol_mat[1], truth2)
        np.testing.assert_array_equal(CS.pol_mat[2], truth3)

    def test_ret_mat(self):

        CS = CalibrationSequence(np.array([0,45,90]), np.array([90,0,45]), np.array([False, False, False]),
                                 np.array([False, True, True]), np.array([False, False, False]),
                                 np.array([1, 2, 3]), ret_0_h=0, dret_h=1, ret_0_45=1, dret_45=2, ret_0_r=1, dret_r=2)

        truth1 = np.diag(np.ones(4))
        truth2 = Data.elliptical_retarder(1, 1., 3., 3.)
        truth3 = Data.rotation(-np.pi/4) @ Data.elliptical_retarder(1, 2., 5., 5.) @ Data.rotation(np.pi / 4)

        self.assertEqual(CS.ret_mat.shape, (3,4,4))
        np.testing.assert_array_equal(CS.ret_mat[0], truth1)
        np.testing.assert_array_equal(CS.ret_mat[1], truth2)
        np.testing.assert_array_equal(CS.ret_mat[2], truth3)

    def test_CM(self):

        CS1 = CalibrationSequence(np.array([0, 45]), np.array([90, 45]),
                                  np.array([True, False]), np.array([True, False]), np.array([False, False]),
                                  np.array([1, 2]), ret_0_h=1, dret_h=1, ret_0_45=1, dret_45=2, ret_0_r=0, dret_r=1)

        CS2 = CalibrationSequence(np.array([0, 45]), np.array([90, 45]),
                                  np.array([True, True]), np.array([True, True]), np.array([False, False]),
                                  np.array([1, 2]), ret_0_h=1, dret_h=1, ret_0_45=1, dret_45=2, ret_0_r=0, dret_r=1)
        CS = CS1 + CS2

        truth1 = Data.rotation(-np.pi/2) @ Data.elliptical_retarder(1, 1, 1, 0) @ Data.rotation(np.pi / 2.) @ Data.polarizer(1, 0)
        truth2 = np.diag(np.ones(4))
        truth3 = Data.rotation(-np.pi/2) @ Data.elliptical_retarder(1, 1, 1, 0) @ Data.rotation(np.pi / 2.) @ Data.polarizer(1, 0)
        truth4 = Data.rotation(-np.pi/4) @ Data.elliptical_retarder(1, 2, 3, 1) @ Data.rotation(np.pi / 4.) @ Data.rotation(-np.pi / 4.) @ Data.polarizer(1, 0) @ Data.rotation(np.pi / 4)

        self.assertEqual(CS.CM.shape, (4,4,4))
        np.testing.assert_allclose(CS.CM[0], truth1)
        np.testing.assert_allclose(CS.CM[1], truth2)
        np.testing.assert_allclose(CS.CM[2], truth3)
        np.testing.assert_allclose(CS.CM[3], truth4)
