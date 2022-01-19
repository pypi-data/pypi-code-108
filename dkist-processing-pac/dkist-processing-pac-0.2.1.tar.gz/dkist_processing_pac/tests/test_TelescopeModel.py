import os
from unittest import TestCase
import numpy as np
from dkist_processing_pac.TelescopeModel import TelescopeModel
from dkist_processing_pac import Data

class TestInit(TestCase):

    def test_array_input(self):

        az = el = tab = np.arange(13.)
        TM = TelescopeModel(az, el, tab)
        self.assertTrue(type(TM.azimuth) is np.ndarray)
        self.assertTrue(type(TM.elevation) is np.ndarray)
        self.assertTrue(type(TM.table_angle) is np.ndarray)
        self.assertTrue(TM.azimuth.shape == (13,))
        self.assertTrue(TM.elevation.shape == (13,))
        self.assertTrue(TM.table_angle.shape == (13,))

    def test_single_input(self):

        TM = TelescopeModel(1.2, 3.4, 5.6)
        self.assertTrue(type(TM.azimuth) is np.ndarray)
        self.assertTrue(type(TM.elevation) is np.ndarray)
        self.assertTrue(type(TM.table_angle) is np.ndarray)
        self.assertTrue(TM.azimuth.shape == (1,))
        self.assertTrue(TM.elevation.shape == (1,))
        self.assertTrue(TM.table_angle.shape == (1,))

    def test_mirror_params(self):

        TM = TelescopeModel([90],[0],[45])
        TM.x34 = 1.
        TM.t34 = 2.
        TM.x56 = 3.
        TM.t56 = 4.
        TM.x12 = 5.
        TM.t12 = 6.
        self.assertEqual(TM.x34, 1)
        self.assertEqual(TM.t34, 2)
        self.assertEqual(TM.x56, 3)
        self.assertEqual(TM.t56, 4)
        self.assertEqual(TM.x12, 5)
        self.assertEqual(TM.t12, 6)

    def test_numsteps(self):

        size = np.random.randint(1, 1000)
        az = el = tab = np.arange(size)
        TM = TelescopeModel(az, el, tab)
        self.assertEqual(TM.numsteps, size)

    def test_unequal_lengths(self):

        az = np.arange(4)
        el = np.arange(5)
        tab = np.arange(6)
        with self.assertRaises(ValueError):
            TM = TelescopeModel(az, el, tab)

    def test_angle_conversion(self):

        TM = TelescopeModel(90, 60, 45)
        np.testing.assert_array_equal(TM.azimuth, np.array([np.pi/2.]))
        np.testing.assert_array_equal(TM.elevation, np.array([np.pi/3.]))
        np.testing.assert_array_equal(TM.table_angle, np.array([np.pi/4.]))

class TestAddition(TestCase):

    def test_concatenation(self):

        TM1 = TelescopeModel([1,2],[3,4],[5,6])
        TM2 = TelescopeModel([3,4],[5,6],[7,8])
        TM = TM1 + TM2
        np.testing.assert_array_equal(TM.azimuth, np.array([1,2,3,4]) * np.pi / 180)
        np.testing.assert_array_equal(TM.elevation, np.array([3,4,5,6]) * np.pi / 180)
        np.testing.assert_array_equal(TM.table_angle, np.array([5,6,7,8]) * np.pi / 180)

    def test_numsteps(self):

        TM1 = TelescopeModel([1,2],[3,4],[5,6])
        TM2 = TelescopeModel([3,4],[5,6],[7,8])
        TM = TM1 + TM2
        self.assertEqual(TM.numsteps, 4)

    def test_new_object(self):

        TM1 = TelescopeModel([1,2],[3,4],[5,6])
        TM2 = TelescopeModel([3,4],[5,6],[7,8])
        TM = TM1 + TM2
        self.assertIsNot(TM1, TM)
        self.assertIsNot(TM2, TM)

class TestComponents(TestCase):

    def setUp(self):

        self.TM = TelescopeModel([0,90.], [60, 75.], [90, 0.])
        self.TM.x12 = self.x12 = np.random.random() * (1.25 - 0.95) + 0.95
        self.TM.x34 = self.x34 = np.random.random() * (1.25 - 0.95) + 0.95
        self.TM.x56 = self.x56 = np.random.random() * (1.25 - 0.95) + 0.95
        self.TM.t12 = self.t12 = np.random.random() * (3.75 - 2.53) + 2.53
        self.TM.t34 = self.t34 = np.random.random() * (3.75 - 2.53) + 2.53
        self.TM.t56 = self.t56 = np.random.random() * (3.75 - 2.53) + 2.53

    def test_M12(self):
        np.testing.assert_array_equal(self.TM.M12, Data.mirror(self.x12, self.t12))
        self.assertEqual(self.TM.M12.shape, (4,4))

    def test_M34(self):
        np.testing.assert_array_equal(self.TM.M34, Data.mirror(self.x34, self.t34))
        self.assertEqual(self.TM.M34.shape, (4,4))

    def test_M56(self):
        np.testing.assert_array_equal(self.TM.M56, Data.mirror(self.x56, self.t56))
        self.assertEqual(self.TM.M56.shape, (4,4))

    def test_R23(self):
        np.testing.assert_array_equal(self.TM.R23, Data.rotation(-np.pi/2.))
        self.assertEqual(self.TM.R23.shape, (4,4))

    def test_R45(self):
        np.testing.assert_array_equal(self.TM.R45, np.transpose(np.dstack((Data.rotation(-np.pi/3.),
                                                                           Data.rotation(-75 * np.pi / 180))), (2,0,1)))
        self.assertEqual(self.TM.R45.shape, (2,4,4))

    def test_R67(self):
        np.testing.assert_array_equal(self.TM.R67, np.transpose(np.dstack((Data.rotation(0.),
                                                                           Data.rotation(np.pi))), (2,0,1)))
        self.assertEqual(self.TM.R67.shape, (2,4,4))

    def test_TM(self):
        np.testing.assert_array_equal(self.TM.TM, self.TM.R67 @ self.TM.M56 @ self.TM.R45 @ self.TM.M34 @ self.TM.R23)
        self.assertEqual(self.TM.TM.shape, (2,4,4))

class TestLoadDatabase(TestCase):

    def setUp(self):
        self.dbfile = 'tmpdb.txt'
        with open(self.dbfile, 'a') as f:
            f.write(str('{:15.6f}' + '{:8.2f}' + '{:7.3f}'*6 + '\n').format(55000,
                                                                            500,
                                                                            1, 10,
                                                                            3, 30,
                                                                            5, 50))
            f.write(str('{:15.6f}' + '{:8.2f}' + '{:7.3f}'*6 + '\n').format(56000,
                                                                            500,
                                                                            2, 20,
                                                                            4, 40,
                                                                            6, 60))
            f.write(str('{:15.6f}' + '{:8.2f}' + '{:7.3f}'*6 + '\n').format(55000,
                                                                            600,
                                                                            1.5, 15,
                                                                            3.5, 35,
                                                                            5.5, 55))
            f.write(str('{:15.6f}' + '{:8.2f}' + '{:7.3f}'*6 + '\n').format(56000,
                                                                            600,
                                                                            2.5, 25,
                                                                            4.5, 45,
                                                                            6.5, 65))

    def tearDown(self):
        os.remove(self.dbfile)

    def test_exact_match(self):

        TM = TelescopeModel(1,2,3)
        TM.load_from_database(self.dbfile, 55000, 500.)
        self.assertEqual(TM.x12, 1)
        self.assertEqual(TM.t12, 10)
        self.assertEqual(TM.x34, 3)
        self.assertEqual(TM.t34, 30)
        self.assertEqual(TM.x56, 5)
        self.assertEqual(TM.t56, 50)
        self.assertEqual(TM.wavelength, 500)
        self.assertEqual(TM.obstime, 55000)

    def test_wave_linear_interp(self):

        TM = TelescopeModel(1,2,3)
        TM.load_from_database(self.dbfile, 55000, 550, method='linear')
        self.assertEqual(TM.x12, 1.25)
        self.assertEqual(TM.t12, 12.5)
        self.assertEqual(TM.x34, 3.25)
        self.assertEqual(TM.t34, 32.5)
        self.assertEqual(TM.x56, 5.25)
        self.assertEqual(TM.t56, 52.5)
        self.assertEqual(TM.wavelength, 550)
        self.assertEqual(TM.obstime, 55000)

    def test_time_linear_interp(self):

        TM = TelescopeModel(1, 2, 3)
        TM.load_from_database(self.dbfile, 55500, 500, method='linear')
        self.assertEqual(TM.x12, 1.5)
        self.assertEqual(TM.t12, 15)
        self.assertEqual(TM.x34, 3.5)
        self.assertEqual(TM.t34, 35)
        self.assertEqual(TM.x56, 5.5)
        self.assertEqual(TM.t56, 55)
        self.assertEqual(TM.wavelength, 500)
        self.assertEqual(TM.obstime, 55500)

    def test_both_linear_interp(self):

        TM = TelescopeModel(1, 2, 3)
        TM.load_from_database(self.dbfile, 55500, 550, method='linear')
        self.assertEqual(TM.x12, 1.75)
        self.assertEqual(TM.t12, 17.5)
        self.assertEqual(TM.x34, 3.75)
        self.assertEqual(TM.t34, 37.5)
        self.assertEqual(TM.x56, 5.75)
        self.assertEqual(TM.t56, 57.5)
        self.assertEqual(TM.wavelength, 550)
        self.assertEqual(TM.obstime, 55500)

    def test_wave_nearest_interp(self):

        TM = TelescopeModel(1, 2, 3)
        TM.load_from_database(self.dbfile, 55000, 550, method='nearest')
        self.assertEqual(TM.x12, 1)
        self.assertEqual(TM.t12, 10)
        self.assertEqual(TM.x34, 3)
        self.assertEqual(TM.t34, 30)
        self.assertEqual(TM.x56, 5)
        self.assertEqual(TM.t56, 50)
        self.assertEqual(TM.wavelength, 550)
        self.assertEqual(TM.obstime, 55000)

    def test_time_nearest_interp(self):

        TM = TelescopeModel(1, 2, 3)
        TM.load_from_database(self.dbfile, 55501, 500, method='nearest')
        self.assertEqual(TM.x12, 2)
        self.assertEqual(TM.t12, 20)
        self.assertEqual(TM.x34, 4)
        self.assertEqual(TM.t34, 40)
        self.assertEqual(TM.x56, 6)
        self.assertEqual(TM.t56, 60)
        self.assertEqual(TM.wavelength, 500)
        self.assertEqual(TM.obstime, 55501)

    def test_both_nearest_interp(self):

        TM = TelescopeModel(1, 2, 3)
        TM.load_from_database(self.dbfile, 55500, 551, method='nearest')
        self.assertEqual(TM.x12, 1.5)
        self.assertEqual(TM.t12, 15)
        self.assertEqual(TM.x34, 3.5)
        self.assertEqual(TM.t34, 35)
        self.assertEqual(TM.x56, 5.5)
        self.assertEqual(TM.t56, 55)
        self.assertEqual(TM.wavelength, 551)
        self.assertEqual(TM.obstime, 55500)

    def test_wave_out_of_bounds_linear(self):
        TM = TelescopeModel(1, 2, 3)
        TM.load_from_database(self.dbfile, 55000, 700, method='linear')
        self.assertEqual(TM.x12, 1.5)
        self.assertEqual(TM.t12, 15)
        self.assertEqual(TM.x34, 3.5)
        self.assertEqual(TM.t34, 35)
        self.assertEqual(TM.x56, 5.5)
        self.assertEqual(TM.t56, 55)
        self.assertEqual(TM.wavelength, 700)
        self.assertEqual(TM.obstime, 55000)

    def test_time_out_of_bounds_linear(self):
        TM = TelescopeModel(1, 2, 3)
        TM.load_from_database(self.dbfile, 4, 500, method='linear')
        self.assertEqual(TM.x12, 1)
        self.assertEqual(TM.t12, 10)
        self.assertEqual(TM.x34, 3)
        self.assertEqual(TM.t34, 30)
        self.assertEqual(TM.x56, 5)
        self.assertEqual(TM.t56, 50)
        self.assertEqual(TM.wavelength, 500)
        self.assertEqual(TM.obstime, 4)

    def test_both_out_of_bounds_linear(self):
        TM = TelescopeModel(1, 2, 3)
        TM.load_from_database(self.dbfile, 1e7, 2, method='linear')
        self.assertEqual(TM.x12, 2)
        self.assertEqual(TM.t12, 20)
        self.assertEqual(TM.x34, 4)
        self.assertEqual(TM.t34, 40)
        self.assertEqual(TM.x56, 6)
        self.assertEqual(TM.t56, 60)
        self.assertEqual(TM.wavelength, 2)
        self.assertEqual(TM.obstime, 1e7)

    def test_wave_out_of_bounds_nearest(self):
        TM = TelescopeModel(1, 2, 3)
        TM.load_from_database(self.dbfile, 55000, 700, method='nearest')
        self.assertEqual(TM.x12, 1.5)
        self.assertEqual(TM.t12, 15)
        self.assertEqual(TM.x34, 3.5)
        self.assertEqual(TM.t34, 35)
        self.assertEqual(TM.x56, 5.5)
        self.assertEqual(TM.t56, 55)
        self.assertEqual(TM.wavelength, 700)
        self.assertEqual(TM.obstime, 55000)

    def test_time_out_of_bounds_nearest(self):
        TM = TelescopeModel(1, 2, 3)
        TM.load_from_database(self.dbfile, 4, 500, method='nearest')
        self.assertEqual(TM.x12, 1)
        self.assertEqual(TM.t12, 10)
        self.assertEqual(TM.x34, 3)
        self.assertEqual(TM.t34, 30)
        self.assertEqual(TM.x56, 5)
        self.assertEqual(TM.t56, 50)
        self.assertEqual(TM.wavelength, 500)
        self.assertEqual(TM.obstime, 4)

    def test_both_out_of_bounds_nearest(self):
        TM = TelescopeModel(1, 2, 3)
        TM.load_from_database(self.dbfile, 1e7, 2, method='nearest')
        self.assertEqual(TM.x12, 2)
        self.assertEqual(TM.t12, 20)
        self.assertEqual(TM.x34, 4)
        self.assertEqual(TM.t34, 40)
        self.assertEqual(TM.x56, 6)
        self.assertEqual(TM.t56, 60)
        self.assertEqual(TM.wavelength, 2)
        self.assertEqual(TM.obstime, 1e7)

    def test_wave_out_of_bounds_cubic(self):
        TM = TelescopeModel(1, 2, 3)
        TM.load_from_database(self.dbfile, 55000, 700, method='cubic')
        self.assertEqual(TM.x12, 1.5)
        self.assertEqual(TM.t12, 15)
        self.assertEqual(TM.x34, 3.5)
        self.assertEqual(TM.t34, 35)
        self.assertEqual(TM.x56, 5.5)
        self.assertEqual(TM.t56, 55)
        self.assertEqual(TM.wavelength, 700)
        self.assertEqual(TM.obstime, 55000)

    def test_time_out_of_bounds_cubic(self):
        TM = TelescopeModel(1, 2, 3)
        TM.load_from_database(self.dbfile, 4, 500, method='cubic')
        self.assertEqual(TM.x12, 1)
        self.assertEqual(TM.t12, 10)
        self.assertEqual(TM.x34, 3)
        self.assertEqual(TM.t34, 30)
        self.assertEqual(TM.x56, 5)
        self.assertEqual(TM.t56, 50)
        self.assertEqual(TM.wavelength, 500)
        self.assertEqual(TM.obstime, 4)

    def test_both_out_of_bounds_cubic(self):
        TM = TelescopeModel(1, 2, 3)
        TM.load_from_database(self.dbfile, 1e7, 2, method='cubic')
        self.assertEqual(TM.x12, 2)
        self.assertEqual(TM.t12, 20)
        self.assertEqual(TM.x34, 4)
        self.assertEqual(TM.t34, 40)
        self.assertEqual(TM.x56, 6)
        self.assertEqual(TM.t56, 60)
        self.assertEqual(TM.wavelength, 2)
        self.assertEqual(TM.obstime, 1e7)

class TestSaveDatabase(TestCase):

    def setUp(self):
        self.dbfile = 'tmpdb.txt'
        self.x12 = 1.2
        self.t12 = 12.3
        self.x34 = 3.4
        self.t34 = 34.5
        self.x56 = 5.6
        self.t56 = 56.7
        self.TM = TelescopeModel(1,2,3)
        self.TM.x12 = self.x12
        self.TM.t12 = self.t12
        self.TM.x34 = self.x34
        self.TM.t34 = self.t34
        self.TM.x56 = self.x56
        self.TM.t56 = self.t56
        with open(self.dbfile, 'a') as f:
            f.write(str('{:15.6f}' + '{:8.2f}' + '{:7.3f}'*6 + '\n').format(55000,
                                                                            500,
                                                                            1, 10,
                                                                            3, 30,
                                                                            5, 50))

    def tearDown(self):
        os.remove(self.dbfile)

    def test_save(self):

        truth = str('{:15.6f}' + '{:8.2f}' + '{:7.3f}'*6 + '\n').format(100,
                                                                        200,
                                                                        self.x12, self.t12,
                                                                        self.x34, self.t34,
                                                                        self.x56, self.t56)
        self.TM.save_to_database(self.dbfile, 100, 200)
        with open(self.dbfile, 'r') as f:
            lines = f.readlines()
        self.assertEqual(lines[-1], truth)

    def test_save_class_wave(self):

        truth = str('{:15.6f}' + '{:8.2f}' + '{:7.3f}'*6 + '\n').format(100,
                                                                        222,
                                                                        self.x12, self.t12,
                                                                        self.x34, self.t34,
                                                                        self.x56, self.t56)
        self.TM.wavelength = 222.
        self.TM.save_to_database(self.dbfile, obstime=100)
        with open(self.dbfile, 'r') as f:
            lines = f.readlines()
        self.assertEqual(lines[-1], truth)

    def test_save_class_time(self):

        truth = str('{:15.6f}' + '{:8.2f}' + '{:7.3f}'*6 + '\n').format(111,
                                                                        200,
                                                                        self.x12, self.t12,
                                                                        self.x34, self.t34,
                                                                        self.x56, self.t56)
        self.TM.obstime = 111
        self.TM.save_to_database(self.dbfile, obswave=200)
        with open(self.dbfile, 'r') as f:
            lines = f.readlines()
        self.assertEqual(lines[-1], truth)

    def test_save_class_both(self):

        truth = str('{:15.6f}' + '{:8.2f}' + '{:7.3f}'*6 + '\n').format(111,
                                                                        222,
                                                                        self.x12, self.t12,
                                                                        self.x34, self.t34,
                                                                        self.x56, self.t56)
        self.TM.obstime = 111
        self.TM.wavelength = 222
        self.TM.save_to_database(self.dbfile)
        with open(self.dbfile, 'r') as f:
            lines = f.readlines()
        self.assertEqual(lines[-1], truth)

    def test_save_no_wave(self):

        self.TM.obstime = 111
        with self.assertRaises(ValueError):
            self.TM.save_to_database(self.dbfile)

    def test_save_no_time(self):

        with self.assertRaises(ValueError):
            self.TM.save_to_database(self.dbfile, obswave=200)

