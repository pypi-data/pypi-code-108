import numpy as np

from magnumapi.commons import json_file
from magnumapi.optimization.config.UpdateOperatorConfig import UpdateOperatorConfig
from magnumapi.optimization.design_variable import DesignVariableFactory
from magnumapi.optimization.genetic.crossover_operators import CrossOverOperator
from magnumapi.optimization.genetic.mutation_operators import MutationOperator
from magnumapi.optimization.genetic.selection_operators import SelectionOperator
from magnumapi.optimization.genetic.update_operators import UpdateOperator, ElitismUpdateOperator, UpdateOperatorFactory
from tests.resource_files import create_resources_path
from magnumapi.optimization.design_variable.Individual import Individual

csv_global_file_path = create_resources_path(
    'resources/optimization/mock_programmable/design_variables_programmable_geometry.csv')
dv_gens = DesignVariableFactory.init_genetic_design_variables_with_csv(csv_global_file_path)


individuals = []
for score in [10, 20, 1, 5]:
    individual = Individual(dv_gens)
    individual.score = score
    individuals.append(individual)


def test_update():
    np.random.seed(0)
    # arrange
    crossover_operator = CrossOverOperator(r_cross=0)
    mutation_operator = MutationOperator(r_mut=0)
    selection_operator = SelectionOperator(k_selection=2)

    update_operator = UpdateOperator(crossover_operator=crossover_operator,
                                     mutation_operator=mutation_operator,
                                     selection_operator=selection_operator)

    # act
    individuals_updated = update_operator.update_generation(individuals)

    # assert
    assert id(individuals_updated[0]) != id(individuals[2])
    assert id(individuals_updated[1]) != id(individuals[3])
    assert id(individuals_updated[2]) != id(individuals[0])
    assert id(individuals_updated[3]) != id(individuals[1])


def test_build_default():
    # arrange
    update_operator_config_path = create_resources_path(
        'resources/optimization/config/default_update_operator_config.json')
    update_operator_config_dct = json_file.read(update_operator_config_path)
    update_operator_config = UpdateOperatorConfig.initialize_config(update_operator_config_dct)
    update_operator = UpdateOperatorFactory.build(update_operator_config)

    assert isinstance(update_operator, UpdateOperator)
    assert isinstance(update_operator.mutation_operator, MutationOperator)
    assert update_operator.mutation_operator.r_mut == 0.5
    assert isinstance(update_operator.selection_operator, SelectionOperator)
    assert update_operator.selection_operator.k_selection == 3
    assert isinstance(update_operator.crossover_operator, CrossOverOperator)
    assert update_operator.crossover_operator.r_cross == 0.5


def test_update_with_config():
    np.random.seed(0)
    # arrange
    update_operator_config_path = create_resources_path(
        'resources/optimization/config/default_update_operator_config.json')
    update_operator_config_dct = json_file.read(update_operator_config_path)
    update_operator_config = UpdateOperatorConfig.initialize_config(update_operator_config_dct)
    update_operator = UpdateOperatorFactory.build(update_operator_config)

    # act
    individuals_updated = update_operator.update_generation(individuals)

    # assert
    assert id(individuals_updated[0]) != id(individuals[2])
    assert id(individuals_updated[1]) != id(individuals[3])
    assert id(individuals_updated[2]) != id(individuals[0])
    assert id(individuals_updated[3]) != id(individuals[1])


def test_update_elitism():
    np.random.seed(0)
    # arrange
    crossover_operator = CrossOverOperator(r_cross=0)
    mutation_operator = MutationOperator(r_mut=0)
    selection_operator = SelectionOperator(k_selection=2)

    update_operator = ElitismUpdateOperator(crossover_operator=crossover_operator,
                                            mutation_operator=mutation_operator,
                                            selection_operator=selection_operator,
                                            n_elite=2)

    # act
    individuals_updated = update_operator.update_generation(individuals)

    # assert
    assert id(individuals_updated[0]) == id(individuals[2])
    assert id(individuals_updated[1]) == id(individuals[3])
    assert id(individuals_updated[2]) != id(individuals[0])
    assert id(individuals_updated[3]) != id(individuals[1])


def test_build_elitism():
    # arrange
    update_operator_config_path = create_resources_path(
        'resources/optimization/config/elitism_update_operator_config.json')
    update_operator_config_dct = json_file.read(update_operator_config_path)
    update_operator_config = UpdateOperatorConfig.initialize_config(update_operator_config_dct)
    update_operator = UpdateOperatorFactory.build(update_operator_config)

    assert isinstance(update_operator, ElitismUpdateOperator)
    assert update_operator.n_elite == 2
    assert isinstance(update_operator.mutation_operator, MutationOperator)
    assert update_operator.mutation_operator.r_mut == 0.5
    assert isinstance(update_operator.selection_operator, SelectionOperator)
    assert update_operator.selection_operator.k_selection == 3
    assert isinstance(update_operator.crossover_operator, CrossOverOperator)
    assert update_operator.crossover_operator.r_cross == 0.5


def test_update_elitism_with_config():
    np.random.seed(0)
    # arrange
    update_operator_config_path = create_resources_path(
        'resources/optimization/config/elitism_update_operator_config.json')
    update_operator_config_dct = json_file.read(update_operator_config_path)
    update_operator_config = UpdateOperatorConfig.initialize_config(update_operator_config_dct)
    update_operator = UpdateOperatorFactory.build(update_operator_config)

    # act
    individuals_updated = update_operator.update_generation(individuals)

    # assert
    assert id(individuals_updated[0]) == id(individuals[2])
    assert id(individuals_updated[1]) == id(individuals[3])
    assert id(individuals_updated[2]) != id(individuals[0])
    assert id(individuals_updated[3]) != id(individuals[1])
