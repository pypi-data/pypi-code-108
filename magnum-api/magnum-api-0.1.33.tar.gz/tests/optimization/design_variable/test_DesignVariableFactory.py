from magnumapi.optimization.design_variable import DesignVariableFactory
from tests.resource_files import create_resources_path


def test_decode_chromosome_with_global_parameter():
    # arrange
    csv_global_file_path = create_resources_path('resources/optimization/optim_input_enlarged_with_global.csv')

    # act
    dv_gens = DesignVariableFactory.init_genetic_design_variables_with_csv(csv_global_file_path)

    # assert
    assert len(dv_gens) == 29
