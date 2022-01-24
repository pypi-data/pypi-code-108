from unittest import TestCase

import pandas as pd

from magnumapi.cadata.CableDatabase import CableDatabase
from tests.resource_files import create_resources_path, read_csv_as_pd


class TestCableDatabase(TestCase):
    cadata_file_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
    cadata = CableDatabase.read_cadata(cadata_file_path)

    def test_write_json(self):
        json_file_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.json')
        self.cadata.write_json(json_file_path)

    def test_write_cadata(self):
        cadata_file_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2_written.cadata')
        self.cadata.write_cadata(cadata_file_path)

    def test_read_json(self):
        json_file_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.json')
        CableDatabase.read_json(json_file_path)

    def test_get_insulation_dataframe(self):
        # arrange

        # act
        insul_df = self.cadata.get_insul_df()

        # assert
        insul_ref_df = read_csv_as_pd('resources/geometry/roxie/16T/cadata/insul.csv')
        pd.testing.assert_frame_equal(insul_df, insul_ref_df)

    def test_get_remfit_dataframe(self):
        # arrange

        # act
        remfit_df = self.cadata.get_remfit_df()

        # assert
        remfit_ref_df = read_csv_as_pd('resources/geometry/roxie/16T/cadata/remfit.csv')
        pd.testing.assert_frame_equal(remfit_df, remfit_ref_df)

    def test_get_filament_df(self):
        # arrange

        # act
        filament_df = self.cadata.get_filament_df()

        # assert
        filament_ref_df = read_csv_as_pd('resources/geometry/roxie/16T/cadata/filament.csv')
        pd.testing.assert_frame_equal(filament_df, filament_ref_df)

    def test_get_strand_df(self):
        # arrange

        # act
        strand_df = self.cadata.get_strand_df()

        # assert
        strand_ref_df = read_csv_as_pd('resources/geometry/roxie/16T/cadata/strand.csv')
        pd.testing.assert_frame_equal(strand_df, strand_ref_df)

    def test_get_transient_df(self):
        # arrange

        # act
        transient_df = self.cadata.get_transient_df()

        # assert
        transient_ref_df = read_csv_as_pd('resources/geometry/roxie/16T/cadata/transient.csv')
        pd.testing.assert_frame_equal(transient_df, transient_ref_df)

    def test_get_quench_df(self):
        # arrange

        # act
        quench_df = self.cadata.get_quench_df()

        # assert
        quench_ref_df = read_csv_as_pd('resources/geometry/roxie/16T/cadata/quench.csv')
        pd.testing.assert_frame_equal(quench_df, quench_ref_df)

    def test_get_cable_df(self):
        # arrange

        # act
        cable_df = self.cadata.get_cable_df()

        # assert
        cable_ref_df = read_csv_as_pd('resources/geometry/roxie/16T/cadata/cable.csv')
        cable_ref_df = cable_ref_df.fillna('')
        pd.testing.assert_frame_equal(cable_df, cable_ref_df)

    def test_get_conductor_df(self):
        # arrange

        # act
        conductor_df = self.cadata.get_conductor_df()

        # assert
        conductor_ref_df = read_csv_as_pd('resources/geometry/roxie/16T/cadata/conductor.csv')
        conductor_ref_df = conductor_ref_df.fillna('')
        pd.testing.assert_frame_equal(conductor_df, conductor_ref_df)

    def test_get_insul_definition_for_condname(self):
        # arrange
        condname = '16TOL8'

        # act
        insul_definition = self.cadata.get_insul_definition(condname)

        # assert
        self.assertEqual('16TINS', insul_definition.name)
        self.assertAlmostEqual(0.075, insul_definition.thickness, places=2)
        self.assertAlmostEqual(0.075, insul_definition.width, places=2)
        self.assertEqual('EUROCIRCOL                    ', insul_definition.comment)

    def test_get_remfit_definition_for_condname(self):
        # arrange
        condname = '16TOL8'

        # act
        remfit_definition = self.cadata.get_remfit_definition(condname)

        # assert
        self.assertEqual('LASAEU', remfit_definition.name)
        self.assertAlmostEqual(2.67845e+11, remfit_definition.c1, places=5)
        self.assertAlmostEqual(2.93800e+01, remfit_definition.c2, places=5)
        self.assertAlmostEqual(1.60000e+01, remfit_definition.c3, places=5)
        self.assertAlmostEqual(9.60000e-01, remfit_definition.c4, places=5)
        self.assertAlmostEqual(1.52000e+00, remfit_definition.c5, places=5)
        self.assertAlmostEqual(5.00000e-01, remfit_definition.c6, places=5)
        self.assertAlmostEqual(2.00000e+00, remfit_definition.c7, places=5)
        self.assertAlmostEqual(0.00000e+00, remfit_definition.c8, places=5)
        self.assertAlmostEqual(0.00000e+00, remfit_definition.c9, places=5)
        self.assertAlmostEqual(0.00000e+00, remfit_definition.c10, places=5)
        self.assertAlmostEqual(0.00000e+00, remfit_definition.c11, places=5)

        self.assertEqual(11, remfit_definition.type)
        self.assertEqual('                              ', remfit_definition.comment)

    def test_get_filament_definition_for_condname(self):
        # arrange
        condname = '16TOL8'

        # act
        filament_definition = self.cadata.get_filament_definition(condname)

        # assert
        self.assertEqual('NB3SN', filament_definition.name)
        self.assertAlmostEqual(0, filament_definition.d_fil_in, places=1)
        self.assertAlmostEqual(50.0, filament_definition.d_fil_out, places=1)
        self.assertEqual('LASAEU', filament_definition.fit_j_c)
        self.assertEqual('LASAEU', filament_definition.fit_perp)
        self.assertEqual('NB2SN TWENTE                  ', filament_definition.comment)

    def test_get_strand_definition_for_condname(self):
        # arrange
        condname = '16TOL8'

        # act
        strand_definition = self.cadata.get_strand_definition(condname)

        # assert

        self.assertAlmostEqual(14.0, strand_definition.b_ref, places=1)
        self.assertEqual('EUROCIRCOL outer              ', strand_definition.comment)
        self.assertAlmostEqual(2359.0, strand_definition.j_c_at_b_ref_t_ref, places=1)
        self.assertEqual('STR07', strand_definition.name)
        self.assertEqual(100, strand_definition.rrr)
        self.assertAlmostEqual(4.2, strand_definition.temp_ref, places=1)
        self.assertAlmostEqual(2.2, strand_definition.f_cu_nocu, places=1)
        self.assertAlmostEqual(493.3, strand_definition.dj_c_over_db, places=1)
        self.assertAlmostEqual(0.7, strand_definition.d_strand, places=1)

    def test_get_transient_definition_for_condname_default(self):
        # arrange
        condname = '16TOL8'

        # act
        transient_definition = self.cadata.get_transient_definition(condname)

        # assert
        self.assertEqual('', transient_definition.comment)
        self.assertEqual('', transient_definition.name)
        self.assertAlmostEqual(0.0, transient_definition.r_a, places=1)
        self.assertAlmostEqual(0.0, transient_definition.r_c, places=1)
        self.assertAlmostEqual(0.0, transient_definition.res_0, places=1)
        self.assertAlmostEqual(0.0, transient_definition.dres_over_db, places=1)
        self.assertAlmostEqual(0.0, transient_definition.l_fil_tp, places=1)
        self.assertAlmostEqual(0.0, transient_definition.f_strand_fill, places=1)

    def test_get_transient_definition_for_condname_nondefault(self):
        # arrange
        condname = 'YELLONIN'

        # act
        transient_definition = self.cadata.get_transient_definition(condname)

        # assert
        self.assertEqual('LHC cable resitances          ', transient_definition.comment)
        self.assertEqual('TRANS1', transient_definition.name)
        self.assertAlmostEqual(1e-7, transient_definition.r_a, places=7)
        self.assertAlmostEqual(1e-6, transient_definition.r_c, places=7)
        self.assertAlmostEqual(0.0, transient_definition.res_0, places=1)
        self.assertAlmostEqual(0.0, transient_definition.dres_over_db, places=1)
        self.assertAlmostEqual(0.0, transient_definition.l_fil_tp, places=1)
        self.assertAlmostEqual(0.0, transient_definition.f_strand_fill, places=1)

    def test_get_quench_definition_for_condname(self):
        # arrange
        condname = '16TOL8'

        # act
        quench_definition = self.cadata.get_quench_definition(condname)

        # assert
        self.assertEqual('NIST                          ', quench_definition.comment)
        self.assertEqual('NB3SN', quench_definition.name)
        self.assertEqual(3, quench_definition.res_cu)
        self.assertEqual(3, quench_definition.cp_cu)
        self.assertEqual(3, quench_definition.k_cu)
        self.assertEqual(4, quench_definition.cp_fill)
        self.assertEqual(0, quench_definition.perc_he)
        self.assertEqual(2, quench_definition.cp_ins)
        self.assertEqual(5, quench_definition.k_ins)
        self.assertEqual(3, quench_definition.cp_sc)

    def test_get_quench_definition_for_condname_empty(self):
        # arrange
        condname = '16TIL8'

        # act
        quench_definition = self.cadata.get_quench_definition(condname)

        # assert
        self.assertEqual('', quench_definition.comment)
        self.assertEqual('', quench_definition.name)
        self.assertEqual('', quench_definition.res_cu)
        self.assertEqual('', quench_definition.cp_cu)
        self.assertEqual('', quench_definition.k_cu)
        self.assertEqual('', quench_definition.cp_fill)
        self.assertEqual('', quench_definition.perc_he)
        self.assertEqual('', quench_definition.cp_ins)
        self.assertEqual('', quench_definition.k_ins)
        self.assertEqual('', quench_definition.cp_sc)


    def test_get_cable_definition_for_condname_index_error(self):
        # arrange
        condname = 'WRONG_COND_NAME'

        # act
        # assert
        with self.assertRaises(KeyError) as context:
            self.cadata.get_cable_definition(condname)

        self.assertTrue('Conductor name WRONG_COND_NAME not present in conductor definitions.'
                        in str(context.exception))

    def test_get_cable_definition_for_condname(self):
        # arrange
        condname = '16TOL8'

        # act
        cable_definition = self.cadata.get_cable_definition(condname)

        # assert
        self.assertEqual('16TOLG8', cable_definition.name)
        self.assertAlmostEqual(13.65, cable_definition.width, places=2)
        self.assertAlmostEqual(1.204, cable_definition.thickness_i, places=2)
        self.assertAlmostEqual(1.3231, cable_definition.thickness_o, places=2)
        self.assertEqual(37, cable_definition.n_s)
        self.assertEqual(100, cable_definition.l_tp)
        self.assertEqual(0, cable_definition.f_degrad)
        self.assertEqual('EUROCIRCOL 37 STR             ', cable_definition.comment)

    def test_get_conductor_definition_for_condname(self):
        # arrange
        condname = '16TOL8'

        # act
        cond_definition = self.cadata.get_conductor_definition(condname)

        # assert
        self.assertEqual('16TOLG8', cond_definition.cable_geom)
        self.assertEqual('eurocircol                    ', cond_definition.comment)
        self.assertEqual('NB3SN', cond_definition.filament)
        self.assertEqual('16TINS', cond_definition.insulation)
        self.assertEqual('16TOL8', cond_definition.name)
        self.assertEqual('NB3SN', cond_definition.quench_mat)
        self.assertEqual('STR07', cond_definition.strand)
        self.assertAlmostEqual(1.9, cond_definition.temp_ref, places=1)
        self.assertEqual('NONE', cond_definition.transient)
        self.assertEqual(1, cond_definition.type)
