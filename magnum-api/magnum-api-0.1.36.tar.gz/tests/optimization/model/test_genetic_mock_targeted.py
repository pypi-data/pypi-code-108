# import shutil
# from io import StringIO
# from unittest.mock import patch

# import numpy as np
# import pandas as pd

# from magnumapi.commons import json_file
# from magnumapi.optimization.GeneticOptimization import GeneticOptimizationBuilder
# from magnumapi.optimization.config.OptimizationConfig import OptimizationConfig
# from tests.resource_files import create_resources_path


# def test_optimize_mock_targeted(mocker):
#     np.random.seed(0)
#     mocker.patch("magnumapi.optimization.model.NotebookExecutor.Executor.calculate_figures_of_merit",
#                  return_value={'B_3_1': 1, 'B_5_1': 2, 'MARGMI_0_0': 3, 'seqv': 4})
#     mocker.patch('magnumapi.optimization.logger.Logger.Logger.save_logger')

#     # arrange
#     json_path = create_resources_path('resources/optimization/mock_targeted/genetic_optimization_config.json')
#     config = OptimizationConfig.initialize_config(json_path)
#     root_output_abs_path = create_resources_path('resources/optimization/')
#     config.root_abs_path = root_output_abs_path
#     config.output_abs_path = root_output_abs_path
#     model_input_path = create_resources_path('resources/optimization/mock_targeted/16T_rel.json')
#     model_input_temp_path = create_resources_path('resources/optimization/mock_targeted/16T_rel_temp.json')
#     shutil.copy(model_input_path, model_input_temp_path)

#     # # optimization
#     output_subdirectory_dir = create_resources_path('resources/optimization')
#     gen_opt = GeneticOptimizationBuilder.build(config, output_subdirectory_dir=output_subdirectory_dir)

#     # act
#     with patch('sys.stdout', new=StringIO()) as fake_out:
#         gen_opt.optimize()

#     # assert
#     output_ref = """Generation: 0
# 	Individual: 0
# 	Individual: 1
# 	Individual: 2
# 	Individual: 3
# [2.454, 2.454, 2.454, 2.454]
# Generation: 1
# 	Individual: 0
# 	Individual: 1
# 	Individual: 2
# 	Individual: 3
# [2.454, 2.454, 2.454, 2.454]
# Generation: 2
# 	Individual: 0
# 	Individual: 1
# 	Individual: 2
# 	Individual: 3
# [2.454, 2.454, 2.454, 2.454]
# Generation: 3
# 	Individual: 0
# 	Individual: 1
# 	Individual: 2
# 	Individual: 3
# [2.454, 2.454, 2.454, 2.454]"""

#     assert output_ref == fake_out.getvalue().strip()

#     for i in range(4):
#         model_path = create_resources_path('resources/optimization/mock_programmable/16T_rel_slotted_temp_%d.json' % i)
#         model_ref_path = create_resources_path('resources/optimization/mock_programmable/16T_rel_slotted_temp_%d_ref.json' % i)

#         model = json_file.read(model_path)
#         model_ref = json_file.read(model_ref_path)
#         pd.testing.assert_frame_equal(pd.DataFrame(model['block_defs']),
#                                       pd.DataFrame(model_ref['block_defs']))
#         pd.testing.assert_frame_equal(pd.DataFrame(model['layer_defs']),
#                                       pd.DataFrame(model_ref['layer_defs']))
