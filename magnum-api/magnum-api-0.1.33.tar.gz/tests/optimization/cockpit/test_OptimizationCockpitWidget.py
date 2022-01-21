from unittest import TestCase

import pandas as pd

from magnumapi.optimization.design_variable.DesignVariableFactory import init_genetic_design_variables_with_csv
from magnumapi.optimization.logger.Logger import Logger
from magnumapi.optimization.cockpit.OptimizationCockpitWidget import create_objective_table, transpose_objective_table
from magnumapi.optimization.config.OptimizationConfig import OptimizationConfig
from tests.resource_files import create_resources_path


class TestOptimizationCockpitWidget(TestCase):
    def setUp(self) -> None:
        prefix = 'resources/optimization/'
        logger_path = create_resources_path('%sGeneticOptimizationGlobalMultiIndex.csv' % prefix)
        self.logger_df = pd.read_csv(logger_path)
        self.min_logger_df = Logger.extract_min_rows_from_logger_df(self.logger_df, n_pop=20)

        dv_path = create_resources_path('%smock/design_variables_geometry.csv' % prefix)
        self.dv = init_genetic_design_variables_with_csv(dv_path)

        json_path = create_resources_path('%smock/genetic_optimization_config.json' % prefix)
        self.config = OptimizationConfig.initialize_config(json_path)

    def test_create_objective_table(self):
        # arrange

        # act
        objective_table_df = create_objective_table(self.config, self.min_logger_df, index=0)

        # assert
        objective_table_ref_df = pd.DataFrame(
            {'objective': {'B_3_1': 45.83, 'B_5_1': 25.94, 'MARGMI_0_0': 9.105455625, 'seqv': 1756.2},
             'weights': {'B_3_1': 0.1, 'B_5_1': 0.1, 'MARGMI_0_0': 1.0, 'seqv': 0.001},
             'constraints': {'B_3_1': 0.0, 'B_5_1': 0.0, 'MARGMI_0_0': 0.85, 'seqv': 0.0},
             'objective_weighted': {'B_3_1': 4.583, 'B_5_1': 2.5940000000000003, 'MARGMI_0_0': 8.255455625, 'seqv': 1.7562}}
        )
        pd.testing.assert_frame_equal(objective_table_ref_df, objective_table_df)

    def test_transpose_objective_table(self):
        # arrange

        # act
        objective_table_df = create_objective_table(self.config, self.min_logger_df, index=0)
        objective_table_trans_df = transpose_objective_table(objective_table_df)

        # assert
        objective_table_trans_ref_df = pd.DataFrame(
            {'': {0: 'objective', 1: 'weights', 2: 'constraints', 3: 'objective_weighted'},
             'B_3_1': {0: 45.83, 1: 0.1, 2: 0.0, 3: 4.583},
             'B_5_1': {0: 25.94, 1: 0.1, 2: 0.0, 3: 2.5940000000000003},
             'MARGMI_0_0': {0: 9.105455625, 1: 1.0, 2: 0.85, 3: 8.255455625},
             'seqv': {0: 1756.2, 1: 0.001, 2: 0.0, 3: 1.7562}}
        )
        pd.testing.assert_frame_equal(objective_table_trans_ref_df, objective_table_trans_df)

    # def test_prepare_fractions_for_bar_plot(self):
    #     # arrange
    #
    #     # act
    #     index_act = 0
    #     fractions = prepare_fractions_for_bar_plot(self.dv, self.min_logger_df, index_act)
    #
    #     # assert
    #     fractions_ref = [0.671875, 0.390625, 0.65625, 0.875, 0.25, 0.796875, 0.8125, 0.421875, 0.015625, 0.453125,
    #                      0.421875, 0.296875, 0.84375, 0.375, 0.359375, 0.171875, 0.0, 0.8571428571428571, 1.0,
    #                      0.3333333333333333, 0.42857142857142855, 0.0, 0.0, 1.0, 0.5714285714285714, 0.6666666666666666,
    #                      1.0, 1.0, 1.8125, 0.587890625]
    #     self.assertListEqual(fractions_ref, fractions)

    # def test_prepare_hover_texts_for_bar_plot(self):
    #     # arrange
    #     design_variables = initialize_design_variables(self.dv)
    #
    #     # act
    #     index_act = 0
    #     hover_texts = prepare_hover_texts_for_bar_plot(design_variables, self.min_logger_df, index_act)
    #
    #     # assert
    #     hover_texts_ref = ['value: 7.703, range: [3.000, 10.000]', 'value: 5.734, range: [3.000, 10.000]',
    #                        'value: 7.594, range: [3.000, 10.000]', 'value: 9.125, range: [3.000, 10.000]',
    #                        'value: 4.750, range: [3.000, 10.000]', 'value: 8.578, range: [3.000, 10.000]',
    #                        'value: 8.688, range: [3.000, 10.000]', 'value: 5.953, range: [3.000, 10.000]',
    #                        'value: 0.156, range: [0.000, 10.000]', 'value: 4.531, range: [0.000, 10.000]',
    #                        'value: 4.219, range: [0.000, 10.000]', 'value: 2.969, range: [0.000, 10.000]',
    #                        'value: 8.438, range: [0.000, 10.000]', 'value: 3.750, range: [0.000, 10.000]',
    #                        'value: 3.594, range: [0.000, 10.000]', 'value: 1.719, range: [0.000, 10.000]',
    #                        'value: 0, range: [0, 7]', 'value: 6, range: [0, 7]', 'value: 3, range: [0, 3]',
    #                        'value: 1, range: [0, 3]', 'value: 6, range: [3, 10]', 'value: 7, range: [7, 14]',
    #                        'value: 0, range: [0, 3]', 'value: 20, range: [13, 20]', 'value: 11, range: [7, 14]',
    #                        'value: 2, range: [0, 3]', 'value: 30, range: [27, 30]', 'value: 12, range: [9, 12]',
    #                        'value: 1.453, range: [1.000, 1.250]', 'value: 13175.781, range: [12000.000, 14000.000]']
    #
    #     self.assertListEqual(hover_texts_ref, hover_texts)

    # def test_build_programmable_geometry(self):
    #     model_input_path = create_resources_path('resources/geometry/roxie/16T/16T_rel_slotted.json')
    #     cadata_abs_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
    #     cadata = CableDatabase.read_cadata(cadata_abs_path)
    #     geometry = GeometryFactory.init_slotted_with_json(model_input_path, cadata)
    #
    #     path_str = 'resources/optimization/mock_programmable/design_variables_programmable_geometry.csv'
    #     csv_global_file_path = create_resources_path(path_str)
    #     design_variables_df = pd.read_csv(csv_global_file_path)
    #
    #     json_path = create_resources_path('resources/optimization/config.json')
    #     config = OptimizationConfig.initialize_config(json_path)
    #
    #     prefix = 'resources/optimization/'
    #     logger_path = create_resources_path('%sGeneticOptimizationProgrammableGeometry.csv' % prefix)
    #     logger_df = pd.read_csv(logger_path)
    #
    #     roxie_gen_opt = RoxieGeneticOptimization(config=config,
    #                                              design_variables_df=design_variables_df,
    #                                              geometry=geometry,
    #                                              model_input_path=model_input_path,
    #                                              is_script_executed=True,
    #                                              output_subdirectory_dir='')
    #     widget = OptimizationCockpitWidget(roxie_gen_opt, logger_df, config, design_variables_df)
    #     widget.build()
