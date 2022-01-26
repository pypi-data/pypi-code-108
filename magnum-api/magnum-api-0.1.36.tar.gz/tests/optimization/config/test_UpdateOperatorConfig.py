from magnumapi.commons import json_file
from magnumapi.optimization.config.UpdateOperatorConfig import UpdateOperatorConfig
from tests.resource_files import create_resources_path


def test_update_operator_config_default():
    # arrange
    # act
    update_operator_config_path = create_resources_path('resources/optimization/config/default_update_operator_config.json')
    update_operator_config_dct = json_file.read(update_operator_config_path)
    update_operator_config = UpdateOperatorConfig.initialize_config(update_operator_config_dct)

    # assert
    assert update_operator_config.type == "default"
    assert update_operator_config.params == {}
    assert update_operator_config.mutation_operator.type == "default"
    assert update_operator_config.mutation_operator.params == {"r_mut": 0.5}
    assert update_operator_config.selection_operator.type == "default"
    assert update_operator_config.selection_operator.params == {"k_selection": 3}
    assert update_operator_config.crossover_operator.type == "default"
    assert update_operator_config.crossover_operator.params == {"r_cross": 0.5}


def test_update_operator_config_elitism():
    # arrange
    # act
    update_operator_config_path = create_resources_path('resources/optimization/config/elitism_update_operator_config.json')
    update_operator_config_dct = json_file.read(update_operator_config_path)
    update_operator_config = UpdateOperatorConfig.initialize_config(update_operator_config_dct)

    # assert
    assert update_operator_config.type == "elitism"
    assert update_operator_config.params == {"n_elite": 2}
    assert update_operator_config.mutation_operator.type == "default"
    assert update_operator_config.mutation_operator.params == {"r_mut": 0.5}
    assert update_operator_config.selection_operator.type == "default"
    assert update_operator_config.selection_operator.params == {"k_selection": 3}
    assert update_operator_config.crossover_operator.type == "default"
    assert update_operator_config.crossover_operator.params == {"r_cross": 0.5}
