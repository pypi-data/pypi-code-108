import shutil
import tempfile
from unittest import TestCase
import numpy as np
from types import SimpleNamespace

import pytest
from astropy.io import fits as pyfits

from dkist_processing_pac import CUModel, TelescopeModel, FittingFramework, generic
from dkist_processing_pac.utils import gen_fake_data

RTOL=1e-6
ATOL=1e-6

class TestGenerateParameters(TestCase):

    def setUp(self):
        self.mode_opts = generic.init_fit_mode('baseline', 666, False)
        self.nummod = 10

    def get_number_in_parameter_range(self, parameter):

        num = (self.mode_opts[parameter]['max'] - self.mode_opts[parameter]['min']) * \
               np.random.random() + self.mode_opts[parameter]['min']

        if np.isnan(num):
            num = np.random.random()

        return num

    def test_correct(self):

        TM = TelescopeModel.TelescopeModel([90],[0],[45])
        TM.x34 = self.get_number_in_parameter_range('x34')
        TM.t34 = self.get_number_in_parameter_range('t34')
        TM.x56 = self.get_number_in_parameter_range('x56')
        TM.t56 = self.get_number_in_parameter_range('t56')
        CS = CUModel.CalibrationSequence(np.array([0]), np.array([0]), np.array([True]), np.array([True]),
                                         np.array([False]),  np.array([57530]))

        params = FittingFramework.generate_parameters([100], TM, CS, self.mode_opts, self.nummod, fit_TM=False)
        d = params.valuesdict()
        self.assertTrue('x34' in d.keys())
        self.assertTrue('t34' in d.keys())
        self.assertTrue('x56' in d.keys())
        self.assertTrue('t56' in d.keys())
        self.assertTrue('ret0h_CS00' in d.keys())
        self.assertTrue('dreth_CS00' in d.keys())
        self.assertTrue('ret045_CS00' in d.keys())
        self.assertTrue('dret45_CS00' in d.keys())
        self.assertTrue('ret0r_CS00' in d.keys())
        self.assertTrue('dretr_CS00' in d.keys())
        self.assertTrue('t_pol_CS00' in d.keys())
        self.assertTrue('t_ret_CS00' in d.keys())
        self.assertTrue('I_sys_CS00' in d.keys())
        self.assertTrue('Q_in' in d.keys())
        self.assertTrue('U_in' in d.keys())
        self.assertTrue('V_in' in d.keys())
        self.assertEqual(d['x34'], TM.x34, msg='x34')
        self.assertEqual(d['t34'], TM.t34, msg='t34')
        self.assertEqual(d['x56'], TM.x56, msg='x56')
        self.assertEqual(d['t56'], TM.t56, msg='t56')
        self.assertEqual(d['ret0h_CS00'], self.mode_opts['ret0h']['value'])
        self.assertEqual(d['dreth_CS00'], self.mode_opts['dreth']['value'])
        self.assertEqual(d['ret045_CS00'], self.mode_opts['ret045']['value'])
        self.assertEqual(d['dret45_CS00'], self.mode_opts['dret45']['value'])
        self.assertEqual(d['ret0r_CS00'], self.mode_opts['ret0r']['value'])
        self.assertEqual(d['dretr_CS00'], self.mode_opts['dretr']['value'])
        self.assertEqual(d['t_pol_CS00'], self.mode_opts['t_pol']['value'])
        self.assertEqual(d['t_ret_CS00'], self.mode_opts['t_ret']['value'])
        self.assertEqual(d['I_sys_CS00'], 100)
        self.assertEqual(d['Q_in'], self.mode_opts['Q_in']['value'])
        self.assertEqual(d['U_in'], self.mode_opts['U_in']['value'])
        self.assertEqual(d['V_in'], self.mode_opts['V_in']['value'])

    def test_TM_true(self):

        TM = TelescopeModel.TelescopeModel([90],[0],[45])
        CS = CUModel.CalibrationSequence(np.array([0]), np.array([0]), np.array([True]), np.array([True]),
                                         np.array([False]), np.array([57530]))

        params = FittingFramework.generate_parameters([100], TM, CS, self.mode_opts, self.nummod, fit_TM=True)
        self.assertTrue(params['x34'].vary)
        self.assertTrue(params['t34'].vary)
        self.assertTrue(params['x56'].vary)
        self.assertTrue(params['t56'].vary)

    def test_TM_false(self):

        TM = TelescopeModel.TelescopeModel([90],[0],[45])
        CS = CUModel.CalibrationSequence(np.array([0]), np.array([0]), np.array([True]), np.array([True]),
                                         np.array([False]), np.array([57530]))

        params = FittingFramework.generate_parameters([100], TM, CS, self.mode_opts, self.nummod, fit_TM=False)
        self.assertFalse(params['x34'].vary)
        self.assertFalse(params['t34'].vary)
        self.assertFalse(params['x56'].vary)
        self.assertFalse(params['t56'].vary)

    def test_out_of_range_TM_pars(self):
        """We only need to test TM pars because the CM pars are set directly from the fit recipe"""

        TM = TelescopeModel.TelescopeModel([90],[0],[45])
        TM.x34 = self.mode_opts['x34']['max'] + 1
        TM.t34 = self.mode_opts['t34']['min'] - 1
        TM.x56 = self.mode_opts['x56']['min'] - 1
        TM.t56 = self.mode_opts['t56']['max'] + 1
        CS = CUModel.CalibrationSequence(np.array([0]), np.array([0]), np.array([True]), np.array([True]),
                                         np.array([False]), np.array([57530]))

        params = FittingFramework.generate_parameters([100], TM, CS, self.mode_opts, self.nummod, fit_TM=False)
        d = params.valuesdict()
        self.assertEqual(d['x34'], self.mode_opts['x34']['max'])
        self.assertEqual(d['t34'], self.mode_opts['t34']['min'])
        self.assertEqual(d['x56'], self.mode_opts['x56']['min'])
        self.assertEqual(d['t56'], self.mode_opts['t34']['max'])

    def test_multi_CS(self):

        TM = TelescopeModel.TelescopeModel([90],[0],[45])
        CS1 = CUModel.CalibrationSequence(np.array([0]), np.array([0]), np.array([True]), np.array([True]),
                                          np.array([False]), np.array([57530]), ret_0_r=0.98, dret_r=0.75)
        CS2 = CUModel.CalibrationSequence(np.array([0]), np.array([0]), np.array([True]), np.array([True]),
                                          np.array([False]), np.array([57560]), ret_0_h=1., dret_h=0.8)
        CS3 = CUModel.CalibrationSequence(np.array([0]), np.array([0]), np.array([True]), np.array([True]),
                                          np.array([False]), np.array([57590]), ret_0_h=2., dret_h=0.9)
        CS = CS1 + CS2 + CS3

        params = FittingFramework.generate_parameters([100, 200, 300], TM, CS, self.mode_opts, self.nummod)
        d = params.valuesdict()
        self.assertTrue('ret0h_CS00' in d.keys())
        self.assertTrue('dreth_CS00' in d.keys())
        self.assertTrue('ret045_CS00' in d.keys())
        self.assertTrue('dret45_CS00' in d.keys())
        self.assertTrue('ret0r_CS00' in d.keys())
        self.assertTrue('dretr_CS00' in d.keys())
        self.assertTrue('ret0h_CS01' in d.keys())
        self.assertTrue('dreth_CS01' in d.keys())
        self.assertTrue('ret045_CS01' in d.keys())
        self.assertTrue('dret45_CS01' in d.keys())
        self.assertTrue('ret0r_CS01' in d.keys())
        self.assertTrue('dretr_CS01' in d.keys())
        self.assertTrue('ret0h_CS02' in d.keys())
        self.assertTrue('dreth_CS02' in d.keys())
        self.assertTrue('ret045_CS02' in d.keys())
        self.assertTrue('dret45_CS02' in d.keys())
        self.assertTrue('ret0r_CS02' in d.keys())
        self.assertTrue('dretr_CS02' in d.keys())

    def test_relative_I(self):

        TM = TelescopeModel.TelescopeModel([90],[0],[45])
        TM.x34 = self.get_number_in_parameter_range('x34')
        TM.t34 = self.get_number_in_parameter_range('t34')
        TM.x56 = self.get_number_in_parameter_range('x56')
        TM.t56 = self.get_number_in_parameter_range('t56')
        CS = CUModel.CalibrationSequence(np.array([0]), np.array([0]), np.array([True]), np.array([True]),
                                         np.array([False]),  np.array([57530]))

        params = FittingFramework.generate_parameters([100], TM, CS, self.mode_opts, self.nummod)
        self.assertEqual(params['I_sys_CS00'].min, 100 * self.mode_opts['I_sys']['min'])
        self.assertEqual(params['I_sys_CS00'].max, 100 * self.mode_opts['I_sys']['max'])

    def test_modmat_correct_num(self):

        TM = TelescopeModel.TelescopeModel([90],[0],[45])
        TM.x34 = self.get_number_in_parameter_range('x34')
        TM.t34 = self.get_number_in_parameter_range('t34')
        TM.x56 = self.get_number_in_parameter_range('x56')
        TM.t56 = self.get_number_in_parameter_range('t56')
        CS = CUModel.CalibrationSequence(np.array([0]), np.array([0]), np.array([True]), np.array([True]),
                                        np.array([False]),  np.array([57530]))

        params = FittingFramework.generate_parameters([100], TM, CS, self.mode_opts, self.nummod)
        d = params.valuesdict()

        for s in ['I', 'Q', 'U', 'V']:
            for i in range(self.nummod):
                with self.subTest(stokes=s, m=i):
                    self.assertTrue('modmat_{}{}'.format(i,s) in d.keys())

    def test_modmat_norange(self):

        TM = TelescopeModel.TelescopeModel([90],[0],[45])
        TM.x34 = self.get_number_in_parameter_range('x34')
        TM.t34 = self.get_number_in_parameter_range('t34')
        TM.x56 = self.get_number_in_parameter_range('x56')
        TM.t56 = self.get_number_in_parameter_range('t56')
        CS = CUModel.CalibrationSequence(np.array([0]), np.array([0]), np.array([True]), np.array([True]),
                                        np.array([False]),  np.array([57530]))

        params = FittingFramework.generate_parameters([100], TM, CS, self.mode_opts, self.nummod)

        for s in ['I', 'Q', 'U', 'V']:
            for i in range(self.nummod):
                with self.subTest(stokes=s, m=i):
                    self.assertEqual(params['modmat_{}{}'.format(i,s)].min, -np.inf)
                    self.assertEqual(params['modmat_{}{}'.format(i,s)].max, np.inf)

    def test_modmat_yesrange(self):

        TM = TelescopeModel.TelescopeModel([90],[0],[45])
        TM.x34 = self.get_number_in_parameter_range('x34')
        TM.t34 = self.get_number_in_parameter_range('t34')
        TM.x56 = self.get_number_in_parameter_range('x56')
        TM.t56 = self.get_number_in_parameter_range('t56')
        CS = CUModel.CalibrationSequence(np.array([0]), np.array([0]), np.array([True]), np.array([True]),
                                        np.array([False]),  np.array([57530]))

        self.mode_opts['switches']['fit_bounds'] = True

        params = FittingFramework.generate_parameters([100], TM, CS, self.mode_opts, self.nummod)

        for s in ['Q', 'U', 'V']:
            for i in range(self.nummod):
                with self.subTest(stokes=s, m=i):
                    self.assertEqual(params['modmat_{}{}'.format(i,s)].min, -1.5)
                    self.assertEqual(params['modmat_{}{}'.format(i,s)].max, 1.5)

        for i in range(self.nummod):
            with self.subTest(m=i):
                self.assertEqual(params['modmat_{}I'.format(i)].min, 0.5)
                self.assertEqual(params['modmat_{}I'.format(i)].max, 1.5)

class TestFitModulationMatrix(TestCase):

    def test_by_hand(self):
        TM = SimpleNamespace(M12=np.diag(np.ones(4)))
        TM.TM = np.dstack((np.diag(np.ones(4)) * 2, np.diag(np.ones(4)))).T
        CS = SimpleNamespace(s_in=np.array([1,0,0,0.]))
        CS.CM = np.dstack((np.ones((4,4)), np.diag(np.ones(4)) * 3)).T
        truth = np.array([[8, 0, 0, 0.],
                          [2, 2, 2, 2,],
                          [3, 0, 0, 0]])
        truth /= truth[0,0]
        I_cal = truth @ (TM.TM @ CS.CM @ TM.M12 @ CS.s_in).T
        S = (TM.TM @ CS.CM @ TM.M12 @ CS.s_in).T

        O = FittingFramework.fit_modulation_matrix(I_cal, S)
        np.testing.assert_allclose(truth, O, rtol=RTOL, atol=ATOL)

    def test_random(self):
        TM = SimpleNamespace(M12=np.diag(np.ones(4)), TM=np.random.random((45,4,4)))
        CS = SimpleNamespace(s_in=np.array([1,0,0,0.]), CM=np.random.random((45,4,4)))
        truth = np.random.random((10,4))
        truth /= truth[0,0]
        I_cal = truth @ (TM.TM @ CS.CM @ TM.M12 @ CS.s_in).T
        S = (TM.TM @ CS.CM @ TM.M12 @ CS.s_in).T

        O = FittingFramework.fit_modulation_matrix(I_cal, S)
        np.testing.assert_allclose(truth, O, rtol=RTOL, atol=ATOL)

class TestGenerateModelI(TestCase):

    def test_by_hand(self):
        TM = SimpleNamespace(M12=np.diag(np.ones(4)))
        TM.TM = np.dstack((np.diag(np.ones(4)) * 2, np.diag(np.ones(4)))).T
        CS = SimpleNamespace(s_in=np.array([1,0,0,0.]))
        CS.CM = np.dstack((np.ones((4,4)), np.diag(np.ones(4)) * 3)).T
        O = np.array([[1, 0, 0, 0.],
                      [2, 2, 2, 2,],
                      [3, 0, 0, 0]])
        truth = np.array([[2, 3],
                          [16,6],
                          [6, 9]])
        S = (TM.TM @ CS.CM @ TM.M12 @ CS.s_in).T

        I = FittingFramework.generate_model_I(O, S)
        np.testing.assert_allclose(truth, I, rtol=RTOL, atol=ATOL)

    def test_random(self):
        TM = SimpleNamespace(M12=np.diag(np.ones(4)), TM=np.random.random((45,4,4)))
        CS = SimpleNamespace(s_in=np.array([1,0,0,0.]), CM=np.random.random((45,4,4)))
        O = np.random.random((10,4))
        truth = O @ (TM.TM @ CS.CM @ TM.M12 @ CS.s_in).T
        S = (TM.TM @ CS.CM @ TM.M12 @ CS.s_in).T

        I = FittingFramework.generate_model_I(O, S)
        np.testing.assert_allclose(I, truth, rtol=RTOL, atol=ATOL)

@pytest.mark.skip(reason="Depends on SV-style data")
class TestNaNValues(TestCase):

    def setUp(self) -> None:
        self.SoCC_dir = tempfile.mkdtemp()
        self.num_pos = 5
        gen_fake_data.SoCC_multi_day(self.SoCC_dir, numdays=3, shape=(1, 1, self.num_pos), DHS=False, CS_name='may_CS')

        self.CU_NaN_pos = np.random.choice(range(self.num_pos))
        self.TM_NaN_pos = np.random.choice(range(self.num_pos))
        for s, pos in zip([0, 2], [self.CU_NaN_pos, self.TM_NaN_pos]):
            step = np.random.choice(range(10)) + 2  # 2 comes from initial dark and clear
            mod = np.random.choice(range(10))
            hdl = pyfits.open('{:}/day{:}/VISP.C{:03n}.FITS'.format(self.SoCC_dir, s, step), mode='update')
            hdl[mod + 1].data[0, 0, pos] = np.nan
            hdl.flush()
            hdl.close()

        return

    def tearDown(self) -> None:
        self.CMP.cleanup()
        self.TMP.cleanup()
        shutil.rmtree(self.SoCC_dir)

    def test_CU_NaN(self):
        self.CMP, self.TMP, _ = FittingFramework.run_fits(['{}/day0'.format(self.SoCC_dir)], fit_TM=False,
                                                          telescope_db=generic.get_default_telescope_db())

        nan_list = list(self.CMP[0, 0, self.CU_NaN_pos].values())
        truth = np.zeros(len(nan_list))
        truth[-self.CMP.nummod * 4::4] = 1. / self.CMP.nummod
        np.testing.assert_equal(nan_list, truth)

    def test_CU_non_NaN(self):
        self.CMP, self.TMP, _ = FittingFramework.run_fits(['{}/day0'.format(self.SoCC_dir)], fit_TM=False,
                                                          telescope_db=generic.get_default_telescope_db())

        pos = (self.CU_NaN_pos + 1) % self.num_pos # guaranteed not to be the NaN position
        nan_list = list(self.CMP[0, 0, pos].values())
        truth = np.zeros(len(nan_list))
        truth[-self.CMP.nummod * 4::4] = 1. / self.CMP.nummod
        self.assertTrue(np.any(np.not_equal(nan_list, truth)))

    def test_TM_NaN(self):
        dirlist = ['{}/day{}'.format(self.SoCC_dir, i) for i in range(3)]
        self.CMP, self.TMP, _ = FittingFramework.run_fits(dirlist, fit_TM=True, threads=2,
                                                          telescope_db=generic.get_default_telescope_db())

        dummy_TM = np.array([0., 1., 0., 1., 0., 1.])
        np.testing.assert_equal(self.TMP[0, 0, self.CU_NaN_pos], dummy_TM)
        np.testing.assert_equal(self.TMP[0, 0, self.TM_NaN_pos], dummy_TM)

    def test_TM_non_NaN(self):
        dirlist = ['{}/day{}'.format(self.SoCC_dir, i) for i in range(3)]
        self.CMP, self.TMP, _ = FittingFramework.run_fits(dirlist, fit_TM=True, threads=2,
                                                          telescope_db=generic.get_default_telescope_db())

        pos1 = (self.CU_NaN_pos + 1) % self.num_pos
        if pos1 == self.TM_NaN_pos:
            pos1 = (pos1 + 1) % self.num_pos
        pos2 = (self.TM_NaN_pos + 1) % self.num_pos
        if pos2 == self.CU_NaN_pos:
            pos2 = (pos2 + 1) % self.num_pos

        dummy_TM = np.array([0., 1., 0., 1., 0., 1.])
        self.assertTrue(np.any(np.not_equal(self.TMP[0, 0, pos1], dummy_TM)))
        self.assertTrue(np.any(np.not_equal(self.TMP[0, 0, pos2], dummy_TM)))
